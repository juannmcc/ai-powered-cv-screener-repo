"""
Infrastructure adapter: Google Gemini
Implements LLMPort using Gemini API.
"""

import requests
from app.domain.ports.llm_port import LLMPort


class GeminiAdapter(LLMPort):

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model   = model
        self.base_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models"
            f"/{model}:generateContent"
        )

    def chat(self, messages: list[dict]) -> str:
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        r = requests.post(
            f"{self.base_url}?key={self.api_key}",
            json={"contents": contents},
            timeout=60,
        )
        if r.status_code == 429:
            raise RuntimeError("Gemini quota exceeded or region restricted")
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def is_available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "No API key set"
        try:
            r = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": "hi"}]}]},
                timeout=10,
            )
            if r.status_code == 200:
                return True, "Gemini ready"
            if r.status_code == 429:
                return False, "Quota exceeded or region restricted"
            return False, "Invalid API key"
        except Exception as e:
            return False, str(e)
    