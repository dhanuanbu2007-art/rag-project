from pathlib import Path

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def create_chunks(text):
    chunks = []

    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


print("Loading BGE-M3...")
model = SentenceTransformer("BAAI/bge-m3")

print("Connecting to Qdrant...")
client = QdrantClient(path="./qdrant_db")

collection_name = "documents"

# Create collection if it doesn't exist
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=1024,
            distance=Distance.COSINE
        )
    )

# Find all PDFs
pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

print(f"\nFound {len(pdf_files)} PDF file(s)")

# Get existing points count
collection_info = client.get_collection(collection_name)
point_id = collection_info.points_count or 0

for pdf_path in pdf_files:

    print(f"\n==============================")
    print(f"Reading: {pdf_path.name}")
    print("==============================")

    reader = PdfReader(str(pdf_path))

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    print(f"Pages: {len(reader.pages)}")
    print(f"Characters: {len(text)}")

    chunks = create_chunks(text)

    print(f"Chunks: {len(chunks)}")

    for chunk in chunks:

        embedding = model.encode(chunk).tolist()

        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": chunk,
                "source": pdf_path.name
            }
        )

        client.upsert(
            collection_name=collection_name,
            points=[point]
        )

        point_id += 1

print("\n==============================")
print("INGESTION COMPLETE")
print("==============================")
print(f"Total vectors in Qdrant: {point_id}")

client.close()