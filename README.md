# Multi-Document RAG Project

A Retrieval-Augmented Generation (RAG) system with a FastAPI backend, Qdrant vector database, BGE-M3 embeddings, Google Gemini generative AI, and a modern React (Vite) frontend.

## Architecture

- **Backend**: FastAPI (Python) with CORS support
- **Embeddings**: `BAAI/bge-m3` via Sentence Transformers (1024 dimensions)
- **Vector Database**: Qdrant (local vector storage)
- **LLM**: Google Gemini (`gemini-3.6-flash`) via `google-genai`
- **Frontend**: React + Vite with responsive UI and markdown rendering

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Copy `.env.example` to `.env` and configure your API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
5. Ingest documents into Qdrant:
   ```bash
   python ingest.py
   ```
6. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
