"""
Ingest CVs into ChromaDB using IngestUseCase.
Run: uv run ingest-cvs
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    from app.core.config import CVS_DIR
    from app.infrastructure.pdf.factory import get_pdf_reader
    from app.infrastructure.embeddings.factory import get_embedder
    from app.infrastructure.vector_store.factory import get_vector_store
    from app.application.ingest_use_case import IngestUseCase

    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, default=None)
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
        folders = sorted([f for f in CVS_DIR.iterdir() if f.is_dir()], reverse=True)
        if not folders:
            print("No CV folders found.")
            return
        cvs_dir = folders[0]
        print(f"Using folder: {cvs_dir.name}")

    use_case = IngestUseCase(
        pdf_reader=get_pdf_reader(),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )

    results = use_case.execute(cvs_dir)

    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for e in results["errors"]:
            print(f"  {e['file']}: {e['error']}")


if __name__ == "__main__":
    main()
