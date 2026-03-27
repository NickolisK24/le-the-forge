#!/usr/bin/env python3
"""
diagnose_icons.py — Scan ALL Windows Unity bundles to find which one contains
the passive tree node icon sprites (numeric IDs like 16303, 18457, etc.).

Run on Windows from repo root:
    python scripts\\diagnose_icons.py --data "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Last Epoch\\Last Epoch_Data"

After running, commit and push scripts/found_sprites.txt
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PASSIVE_TREES_JSON = REPO_ROOT / "last-epoch-data/exports_json/passive_trees.json"


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

    # Load passive tree numeric icon IDs we need to find
    numeric_icons: set[str] = set()
    if PASSIVE_TREES_JSON.exists():
        with open(PASSIVE_TREES_JSON, encoding="utf-8") as f:
            pt = json.load(f)
        for tree in pt.get("passiveTrees", []):
            for node in tree.get("nodes", []):
                icon = node.get("icon")
                if icon:
                    numeric_icons.add(str(icon))
        print(f"Hunting for {len(numeric_icons)} passive tree numeric icon IDs...")
    else:
        print("WARNING: passive_trees.json not found")

    all_sprites: dict[str, str] = {}  # name → bundle filename
    found_passive: dict[str, str] = {}  # numeric id → bundle name

    bundles = sorted(p for p in bundle_dir.iterdir() if p.suffix == ".bundle")
    print(f"Scanning {len(bundles)} bundles...\n")

    for bpath in bundles:
        bname = bpath.name
        try:
            env = UnityPy.load(str(bpath))
        except Exception:
            continue

        bundle_sprites: list[str] = []
        for obj in env.objects:
            if obj.type.name not in ("Sprite", "SpriteAtlas"):
                continue
            try:
                d = obj.read()
                if obj.type.name == "SpriteAtlas":
                    for ps in getattr(d, "m_PackedSprites", []):
                        try:
                            psd = ps.read()
                            n = psd.m_Name or ""
                            if n:
                                bundle_sprites.append(n)
                                all_sprites[n] = bname
                        except Exception:
                            pass
                else:
                    n = d.m_Name or ""
                    if n:
                        bundle_sprites.append(n)
                        all_sprites[n] = bname
            except Exception:
                pass

        # Check if any passive icon IDs are in this bundle
        hits = [n for n in bundle_sprites if n in numeric_icons]
        if hits:
            print(f"  *** HIT in {bname}: {hits[:5]}")
            for h in hits:
                found_passive[h] = bname

    print(f"\nTotal unique sprites found: {len(all_sprites)}")
    print(f"Passive icon IDs found: {len(found_passive)} / {len(numeric_icons)}")
    if found_passive:
        print("Found in bundles:", set(found_passive.values()))
        print("Sample matches:", list(found_passive.items())[:10])

    # Save full list
    out_file = REPO_ROOT / "scripts/found_sprites.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        for n in sorted(all_sprites.keys()):
            f.write(f"{n}\t{all_sprites[n]}\n")
    print(f"\nFull sprite list saved to: {out_file}")
    print("Now run: git add scripts\\found_sprites.txt && git commit -m 'data: full sprite dump' && git push")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", "-d", required=True,
                        help="Path to Last Epoch_Data directory")
    args = parser.parse_args()
    run(args.data)


if __name__ == "__main__":
    main()
