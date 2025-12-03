# from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from FlagEmbedding import FlagReranker
from qdrant_client import AsyncQdrantClient, models
import asyncio
async_client = AsyncQdrantClient(url=os.getenv("QDRANT_URL"), prefer_grpc=True)

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key="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")
query_vector = embeddings.embed_query("Can I integrate Salesmate with other software?")
# reranking the documents
async def reranking_bge_results(query,data):
    reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation
    score = reranker.compute_score([query, data])
    print(score) 


async def get_data():
    results = await async_client.search(
                collection_name="knowledge_documents_openai_embeddings",
                query_vector=query_vector,
                with_payload=True,
                limit=10,
                # query_filter=filters,
            )
    categorized: dict[str, list[dict]] = {}
    def bucket(src: str):
        src = src.lower()
        if src not in categorized:
            categorized[src] = []
    for _, docs in results:
            for doc in docs:
                meta = doc.payload.get("metadata", {})
                src  = meta.get("source_type")
                if not src:
                    continue
                bucket(src).append({
                    "point_id": doc.id,
                    "kb_id":     doc.payload.get("kb_id", ""),
                    "id":    meta.get("doc_id", "")
                })
    print(bucket)
# for hit in hits:
#     print(hit.payload," score: ", hit.score)

asyncio.run(get_data())