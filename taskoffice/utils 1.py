"""
Description: This file contains class for querying cockroach db and solr.

a) get_df_sparksolr - Creating a spark dataframe from solr database.
b) get_tagger_df_sparksolr - Creating a spark dataframe from the tagger collection's Solr database.
c) get_df_event - Creating a spark dataframe from the event table's cockroach database.
d) store_df - Stored dataframe into solr database.

"""

import json
import os
import re
import time
import requests
from requests.auth import HTTPBasicAuth

# Third-party imports
import aiohttp
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from pyspark.sql import functions as F

# Local imports
from common.env_data import get_env_data


solr_config, _, _, _, _, _, _ = get_env_data()
basicAuth = HTTPBasicAuth(solr_config["user"], solr_config["password"])
base_solr_url = f"http://{solr_config['host']}:{solr_config['port']}/solr/"

openai_key = os.environ.get("OPENAI_CREDENTIALS")


# This function returns spark dataframe from solr collection
async def get_df_sparksolr_search(
    cockroach_db_pool,
    logger,
    args,
    spark,
    collection,
    field_list=None,
    filter_list=None,
    concate_item_cols=None,
    items_list=None,
):
    logger.info(f"this is the solr collection type:{type(collection)}")
    try:
        size = requests.get(f"{base_solr_url}{collection}/select?q=*:*", auth=basicAuth).json()["response"]["numFound"]
    except Exception as e:
        logger.exception(e)
        logger.exception("Couldn't query solr collection!")
        return None

    flag = False
    if field_list != None and field_list != "None":
        columns_list = field_list
        fields = ",".join(columns_list)
        res = requests.get(
            f"{base_solr_url}{collection}/select?q=*:*&rows={size}&fl={fields}",
            auth=basicAuth,
        ).json()["response"]["docs"]
    else:
        item_id_col = "sku_esi"
        res = requests.get(
            f"{base_solr_url}{collection}/select?q=*:*&rows={size}",
            auth=basicAuth,
        ).json()[
            "response"
        ]["docs"]

    # Query solr using spark-solr connector with options defined in signal_opts
    sparksolrDF = spark.createDataFrame(res)
    sparksolrDF = sparksolrDF.dropDuplicates()
    logger.info(f"spark solr dataframe")
    sparksolrDF.show(20)
    logger.info(f"spark solr df schema : {sparksolrDF.printSchema()}")

    try:
        # Returning exclude categories list
        exclude_categories_res = cockroach_db_pool.execute(
            f"SELECT categories FROM excluded_categories where tenant_id = '{args.tenant}'\
                  and workspace_id = '{args.wksp}' and environment_id = '{args.env}';"
        )
        try:
            category_list = [str(category).strip("'\"") for category in exclude_categories_res[0][0].split(",")]
        except:
            category_list = []
        exclude_categories = tuple(category_list)

        # Returning exclude skus list
        exclude_skus_res = cockroach_db_pool.execute(
            f"SELECT skus FROM excluded_skus where tenant_id = '{args.tenant}'\
                  and workspace_id = '{args.wksp}' and environment_id = '{args.env}';"
        )
        try:
            skus_list = [str(sku).strip("'\"") for sku in exclude_skus_res[0][0].split(",")]
        except:
            skus_list = []
        exclude_skus = tuple(skus_list)
        logger.info(f"exclude categories::{exclude_categories} && exclude skus::{exclude_skus}")

        if len(exclude_categories) != 0 or len(exclude_skus) != 0:
            exclude_skus = ",".join(exclude_skus)
            exclude_categories = list(exclude_categories)
            sparksolrDF_ = sparksolrDF.withColumn(
                "exclude_categories",
                F.array([F.lit(x) for x in exclude_categories]),
            )
            sparksolrDF_ = sparksolrDF_.withColumn("exclude_skus", F.lit(exclude_skus))
            sparksolrDF = sparksolrDF_.filter(
                (F.size(F.array_intersect("exclude_categories", "category_ids_esai")) == 0)
                & (~F.col("exclude_skus").contains(F.col("sku_for_analytics_esli")))
            ).drop("exclude_categories", "exclude_skus")
            # if flag:
            #     sparksolrDF = sparksolrDF.drop("category_ids_esai")

        logger.info(f"Items count after remove exclude categories and skus {sparksolrDF.count()}")

    except Exception as e:
        logger.exception(e)
        logger.exception("Couldn't query solr collection!")
    return sparksolrDF


