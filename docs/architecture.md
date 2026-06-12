# Architecture Overview

## Data Flow
User question
→ Frontend (Next.js 15)
→ POST /api/chat (FastAPI)
→ Embed question (Ollama nomic-embed-text)
→ Vector search (ChromaDB — cosine similarity)
→ Top-5 chunks with source metadata
→ Build prompt with context + system instructions
→ Generate answer (Ollama llama3.2)
→ Return answer + sources (candidate, file, score)
→ Display in chat UI with source badges

## Components

### Provider Layer
Abstracted LLM provider supporting Ollama (local), Gemini, and OpenRouter.
Active provider configured via `LLM_PROVIDER` in `.env`.
Image generation supports Cloudflare Workers AI (FLUX), OpenAI DALL-E 3, and placeholder avatars.

### CV Generation (offline script)
- Generates 25 realistic fake CVs via Ollama llama3.2
- AI-generated photos via Cloudflare Workers AI (FLUX-1-schnell)
- ReportLab PDF layout with photo, contact, experience, education, skills
- Output: timestamped folders in `data/cvs/YYYYMMDD-HHMM/`

### RAG Ingestion Pipeline
- `pdfplumber` extracts text from each PDF
- Text split into 500-char chunks with 50-char overlap
- `nomic-embed-text` (Ollama) generates embeddings per chunk
- ChromaDB persists embeddings + metadata (candidate name, source file, chunk index)

### Chat API (FastAPI)
- `POST /api/chat` receives question
- Question embedded → cosine similarity search in ChromaDB
- Top-5 chunks injected into system prompt as context
- LLM generates answer grounded in CV data
- Response includes answer + deduplicated sources with scores
- `GET /api/stats` returns CV count, chunk count, active provider/model
- `GET /health` for frontend health check

### Frontend (Next.js 15)
- Chat UI with message bubbles, typing indicator
- Source attribution badges with candidate name + relevance score
- Backend health indicator (green/yellow/red)
- Dynamic CV count from /api/stats
- Suggestion cards for common queries
- New conversation reset button

## Error Handling
- `ProviderError`: LLM provider unavailable (503)
- `CollectionEmptyError`: No CVs ingested (404)
- Frontend displays specific messages per error type
