"""
Infrastructure adapter: pdfplumber
Implements PDFPort using pdfplumber for text extraction.
"""

from pathlib import Path
import pdfplumber
from app.domain.ports.pdf_port import PDFPort


class PDFPlumberAdapter(PDFPort):

    def extract_text(self, path: Path) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        chunks = []
        start  = 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            start += chunk_size - overlap
        return chunks
    