async def get_tagger_df_sparksolr(logger, args, spark, type):
    collection = args.solr_tagger_collection_name

    try:
        size = requests.get(f"{base_solr_url}{collection}/select?q=*:*", auth=basicAuth).json()["response"]["numFound"]

    except Exception as solr_query_error:
        logger.exception(f"Couldn't query solr collection!:{solr_query_error}")
        return None

    try:
        res = requests.get(
            f"{base_solr_url}{collection}/select?q=*:*&rows={size}&fl=surface_form,canonical_form,type,is_user_defined,created_by,confidence,frequency,actual_form,display_form,environment_id,tenant_id,workspace_id,status",
            auth=basicAuth,
        ).json()["response"]["docs"]

        if len(res) == 0:
            return None

        taggerDF = spark.createDataFrame(res)
        taggerDF = taggerDF.dropDuplicates()
        schema = taggerDF.schema
        logger.info(f"taggerDF Schema :{taggerDF.printSchema()}")
        tempDF = spark.createDataFrame([], schema=schema)

        if type == "phr":
            tempDF1 = taggerDF.where(taggerDF.type == "PHRASES")
            tempDF = tempDF.unionByName(tempDF1)

        elif type == "syn":
            tempDF2 = taggerDF.where(taggerDF.type == "SYNONYMS")
            tempDF = tempDF.unionByName(tempDF2)

        elif type == "spl":
            tempDF3 = taggerDF.where(taggerDF.type == "SPELLCHECK")
            tempDF = tempDF.unionByName(tempDF3)

        taggerDF = tempDF.dropDuplicates()

    except Exception as solr_query_error:
        logger.exception(f"Couldn't query solr collection!:{solr_query_error}")

        return None

    taggerDF.show()

    return taggerDF


# Function will store the data into solr dataframe
async def store_df(logger, args, df):
    collection = args.solr_tagger_collection_name
    docs = df.toJSON().map(json.loads).collect()
    logger.info(f"Indexing into solr")

    try:
        response = requests.post(
            base_solr_url + collection + "/update?commit=true",
            json=docs,
            auth=basicAuth,
        ).json()
        logger.info("\nresponse: %s\n", response)

    except Exception as solr_index_error:
        logger.exception(f"Error while indexing into Solr!--{solr_index_error}")
    return


# function to call singular plural api
async def singular_plural_inference(args, word):
    parameters = {
        "environment_id": f"{args.env}",
        "workspace_id": f"{args.wksp}",
        "tenant_id": f"{args.tenant}",
        "channel_ids": f"{args.channel_ids}",
        "channel_locale": f"{args.channel_locale}",
        "search_query": f"{word}",
        "internal_query": True,
    }
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        singular_inference_api = "http://search-inference-api-svc:8082/api/v1/get-singular-plural"
        async with session.post(singular_inference_api, json=parameters, headers=headers) as response:
            text_response = await response.text()

            # Check if response is empty or None
            if not text_response:
                print("Response is empty, returning []")
                return []

            try:
                fetched_result = json.loads(text_response)
            except json.JSONDecodeError:
                print("Error decoding JSON response, returning []")
                return []

            # Optionally, ensure expected key exists in the result
            if not fetched_result or "inflected_words" not in fetched_result:
                print("Fetched result is empty or missing 'inflected_words', returning []")
                return []

            print("Response:✅️", fetched_result)
            unique_words = set()
            for words in fetched_result["inflected_words"].values():
                unique_words.update(words)
            unique_word_list = list(unique_words)
            print(f"List before sending to main function:🟢 {unique_word_list}")
            return unique_word_list


class ColorClusters(BaseModel):
    clusters: dict = Field(..., description="Dictionary of color clusters")


