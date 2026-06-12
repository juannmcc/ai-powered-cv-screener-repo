from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.exceptions import (
    ProviderError, CollectionEmptyError,
    provider_error_handler, collection_empty_handler, generic_error_handler,
)
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import AVATARS_DIR

AVATARS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI-Powered CV Screener",
    description="RAG-based CV screening API",
    version="0.3.1",
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
app.mount("/avatars", StaticFiles(directory=str(AVATARS_DIR)), name="avatars")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.3.1"}
