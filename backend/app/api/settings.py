"""
Settings API — read and write backend configuration (.env file).
"""

import os
import re
import requests
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router   = APIRouter()
ENV_PATH = Path(__file__).parent.parent.parent / ".env"


class SettingsUpdate(BaseModel):
    key:   str
    value: str


def read_env() -> dict:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def write_env_key(key: str, value: str):
    content   = ENV_PATH.read_text() if ENV_PATH.exists() else ""
    lines     = content.splitlines()
    pattern   = re.compile(rf"^{re.escape(key)}\s*=")
    updated   = False
    new_lines = []
    for line in lines:
        if pattern.match(line):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n")


@router.get("/settings")
async def get_settings():
    env = read_env()
    return {
        "llm_provider":       env.get("LLM_PROVIDER", "ollama"),
        "llm_model":          env.get("LLM_MODEL", "llama3.2"),
        "embed_model":        env.get("EMBED_MODEL", "nomic-embed-text"),
        "image_provider":     env.get("IMAGE_PROVIDER", "placeholder"),
        "ollama_base_url":    env.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        "has_gemini_key":     bool(env.get("GEMINI_API_KEY", "")),
        "has_openrouter_key": bool(env.get("OPENROUTER_API_KEY", "")),
        "has_cloudflare_key": bool(env.get("CLOUDFLARE_API_TOKEN", "")),
        "has_openai_key":     bool(env.get("OPENAI_API_KEY", "")),
    }


@router.post("/settings")
async def update_setting(update: SettingsUpdate):
    allowed = {
        "LLM_PROVIDER", "LLM_MODEL", "EMBED_MODEL", "IMAGE_PROVIDER",
        "OLLAMA_BASE_URL", "GEMINI_API_KEY", "OPENROUTER_API_KEY",
        "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN", "OPENAI_API_KEY",
    }
    if update.key not in allowed:
        return {"success": False, "error": f"Key '{update.key}' not allowed"}
    write_env_key(update.key, update.value)
    return {"success": True, "key": update.key}


@router.get("/settings/validate/{provider}")
async def validate_provider(provider: str):
    env = read_env()

    if provider == "ollama":
        try:
            ollama_url = env.get("OLLAMA_BASE_URL", "http://localhost:11434")
            r = requests.get(f"{ollama_url}/api/tags", timeout=3)
            if r.status_code == 200:
                models = [m["name"].split(":")[0] for m in r.json().get("models", [])]
                return {"valid": True, "message": "Ollama running", "models": models}
            return {"valid": False, "message": "Ollama not responding"}
        except Exception:
            return {"valid": False, "message": "Ollama offline — run: ollama serve"}

    if provider == "gemini":
        key = env.get("GEMINI_API_KEY", "")
        if not key:
            return {"valid": False, "message": "No API key set"}
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": "hi"}]}]},
                timeout=10,
            )
            if r.status_code == 200:
                return {"valid": True, "message": "Gemini ready"}
            if r.status_code == 429:
                return {"valid": False, "message": "Quota exceeded or region restricted"}
            return {"valid": False, "message": "Invalid API key"}
        except Exception as e:
            return {"valid": False, "message": str(e)}

    if provider == "openrouter":
        key = env.get("OPENROUTER_API_KEY", "")
        if not key:
            return {"valid": False, "message": "No API key set"}
        try:
            r = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10,
            )
            if r.status_code == 200:
                data    = r.json()
                credits = data.get("data", {}).get("limit_remaining")
                if credits is not None and credits <= 0:
                    return {"valid": False, "message": "No credits remaining"}
                return {"valid": True, "message": f"Ready · {credits or 'free tier'}"}
            return {"valid": False, "message": "Invalid API key"}
        except Exception as e:
            return {"valid": False, "message": str(e)}

    if provider == "cloudflare":
        token   = env.get("CLOUDFLARE_API_TOKEN", "")
        account = env.get("CLOUDFLARE_ACCOUNT_ID", "")
        if not token or not account:
            return {"valid": False, "message": "Missing token or account ID"}
        try:
            r = requests.get(
                "https://api.cloudflare.com/client/v4/user/tokens/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if r.status_code == 200:
                return {"valid": True, "message": "Cloudflare token valid"}
            return {"valid": False, "message": "Invalid token"}
        except Exception as e:
            return {"valid": False, "message": str(e)}

    return {"valid": False, "message": f"Unknown provider: {provider}"}


@router.get("/settings/ollama-models")
async def ollama_models():
    env        = read_env()
    ollama_url = env.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        r = requests.get(f"{ollama_url}/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"].split(":")[0] for m in r.json().get("models", [])]
            return {"models": models}
    except Exception:
        pass
    return {"models": []}
