"""
CV Management API — list, generate, ingest, and delete CV collections.
"""

import asyncio
import shutil
import sqlite3
import subprocess
import sys
import os
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import AVATARS_DIR, BASE_DIR, CHROMA_DIR, CVS_DIR

router = APIRouter()


def _folder_info(folder: Path) -> dict:
    pdfs = list(folder.glob("*.pdf"))
    return {
        "name":  folder.name,
        "count": len(pdfs),
        "pdfs":  [p.name for p in sorted(pdfs)],
    }


@router.get("/cvs")
async def list_cvs():
    if not CVS_DIR.exists():
        return {"folders": [], "total_pdfs": 0, "ingested_chunks": 0}

    folders    = sorted([f for f in CVS_DIR.iterdir() if f.is_dir()], reverse=True)
    total_pdfs = sum(len(list(f.glob("*.pdf"))) for f in folders)

    chunks = 0
    try:
        db = CHROMA_DIR / "chroma.sqlite3"
        if db.exists():
            conn = sqlite3.connect(str(db))
            cur  = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM embeddings")
            chunks = cur.fetchone()[0]
            conn.close()
    except Exception:
        pass

    return {
        "folders":        [_folder_info(f) for f in folders],
        "total_pdfs":     total_pdfs,
        "ingested_chunks": chunks,
    }


@router.delete("/cvs/{folder_name}")
async def delete_folder(folder_name: str):
    folder = CVS_DIR / folder_name
    if not folder.exists():
        return {"success": False, "error": "Folder not found"}
    shutil.rmtree(folder)
    return {"success": True, "deleted": folder_name}


@router.delete("/cvs")
async def delete_all():
    if CVS_DIR.exists():
        for f in CVS_DIR.iterdir():
            if f.is_dir():
                shutil.rmtree(f)

    if AVATARS_DIR.exists():
        shutil.rmtree(AVATARS_DIR)
        AVATARS_DIR.mkdir()

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        CHROMA_DIR.mkdir()

    return {"success": True}


@router.post("/cvs/ingest")
async def ingest_cvs(folder: str = None):
    async def stream():
        args = [sys.executable, "-u", "-m", "scripts.ingest_cvs"]
        if folder:
            args.extend(["--folder", folder])
        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(BASE_DIR),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            async for line in process.stdout:
                yield f"data: {line.decode().rstrip()}\n\n"
            await process.wait()
            yield "data: __DONE__\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            yield "data: __DONE__\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


from fastapi import Query

@router.post("/cvs/generate")
async def generate_cvs(
    limit: int = Query(default=25),
    no_image: bool = Query(default=False),
):
    async def stream():
        args = [sys.executable, "-u", "-m", "scripts.generate_cvs", "--limit", str(limit)]
        if no_image:
            args.append("--no-image")
        
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(BASE_DIR),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        async for line in process.stdout:
            yield f"data: {line.decode().rstrip()}\n\n"
        await process.wait()
        yield "data: __DONE__\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")