from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.rag import search
from app.services.llm import chat
from app.core.exceptions import CollectionEmptyError
from app.core.config import AVATARS_DIR

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    candidate: str
    source: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


SYSTEM_PROMPT = """You are an AI assistant helping to screen and evaluate candidates based on their CVs.
Answer questions based ONLY on the CV information provided in the context below.
Be concise, professional, and specific. If the information is not in the context, say so clearly.
When mentioning candidates, use their full name."""


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    hits = search(request.question)

    if not hits:
        raise CollectionEmptyError()

    context = "\n\n---\n\n".join([
        f"From {h['candidate']}:\n{h['content']}"
        for h in hits
    ])

    seen    = set()
    sources = []
    for h in hits:
        if h["candidate"] not in seen:
            seen.add(h["candidate"])
            sources.append(Source(
                candidate=h["candidate"],
                source=h["source"],
                score=h["score"],
            ))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.question}"},
    ]

    answer = chat(messages)
    return ChatResponse(answer=answer, sources=sources)


@router.get("/stats")
async def stats():
    import sqlite3
    from app.core.config import CHROMA_DIR, LLM_PROVIDER, LLM_MODEL
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
    import sqlite3
    from app.core.config import CHROMA_DIR
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

        candidates = []
        for name, source in rows:
            slug = source.replace(".pdf", "")
            candidates.append({
                "name":   name,
                "source": source,
                "avatar": f"/avatars/{slug}.jpg",
            })

        return {"candidates": candidates, "total": len(candidates)}
    except Exception as e:
        return {"candidates": [], "total": 0}


@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    path = AVATARS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Avatar not found")
    return FileResponse(path, media_type="image/jpeg")


@router.post("/suggestions")
async def suggestions(request: ChatRequest):
    prompt = f"""Based on this question about CV screening: "{request.question}"
    
Generate exactly 3 short follow-up questions a recruiter might ask next.
Return ONLY a JSON array of 3 strings, no explanation, no markdown:
["question 1", "question 2", "question 3"]"""

    try:
        messages = [{"role": "user", "content": prompt}]
        response = chat(messages)
        start = response.find("[")
        end   = response.rfind("]") + 1
        if start != -1 and end > start:
            import json
            questions = json.loads(response[start:end])
            return {"suggestions": questions[:3]}
    except Exception:
        pass
    return {"suggestions": []}


@router.post("/reload")
async def reload():
    import gc
    import chromadb
    from app.core.config import CHROMA_DIR, COLLECTION_NAME
    try:
        client     = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_or_create_collection(COLLECTION_NAME)
        count      = collection.count()
        del client
        gc.collect()
        return {"reloaded": True, "chunks": count}
    except Exception as e:
        return {"reloaded": False, "error": str(e)}