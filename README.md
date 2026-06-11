# AI-Powered CV Screener

> A full-stack prototype for screening CVs using a RAG pipeline. Ask natural language questions about a collection of candidates and get AI-powered answers with source attribution.

## Version: 0.1.0

## Tech Stack

| Layer | Technology |
|---|---|
| LLM & Embeddings | Ollama (local) · Gemini · OpenRouter |
| Vector Store | ChromaDB (local, embedded) |
| PDF Processing | pdfplumber |
| Backend | FastAPI + Python (uv) |
| Frontend | Next.js 15 + Tailwind CSS |

## Project Structure
ai-powered-cv-screener-repo/
├── backend/
│   ├── app/          # FastAPI app, core config, services
│   ├── scripts/      # CV generation + provider checker
│   └── data/         # CVs (PDF) + ChromaDB store
├── frontend/         # Next.js chat interface
└── docs/             # Architecture & workflow docs

## Prerequisites

- Python 3.10+ with uv
- Node.js 18+
- Ollama running locally (`ollama serve`)

## Changelog

### v0.1.0
- Initial project scaffold
