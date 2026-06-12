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
    import shutil
    from pathlib import Path

    target = sys.argv[1] if len(sys.argv) > 1 else None
    CVS_DIR    = Path(__file__).parent.parent / "data" / "cvs"
    AVATARS_DIR = Path(__file__).parent.parent / "data" / "avatars"

    folders = [CVS_DIR / target] if target else [f for f in CVS_DIR.iterdir() if f.is_dir()]

    if target and not (CVS_DIR / target).exists():
        print(f"Folder '{target}' not found.")
        print(f"Available: {[f.name for f in CVS_DIR.iterdir() if f.is_dir()]}")
        return

    if not folders:
        print("No CV output folders found.")
        return

    print(f"Found {len(folders)} folder(s):")
    for f in folders:
        count = len(list(f.glob("*.pdf")))
        print(f"  {f.name}  ({count} PDFs)")

    avatars_count = len(list(AVATARS_DIR.glob("*.jpg"))) if AVATARS_DIR.exists() else 0
    print(f"  avatars/  ({avatars_count} JPGs)")

    confirm = input("\nDelete all? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    for f in folders:
        shutil.rmtree(f)
        print(f"  Deleted: {f.name}")

    if AVATARS_DIR.exists():
        shutil.rmtree(AVATARS_DIR)
        AVATARS_DIR.mkdir()
        print(f"  Cleared: avatars/")

    print("\nDone.")


if __name__ == "__main__":
    main()
