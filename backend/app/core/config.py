from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# LLM Provider
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL       = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL     = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")

# Paths
CVS_DIR    = BASE_DIR / "data" / "cvs"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
AVATARS_DIR = BASE_DIR / "data" / "avatars"

# RAG
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50
TOP_K_RESULTS   = 5
COLLECTION_NAME = "cvs"

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
