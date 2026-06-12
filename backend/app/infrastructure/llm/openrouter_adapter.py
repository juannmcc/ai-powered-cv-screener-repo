"""
Infrastructure adapter: OpenRouter
Implements LLMPort using OpenRouter API.
"""

import requests
from app.domain.ports.llm_port import LLMPort


class OpenRouterAdapter(LLMPort):

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model   = model

    def chat(self, messages: list[dict]) -> str:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "messages": messages},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def is_available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "No API key set"
        try:
            r = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if r.status_code == 200:
                credits = r.json().get("data", {}).get("limit_remaining")
                if credits is not None and credits <= 0:
                    return False, "No credits remaining"
                return True, f"Ready · {credits or 'free tier'}"
            return False, "Invalid API key"
        except Exception as e:
            return False, str(e)
    