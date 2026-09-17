from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


print("Loading BGE-M3...")
model = SentenceTransformer("BAAI/bge-m3")

print("Connecting to Qdrant...")
client = QdrantClient(path="./qdrant_db")


question = input("\nAsk a question: ")

# Convert the question into a vector
question_vector = model.encode(question).tolist()

# Search Qdrant
results = client.query_points(
    collection_name="documents",
    query=question_vector,
    limit=3,
).points


print("\n===== SEARCH RESULTS =====")

for i, result in enumerate(results, start=1):

    print(f"\n--- Result {i} ---")
    print("Source:", result.payload["source"])
    print("Score:", result.score)
    print("Text:")
    print(result.payload["text"])


client.close()