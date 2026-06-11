"""
LLM service — generates chat responses via configured provider.
Supports: ollama | gemini | openrouter
"""

import requests
from app.core.config import (
    LLM_PROVIDER, LLM_MODEL,
    OLLAMA_BASE_URL, OPENROUTER_API_KEY, GEMINI_API_KEY,
)


def _chat_ollama(messages: list[dict]) -> str:
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": LLM_MODEL, "messages": messages, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]


def _chat_openrouter(messages: list[dict]) -> str:
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"model": LLM_MODEL, "messages": messages},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _chat_gemini(messages: list[dict]) -> str:
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{LLM_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    r = requests.post(url, json={"contents": contents}, timeout=60)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def chat(messages: list[dict]) -> str:
    if LLM_PROVIDER == "ollama":
        return _chat_ollama(messages)
    elif LLM_PROVIDER == "openrouter":
        return _chat_openrouter(messages)
    elif LLM_PROVIDER == "gemini":
        return _chat_gemini(messages)
    raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")
