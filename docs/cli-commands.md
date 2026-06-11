# CLI Commands

## Setup (once)
```bash
cd backend
uv pip install -e .
```

## Usage

All commands run via `uv run` inside the `backend/` directory.

### check-providers
Validates connectivity and availability of all configured LLM providers.
Run this before starting the app to confirm your active provider is ready.

```bash
uv run check-providers
```

### Configuration
Edit `backend/.env` to switch providers or add API keys:

```env
# Active provider: "gemini" | "openrouter" | "ollama"
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
```

Providers not configured will show as "Not available" — this is expected.
