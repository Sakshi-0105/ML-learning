import asyncio
import concurrent.futures
import logging
import os
import time
import random
import pandas as pd
import tiktoken
from langchain_openai import ChatOpenAI
from tqdm import tqdm
from datetime import datetime

arguments = loggers = None

# Define arguments and logger
class Args:
    domain = "e-commerce"
    website_details = "Sports and lifestyle store"
    prompt_instruction = ""
    generation_example = ""
    env = "prod"
    tenant = "tenant1"
    wksp = "wksp1"
    channel_ids = "ch1"
    channel_locale = "en"

class Logger:
    def info(self, msg): print(msg)
# Function to count tokens for cost estimation

def count_tokens(text, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


# Function to process each query with a specific model
def process_query_with_model(query: str, model_name: str, api_key: str):
    start_time = time.time()
    time.sleep(random.uniform(0.2, 0.8))  # Avoid rate limiting

    llm = ChatOpenAI(
        temperature=1, model=model_name, api_key=api_key, timeout=30, max_retries=2
    )
    try:
        messages = [
            {
                "role": "system",
                "content": f"""
                You are a {arguments.domain} expert. Your task is to generate high-quality, user-friendly auto-suggest search phrases based on the provided product text data.
                Website details:
                    {arguments.website_details}
                Guidelines:
                    If you don't have enough information to generate a phrase, you can skip that information and use rest of information.
                    Don't give only special characters, and meaningless words until it's name like brand name, color name, and so on as output.
                    Don't add extra words or phrases that are not present in the product details. 
                    Use only the product details for generating the phrases.
                    Generate a mix of two-word, three-word, and four-word phrases (maximum).
                    Focus on realistic, concise, and user-relevant suggestions. Avoid unnatural or overly generic combinations.
                    If multiple colors are mentioned, include separate phrases for each color.
                    Ensure the output follows the fixed format shown below.
                    In Example below which type of good phrases which are user-friendly and relevant to the user.
                    For example 'Muscle Pullover', Cotton Sleeveless are not good but user-friendly are 'Muscle Pullover Hoodie', 'Cotton Sleeveless Hoodie' is good.
                    {arguments.prompt_instruction}
                    Example for Generated phrases and Expected phrases:
                    Query: id: P-e0d2a8d7-f65c-475d-8684-ede91cf612a3-44663-1 & product_sku: TF419953 & product name: Men's Navy Atlanta Braves Jersey Muscle Sleeveless Pullover Hoodie, 
                           brand: Profile & main category, sub-category:['Men', "Men's sports wear"], 
                           colors: & Extra information: ['Cotton', 'Machine Wash', 'Tumble Dry Low']
                    Generated Phrases: P-e0d2a8d7-f65c-475d-8684-ede91cf612a3-44663-1, TF419953: Navy Jersey, Braves Hoodie, Muscle Pullover, Sleeveless Hoodie, Cotton Jersey, Navy Braves Jersey, Muscle Sleeveless Pullover, Cotton Sleeveless Hoodie
                    Expected phrases: P-e0d2a8d7-f65c-475d-8684-ede91cf612a3-44663-1, TF419953: Navy Jersey, Braves Hoodie, Sleeveless Hoodie, Cotton Jersey, Navy Braves Jersey, Cotton Sleeveless Hoodie, sports wear Hoodie, sports wear Jersey, men's Hoodie, men's Jersey
                    {arguments.generation_example}
                    Output Format:
                    Keywords: id, product_sku: phrase1, phrase2, phrase3, ...
                Ensure the output strictly adheres to the fixed format and excludes words from the product name while focusing on high-quality, user-relevant search suggestions.
                It's user-come and search on my website, so please ensure the phrases are user-friendly. I want to better search experience for my users.
                """,
            },
            {"role": "user", "content": str(query)},
        ]

        result = llm.invoke(messages).content
        phrases = result.split("Keywords:")[-1].strip().split("\n\n")[0]
        latency = time.time() - start_time
        input_tokens = count_tokens(str(messages), model_name)
        output_tokens = count_tokens(phrases, model_name)

        # Calculate cost (based on 2025 pricing)
        if model_name == "gpt-4o-mini":
            cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
        else:  # gpt-5-nano
            cost = (input_tokens * 0.05 + output_tokens * 0.40) / 1_000_000

        return {
            "query": str(query),
            "model": model_name,
            "phrases": phrases,
            "latency": latency,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
        }
    except Exception as e:
        loggers.info(f"Error processing query with {model_name}: {query}, Error: {e}")
        return {
            "query": str(query),
            "model": model_name,
            "phrases": f"Error: {e}",
            "latency": time.time() - start_time,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0,
        }


# Main function to test models and generate Excel
async def generate_product_suggestions(
    product_data: list, args: object, logger: object
) -> bool:

    global arguments
    global loggers
    arguments, loggers = args, logger
    api_key = os.getenv("OPENAI_API_KEY")

    # Models to test
    models = ["gpt-4o-mini", "gpt-5-nano"]
    results = []

    # Process queries for each model concurrently
    for model_name in models:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            model_results = list(
                tqdm(
                    executor.map(
                        lambda query: process_query_with_model(
                            query, model_name, api_key
                        ),
                        product_data,
                    ),
                    total=len(product_data),
                    desc=f"Processing with {model_name}",
                )
            )
            results.extend(model_results)

    # Create DataFrame
    df = pd.DataFrame(results)

    # Pivot for side-by-side comparison
    pivot_df = df.pivot(
        index="query",
        columns="model",
        values=["phrases", "latency", "input_tokens", "output_tokens", "cost"],
    )
    pivot_df.columns = [f"{col[0]}_{col[1]}" for col in pivot_df.columns]
    pivot_df.reset_index(inplace=True)

    # Calculate similarity between phrases
    def calculate_similarity(row):
        try:
            from difflib import SequenceMatcher

            return SequenceMatcher(
                None, row["phrases_gpt-4o-mini"], row["phrases_gpt-5-nano:minimal"]
            ).ratio()
        except:
            return 0.0

    pivot_df["phrase_similarity"] = pivot_df.apply(calculate_similarity, axis=1)

    # Save to Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"./output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/model_comparison_{timestamp}.xlsx"
    pivot_df.to_excel(output_file, index=False)

    loggers.info(f"Excel file saved: {output_file}")
    return True


product_data = [
    "id: P-1a2b3c4d-5e6f-7a8b-9c0d-123456789012 & product_sku: SP123456 & product_name: Men's Black Nike Dri-FIT Running Short Sleeve T-Shirt, brand: Nike & main_category, sub-category: ['Men', \"Men's activewear\"], colors: ['Black', 'White'] & extra_information: ['Polyester', 'Breathable Mesh', 'Machine Wash']"
]
args = Args()
logger = Logger()
asyncio.run(generate_product_suggestions(product_data, args, logger))
