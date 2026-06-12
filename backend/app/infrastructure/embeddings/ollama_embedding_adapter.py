"""
Infrastructure adapter: Ollama Embeddings
Implements EmbeddingPort using Ollama local API.
"""

import requests
from app.domain.ports.embedding_port import EmbeddingPort


class OllamaEmbeddingAdapter(EmbeddingPort):

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model    = model

    def embed(self, text: str) -> list[float]:
        r = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]
