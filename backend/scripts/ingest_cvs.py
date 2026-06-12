"""
Ingest all CVs into ChromaDB.
Run: uv run ingest-cvs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag import ingest_all


def main():
    import argparse
    from pathlib import Path
    from app.core.config import CVS_DIR

    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, default=None,
                        help="Specific folder name to ingest")
    args = parser.parse_args()

    if args.folder:
        cvs_dir = CVS_DIR / args.folder
        if not cvs_dir.exists():
            print(f"Folder '{args.folder}' not found.")
            return
        if not list(cvs_dir.glob("*.pdf")):
            print(f"No PDFs found in '{args.folder}'. Generate CVs first.")
            return
    else:
        cvs_dir = None

    from app.services.rag import ingest_all
    results = ingest_all(cvs_dir)
    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for e in results["errors"]:
            print(f"  {e['file']}: {e['error']}")


if __name__ == "__main__":
    main()
