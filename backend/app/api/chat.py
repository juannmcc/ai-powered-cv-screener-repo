"""
Chat API endpoint — RAG + LLM response generation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import search
from app.services.llm import chat

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

    # Retrieve chunks
    hits = search(request.question)

    if not hits:
        return ChatResponse(
            answer="I couldn't find relevant information in the CV database. Make sure CVs have been ingested.",
            sources=[],
        )

    # Build context
    context = "\n\n---\n\n".join([
        f"From {h['candidate']}:\n{h['content']}"
        for h in hits
    ])

    # Deduplicate sources
    seen     = set()
    sources  = []
    for h in hits:
        if h["candidate"] not in seen:
            seen.add(h["candidate"])
            sources.append(Source(
                candidate=h["candidate"],
                source=h["source"],
                score=h["score"],
            ))

    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.question}"},
    ]

    answer = chat(messages)

    return ChatResponse(answer=answer, sources=sources)
