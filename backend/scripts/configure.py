"""
Interactive configuration CLI for CV Screener.
Run: uv run configure
"""

import os
import re
import subprocess
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)


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
    content = ENV_PATH.read_text() if ENV_PATH.exists() else ""
    lines   = content.splitlines()
    pattern = re.compile(rf"^{re.escape(key)}\s*=")
    updated = False

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


def current(env: dict, key: str, default: str = "not set") -> str:
    return env.get(key, default)


def hr():
    print("─" * 50)


def get_ollama_models() -> list[str]:
    try:
        r = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=5,
        )
        lines  = r.stdout.strip().splitlines()[1:]  # skip header
        return [l.split()[0].split(":")[0] for l in lines if l.strip()]
    except Exception:
        return []


def ollama_pull(model: str) -> bool:
    print(f"\n  Pulling {model} from Ollama library...")
    try:
        result = subprocess.run(["ollama", "pull", model])
        return result.returncode == 0
    except Exception as e:
        print(f"  Error: {e}")
        return False


LLM_PROVIDERS = {
    "ollama": {
        "desc": "Free, local. No API key needed.",
        "keys": [],
    },
    "gemini": {
        "desc": "Free tier (region restricted). Requires GEMINI_API_KEY.",
        "keys": ["GEMINI_API_KEY"],
        "url":  "https://aistudio.google.com/apikey",
    },
    "openrouter": {
        "desc": "Free tier / pay-as-you-go. Requires OPENROUTER_API_KEY.",
        "keys": ["OPENROUTER_API_KEY"],
        "url":  "https://openrouter.ai/settings/keys",
    },
}

IMAGE_PROVIDERS = {
    "openai": {
        "desc": "Pay-as-you-go. DALL-E 3, high quality. ~$0.04/image.",
        "keys": ["OPENAI_API_KEY"],
        "url":  "https://platform.openai.com/api-keys",
    },
    "cloudflare": {
        "desc": "Free (10k/day). Real FLUX AI-generated photos.",
        "keys": ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"],
        "url":  "https://dash.cloudflare.com → Workers AI → API Tokens",
    },
    "placeholder": {
        "desc": "Free, no setup. Colored avatar with initials.",
        "keys": [],
    },
}


def configure_llm_provider(env: dict):
    hr()
    print("  LLM PROVIDER\n")
    active = current(env, "LLM_PROVIDER", "ollama")

    for name, cfg in LLM_PROVIDERS.items():
        marker = " [ACTIVE]" if name == active else ""
        print(f"    {name:<12} — {cfg['desc']}{marker}")

    print(f"\n  Browse models:")
    print(f"    OpenRouter → https://openrouter.ai/models")
    print(f"    Gemini     → https://ai.google.dev/gemini-api/docs/models")

    choice = input("\n  Change provider? [name / n to cancel]: ").strip().lower()

    if choice == "n" or choice == "":
        print("  Cancelled.")
        return

    if choice not in LLM_PROVIDERS:
        print(f"  Provider '{choice}' not found. Available: {', '.join(LLM_PROVIDERS)}")
        return

    cfg = LLM_PROVIDERS[choice]
    missing = [k for k in cfg["keys"] if not env.get(k)]

    if missing:
        print(f"\n  Missing credentials: {', '.join(missing)}")
        if "url" in cfg:
            print(f"  Get your key at: {cfg['url']}")
        print(f"  Add them to backend/.env and run configure again.")
        return

    write_env_key("LLM_PROVIDER", choice)
    print(f"\n  LLM provider changed to '{choice}' ✓")


def configure_image_provider(env: dict):
    hr()
    print("  IMAGE PROVIDER\n")
    active = current(env, "IMAGE_PROVIDER", "placeholder")

    for name, cfg in IMAGE_PROVIDERS.items():
        marker = " [ACTIVE]" if name == active else ""
        print(f"    {name:<12} — {cfg['desc']}{marker}")

    choice = input("\n  Change provider? [name / n to cancel]: ").strip().lower()

    if choice == "n" or choice == "":
        print("  Cancelled.")
        return

    if choice not in IMAGE_PROVIDERS:
        print(f"  Provider '{choice}' not found. Available: {', '.join(IMAGE_PROVIDERS)}")
        return

    cfg     = IMAGE_PROVIDERS[choice]
    missing = [k for k in cfg["keys"] if not env.get(k)]

    if missing:
        print(f"\n  Missing credentials: {', '.join(missing)}")
        if "url" in cfg:
            print(f"  Setup guide: {cfg['url']}")
        print(f"  Add them to backend/.env and run configure again.")
        return

    write_env_key("IMAGE_PROVIDER", choice)
    print(f"\n  Image provider changed to '{choice}' ✓")


def configure_llm_model(env: dict):
    hr()
    print("  LLM MODEL\n")
    active   = current(env, "LLM_MODEL", "llama3.2")
    provider = current(env, "LLM_PROVIDER", "ollama")
    installed = get_ollama_models()

    if installed:
        print("  Installed Ollama models:")
        for m in installed:
            marker = " [ACTIVE]" if m == active else ""
            print(f"    {m}{marker}")
    else:
        print("  No Ollama models found (is ollama serve running?)")

    print(f"\n  Browse more models:")
    print(f"    Ollama     → https://ollama.com/library")
    print(f"    OpenRouter → https://openrouter.ai/models")
    print(f"    Gemini     → https://ai.google.dev/gemini-api/docs/models")

    choice = input("\n  Enter model name [or n to cancel]: ").strip()

    if choice.lower() == "n" or choice == "":
        print("  Cancelled.")
        return

    if provider == "ollama" and choice not in installed:
        print(f"\n  Model '{choice}' is not installed locally.")
        pull = input(f"  Pull from Ollama library now? [y/n]: ").strip().lower()
        if pull == "y":
            success = ollama_pull(choice)
            if not success:
                print(f"  Pull failed. Check the model name at https://ollama.com/library")
                return
        else:
            print("  Cancelled.")
            return

    write_env_key("LLM_MODEL", choice)
    print(f"\n  LLM model changed to '{choice}' ✓")


def main():
    env = read_env()

    while True:
        hr()
        print("\n  CV SCREENER — Configuration\n")
        print(f"  Current settings:")
        print(f"    LLM Provider  : {current(env, 'LLM_PROVIDER', 'ollama')}")
        print(f"    LLM Model     : {current(env, 'LLM_MODEL', 'llama3.2')}")
        print(f"    Image Provider: {current(env, 'IMAGE_PROVIDER', 'placeholder')}")
        print()
        print("  What do you want to configure?")
        print("    1. LLM Provider")
        print("    2. Image Provider")
        print("    3. LLM Model")
        print("    4. Exit")

        choice = input("\n  Choice [1-4]: ").strip()

        if choice == "1":
            configure_llm_provider(env)
        elif choice == "2":
            configure_image_provider(env)
        elif choice == "3":
            configure_llm_model(env)
        elif choice == "4" or choice.lower() == "n":
            print("\n  Bye.\n")
            break
        else:
            print("  Invalid option.")

        env = read_env()


if __name__ == "__main__":
    main()
