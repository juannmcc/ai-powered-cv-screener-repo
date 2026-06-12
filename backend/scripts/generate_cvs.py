"""
CV Generation Script
Generates 25 realistic fake CVs in PDF format using Ollama for content
and ReportLab for PDF layout.
Run: uv run python scripts/generate_cvs.py
"""

import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from io import BytesIO

import requests
from dotenv import load_dotenv
from scripts.cv_data.profiles import PROFILES
from scripts.cv_data.candidates import FIRST_NAMES, LAST_NAMES, CITIES
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus import Image as RLImage
from scripts.cv_data.photo import fetch_photo, image_to_bytes


load_dotenv(Path(__file__).parent.parent / ".env")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL       = os.getenv("LLM_MODEL", "llama3.2")

AVATARS_DIR = Path(__file__).parent.parent / "data" / "avatars"
AVATARS_DIR.mkdir(parents=True, exist_ok=True)


def generate_cv_content(name: str, role: str, stack: str) -> dict:
    prompt = f"""Generate a realistic professional CV for a fake person.
Name: {name}
Role: {role}
Stack: {stack}

Return ONLY a valid JSON object, no markdown, no explanation:
{{
  "summary": "2-3 sentence professional summary",
  "experience": [
    {{
      "title": "Job title",
      "company": "Company name",
      "period": "MMM YYYY - MMM YYYY",
      "bullets": ["quantified achievement 1", "quantified achievement 2", "quantified achievement 3"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree name",
      "institution": "University name",
      "year": "YYYY"
    }}
  ],
  "skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8"],
  "languages": ["English - Native", "Spanish - Intermediate"],
  "certifications": ["Certification 1", "Certification 2"]
}}

Rules:
- 2-3 experience entries, most recent first
- 3 bullet points per experience with quantified achievements
- 1-2 education entries
- 8-10 skills relevant to the stack
- 1-3 certifications relevant to the role
"""
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end   = content.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(content[start:end])
        else:
            raise

    if isinstance(data.get("experience"), list):
        data["experience"] = [
            exp for exp in data["experience"] if isinstance(exp, dict)
        ]

    for exp in data.get("experience", []):
        if not isinstance(exp, dict):
            continue
        exp.setdefault("title", exp.get("job_title", exp.get("position", "Unknown Title")))
        exp.setdefault("company", exp.get("organization", exp.get("employer", "Unknown Company")))
        exp.setdefault("period", exp.get("duration", exp.get("dates", "N/A")))
        exp.setdefault("bullets", exp.get("achievements", exp.get("responsibilities", [])))

    return data

ACCENT = colors.HexColor("#2563EB")
DARK   = colors.HexColor("#111827")
MID    = colors.HexColor("#6B7280")
LIGHT  = colors.HexColor("#E5E7EB")


def build_styles() -> dict:
    return {
        "name": ParagraphStyle("name", fontSize=22, textColor=DARK,
                               fontName="Helvetica-Bold", spaceAfter=14),
        "role": ParagraphStyle("role", fontSize=12, textColor=ACCENT,
                               fontName="Helvetica", spaceAfter=8),
        "section": ParagraphStyle("section", fontSize=10, textColor=ACCENT,
                                  fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=9, textColor=DARK,
                               fontName="Helvetica", spaceAfter=3, leading=14),
        "bullet": ParagraphStyle("bullet", fontSize=9, textColor=DARK,
                                 fontName="Helvetica", leftIndent=12,
                                 spaceAfter=2, leading=13),
        "small": ParagraphStyle("small", fontSize=8, textColor=MID,
                                fontName="Helvetica", spaceAfter=2),
        "contact": ParagraphStyle("contact", fontSize=8, textColor=MID,
                                  fontName="Helvetica"),
    }


