"""
Domain entity: Chunk
Represents a text chunk extracted from a CV.
"""

from dataclasses import dataclass


@dataclass
class Chunk:
    content:   str
    candidate: str
    source:    str
    chunk_idx: int
    score:     float = 0.0

    @property
    def id(self) -> str:
        stem = self.source.replace(".pdf", "")
        return f"{stem}_chunk_{self.chunk_idx}"
