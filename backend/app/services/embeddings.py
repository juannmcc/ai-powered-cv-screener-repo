"""
Embedding service — generates vector embeddings via Ollama.
"""

import requests
from app.core.config import OLLAMA_BASE_URL, EMBED_MODEL


def embed(text: str) -> list[float]:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def embed_batch(texts: list[str]) -> list[list[float]]:
    return [embed(t) for t in texts]