async def similar_colors_mapper(colors_list):

    result = list(set(colors_list))
    colors_list = []
    for color in result:
        # split on either "/" or ","
        parts = re.split(r"[\/,]", color)
        colors_list.extend(part for part in parts if part)

    SYSTEM_PROMPT = """You are a color naming and grouping expert.

    Your task is to analyze a given list of input color names (even if informal or non-standard) and group them by mapping each to the **closest matching CSS3 named color** from the predefined list. Use your knowledge of color names and shades to match creatively and logically.
    
    Steps:
    1. **Mapping**:
    - For each input color, match it to the most visually or semantically similar color in the standard CSS3 color list.
    - Use human perception of colors (e.g., "peach" is close to "peachpuff", "midnight" maps to "midnightblue", "dark grey space" to "darkgray", etc.).
    - Be lenient in spelling and descriptive differences.

    2. **Semantic Clustering**:
    - Group related CSS3 colors into broader, semantic families (e.g., "crimson" and "maroon" into a "red" family; "lightgray", "darkgray", and "gray" into a "gray" family; "navy", "mediumblue", and "blue" into a "blue" family).
    - Use common color semantics (red, green, blue, yellow/amber, purple, pink, brown, gray, etc.) to define these families.

    3. **Grouping**:
    - After mapping each input to its closest CSS3 color, assign each input to the semantic family cluster corresponding to its CSS3 match.
    - Return a dictionary where each **key** is a semantic color family name, and the **value** is a list of original input names that matched any CSS3 color within that family.

    4. **Generate Minimum Colors**:
    - Always generate minimum 5-7 colors for each family.

    Output format:
    - Provide output as a JSON dictionary with keys as semantic color families and values as lists of matched input names.
    - Preserve the casing of the original input names in values.
    """

    # Prompt template updated
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Group these colors: {input_colors}\n{format_instructions}"),
        ]
    )

    # OpenAI Model
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        request_timeout=120,
        max_retries=0,
        api_key=openai_key,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    # Chain with parser
    chain = prompt | model | JsonOutputParser()

    final_dict = {}

    batch_size = 100
    for start in range(0, len(colors_list), batch_size):
        try:
            batch = colors_list[start : start + batch_size]
            result = chain.invoke(
                {
                    "input_colors": batch,
                    "format_instructions": JsonOutputParser(pydantic_object=ColorClusters).get_format_instructions(),
                }
            )
            result = eval(json.dumps(result, indent=2))
            colors_map = result["clusters"]
            for key, value in colors_map.items():
                # for v in value:
                #     final_dict[v] = value
                for v in value:
                    value = list(set(value))
                    if v in final_dict:
                        final_dict[v].extend(value)
                    else:
                        final_dict[v] = value

        except Exception as e:
            print(f"error while grouping similar colors::::{e}")
            time.sleep(60)

    color_dict = {}
    for key, value in final_dict.items():
        color_dict[key] = list(set(value))

    return color_dict


async def add_singular_plural(word, inflect_engine):
    """
    Convert words to their singular and plural forms, returning a list of lists.
    Each inner list contains unique singular and plural variations for each word.

    Args:
        words: List of words to process
        package: Dictionary containing inflect_words engine

    Returns:
        List of lists where each inner list contains unique singular/plural forms
        Example: [["cat", "cats"], ["dog", "dogs"], ["child", "children"]]
    """
    # result_list = []

    # for word in words:
    # Get singular and plural forms
    singular = inflect_engine.singular_noun(word)
    plural = inflect_engine.plural(word)

    # Create set to store unique forms, starting with original word
    word_forms = {word.lower()}

    # Add singular form if it exists, is not boolean, and is different from original
    if singular and not isinstance(singular, bool):
        word_forms.add(singular.lower())

    # Add plural form if it exists, is not boolean, and is different from original
    if plural and not isinstance(plural, bool):
        word_forms.add(plural.lower())

    # Convert set to sorted list for consistent ordering and append to result
    unique_forms = list(word_forms)
    # result_list.append(unique_forms)
    return unique_forms
