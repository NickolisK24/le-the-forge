#!/usr/bin/env python3
"""
extract_images.py — Extract passive tree node icons from Last Epoch game files.

HOW THE ICON NAMING WORKS
--------------------------
The frontend uses icon IDs like "a-r-292" (from char-tree-layout.json).
These are 1-based indices into the SkillIconsSpriteAtlas packed sprite list
inside resources.assets. So "a-r-292" = atlas.m_PackedSprites[291].

This script extracts all referenced a-r-NNN icons from the atlas and saves them
to frontend/public/assets/passive-icons/a-r-NNN.png.

Install dependency first:
    pip install unitypy Pillow

Usage (point at the game's Data folder containing resources.assets):
    # macOS (direct game install folder):
    python3 scripts/extract_images.py --data "/path/to/Last Epoch_Data"

    # macOS Steam default:
    python3 scripts/extract_images.py \\
        --data "$HOME/Library/Application Support/Steam/steamapps/common/Last Epoch/Last Epoch.app/Contents/Data"

    # Windows Steam default:
    python3 scripts/extract_images.py \\
        --data "C:/Program Files (x86)/Steam/steamapps/common/Last Epoch/Last Epoch_Data"

    # Dry-run (list what would be extracted without writing files):
    python3 scripts/extract_images.py --data "..." --dry-run
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT       = Path(__file__).resolve().parent.parent
PASSIVE_TREES   = REPO_ROOT / "frontend/src/data/passiveTrees/index.ts"
OUT_DIR         = REPO_ROOT / "frontend/public/assets/passive-icons"
ATLAS_NAME_HINT = "SkillIcons"   # substring of the SpriteAtlas m_Name


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


def load_icon_ids() -> list[int]:
    """Return sorted list of unique a-r-NNN numeric indices from passiveTrees/index.ts."""
    with open(PASSIVE_TREES, encoding="utf-8") as f:
        content = f.read()
    nums = sorted(set(int(m) for m in re.findall(r'iconId:"a-r-(\d+)"', content)))
    return nums


def run(data_path: str, dry_run: bool) -> None:
    import UnityPy

    data_root = Path(data_path).resolve()
    resources_assets = data_root / "resources.assets"
    if not resources_assets.exists():
        print(f"ERROR: resources.assets not found at: {resources_assets}")
        print("Make sure --data points to the 'Last Epoch_Data' folder.")
        sys.exit(1)

    icon_nums = load_icon_ids()
    print(f"Loaded {len(icon_nums)} icon IDs from passiveTrees/index.ts")
    print(f"  Range: a-r-{min(icon_nums)} .. a-r-{max(icon_nums)}")
    print(f"Loading: {resources_assets}")

    env = UnityPy.load(str(resources_assets))

    # Find the SkillIconsSpriteAtlas and load its packed sprites in order
    atlas_sprites: list = []
    for obj in env.objects:
        if obj.type.name != "SpriteAtlas":
            continue
        try:
            d = obj.read()
            if ATLAS_NAME_HINT in (d.m_Name or ""):
                print(f"Found atlas: {d.m_Name!r} with "
                      f"{len(getattr(d, 'm_PackedSprites', []))} sprites")
                atlas_sprites = list(getattr(d, "m_PackedSprites", []))
                break
        except Exception:
            pass

    if not atlas_sprites:
        print(f"ERROR: Could not find SpriteAtlas containing '{ATLAS_NAME_HINT}'")
        sys.exit(1)

    print(f"Atlas has {len(atlas_sprites)} packed sprites")

    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    saved = 0
    errors = []
    for ar_num in icon_nums:
        idx = ar_num - 1   # a-r-NNN is 1-based
        if idx >= len(atlas_sprites):
            errors.append(f"a-r-{ar_num}: index {idx} out of range (atlas has {len(atlas_sprites)})")
            continue
        try:
            sprite_data = atlas_sprites[idx].read()
            img = sprite_data.image
            dest = OUT_DIR / f"a-r-{ar_num}.png"
            if dry_run:
                print(f"  [DRY] a-r-{ar_num} → atlas[{idx}] ({sprite_data.m_Name!r})")
            else:
                img.save(dest)
                saved += 1
        except Exception as exc:
            errors.append(f"a-r-{ar_num}: {exc}")

    print()
    if dry_run:
        print(f"DRY RUN: would extract {len(icon_nums)} icons")
    else:
        print(f"Extracted: {saved} / {len(icon_nums)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors[:10]:
            print(f"  {e}")
    else:
        print("All icons extracted successfully!")


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
        help="Path to Last Epoch game data directory containing resources.assets",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="List what would be extracted without writing any files",
    )
    args = parser.parse_args()
    check_deps()
    run(args.data, args.dry_run)


if __name__ == "__main__":
    main()
