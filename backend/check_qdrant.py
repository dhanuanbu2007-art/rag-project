from qdrant_client import QdrantClient

client = QdrantClient(path="./qdrant_db")

collection_name = "documents"

info = client.get_collection(collection_name)

print("Collection:", collection_name)
print("Stored vectors:", info.points_count)
print("Vector size:", info.config.params.vectors.size)

client.close()