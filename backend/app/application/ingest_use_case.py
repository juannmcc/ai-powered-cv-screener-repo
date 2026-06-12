"""
Application Use Case: Ingest
Orchestrates PDF ingestion — extract, chunk, embed, store.
"""

from pathlib import Path
from app.domain.ports.pdf_port import PDFPort
from app.domain.ports.embedding_port import EmbeddingPort
from app.domain.ports.vector_store_port import VectorStorePort
from app.domain.entities.chunk import Chunk
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP


class IngestUseCase:

    def __init__(
        self,
        pdf_reader:   PDFPort,
        embedder:     EmbeddingPort,
        vector_store: VectorStorePort,
    ):
        self.pdf_reader   = pdf_reader
        self.embedder     = embedder
        self.vector_store = vector_store

    def execute(self, cvs_dir: Path) -> dict:
        # Clear existing data
        self.vector_store.clear()

        results   = {"processed": 0, "chunks": 0, "errors": []}
        pdf_files = sorted(cvs_dir.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDFs found in {cvs_dir}")
            return results

        print(f"Ingesting {len(pdf_files)} CVs from {cvs_dir.name}...\n")

        for pdf_path in pdf_files:
            print(f"  Processing: {pdf_path.name}...")
            try:
                n = self._ingest_one(pdf_path)
                results["processed"] += 1
                results["chunks"]    += n
                print(f"             {n} chunks stored")
            except Exception as e:
                results["errors"].append({"file": pdf_path.name, "error": str(e)})
                print(f"             Error: {e}")

        print(f"\nDone. {results['processed']} CVs → {results['chunks']} chunks in ChromaDB")
        return results

    def _ingest_one(self, pdf_path: Path) -> int:
        text = self.pdf_reader.extract_text(pdf_path)
        if not text:
            return 0

        texts  = self.pdf_reader.chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

        stem       = pdf_path.stem
        clean_name = stem.split("_", 2)[-1].replace("_", " ")
        chunks     = [
            Chunk(
                content=t,
                candidate=clean_name,
                source=pdf_path.name,
                chunk_idx=i,
            )
            for i, t in enumerate(texts)
        ]

        embeddings = self.embedder.embed_batch([c.content for c in chunks])
        self.vector_store.upsert(chunks, embeddings)
        return len(chunks)