def create_cv_pdf(name: str, role: str, city: str, data: dict, output_path: Path, use_photo: bool = True):
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=16*mm, bottomMargin=16*mm,
    )
    styles = build_styles()
    story  = []

    # Header
    parts    = name.split()
    first    = parts[0]
    last     = parts[1] if len(parts) > 1 else ""
    email    = f"{first.lower()}.{last.lower()}@email.com"
    phone    = f"+1 {random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
    linkedin = f"linkedin.com/in/{first.lower()}{last.lower()}"

    photo_flowable = None
    photo_img = fetch_photo(name) if use_photo else None
    if photo_img:
        img_bytes = image_to_bytes(photo_img)
        photo_flowable = RLImage(BytesIO(img_bytes), width=28*mm, height=28*mm)

    name_block = [
        Paragraph(name, styles["name"]),
        Paragraph(role, styles["role"]),
        Paragraph(
            f"{city}  ·  {phone}  ·  {email}  ·  {linkedin}",
            styles["contact"],
        ),
    ]

    if photo_flowable:
        header_table = Table(
            [[photo_flowable, name_block]],
            colWidths=[32*mm, None],
        )
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 4*mm),
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph(name, styles["name"]))
        story.append(Paragraph(role, styles["role"]))
        story.append(Paragraph(
            f"{city}  ·  {phone}  ·  {email}  ·  {linkedin}",
            styles["contact"],
        ))

    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 3*mm))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", styles["section"]))
    story.append(Paragraph(data.get("summary", ""), styles["body"]))
    story.append(Spacer(1, 2*mm))

    # Experience
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT))
    story.append(Paragraph("EXPERIENCE", styles["section"]))
    for exp in data.get("experience", []):
        story.append(Paragraph(f"<b>{exp['title']}</b> — {exp['company']}", styles["body"]))
        story.append(Paragraph(exp["period"], styles["small"]))
        for bullet in exp.get("bullets", []):
            story.append(Paragraph(f"• {bullet}", styles["bullet"]))
        story.append(Spacer(1, 2*mm))

    # Education
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT))
    story.append(Paragraph("EDUCATION", styles["section"]))
    for edu in data.get("education", []):
        story.append(Paragraph(
            f"<b>{edu['degree']}</b> — {edu['institution']} ({edu['year']})",
            styles["body"],
        ))

    # Other
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT))

    left_col = [
        Paragraph("SKILLS", styles["section"]),
        Paragraph("  ·  ".join(data.get("skills", [])), styles["body"]),
        Paragraph("LANGUAGES", styles["section"]),
        Paragraph("  ·  ".join(data.get("languages", [])), styles["body"]),
    ]
    right_col = [
        Paragraph("CERTIFICATIONS", styles["section"]),
        Paragraph("  ·  ".join(data.get("certifications", [])), styles["body"]),
    ]

    table = Table([[left_col, right_col]], colWidths=["60%", "40%"])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(table)

    doc.build(story)


def main():
    import argparse
    from io import BytesIO
    from PIL import Image as PILImage

    _timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    OUTPUT_DIR = Path(__file__).parent.parent / "data" / "cvs" / _timestamp
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Generate fake CVs")
    parser.add_argument("--limit", type=int, default=len(PROFILES),
                        help=f"Number of CVs to generate (max {len(PROFILES)})")
    parser.add_argument("--no-image", action="store_true",
                        help="Skip AI photo generation, use placeholder instead")
    args  = parser.parse_args()
    limit = min(args.limit, len(PROFILES))
    names = FIRST_NAMES.copy()
    random.shuffle(names)

    print(f"Generating {limit} CVs...\n")

    for i, profile in enumerate(PROFILES[:limit]):
        name        = f"{names[i]} {random.choice(LAST_NAMES)}"
        city        = random.choice(CITIES)
        slug        = name.replace(" ", "_")
        output_path = OUTPUT_DIR / f"cv_{str(i+1).zfill(2)}_{slug}.pdf"
        pad         = len(str(limit))

        print(f"[{str(i+1).zfill(pad)}/{limit}] {name} — {profile['role']}...")

        try:
            data = generate_cv_content(name, profile["role"], profile["stack"])

            if not args.no_image:
                try:
                    photo     = fetch_photo(name)
                    img_bytes = image_to_bytes(photo)
                    PILImage.open(BytesIO(img_bytes)).verify()
                    avatar_path = AVATARS_DIR / f"{output_path.stem}.jpg"
                    avatar_path.write_bytes(img_bytes)
                except Exception as e:
                    print(f"           Avatar save failed: {e}")

            create_cv_pdf(name, profile["role"], city, data, output_path, use_photo=not args.no_image)
            print(f"           Saved: {output_path.name}")
        except Exception as e:
            print(f"           Error: {e}")

    print(f"\nDone. {limit} CVs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()




if __name__ == "__main__":
    main()