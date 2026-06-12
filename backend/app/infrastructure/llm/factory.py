"""
LLM Factory — returns the correct adapter based on configuration.
"""

from app.domain.ports.llm_port import LLMPort
from app.infrastructure.llm.ollama_adapter import OllamaAdapter
from app.infrastructure.llm.gemini_adapter import GeminiAdapter
from app.infrastructure.llm.openrouter_adapter import OpenRouterAdapter
from app.core.config import (
    LLM_PROVIDER, LLM_MODEL,
    OLLAMA_BASE_URL, GEMINI_API_KEY, OPENROUTER_API_KEY,
)


def get_llm() -> LLMPort:
    if LLM_PROVIDER == "gemini":
        return GeminiAdapter(api_key=GEMINI_API_KEY, model=LLM_MODEL)
    if LLM_PROVIDER == "openrouter":
        return OpenRouterAdapter(api_key=OPENROUTER_API_KEY, model=LLM_MODEL)
    return OllamaAdapter(base_url=OLLAMA_BASE_URL, model=LLM_MODEL)
