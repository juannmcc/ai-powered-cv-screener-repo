from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.exceptions import (
    ProviderError, CollectionEmptyError,
    provider_error_handler, collection_empty_handler, generic_error_handler,
)

app = FastAPI(
    title="AI-Powered CV Screener",
    description="RAG-based CV screening API",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ProviderError, provider_error_handler)
app.add_exception_handler(CollectionEmptyError, collection_empty_handler)
app.add_exception_handler(Exception, generic_error_handler)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.3.0"}
