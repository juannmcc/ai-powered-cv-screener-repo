"""
Remove all generated CV output folders.
Run: uv run remove-cvs
"""

from pathlib import Path
import shutil


CVS_DIR = Path(__file__).parent.parent / "data" / "cvs"


def main():
    folders = [f for f in CVS_DIR.iterdir() if f.is_dir()]

    if not folders:
        print("No CV output folders found.")
        return

    print(f"Found {len(folders)} folder(s):")
    for f in folders:
        count = len(list(f.glob("*.pdf")))
        print(f"  {f.name}  ({count} PDFs)")

    confirm = input("\nDelete all? [y/N] ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    for f in folders:
        shutil.rmtree(f)
        print(f"  Deleted: {f.name}")

    print("\nDone. /data/cvs is clean.")


if __name__ == "__main__":
    main()
