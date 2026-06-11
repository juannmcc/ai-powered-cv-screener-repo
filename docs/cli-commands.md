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
uv run generate-cvs              # generates all 25 CVs
uv run generate-cvs --limit 3   # generates only 3 (useful for testing)
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
