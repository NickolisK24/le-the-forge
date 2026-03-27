#!/usr/bin/env python3
"""
diagnose_icons.py — Discover what passive tree icon sprites are actually
named inside the Windows Unity bundles.

Run this on Windows from the repo root:
    python scripts\diagnose_icons.py --data "C:\Program Files (x86)\Steam\steamapps\common\Last Epoch\Last Epoch_Data"

It will:
  1. List every named Sprite in the skill_icons and SpriteAtlas bundles
  2. Cross-reference with passive_trees.json numeric icon IDs
  3. Try to extract one test sprite so you can see what you get
  4. Print a mapping report so we know how to fix extract_images.py
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PASSIVE_TREES_JSON = REPO_ROOT / "last-epoch-data/exports_json/passive_trees.json"

TARGET_BUNDLES = [
    "skill_icons_assets_all.bundle",
    "database_assets_all.bundle",
    "defaultlocalgroup_assets_all.bundle",
    "pcg_data_assets_all.bundle",
]


def run(data_root_str: str) -> None:
    try:
        import UnityPy
    except ImportError:
        print("ERROR: pip install unitypy Pillow")
        sys.exit(1)

    data_root = Path(data_root_str)
    bundle_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
    if not bundle_dir.exists():
        print(f"ERROR: Bundle dir not found: {bundle_dir}")
        sys.exit(1)

    # ── 1. Collect all sprite names across target bundles ────────────────────
    print("Scanning target bundles for Sprite names...\n")
    all_sprites: dict[str, str] = {}  # name → bundle filename

    for bname in TARGET_BUNDLES:
        bpath = bundle_dir / bname
        if not bpath.exists():
            print(f"  [SKIP] {bname} not found")
            continue
        print(f"  Loading {bname}...")
        env = UnityPy.load(str(bpath))
        count = 0
        for obj in env.objects:
            if obj.type.name in ("Sprite", "SpriteAtlas"):
                try:
                    d = obj.read()
                    # SpriteAtlas: list packed sprite names
                    if obj.type.name == "SpriteAtlas":
                        atlas_name = d.m_Name or ""
                        for ps in getattr(d, "m_PackedSprites", []):
                            try:
                                psd = ps.read()
                                n = psd.m_Name or ""
                                if n:
                                    all_sprites[n] = f"{bname} (atlas: {atlas_name})"
                                    count += 1
                            except Exception:
                                pass
                    else:
                        n = d.m_Name or ""
                        if n:
                            all_sprites[n] = bname
                            count += 1
                except Exception:
                    pass
        print(f"    → {count} named sprites/atlas-entries found")

    print(f"\nTotal unique named sprites: {len(all_sprites)}")

    # ── 2. Load passive tree numeric icon IDs ────────────────────────────────
    numeric_icons: set[int] = set()
    if PASSIVE_TREES_JSON.exists():
        with open(PASSIVE_TREES_JSON, encoding="utf-8") as f:
            pt = json.load(f)
        for tree in pt.get("passiveTrees", []):
            for node in tree.get("nodes", []):
                icon = node.get("icon")
                if icon:
                    numeric_icons.add(int(icon))
        print(f"Passive tree numeric icon IDs: {len(numeric_icons)}")
    else:
        print("WARNING: passive_trees.json not found — skipping numeric ID check")

    # ── 3. Check if any sprite names match numeric IDs ───────────────────────
    numeric_strs = {str(n) for n in numeric_icons}
    numeric_matches = {n: all_sprites[n] for n in all_sprites if n in numeric_strs}
    print(f"Sprites whose name IS a numeric icon ID: {len(numeric_matches)}")
    if numeric_matches:
        print("  Matches:", list(numeric_matches.items())[:10])

    # ── 4. Print a sample of all sprite names so we can identify the pattern ─
    print(f"\n── Sample of all found sprite names (first 60) ──")
    for n in sorted(all_sprites.keys())[:60]:
        print(f"  {n!r}  ←  {all_sprites[n]}")

    # ── 5. Try to extract one sprite as a test ───────────────────────────────
    print("\n── Attempting to extract first available sprite ──")
    for bname in TARGET_BUNDLES:
        bpath = bundle_dir / bname
        if not bpath.exists():
            continue
        env = UnityPy.load(str(bpath))
        for obj in env.objects:
            if obj.type.name == "Sprite":
                try:
                    d = obj.read()
                    n = d.m_Name or ""
                    if n:
                        img = d.image
                        out = Path("C:/tmp") if Path("C:/tmp").exists() else Path.home()
                        dest = out / f"test_sprite_{n[:30]}.png"
                        img.save(dest)
                        print(f"  SUCCESS: {n!r} → {img.size} saved to {dest}")
                        break
                except Exception as e:
                    print(f"  FAIL {n!r}: {e}")
                    break
        break

    # ── 6. Save full sprite name list to file ────────────────────────────────
    out_file = REPO_ROOT / "scripts/found_sprites.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        for n in sorted(all_sprites.keys()):
            f.write(f"{n}\t{all_sprites[n]}\n")
    print(f"\nFull sprite list saved to: {out_file}")
    print("Commit and push that file so we can build the correct name mapping on Mac.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", "-d", required=True,
                        help="Path to Last Epoch_Data directory")
    args = parser.parse_args()
    run(args.data)


if __name__ == "__main__":
    main()
