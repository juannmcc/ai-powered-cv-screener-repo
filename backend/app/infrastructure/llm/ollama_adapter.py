"""
Infrastructure adapter: Ollama LLM
Implements LLMPort using Ollama local API.
"""

import requests
from app.domain.ports.llm_port import LLMPort


class OllamaAdapter(LLMPort):

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model    = model

    def chat(self, messages: list[dict]) -> str:
        try:
            r = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=120,
            )
            r.raise_for_status()
            return r.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Ollama server is not running. Run: ollama serve")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out")

    def is_available(self) -> tuple[bool, str]:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m["name"].split(":")[0] for m in r.json().get("models", [])]
                if any(self.model in m for m in models):
                    return True, f"Ollama running · model {self.model} ready"
                return False, f"Model '{self.model}' not found — run: ollama pull {self.model}"
            return False, "Ollama not responding"
        except Exception:
            return False, "Ollama offline — run: ollama serve"
    