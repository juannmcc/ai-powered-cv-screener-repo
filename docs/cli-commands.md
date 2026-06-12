# CLI Commands

## Setup (once)
```bash
cd backend
uv pip install -e .
```

## Usage

All commands run via `uv run` inside the `backend/` directory.

---

## Commands

### check-providers
Validates connectivity and availability of all configured LLM providers.
Run this before starting the app to confirm your active provider is ready.

```bash
uv run check-providers
```

---

### generate-cvs
Generates fake realistic CVs as PDFs using Ollama. Output saved to `data/cvs/YYYYMMDD-HHMM/`.

```bash
uv run generate-cvs                        # generates all 25 CVs with AI photos
uv run generate-cvs --limit 3             # generates only 3 (useful for testing)
uv run generate-cvs --no-image            # skip AI photo generation (faster)
uv run generate-cvs --limit 3 --no-image  # combine both flags
```

---

### ingest-cvs
Ingests all generated PDFs into ChromaDB (vector store).
Extracts text, chunks it, generates embeddings, and persists them locally.
Run this after generate-cvs and before starting the backend server.

```bash
uv run ingest-cvs
```

---

### remove-cvs
Removes CV output folders from `data/cvs/`.

```bash
uv run remove-cvs                    # removes all folders (with confirmation)
uv run remove-cvs 20260611-1515      # removes specific folder (with confirmation)
```

---

## Typical workflow

```bash
uv run check-providers          # 1. verify Ollama is ready
uv run generate-cvs             # 2. generate 25 CVs
uv run ingest-cvs               # 3. ingest into ChromaDB
```

---

## Configuration

Edit `backend/.env` to switch providers or add API keys:

```env
# Active provider: "gemini" | "openrouter" | "ollama"
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

Providers without API keys will show as "Not available" — this is expected.

---

## Platform notes

### Starting Ollama server

**Mac / Linux:**
```bash
ollama serve &
```

**Windows:**
```bash
start ollama serve
```

### Ollama model setup (all platforms)
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Provider-specific setup

**Gemini (Google AI Studio)**
Add to `backend/.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```
Note: free tier not available in all regions (e.g. Spain). Requires billing enabled.

**OpenRouter**
Add to `backend/.env`:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
```
Note: free tier models may have upstream rate limits. Add credits for reliable use.

**Ollama (local — recommended)**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
```
No API key needed. Requires Ollama installed and running locally.

### start-api
Starts the FastAPI backend server.

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: http://localhost:8000
Swagger docs at: http://localhost:8000/docs
Health check: http://localhost:8000/health

### Endpoints

**POST /api/chat**
```json
// Request
{ "question": "Who has experience with Python?" }

// Response
{
  "answer": "Based on the CVs...",
  "sources": [
    { "candidate": "Aria Lewis", "source": "cv_01_Aria_Lewis.pdf", "score": 0.69 }
  ]
}
```

## Full workflow

```bash
# Terminal 1 — backend
cd backend
uv run check-providers
uv run ingest-cvs
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Backend health check |
| GET | /api/stats | CV count, chunks, active provider/model |
| POST | /api/chat | Ask a question about candidates |

Swagger UI (interactive): http://localhost:8000/docs
