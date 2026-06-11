"""
Provider Health Checker
Tests connectivity and availability of all supported LLM providers.
Run: uv run python scripts/check_providers.py
"""

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")


PROVIDERS = {
    "ollama": {
        "label": "Ollama (local)",
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("LLM_MODEL", "llama3.2"),
        "embed_model": os.getenv("EMBED_MODEL", "nomic-embed-text"),
    },
    "gemini": {
        "label": "Google AI Studio (Gemini)",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "model": "gemini-2.0-flash",
    },
    "openrouter": {
        "label": "OpenRouter",
        "api_key": os.getenv("OPENROUTER_API_KEY", ""),
        "model": "meta-llama/llama-3.3-70b-instruct:free",
    },
}

ACTIVE_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")


# Check Ollama
def check_ollama(cfg: dict) -> tuple[bool, str]:
    base = cfg["base_url"]
    model = cfg["model"]
    embed = cfg["embed_model"]

    try:
        r = requests.get(f"{base}/api/tags", timeout=3)
        if r.status_code != 200:
            return False, "Server not responding — run: ollama serve"
    except requests.exceptions.ConnectionError:
        return False, "Server offline — run: ollama serve"

    available = [m["name"] for m in r.json().get("models", [])]

    model_base = model.split(":")[0]
    if not any(model_base in m for m in available):
        return False, f"Model '{model}' not found — run: ollama pull {model}"

    embed_base = embed.split(":")[0]
    if not any(embed_base in m for m in available):
        return False, f"Embed model '{embed}' not found — run: ollama pull {embed}"

    try:
        r = requests.post(
            f"{base}/api/chat",
            json={"model": model, "messages": [{"role": "user", "content": "hi"}], "stream": False},
            timeout=30,
        )
        if r.status_code != 200:
            return False, f"Inference failed: {r.text[:100]}"
    except Exception as e:
        return False, f"Inference error: {e}"

    return True, f"Models ready: {model} + {embed}"


# Check Gemini
def check_gemini(cfg: dict) -> tuple[bool, str]:
    key = cfg["api_key"]
    if not key or key == "your_gemini_api_key_here":
        return False, "No API key set (GEMINI_API_KEY in .env)"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{cfg['model']}:generateContent?key={key}"
    try:
        r = requests.post(
            url,
            json={"contents": [{"parts": [{"text": "hi"}]}]},
            timeout=10,
        )
        if r.status_code == 200:
            return True, f"Model {cfg['model']} ready"
        if r.status_code == 429:
            data = r.json()
            msg = data.get("error", {}).get("message", "")
            if "limit: 0" in msg:
                return False, "Quota blocked (region restriction — Spain free tier disabled)"
            return False, "Rate limited — wait or upgrade plan"
        if r.status_code in (400, 403):
            return False, "Invalid API key"
        return False, f"Unexpected error {r.status_code}"
    except Exception as e:
        return False, f"Connection error: {e}"

# Check Openrouter
def check_openrouter(cfg: dict) -> tuple[bool, str]:
    key = cfg["api_key"]
    if not key or key == "your_openrouter_api_key_here":
        return False, "No API key set (OPENROUTER_API_KEY in .env)"

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": cfg["model"], "messages": [{"role": "user", "content": "hi"}]},
            timeout=15,
        )
        if r.status_code == 200:
            return True, f"Model {cfg['model']} ready"
        if r.status_code == 429:
            data = r.json()
            raw = data.get("error", {}).get("metadata", {}).get("raw", "")
            if "rate-limited" in raw:
                return False, "Upstream rate limited (free tier saturated — retry later or add credits)"
            return False, "Rate limited"
        if r.status_code == 401:
            return False, "Invalid API key"
        if r.status_code == 404:
            return False, f"Model '{cfg['model']}' not available"
        return False, f"Unexpected error {r.status_code}"
    except Exception as e:
        return False, f"Connection error: {e}"


CHECKERS = {
    "ollama": check_ollama,
    "gemini": check_gemini,
    "openrouter": check_openrouter,
}

def main():
    print("\n --- LLM Provider Health Check ---\n")

    results = {}
    for key, cfg in PROVIDERS.items():
        checker = CHECKERS[key]
        ok, msg = checker(cfg)
        results[key] = ok
        status = "Ready" if ok else "Not available"
        active = "ACTIVE" if key == ACTIVE_PROVIDER else ""
        print(f"  {status}  {cfg['label']}{active}")
        print(f"           {msg}\n")

    active_ok = results.get(ACTIVE_PROVIDER, False)
    print("\n")
    if active_ok:
        print(f"Active provider '{ACTIVE_PROVIDER}' is ready. You can start.\n")
    else:
        print(f"Active provider '{ACTIVE_PROVIDER}' is NOT ready.")
        print(f"Change LLM_PROVIDER in backend/.env to a working provider.\n")


if __name__ == "__main__":
    main()
