"""
Application Use Case: Chat
Orchestrates RAG pipeline — embed question, search, generate answer.
"""

from app.domain.ports.llm_port import LLMPort
from app.domain.ports.embedding_port import EmbeddingPort
from app.domain.ports.vector_store_port import VectorStorePort
from app.domain.entities.chat import ChatResponse, Source
from app.core.config import TOP_K_RESULTS

SYSTEM_PROMPT = """You are an AI assistant helping to screen and evaluate candidates based on their CVs.
Answer questions based ONLY on the CV information provided in the context below.
Be concise, professional, and specific. If the information is not in the context, say so clearly.
When mentioning candidates, use their full name."""


class ChatUseCase:

    def __init__(
        self,
        llm:          LLMPort,
        embedder:     EmbeddingPort,
        vector_store: VectorStorePort,
    ):
        self.llm          = llm
        self.embedder     = embedder
        self.vector_store = vector_store

    def execute(self, question: str) -> ChatResponse:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        query_embedding = self.embedder.embed(question)
        chunks = self.vector_store.search(query_embedding, top_k=TOP_K_RESULTS)

        if not chunks:
            return ChatResponse(
                answer="No CVs found in the database. Please ingest CVs first.",
                sources=[],
            )

        context = "\n\n---\n\n".join([
            f"From {c.candidate}:\n{c.content}"
            for c in chunks
        ])

        seen    = set()
        sources = []
        for c in chunks:
            if c.candidate not in seen:
                seen.add(c.candidate)
                sources.append(Source(
                    candidate=c.candidate,
                    source=c.source,
                    score=c.score,
                ))

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
        answer = self.llm.chat(messages)

        return ChatResponse(answer=answer, sources=sources)

    def suggest(self, question: str) -> list[str]:
        prompt = f"""Based on this CV screening question: "{question}"
Generate exactly 3 short follow-up questions a recruiter might ask next.
Return ONLY a JSON array of 3 strings, no explanation, no markdown:
["question 1", "question 2", "question 3"]"""

        try:
            import json
            response = self.llm.chat([{"role": "user", "content": prompt}])
            start    = response.find("[")
            end      = response.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])[:3]
        except Exception:
            pass
        return []
