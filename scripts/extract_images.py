#!/usr/bin/env python3
"""
extract_images.py — Extract passive tree node icons from Last Epoch game files.

Uses UnityPy to read Unity binary asset files (.assets, .bundle) directly,
finds every Sprite whose name matches an icon ID from char-tree-layout.json
(e.g. "a-r-292"), and exports it as a PNG to:
    frontend/public/assets/passive-icons/<iconId>.png

Install dependency first:
    pip install unitypy Pillow

Usage:
    # Point at the game's Data directory (most common):
    python3 scripts/extract_images.py --data "/path/to/Last Epoch_Data"

    # macOS Steam default:
    python3 scripts/extract_images.py \\
        --data "$HOME/Library/Application Support/Steam/steamapps/common/Last Epoch/Last Epoch.app/Contents/Data"

    # Windows Steam default:
    python3 scripts/extract_images.py \\
        --data "C:/Program Files (x86)/Steam/steamapps/common/Last Epoch/Last Epoch_Data"

    # You can also point at the Unity project export if it contains .assets files:
    python3 scripts/extract_images.py --data /Volumes/DevShare/LE_Export

    # Dry-run (list what would be extracted without writing files):
    python3 scripts/extract_images.py --data "..." --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths relative to repo root
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parent.parent
LAYOUT_JSON = REPO_ROOT / "frontend/src/data/raw/char-tree-layout.json"
OUT_DIR     = REPO_ROOT / "frontend/public/assets/passive-icons"

# Asset file extensions UnityPy can read
ASSET_EXTS = {".assets", ".bundle", ".resS", ""}   # "" catches extension-less files


def check_deps() -> None:
    missing = []
    try:
        import UnityPy  # noqa: F401
    except ImportError:
        missing.append("unitypy")
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        missing.append("Pillow")
    if missing:
        print("ERROR: Missing required packages. Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


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


def iter_asset_files(data_root: Path):
    """Yield all Unity asset/bundle files under data_root."""
    for p in data_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in ASSET_EXTS:
            yield p


def run(data_path: str, dry_run: bool) -> None:
    import UnityPy

    data_root = Path(data_path).resolve()
    if not data_root.exists():
        print(f"ERROR: Path does not exist: {data_root}", file=sys.stderr)
        sys.exit(1)

    icon_ids = load_icon_ids()
    print(f"Loaded {len(icon_ids)} icon IDs from char-tree-layout.json")
    print(f"Scanning: {data_root}")
    print()

    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    found:   dict[str, bool] = {}   # icon_id -> True once saved
    scanned_files = 0

    for asset_file in iter_asset_files(data_root):
        # Skip if all icons already found
        remaining = icon_ids - set(found.keys())
        if not remaining:
            break

        try:
            env = UnityPy.load(str(asset_file))
        except Exception:
            continue

        file_had_match = False
        for obj in env.objects:
            if obj.type.name != "Sprite":
                continue
            try:
                data = obj.read()
            except Exception:
                continue

            name = getattr(data, "name", "") or ""
            if name not in remaining:
                continue

            # Found a match — extract the image
            file_had_match = True
            try:
                img = data.image
                dest = OUT_DIR / f"{name}.png"
                if dry_run:
                    print(f"  [DRY] {name}  ←  {asset_file.name}")
                else:
                    img.save(dest)
                    print(f"  SAVE  {name}.png")
                found[name] = True
            except Exception as exc:
                print(f"  WARN  {name}: could not extract image — {exc}")

        scanned_files += 1
        if file_had_match:
            print(f"  ↳ matched in {asset_file.relative_to(data_root)}")

    # Summary
    print()
    print(f"Scanned {scanned_files} asset files")
    print(f"Extracted: {len(found)} / {len(icon_ids)}")

    missing = sorted(icon_ids - set(found.keys()))
    if missing:
        print(f"\nMissing ({len(missing)} icons not found in any asset file):")
        for m in missing:
            print(f"  {m}")
        missing_log = REPO_ROOT / "scripts/missing_icons.txt"
        if not dry_run:
            missing_log.write_text("\n".join(missing) + "\n")
            print(f"\nSaved missing list → {missing_log.relative_to(REPO_ROOT)}")
    else:
        print("\nAll icons extracted successfully!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Last Epoch passive tree icons using UnityPy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--data", "-d",
        required=True,
        metavar="PATH",
        help="Path to Last Epoch game data directory (e.g. 'Last Epoch_Data') "
             "or Unity project export containing .assets/.bundle files",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="List matching sprites without writing any files",
    )
    args = parser.parse_args()
    check_deps()
    run(args.data, args.dry_run)


if __name__ == "__main__":
    main()
