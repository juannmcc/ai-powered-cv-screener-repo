"""
Custom exceptions and error handlers for the CV Screener API.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class ProviderError(Exception):
    def __init__(self, provider: str, detail: str):
        self.provider = provider
        self.detail   = detail


class CollectionEmptyError(Exception):
    pass


class EmbeddingError(Exception):
    pass


async def provider_error_handler(request: Request, exc: ProviderError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "provider_unavailable",
            "provider": exc.provider,
            "detail": exc.detail,
        },
    )


async def collection_empty_handler(request: Request, exc: CollectionEmptyError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "no_cvs_ingested",
            "detail": "No CVs found in the database. Run: uv run ingest-cvs",
        },
    )


async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "detail": str(exc),
        },
    )
