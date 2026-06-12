"""
Port: EmbeddingPort
Defines the contract that any embedding provider must implement.
"""

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding vector for a single text."""
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts."""
        ...
