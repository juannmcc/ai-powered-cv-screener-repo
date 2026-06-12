# System Architecture Diagram

## Complete Workflow

```mermaid
flowchart TD
    subgraph SETUP ["Setup (offline)"]
        A[uv run generate-cvs] --> B[Ollama llama3.2\nGenerates CV content]
        B --> C[Cloudflare FLUX\nGenerates AI photo]
        B & C --> D[ReportLab\nBuilds PDF]
        D --> E[data/cvs/YYYYMMDD/\n25 PDF files]
        E --> F[uv run ingest-cvs]
        F --> G[pdfplumber\nExtracts text]
        G --> H[Chunker\n500 chars / 50 overlap]
        H --> I[nomic-embed-text\nGenerates embeddings]
        I --> J[(ChromaDB\n105 chunks)]
    end

    subgraph CHAT ["Chat (runtime)"]
        K[User question] --> L[Next.js Frontend]
        L --> M[POST /api/chat\nFastAPI]
        M --> N[nomic-embed-text\nEmbeds question]
        N --> O[ChromaDB\nCosine similarity search]
        O --> P[Top-5 chunks\n+ metadata]
        P --> Q[Prompt builder\nSystem + context + question]
        Q --> R[Ollama llama3.2\nGenerates answer]
        R --> S[Answer + Sources]
        S --> L
        L --> T[Chat UI\nwith source badges]
    end

    subgraph PROVIDERS ["Provider Layer"]
        U[LLM_PROVIDER=ollama\ngemini / openrouter]
        V[IMAGE_PROVIDER=cloudflare\nopenai / placeholder]
    end

    J --> O
    PROVIDERS -.-> CHAT
    PROVIDERS -.-> SETUP
```

## Provider Options

| Layer | Provider | Cost | Status |
|---|---|---|---|
| LLM | Ollama (local) | Free | ✅ Active |
| LLM | Google Gemini | Free tier* | ⚠️ Region restricted |
| LLM | OpenRouter | Free tier / pay | ⚠️ Rate limited |
| Embeddings | nomic-embed-text (Ollama) | Free | ✅ Active |
| Image | Cloudflare Workers AI | Free (10k/day) | ✅ Active |
| Image | OpenAI DALL-E 3 | ~$0.04/image | 🔧 Configured |
| Image | Placeholder avatar | Free | ✅ Fallback |
| Vector DB | ChromaDB (local) | Free | ✅ Active |

*Spain and some EU regions blocked on free tier
