"""
RAG service — PDF ingestion, chunking, vector storage, and retrieval.
"""

from pathlib import Path
import pdfplumber
import chromadb
from app.core.config import (
    CHROMA_DIR, COLLECTION_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS,
)
from app.services.embeddings import embed, embed_batch


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest_cv(pdf_path: Path, collection) -> int:
    candidate_name = pdf_path.stem
    clean_name     = pdf_path.stem.split("_", 2)[-1].replace("_", " ")
    text           = extract_text_from_pdf(pdf_path)

    if not text:
        return 0

    chunks     = chunk_text(text)
    embeddings = embed_batch(chunks)

    ids        = [f"{candidate_name}_chunk_{i}" for i in range(len(chunks))]
    metadatas  = [{"source": pdf_path.name, "candidate": clean_name, "chunk": i}
              for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)


def ingest_all(cvs_dir: Path = None) -> dict:
    if cvs_dir is None:
        from app.core.config import CVS_DIR
        cvs_dir = CVS_DIR

    collection = get_collection()
    results    = {"processed": 0, "chunks": 0, "errors": []}

    pdf_files = sorted(cvs_dir.rglob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {cvs_dir}")
        return results

    print(f"Ingesting {len(pdf_files)} CVs...\n")

    for pdf_path in pdf_files:
        print(f"  Processing: {pdf_path.name}...")
        try:
            n = ingest_cv(pdf_path, collection)
            results["processed"] += 1
            results["chunks"]    += n
            print(f"             {n} chunks stored")
        except Exception as e:
            results["errors"].append({"file": pdf_path.name, "error": str(e)})
            print(f"             Error: {e}")

    print(f"\nDone. {results['processed']} CVs → {results['chunks']} chunks in ChromaDB")
    return results


def search(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    collection    = get_collection()
    query_embedding = embed(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "content":   doc,
            "source":    meta["source"],
            "candidate": meta["candidate"],
            "score":     round(1 - dist, 4),
        })

    return hits