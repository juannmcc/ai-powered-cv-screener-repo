"""
Photo generation for CVs.
Supports:
  - cloudflare  : FLUX-1-schnell via Cloudflare Workers AI (free, 10k/day)
  - openai      : DALL-E 3 via OpenAI API (pay-as-you-go, ~$0.04/image)
  - placeholder : Colored avatar with initials (free, no setup)

Configure via IMAGE_PROVIDER in backend/.env
"""

import base64
import hashlib
import os
import requests
import time
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv(Path(__file__).parent.parent.parent / ".env")

IMAGE_PROVIDER        = os.getenv("IMAGE_PROVIDER", "placeholder")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN  = os.getenv("CLOUDFLARE_API_TOKEN", "")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")

AVATAR_COLORS = [
    "#2563EB", "#7C3AED", "#DB2777", "#D97706",
    "#059669", "#DC2626", "#0891B2", "#65A30D",
]

PHOTO_STYLES = [
    "professional headshot, business attire, neutral background, studio lighting",
    "professional portrait, smart casual, office background, natural lighting",
    "corporate headshot, formal attire, clean background, soft lighting",
]


# CloudFlare Flux
def _fetch_cloudflare(name: str, size: int = 200) -> Image.Image | None:
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        print("           Cloudflare credentials missing — falling back to placeholder")
        return None

    seed   = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    style  = PHOTO_STYLES[seed % len(PHOTO_STYLES)]
    prompt = f"{style}, photorealistic, high quality"

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}"
        f"/ai/run/@cf/black-forest-labs/flux-1-schnell"
    )

    try:
        r = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt, "num_steps": 4},
            timeout=30,
        )
        r.raise_for_status()
        img_b64   = r.json()["result"]["image"]
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        time.sleep(2)
        return img.resize((size, size))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"           Rate limited, waiting 30s...")
            time.sleep(30)
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                r.raise_for_status()
                img_b64   = r.json()["result"]["image"]
                img_bytes = base64.b64decode(img_b64)
                img = Image.open(BytesIO(img_bytes)).convert("RGB")
                return img.resize((size, size))
            except Exception:
                pass
        print(f"           Cloudflare photo failed for {name}: {e}")
        return None


# OpenAI Dall·E3
def _fetch_openai(name: str, size: int = 200) -> Image.Image | None:
    if not OPENAI_API_KEY:
        print("           OpenAI API key missing — falling back to placeholder")
        return None

    seed   = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    style  = PHOTO_STYLES[seed % len(PHOTO_STYLES)]
    prompt = (
        f"A {style} of a professional person. "
        f"Clean, realistic, suitable for a CV or LinkedIn profile. "
        f"No text, no watermarks."
    )

    try:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "b64_json",
            },
            timeout=60,
        )
        r.raise_for_status()
        img_b64   = r.json()["data"][0]["b64_json"]
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        return img.resize((size, size))
    except Exception as e:
        print(f"           OpenAI photo failed for {name}: {e}")
        return None


# Placeholder
def _make_placeholder(name: str, size: int = 200) -> Image.Image:
    seed     = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    color    = AVATAR_COLORS[seed % len(AVATAR_COLORS)]
    parts    = name.split()
    initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()

    img  = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)

    font_size = size // 3
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initials, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2, (size - h) / 2 - 4), initials, fill="white", font=font)

    return img


def fetch_photo(name: str, size: int = 200) -> Image.Image:
    if IMAGE_PROVIDER == "cloudflare":
        img = _fetch_cloudflare(name, size)
        if img:
            return img
    elif IMAGE_PROVIDER == "openai":
        img = _fetch_openai(name, size)
        if img:
            return img
    return _make_placeholder(name, size)


def image_to_bytes(img: Image.Image, fmt: str = "JPEG") -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
