import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from google import genai


load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")


gemini = genai.Client(api_key=api_key)


print("Loading BGE-M3...")

model = SentenceTransformer("BAAI/bge-m3")


print("Connecting to Qdrant...")

client = QdrantClient(path="./qdrant_db")


conversation_history = []


def classify_question(question):

    q = question.lower().strip()

    if any(word in q for word in [
        "hi",
        "hello",
        "hey",
        "how are you",
        "i have a doubt",
        "can you help me",
        "thanks",
        "thank you",
        "bye"
    ]):
        return "casual"

    if any(word in q for word in [
        "difference between",
        "differences between",
        "compare",
        "comparison",
        "versus",
        " vs ",
        "difference"
    ]):
        return "comparison"

    if any(word in q for word in [
        "important topics",
        "most important",
        "important topic",
        "which topics are important",
        "important"
    ]):
        return "important"

    if any(word in q for word in [
        "summarize",
        "summary",
        "overview",
        "explain the whole unit"
    ]):
        return "summary"

    if any(word in q for word in [
        "what topics",
        "which topics",
        "all topics",
        "topics available",
        "topics covered",
        "what is covered",
        "what are the topics",
        "what does the document contain"
    ]):
        return "broad"

    return "normal"


class Question(BaseModel):
    question: str


@app.get("/")
def home():

    return {
        "message": "Multi-Document RAG Chatbot API is working!"
    }


@app.post("/ask")
def ask_question(data: Question):

    question = data.question.strip()

    if not question:

        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    question_type = classify_question(question)

    print("Question type:", question_type)

    question_vector = model.encode(question).tolist()


    if question_type == "comparison":

        unit2_results = client.query_points(
            collection_name="documents",
            query=question_vector,
            limit=5,
        ).points

        relevant_results = unit2_results

    else:

        if question_type in ["broad", "important", "summary"]:
            limit = 12
        else:
            limit = 5

        relevant_results = client.query_points(
            collection_name="documents",
            query=question_vector,
            limit=limit,
        ).points


    context = ""

    for result in relevant_results:

        context += f"""
Source: {result.payload["source"]}

{result.payload["text"]}

"""


    history_text = ""

    for item in conversation_history[-5:]:

        history_text += f"""
User: {item["user"]}
Assistant: {item["assistant"]}
"""


    prompt = f"""
You are a friendly and natural study-material chatbot.

Your job is to help the user understand the uploaded study documents.

QUESTION TYPE:
{question_type}

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{history_text}

CURRENT USER QUESTION:
{question}

RULES:

1. For casual messages such as greetings or "I have a doubt",
   respond naturally and briefly.

2. For study questions, use ONLY information from the
   document context.

3. Never use outside knowledge for study questions.

4. Never invent facts.

5. Never pretend something is in the documents if it is not.

6. For "what is" questions, explain the concept in simple
   language instead of copying the document word-for-word.

7. For topic questions, identify and organize the topic names
   found in the document context.

8. For important-topic questions, identify major topics that
   receive meaningful coverage in the provided documents.
   Do NOT claim that a topic is guaranteed to appear in an exam.

9. For comparison questions, compare information from the
   available documents.

10. For summary questions, summarize the main ideas from the
    provided document context.

11. Use conversation history to understand follow-up references
    such as "it", "its", "this", and "that".

12. If there is not enough information in the document context,
    say:

"I couldn't find enough information about that in the uploaded documents."

13. Do not mention RAG, Qdrant, embeddings, retrieval, or
    internal technical details unless the user specifically asks.

14. Answer like a helpful human tutor, not like a copied PDF.

15. Keep answers clear, natural, and reasonably concise.
"""


    response = gemini.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )


    answer = response.text


    conversation_history.append({
        "user": question,
        "assistant": answer
    })


    sources = list(dict.fromkeys(
        result.payload["source"]
        for result in relevant_results
    ))


    return {
        "answer": answer,
        "sources": sources
    }