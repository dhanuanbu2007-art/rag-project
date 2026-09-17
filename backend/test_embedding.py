from sentence_transformers import SentenceTransformer

print("Loading BGE-M3...")

model = SentenceTransformer("BAAI/bge-m3")

text = "What is information retrieval?"

embedding = model.encode(text)

print("Embedding generated successfully!")
print("Dimension:", len(embedding))
print("First 10 values:", embedding[:10])