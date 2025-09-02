from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
host=os.getenv("QDRANT_HOST","localhost")
port = int(os.getenv("QDRANT_PORT", "6333"))

client = QdrantClient(host=host, port=port)


client.recreate_collection(
    collection_name="movies-data",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)