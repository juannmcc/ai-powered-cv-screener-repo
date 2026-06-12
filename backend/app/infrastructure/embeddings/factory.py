"""
Embedding Factory — returns the correct adapter based on configuration.
"""

from app.domain.ports.embedding_port import EmbeddingPort
from app.infrastructure.embeddings.ollama_embedding_adapter import OllamaEmbeddingAdapter
from app.core.config import OLLAMA_BASE_URL, EMBED_MODEL


def get_embedder() -> EmbeddingPort:
    return OllamaEmbeddingAdapter(base_url=OLLAMA_BASE_URL, model=EMBED_MODEL)
