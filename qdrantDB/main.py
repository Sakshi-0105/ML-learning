from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct,Filter,FieldCondition,MatchValue

# Connect to Qdrant
client = QdrantClient(url="http://localhost:6333")

collection_name = "test_collection"

# Create new collection with vector size = 4 (matching your data)
# client.recreate_collection(
#     collection_name=collection_name,
#     vectors_config=VectorParams(size=4, distance=Distance.COSINE),
# )

# Add points
# operation_info = client.upsert(
#     collection_name=collection_name,
#     wait=True,
#     points=[
#         PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
#         PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
#         PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
#         PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
#         PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
#         PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
#     ],
# )

# print("Upsert Response:", operation_info)

# Search using a query vector
search_result = client.search(
    collection_name=collection_name,
    query_vector=[0.2, 0.1, 0.9, 0.7],
    limit=3,
    with_payload=True,
    query_filter=Filter(
        must=[
            FieldCondition(
                key='city',
                match=MatchValue(value="Berlin")
            )
        ]
    )
)

print("Search Result:")
for point in search_result:
    print(point)
