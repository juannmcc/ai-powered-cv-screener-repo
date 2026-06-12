"""
Dependency injection container.
Wires infrastructure adapters to application use cases.
"""

from functools import lru_cache
from app.infrastructure.llm.factory import get_llm
from app.infrastructure.embeddings.factory import get_embedder
from app.infrastructure.vector_store.factory import get_vector_store
from app.infrastructure.pdf.factory import get_pdf_reader
from app.application.chat_use_case import ChatUseCase
from app.application.ingest_use_case import IngestUseCase


@lru_cache(maxsize=1)
def get_chat_use_case() -> ChatUseCase:
    return ChatUseCase(
        llm=get_llm(),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )


@lru_cache(maxsize=1)
def get_ingest_use_case() -> IngestUseCase:
    return IngestUseCase(
        pdf_reader=get_pdf_reader(),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )
