from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import search
from app.services.llm import chat
from app.core.exceptions import CollectionEmptyError

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