"""
Port: VectorStorePort
Defines the contract that any vector store must implement.
"""

from abc import ABC, abstractmethod
from app.domain.entities.chunk import Chunk


class VectorStorePort(ABC):

    @abstractmethod
    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Store chunks with their embeddings."""
        ...

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int) -> list[Chunk]:
        """Search for similar chunks by embedding."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return total number of stored chunks."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Delete all stored chunks."""
        ...
