#!/usr/bin/env python3
"""
extract_images.py — Extract passive tree node icons from the Last Epoch Unity export.

Usage:
    python3 scripts/extract_images.py --export /path/to/LE_Export

What it does:
  1. Reads char-tree-layout.json to collect all unique icon IDs (e.g. "a-r-292")
  2. Searches the Unity export for matching sprite/texture files
  3. Copies + renames them to frontend/public/assets/passive-icons/<iconId>.png
     (or .webp / whatever format the export contains)

The Unity export path can be a local directory or a mounted network share, e.g.:
    /Volumes/DevShare/LE_Export
    /mnt/devshare/LE_Export

After running, the frontend can load icons via:
    /assets/passive-icons/a-r-292.png
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths relative to repo root
# ---------------------------------------------------------------------------
REPO_ROOT     = Path(__file__).resolve().parent.parent
LAYOUT_JSON   = REPO_ROOT / "frontend/src/data/raw/char-tree-layout.json"
OUT_DIR       = REPO_ROOT / "frontend/public/assets/passive-icons"

# Image extensions to search for (in priority order)
IMAGE_EXTS = [".png", ".webp", ".jpg", ".jpeg", ".tga", ".bmp"]


def load_icon_ids() -> set[str]:
    """Collect every unique icon ID referenced in char-tree-layout.json."""
    with open(LAYOUT_JSON) as f:
        data = json.load(f)

    icons: set[str] = set()
    for tree_data in data.values():
        for region in tree_data.get("nodes", []):
            if region is None:
                continue
            for child in region.get("children", []):
                if child and "icon" in child:
                    icons.add(child["icon"])
    return icons


def build_search_index(export_root: Path) -> dict[str, Path]:
    """
    Walk the export directory and build a mapping of stem → file path.
    The stem is the filename without extension, lowercased.
    Only files whose extension is in IMAGE_EXTS are indexed.
    """
    print(f"Indexing image files under: {export_root}")
    print("(This may take a minute for large exports...)")

    index: dict[str, Path] = {}
    count = 0
    for dirpath, _, filenames in os.walk(export_root):
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix.lower() in IMAGE_EXTS:
                # Store by lowercased stem — we'll search for the icon ID within it
                stem = p.stem.lower()
                # Keep first match (shallowest wins)
                if stem not in index:
                    index[stem] = p
                count += 1

    print(f"Indexed {count} image files ({len(index)} unique stems)")
    return index


def find_icon(icon_id: str, index: dict[str, Path]) -> Path | None:
    """
    Find the best matching file for a given icon ID like "a-r-292".

    Unity export naming varies by tool (AssetRipper, UnityPy, etc.).
    Try several candidate stem patterns before giving up.
    """
    numeric = icon_id.split("-")[-1]   # "292"
    candidates = [
        icon_id.lower(),               # "a-r-292"
        icon_id.replace("-", "_").lower(),  # "a_r_292"
        f"passive_{numeric}",
        f"passiveicon_{numeric}",
        f"icon_{numeric}",
        f"node_{numeric}",
        numeric,                        # just "292"
    ]
    for c in candidates:
        if c in index:
            return index[c]

    # Partial match fallback: look for any stem that ends with the numeric part
    suffix = f"_{numeric}"
    for stem, path in index.items():
        if stem.endswith(suffix):
            return path

    return None


def run(export_path: str, dry_run: bool) -> None:
    export_root = Path(export_path).resolve()
    if not export_root.exists():
        print(f"ERROR: Export path does not exist: {export_root}", file=sys.stderr)
        sys.exit(1)

    icon_ids = load_icon_ids()
    print(f"Found {len(icon_ids)} unique icon IDs in char-tree-layout.json")

    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    index = build_search_index(export_root)

    found = 0
    missing = []

    for icon_id in sorted(icon_ids):
        src = find_icon(icon_id, index)
        if src is None:
            missing.append(icon_id)
            continue

        dest = OUT_DIR / f"{icon_id}{src.suffix.lower()}"

        if dry_run:
            print(f"  [DRY] {icon_id} → {src.name}")
        else:
            shutil.copy2(src, dest)
            print(f"  COPY  {icon_id} → {dest.relative_to(REPO_ROOT)}")

        found += 1

    print()
    print(f"Results: {found} found, {len(missing)} missing")

    if missing:
        print(f"\nMissing icon IDs ({len(missing)}):")
        for m in missing:
            print(f"  {m}")

        missing_log = REPO_ROOT / "scripts/missing_icons.txt"
        if not dry_run:
            missing_log.write_text("\n".join(missing) + "\n")
            print(f"\nMissing list saved to: {missing_log.relative_to(REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract passive tree node icons from a Last Epoch Unity export."
    )
    parser.add_argument(
        "--export", "-e",
        required=True,
        metavar="PATH",
        help="Path to the root of the Unity export (e.g. /Volumes/DevShare/LE_Export)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Print what would be copied without actually copying anything",
    )
    args = parser.parse_args()
    run(args.export, args.dry_run)


if __name__ == "__main__":
    main()
