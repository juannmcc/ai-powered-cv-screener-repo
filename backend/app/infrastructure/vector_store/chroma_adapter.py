"""
Infrastructure adapter: ChromaDB
Implements VectorStorePort using ChromaDB persistent client.
"""

import chromadb
from app.domain.ports.vector_store_port import VectorStorePort
from app.domain.entities.chunk import Chunk
from app.core.config import CHROMA_DIR, COLLECTION_NAME


class ChromaAdapter(VectorStorePort):

    def _client(self):
        return chromadb.PersistentClient(path=str(CHROMA_DIR))

    def _collection(self):
        client = self._client()
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        collection = self._collection()
        collection.upsert(
            ids=[c.id for c in chunks],
            embeddings=embeddings,
            documents=[c.content for c in chunks],
            metadatas=[{
                "source":    c.source,
                "candidate": c.candidate,
                "chunk":     c.chunk_idx,
            } for c in chunks],
        )

    def search(self, query_embedding: list[float], top_k: int) -> list[Chunk]:
        collection = self._collection()
        results    = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(Chunk(
                content=doc,
                candidate=meta["candidate"],
                source=meta["source"],
                chunk_idx=meta["chunk"],
                score=round(1 - dist, 4),
            ))
        return chunks

    def count(self) -> int:
        try:
            import sqlite3
            db = CHROMA_DIR / "chroma.sqlite3"
            if not db.exists():
                return 0
            conn = sqlite3.connect(str(db))
            cur  = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM embeddings")
            count = cur.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    def clear(self) -> None:
        import shutil
        if CHROMA_DIR.exists():
            shutil.rmtree(CHROMA_DIR)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
