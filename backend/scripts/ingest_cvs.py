"""
Ingest all CVs into ChromaDB.
Run: uv run ingest-cvs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag import ingest_all


def main():
    import shutil
    from app.core.config import CHROMA_DIR

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    results = ingest_all()
    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for e in results["errors"]:
            print(f"  {e['file']}: {e['error']}")

    try:
        import requests
        r = requests.post("http://localhost:8000/api/reload", timeout=3)
        if r.status_code == 200:
            print("Backend reloaded successfully.")
    except Exception:
        pass


if __name__ == "__main__":
    main()
