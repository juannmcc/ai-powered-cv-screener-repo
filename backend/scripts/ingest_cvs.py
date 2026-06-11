"""
Ingest all CVs into ChromaDB.
Run: uv run ingest-cvs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag import ingest_all


def main():
    results = ingest_all()
    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for e in results["errors"]:
            print(f"  {e['file']}: {e['error']}")


if __name__ == "__main__":
    main()
