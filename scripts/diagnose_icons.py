#!/usr/bin/env python3
"""
diagnose_icons.py — Discover where passive-tree node icon sprites live inside
the Windows game files and build the a-r-NNN → real sprite name mapping.

Strategy:
  1. Scan ALL .bundle files for Sprite/SpriteAtlas objects
  2. Scan resources.assets for Sprite/Texture2D objects by path_id
  3. Cross-reference with passive_trees.json numeric icon IDs AND
     char-tree-metadata.json a-r-NNN ids
  4. Write results to found_sprites.txt + found_pathids.txt

Run on Windows from repo root:
    python scripts\\diagnose_icons.py --data "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Last Epoch\\Last Epoch_Data"

After running, commit and push the output files.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PASSIVE_TREES_JSON = REPO_ROOT / "last-epoch-data/exports_json/passive_trees.json"
CHAR_TREE_METADATA = REPO_ROOT / "frontend/src/data/raw/char-tree-metadata.json"


def load_target_ids() -> tuple[set[str], set[str]]:
    """Return (numeric_icon_ids_from_passive_trees, ar_nnn_sprite_ids_from_metadata)."""
    numeric: set[str] = set()
    if PASSIVE_TREES_JSON.exists():
        with open(PASSIVE_TREES_JSON, encoding="utf-8") as f:
            pt = json.load(f)
        for tree in pt.get("passiveTrees", []):
            for node in tree.get("nodes", []):
                if node.get("icon"):
                    numeric.add(str(node["icon"]))

    import re
    ar_ids: set[str] = set()
    if CHAR_TREE_METADATA.exists():
        with open(CHAR_TREE_METADATA, encoding="utf-8") as f:
            content = f.read()
        # Extract the numeric part from "a-r-NNN" strings
        ar_ids = set(re.findall(r'"a-r-(\d+)"', content))

    return numeric, ar_ids


def scan_file(path: Path, source_label: str,
              all_sprites: dict, found_pathids: dict,
              numeric_icons: set[str]) -> None:
    """Scan one asset file; update all_sprites and found_pathids in place."""
    import UnityPy
    try:
        env = UnityPy.load(str(path))
    except Exception:
        return

    for obj in env.objects:
        if obj.type.name not in ("Sprite", "SpriteAtlas", "Texture2D"):
            continue
        try:
            d = obj.read()
        except Exception:
            continue

        path_id = str(obj.path_id)

        if obj.type.name == "SpriteAtlas":
            atlas_name = d.m_Name or ""
            for ps in getattr(d, "m_PackedSprites", []):
                try:
                    psd = ps.read()
                    n = psd.m_Name or ""
                    if n:
                        all_sprites[n] = f"{source_label}"
                        if path_id in numeric_icons:
                            found_pathids[path_id] = (n, source_label)
                except Exception:
                    pass
        else:
            n = d.m_Name or ""
            if n:
                all_sprites[n] = source_label
            if path_id in numeric_icons:
                found_pathids[path_id] = (n or f"<unnamed>", source_label)


def run(data_root_str: str) -> None:
    try:
        import UnityPy
    except ImportError:
        print("ERROR: pip install unitypy Pillow")
        sys.exit(1)

    data_root = Path(data_root_str)

    numeric_icons, ar_ids = load_target_ids()
    print(f"Hunting for {len(numeric_icons)} passive tree numeric icon IDs")
    print(f"  (also tracking {len(ar_ids)} a-r-NNN sprite IDs from metadata)")

    all_sprites: dict[str, str] = {}    # sprite name → source label
    found_pathids: dict[str, tuple] = {}  # path_id string → (name, source)

    # ── 1. Scan resources.assets (non-addressable) ───────────────────────────
    res_assets = data_root / "resources.assets"
    if res_assets.exists():
        print(f"\nScanning resources.assets...")
        scan_file(res_assets, "resources.assets", all_sprites, found_pathids, numeric_icons)
        print(f"  → {len(all_sprites)} sprites so far, {len(found_pathids)} path_id hits")
    else:
        print("WARNING: resources.assets not found")

    # ── 2. Scan ALL .bundle files ────────────────────────────────────────────
    bundle_dir = data_root / "StreamingAssets/aa/StandaloneWindows64"
    if bundle_dir.exists():
        bundles = sorted(p for p in bundle_dir.iterdir() if p.suffix == ".bundle")
        print(f"\nScanning {len(bundles)} bundles...")
        before = len(all_sprites)
        for bpath in bundles:
            scan_file(bpath, bpath.name, all_sprites, found_pathids, numeric_icons)
        print(f"  → {len(all_sprites) - before} new sprites from bundles")
        print(f"  → {len(found_pathids)} total path_id hits")
    else:
        print("WARNING: bundle dir not found")

    # ── 3. Summary ───────────────────────────────────────────────────────────
    print(f"\nTotal unique sprites found: {len(all_sprites)}")
    print(f"Passive icon path_id hits: {len(found_pathids)} / {len(numeric_icons)}")
    if found_pathids:
        print("Sample path_id hits:")
        for pid, (name, src) in list(found_pathids.items())[:10]:
            print(f"  path_id={pid} → {name!r}  in  {src}")

    # ── 4. Save output files ─────────────────────────────────────────────────
    out_sprites = REPO_ROOT / "scripts/found_sprites.txt"
    with open(out_sprites, "w", encoding="utf-8") as f:
        for n in sorted(all_sprites.keys()):
            f.write(f"{n}\t{all_sprites[n]}\n")
    print(f"\nSprite list → {out_sprites}")

    out_pathids = REPO_ROOT / "scripts/found_pathids.txt"
    with open(out_pathids, "w", encoding="utf-8") as f:
        for pid in sorted(found_pathids.keys(), key=int):
            name, src = found_pathids[pid]
            f.write(f"{pid}\t{name}\t{src}\n")
    print(f"Path_id hits → {out_pathids}")

    print("\nNext steps:")
    print("  git add scripts\\found_sprites.txt scripts\\found_pathids.txt")
    print("  git commit -m 'data: sprite/pathid dump'")
    print("  git push")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", "-d", required=True,
                        help="Path to Last Epoch_Data directory")
    args = parser.parse_args()
    run(args.data)


if __name__ == "__main__":
    main()
