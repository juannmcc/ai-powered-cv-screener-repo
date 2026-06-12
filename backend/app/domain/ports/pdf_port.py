"""
Port: PDFPort
Defines the contract for PDF text extraction.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class PDFPort(ABC):

    @abstractmethod
    def extract_text(self, path: Path) -> str:
        """Extract all text from a PDF file."""
        ...

    @abstractmethod
    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text into overlapping chunks."""
        ...
