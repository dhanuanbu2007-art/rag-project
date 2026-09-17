import os

from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


# Load environment variables
load_dotenv()

# Gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found!")
    exit()

gemini = genai.Client(api_key=api_key)


# Embedding model
print("Loading BGE-M3...")
model = SentenceTransformer("BAAI/bge-m3")


# Qdrant
print("Connecting to Qdrant...")
client = QdrantClient(path="./qdrant_db")


# Ask question
question = input("\nAsk a question: ")


# Convert question into vector
question_vector = model.encode(question).tolist()


# Search Qdrant
results = client.query_points(
    collection_name="documents",
    query=question_vector,
    limit=3,
).points


# Build context
context = ""

for result in results:
    context += f"\nSource: {result.payload['source']}\n"
    context += result.payload["text"]
    context += "\n"


# Prompt Gemini
prompt = f"""
You are a helpful document question-answering assistant.

Answer the user's question using ONLY the information provided in the context.

If the answer is not available in the context, say:
"I could not find the answer in the uploaded documents."

Context:
{context}

Question:
{question}

Give a clear and simple answer.
"""


# Generate answer
response = gemini.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)


print("\n==============================")
print("ANSWER")
print("==============================")
print(response.text)

print("\n==============================")
print("SOURCES")
print("==============================")

for result in results:
    print("-", result.payload["source"])


client.close()