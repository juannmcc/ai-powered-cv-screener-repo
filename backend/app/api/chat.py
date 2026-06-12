"""
Chat API — interfaces layer.
Delegates to ChatUseCase via dependency injection.
"""

import json
import sqlite3
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.application.chat_use_case import ChatUseCase
from app.core.dependencies import get_chat_use_case
from app.core.config import CHROMA_DIR, LLM_PROVIDER, LLM_MODEL

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    candidate: str
    source:    str
    score:     float


class ChatResponse(BaseModel):
    answer:  str
    sources: list[Source]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request:  ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = use_case.execute(request.question)

    return ChatResponse(
        answer=result.answer,
        sources=[
            Source(candidate=s.candidate, source=s.source, score=s.score)
            for s in result.sources
        ],
    )


@router.post("/suggestions")
async def suggestions(
    request:  ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    questions = use_case.suggest(request.question)
    return {"suggestions": questions}


@router.get("/stats")
async def stats():
    try:
        db_path = CHROMA_DIR / "chroma.sqlite3"
        if not db_path.exists():
            return {"chunks": 0, "estimated_cvs": 0, "provider": LLM_PROVIDER, "model": LLM_MODEL}
        conn    = sqlite3.connect(str(db_path))
        cur     = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM embeddings")
        count   = cur.fetchone()[0]
        conn.close()
        cv_count = round(count / 4.2) if count > 0 else 0
        return {
            "chunks":        count,
            "estimated_cvs": cv_count,
            "provider":      LLM_PROVIDER,
            "model":         LLM_MODEL,
        }
    except Exception:
        return {"chunks": 0, "estimated_cvs": 0, "provider": LLM_PROVIDER, "model": LLM_MODEL}


@router.get("/candidates")
async def candidates():
    try:
        db_path = CHROMA_DIR / "chroma.sqlite3"
        if not db_path.exists():
            return {"candidates": [], "total": 0}
        conn = sqlite3.connect(str(db_path))
        cur  = conn.cursor()
        cur.execute("""
            SELECT DISTINCT em_name.string_value, em_source.string_value
            FROM embedding_metadata em_name
            JOIN embedding_metadata em_source
                ON em_name.id = em_source.id
            WHERE em_name.key = 'candidate'
            AND em_source.key = 'source'
            ORDER BY em_name.string_value
        """)
        rows = cur.fetchall()
        conn.close()
        candidates = [
            {"name": name, "source": source, "avatar": f"/avatars/{source.replace('.pdf', '')}.jpg"}
            for name, source in rows
        ]
        return {"candidates": candidates, "total": len(candidates)}
    except Exception:
        return {"candidates": [], "total": 0}
