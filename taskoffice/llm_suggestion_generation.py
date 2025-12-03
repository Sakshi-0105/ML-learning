import asyncio
import concurrent.futures
import os
import time
import random
import logging

from langchain_openai import ChatOpenAI
from tqdm import tqdm
arguments = loggers = None

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


# Function to process each query
def process_query(query: str):
    # Add small delay to avoid rate limiting
    time.sleep(random.uniform(0.2, 0.8))

    api_key = os.getenv("OPENAI_CREDENTIALS")
    llm = ChatOpenAI(
        temperature=0, model="gpt-4.1-nano", api_key=api_key, timeout=30, max_retries=2  # Add 30 second timeout
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
                    Generate atleast 8 phrases per query if possible, ensuring a mix of two-word, three-word, and four-word phrases (maximum).
                    Focus on realistic, concise, and user-relevant suggestions. Avoid unnatural or overly generic combinations.
                    If multiple colors are mentioned, include separate phrases for each color.
                    Ensure the output follows the fixed format shown below.
                    In Example below which type of good phrases which are user-friendly and relevant to the user.
                    For example 'Muscle Pullover', Cotton Sleeveless are not good but user-friendly are 'Muscle Pullover Hoodie', 'Cotton Sleeveless Hoodie' is good.
                    {arguments.prompt_instruction}
                    Examples for Generated phrases and Expected phrases:
                    Example1:
                    Query: id: P-e0d2a8d7-f65c-475d-8684-ede91cf612a3-44663-1 & product_sku: TF419953 & product name: Men's Navy Atlanta Braves Jersey Muscle Sleeveless Pullover Hoodie, 
                           brand: Profile & main category, sub-category:['Men', "Men's sports wear"], 
                           colors: & Extra information: ['Cotton', 'Machine Wash', 'Tumble Dry Low']
                    Generated Phrases: P-e0d2a8d7-f65c-475d-8684-ede91cf612a3-44663-1, TF419953: Navy Jersey, Braves Hoodie, Muscle Pullover, Sleeveless Hoodie, Cotton Jersey, Navy Braves Jersey, Muscle Sleeveless Pullover, Cotton Sleeveless Hoodie
                    Expected phrases: P-e0d2a8d7-f65c-475d-8684-ede91cf612a3-44663-1, TF419953: Navy Jersey, Braves Hoodie, Sleeveless Hoodie, Cotton Jersey, Navy Braves Jersey, Cotton Sleeveless Hoodie, sports wear Hoodie, sports wear Jersey, men's Hoodie, men's Jersey
                    Example 2:
                    Query: id: P-2b3c4d5e-6f7a-8b9c-0d1e-234567890123 & product_sku: FW789012 & product_name: Women's Adidas Ultraboost 22 Blue Running Shoes, brand: Adidas & main_category, sub-category: ['Women', "Women's footwear"], colors: ['Blue', 'Grey'] & extra_information: ['Rubber Sole', 'Cushioned Midsole', 'Lace-Up']
                    Expected phrases: Keywords: P-2b3c4d5e-6f7a-8b9c-0d1e-234567890123, FW789012: Adidas Ultraboost, Blue Running Shoes, Grey Running Shoes, Women's Running Shoes, Cushioned Midsole Shoes, Rubber Sole Shoes, Lace-Up Shoes, Women's Footwear, Adidas Running Shoes, Blue Ultraboost Shoes
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
        res = result.split("Keywords:")[-1].strip().split("\n\n")
        # loggers.info(f"query:{query},res:{res}")
        with open(
            f"./gpt-4.1-nano2.txt",
            "a",
        ) as f:
            f.write(f"{', '.join(res)}\n")

    except Exception as e:
        loggers.info(f"Error processing query or parsing result {query}: {e}")


async def generate_product_suggestions(product_data: list, args: object, logger: object) -> bool:
    global arguments
    global loggers
    arguments, loggers = args, logger

    # Concurrently generating ai suggestions based on product data
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(
            tqdm(
                executor.map(process_query, product_data),
                total=len(product_data),
            )
        )

    return True



product_data = [
    "id: P-1a2b3c4d-5e6f-7a8b-9c0d-123456789012 & product_sku: SP123456 & product_name: Men's Black Nike Dri-FIT Running Short Sleeve T-Shirt, brand: Nike & main_category, sub-category: ['Men', \"Men's activewear\"], colors: ['Black', 'White'] & extra_information: ['Polyester', 'Breathable Mesh', 'Machine Wash']",
    
    "id: P-2b3c4d5e-6f7a-8b9c-0d1e-234567890123 & product_sku: FW789012 & product_name: Women's Adidas Ultraboost 22 Blue Running Shoes, brand: Adidas & main_category, sub-category: ['Women', \"Women's footwear\"], colors: ['Blue', 'Grey'] & extra_information: ['Rubber Sole', 'Cushioned Midsole', 'Lace-Up']",
    
    "id: P-3c4d5e6f-7a8b-9c0d-1e2f-345678901234 & product_sku: EL456789 & product_name: Bose QuietComfort 45 Wireless Noise-Cancelling Headphones Black, brand: Bose & main_category, sub-category: ['Electronics', 'Audio accessories'], colors: ['Black'] & extra_information: ['Bluetooth', 'USB-C Charging', 'Up to 24h Battery']",
    
    "id: P-4d5e6f7a-8b9c-0d1e-2f3a-456789012345 & product_sku: CA901234 & product_name: Unisex Red Cotton Graphic T-Shirt, brand: H&M & main_category, sub-category: ['Unisex', 'Casual clothing'], colors: ['Red'] & extra_information: ['Cotton', 'Machine Wash']",
    
    "id: P-5e6f7a8b-9c0d-1e2f-3a4b-567890123456 & product_sku: AC567890 & product_name: Ray-Ban Classic Wayfarer Sunglasses Black and Tortoise, brand: Ray-Ban & main_category, sub-category: ['Accessories', 'Sunglasses'], colors: ['Black', 'Tortoise'] & extra_information: ['Polarized Lenses', 'UV Protection']",
    
    "id: P-6f7a8b9c-0d1e-2f3a-4b5c-678901234567 & product_sku: TO345678 & product_name: Kids Marvel Spider-Man Action Figure Set, brand: Hasbro & main_category, sub-category: ['Kids', 'Toys'], colors: ['Red', 'Blue'] & extra_information: ['Plastic', 'Ages 5+', 'Collectible']",
    
    "id: P-7a8b9c0d-1e2f-3a4b-5c6d-789012345678 & product_sku: HM012345 & product_name: Stainless Steel Blender with Glass Jar, brand: KitchenAid & main_category, sub-category: ['Home', 'Kitchen appliances'], colors: ['Silver'] & extra_information: ['Glass Jar', 'High-Speed Blades', 'Dishwasher Safe']",
    
    "id: P-8b9c0d1e-2f3a-4b5c-6d7e-890123456789 & product_sku: BS678901 & product_name: Organic Face Moisturizer Cream for Sensitive Skin, brand: The Ordinary & main_category, sub-category: ['Beauty', 'Skincare'], colors: [] & extra_information: ['Hyaluronic Acid', 'Paraben-Free', 'Daily Use']",
    
    "id: P-9c0d1e2f-3a4b-5c6d-7e8f-901234567890 & product_sku: BK234567 & product_name: Paperback Thriller Novel 'The Silent Patient', brand: Penguin Random House & main_category, sub-category: ['Books', 'Fiction'], colors: [] & extra_information: ['Paperback', '300 Pages', 'Bestseller']",
    
    "id: P-0d1e2f3a-4b5c-6d7e-8f9a-012345678901 & product_sku: SE890123 & product_name: Wilson Pro Staff Tennis Racket for Advanced Players, brand: Wilson & main_category, sub-category: ['Sports', 'Tennis equipment'], colors: ['Black', 'Red'] & extra_information: ['Graphite Frame', 'Strung', 'Professional Grade']",
    
    "id: P-1e2f3a4b-5c6d-7e8f-9a0b-123456789012 & product_sku: EL456789 & product_name: Samsung Galaxy S25 Ultra Smartphone with 512GB Storage, brand: Samsung & main_category, sub-category: ['Electronics', 'Smartphones'], colors: ['Phantom Black'] & extra_information: ['5G Enabled', 'Triple Camera', 'Wireless Charging']",
    
    "id: P-2f3a4b5c-6d7e-8f9a-0b1c-234567890123 & product_sku: AP012345 & product_name: Women's Floral Summer Maxi Dress in Cotton, brand: Zara & main_category, sub-category: ['Women', 'Women's dresses'], colors: ['Floral Print'] & extra_information: ['Cotton Blend', 'Machine Wash', 'Midi Length']",
    
    "id: P-3a4b5c6d-7e8f-9a0b-1c2d-345678901234 & product_sku: HM678901 & product_name: Wooden Coffee Table with Storage Shelf, brand: IKEA & main_category, sub-category: ['Home', 'Furniture'], colors: ['Oak Wood'] & extra_information: ['Solid Wood', 'Assembly Required', 'Modern Design']",
    
    "id: P-4b5c6d7e-8f9a-0b1c-2d3e-456789012345 & product_sku: MK234567 & product_name: Matte Liquid Lipstick in Nude Shade, brand: MAC & main_category, sub-category: ['Beauty', 'Makeup'], colors: ['Nude'] & extra_information: ['Long-Lasting', 'Cruelty-Free', 'Transfer-Proof']",
    
    "id: P-5c6d7e8f-9a0b-1c2d-3e4f-567890123456 & product_sku: JW890123 & product_name: Sterling Silver Hoop Earrings with Gemstone Accents, brand: Tiffany & Co. & main_category, sub-category: ['Accessories', 'Jewelry'], colors: ['Silver'] & extra_information: ['Sterling Silver', 'Hypoallergenic', '14k Gold Plated']"
]
args = Args()
logger = Logger()
asyncio.run(generate_product_suggestions(product_data, args, logger))