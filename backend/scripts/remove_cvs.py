"""
Remove CV output folders.
Run: uv run remove-cvs              # removes all folders
     uv run remove-cvs 20260611-1515  # removes specific folder
"""

import sys
import shutil
from pathlib import Path

CVS_DIR = Path(__file__).parent.parent / "data" / "cvs"


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None

    if target:
        folder = CVS_DIR / target
        if not folder.exists():
            print(f"Folder '{target}' not found in data/cvs/")
            print(f"Available: {[f.name for f in CVS_DIR.iterdir() if f.is_dir()]}")
            return
        folders = [folder]
    else:
        folders = [f for f in CVS_DIR.iterdir() if f.is_dir()]

    if not folders:
        print("No CV output folders found.")
        return

    print(f"Found {len(folders)} folder(s):")
    for f in folders:
        count = len(list(f.glob("*.pdf")))
        print(f"  {f.name}  ({count} PDFs)")

    confirm = input("\nDelete? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    for f in folders:
        shutil.rmtree(f)
        print(f"  Deleted: {f.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
