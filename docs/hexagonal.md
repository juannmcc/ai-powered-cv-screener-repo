# Hexagonal Architecture

## Overview

The backend follows a Hexagonal Architecture (also known as Ports & Adapters), introduced in v1.1.0 as a refactor from the initial layered architecture.

The core idea: **the domain and application logic are completely isolated from infrastructure details**. The domain doesn't know if it's talking to Ollama, Gemini, ChromaDB or any other concrete technology.

## Layer Structure
backend/app/
├── domain/              # Core business logic — no external dependencies
│   ├── entities/        # Pure data structures
│   │   ├── candidate.py # CV candidate
│   │   ├── chunk.py     # Text chunk with embedding metadata
│   │   └── chat.py      # ChatResponse, Source
│   └── ports/           # Abstract interfaces (contracts)
│       ├── llm_port.py          # LLMPort
│       ├── embedding_port.py    # EmbeddingPort
│       ├── vector_store_port.py # VectorStorePort
│       └── pdf_port.py          # PDFPort
│
├── application/         # Use cases — orchestrate domain
│   ├── chat_use_case.py   # RAG pipeline: embed → search → generate
│   └── ingest_use_case.py # PDF ingestion: extract → chunk → embed → store
│
├── infrastructure/      # Concrete adapters — implement ports
│   ├── llm/
│   │   ├── ollama_adapter.py      # Implements LLMPort
│   │   ├── gemini_adapter.py      # Implements LLMPort
│   │   ├── openrouter_adapter.py  # Implements LLMPort
│   │   └── factory.py             # Returns correct adapter from config
│   ├── embeddings/
│   │   ├── ollama_embedding_adapter.py  # Implements EmbeddingPort
│   │   └── factory.py
│   ├── vector_store/
│   │   ├── chroma_adapter.py  # Implements VectorStorePort
│   │   └── factory.py
│   └── pdf/
│       ├── pdfplumber_adapter.py  # Implements PDFPort
│       └── factory.py
│
├── interfaces/          # FastAPI routers — entry points
│   └── api/
│       ├── chat.py      # POST /api/chat, GET /api/stats, GET /api/candidates
│       ├── cvs.py       # CV management endpoints
│       └── settings.py  # Provider configuration endpoints
│
└── core/
├── config.py        # Environment configuration
├── dependencies.py  # Dependency injection (wires adapters → use cases)
└── exceptions.py    # Custom exception handlers

## Dependency Flow
interfaces/ (FastAPI)
→ application/ (Use Cases)
→ domain/ports/ (Abstractions)
← infrastructure/ (Concrete implementations)

The interfaces layer depends on use cases.
Use cases depend only on ports (abstractions).
Infrastructure implements the ports.
**The domain never depends on infrastructure.**

## Dependency Injection

FastAPI's `Depends` system wires everything together at runtime:

```python
# core/dependencies.py
def get_chat_use_case() -> ChatUseCase:
    return ChatUseCase(
        llm=get_llm(),           # Returns OllamaAdapter | GeminiAdapter | ...
        embedder=get_embedder(), # Returns OllamaEmbeddingAdapter
        vector_store=get_vector_store(), # Returns ChromaAdapter
    )

# api/chat.py
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    result = use_case.execute(request.question)
```

## Why Hexagonal?

| Concern | Benefit |
|---|---|
| **Testability** | Use cases can be tested with mock adapters |
| **Replaceability** | Swap ChromaDB for Pinecone without touching business logic |
| **Provider agnostic** | Add new LLM provider by implementing LLMPort |
| **Clarity** | Business rules live in one place, infrastructure in another |

## Adding a New LLM Provider

1. Create `infrastructure/llm/new_provider_adapter.py` implementing `LLMPort`
2. Add it to `infrastructure/llm/factory.py`
3. Add the provider key to `core/config.py`
4. Done — no changes needed in domain or application layer

## Evolution

| Version | Architecture |
|---|---|
| v1.0.0 | Layered: `api/ → services/ → external APIs` |
| v1.1.0 | Hexagonal: `interfaces/ → application/ → domain/ ← infrastructure/` |
