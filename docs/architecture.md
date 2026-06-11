# Architecture Overview

## Data Flow
User question
→ Frontend (Next.js)
→ POST /api/chat (FastAPI)
→ Embed question (Ollama nomic-embed-text)
→ Vector search (ChromaDB)
→ Build prompt with top-K chunks
→ Generate answer (Ollama llama3.2)
→ Return answer + source CVs
→ Display in chat UI

## Components

### 1. Provider Layer
Abstracted LLM provider supporting Ollama (local), Gemini, and OpenRouter.
Active provider configured via `LLM_PROVIDER` env var.

### 2. CV Generation (offline script)
Generates 25 realistic fake CVs via LLM + ReportLab PDF layout.

### 3. RAG Ingestion Pipeline
pdfplumber → text chunks → embeddings → ChromaDB

### 4. Chat API (FastAPI)
Semantic search → context injection → LLM response + sources

### 5. Frontend (Next.js)
Chat UI with source attribution display
