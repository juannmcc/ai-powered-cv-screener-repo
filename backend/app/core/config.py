from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Provider
LLM_PROVIDER   = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL      = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL    = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Paths
CVS_DIR        = BASE_DIR / "data" / "cvs"
CHROMA_DIR     = BASE_DIR / "data" / "chroma_db"

# RAG
CHUNK_SIZE     = 500
CHUNK_OVERLAP  = 50
TOP_K_RESULTS  = 5
COLLECTION_NAME = "cvs"