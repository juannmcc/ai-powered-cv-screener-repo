# System Architecture Diagram

## Complete Workflow

```mermaid
flowchart TD
    subgraph SETUP ["⚙️ Setup (offline)"]
        A[Settings Panel / CLI] --> B[generate-cvs]
        B --> C[Ollama llama3.2\nGenerates CV content]
        B --> D[Cloudflare FLUX\nGenerates AI photo]
        C & D --> E[ReportLab\nBuilds PDF]
        E --> F[data/cvs/YYYYMMDD/\n25 PDF files]
        F --> G[ingest-cvs]
        G --> H[pdfplumber\nExtracts text]
        H --> I[Chunker\n500 chars / 50 overlap]
        I --> J[nomic-embed-text\nGenerates embeddings]
        J --> K[(ChromaDB\n~105 chunks)]
    end

    subgraph CHAT ["💬 Chat (runtime)"]
        L[User question] --> M[Next.js Frontend]
        M --> N[POST /api/chat\nFastAPI]
        N --> O[nomic-embed-text\nEmbeds question]
        O --> P[ChromaDB\nCosine similarity search]
        P --> Q[Top-5 chunks\n+ metadata]
        Q --> R[Prompt builder\nSystem + context + question]
        R --> S[Ollama llama3.2\nGenerates answer]
        S --> T[Answer + Sources\n+ Follow-up questions]
        T --> M
    end

    subgraph UI ["🖥️ Frontend Features"]
        U[Chat interface\nwith source badges]
        V[Candidate browser\nwith AI avatars]
        W[Settings panel\nProvider + CV management]
        X[Ingest status\nbanner + polling]
    end

    subgraph PROVIDERS ["🔌 Provider Layer"]
        Y[LLM: ollama / gemini / openrouter]
        Z[Images: cloudflare / openai / placeholder]
    end

    K --> P
    M --- UI
    PROVIDERS -.-> SETUP
    PROVIDERS -.-> CHAT
```

## Provider Options

| Layer | Provider | Cost | Status |
|---|---|---|---|
| LLM | Ollama (local) | Free | ✅ Recommended |
| LLM | Google Gemini | Free tier* | ⚠️ Region restricted |
| LLM | OpenRouter | Free tier / pay | ⚠️ Rate limited |
| Embeddings | nomic-embed-text (Ollama) | Free | ✅ Active |
| Image | Cloudflare Workers AI | Free (10k/day) | ✅ Recommended |
| Image | OpenAI DALL-E 3 | ~$0.04/image | 🔧 Configured |
| Image | Placeholder avatar | Free | ✅ Fallback |
| Vector DB | ChromaDB (local) | Free | ✅ Active |

*Spain and some EU regions blocked on free tier
