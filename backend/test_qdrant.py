from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

print("Starting Qdrant...")

client = QdrantClient(path="./qdrant_db")

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE
    )
)

print("Qdrant collection created successfully!")
print("Vector size: 1024")
print("Distance: COSINE")

client.close()