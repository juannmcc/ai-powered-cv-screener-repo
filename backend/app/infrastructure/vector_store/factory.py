from app.domain.ports.vector_store_port import VectorStorePort
from app.infrastructure.vector_store.chroma_adapter import ChromaAdapter


def get_vector_store() -> VectorStorePort:
    return ChromaAdapter()
