"""
Photo generation for CVs.
Supports: cloudflare (FLUX, AI-generated) | placeholder (initials, no API)
Configured via IMAGE_PROVIDER in .env
"""

import base64
import hashlib
import os
from io import BytesIO
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv(Path(__file__).parent.parent.parent / ".env")

IMAGE_PROVIDER       = os.getenv("IMAGE_PROVIDER", "placeholder")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN  = os.getenv("CLOUDFLARE_API_TOKEN", "")

AVATAR_COLORS = [
    "#2563EB", "#7C3AED", "#DB2777", "#D97706",
    "#059669", "#DC2626", "#0891B2", "#65A30D",
]


def _fetch_cloudflare(name: str, size: int = 200) -> Image.Image | None:
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        print(f"           Cloudflare credentials missing — falling back to placeholder")
        return None

    seed   = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    styles = [
        "professional headshot, business attire, neutral background, studio lighting",
        "professional portrait, smart casual, office background, natural lighting",
        "corporate headshot, formal attire, clean background, soft lighting",
    ]
    style  = styles[seed % len(styles)]
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
        data     = r.json()
        img_b64  = data["result"]["image"]
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        return img.resize((size, size))
    except Exception as e:
        print(f"           Cloudflare photo failed for {name}: {e}")
        return None


def _make_placeholder(name: str, size: int = 200) -> Image.Image:
    seed   = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    color  = AVATAR_COLORS[seed % len(AVATAR_COLORS)]
    parts  = name.split()
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
    return _make_placeholder(name, size)


def image_to_bytes(img: Image.Image, fmt: str = "JPEG") -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
