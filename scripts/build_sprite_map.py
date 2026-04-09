#!/usr/bin/env python3
"""
build_sprite_map.py — Builds the complete numeric icon ID → sprite atlas mapping
by cross-referencing two data sources that already exist in the repo.

Data sources:
  1. frontend/src/data/skillTrees/index.ts  (local skill tree data)
     - Nodes have `iconId` in "a-r-NNN" format (string)
     - These a-r-* keys are fully mapped in iconSpriteMap.json with atlas [x, y] coords

  2. data/classes/community_skill_trees.json  (API skill tree data)
     - Nodes have `icon` as raw integers (Unity path_ids)
     - Only ~390/939 of these are currently mapped in iconSpriteMap.json

Both sources share the same tree IDs (e.g., "to50" for Tornado, "fi9" for Fireball)
and the same node names. This script joins on (tree_id, normalized_node_name) to
produce the complete numeric → a-r-* mapping.

When to re-run: After game patches that add new skill tree nodes. Run from the repo
root: python scripts/build_sprite_map.py

Output: Updates frontend/src/data/iconSpriteMap.json in-place with new entries.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_TREES_PATH = ROOT / "frontend" / "src" / "data" / "skillTrees" / "index.ts"
API_TREES_PATH = ROOT / "data" / "classes" / "community_skill_trees.json"
SPRITE_MAP_PATH = ROOT / "frontend" / "src" / "data" / "iconSpriteMap.json"


def normalize_name(name: str) -> str:
    """Normalize a node name for fuzzy matching.

    Lowercases, strips punctuation/accents, collapses whitespace.
    """
    # Lowercase
    s = name.lower().strip()
    # Remove accents (e.g., Eterra's → eterras)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # Remove possessives and punctuation
    s = s.replace("'", "").replace("'", "").replace("'", "")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_local_trees(ts_path: Path) -> dict[str, dict[str, str]]:
    """Parse the TypeScript skill tree data to extract {tree_id: {normalized_name: iconId}}.

    Returns a dict mapping tree_id → {normalized_node_name → "a-r-NNN"}.
    """
    content = ts_path.read_text(encoding="utf-8")

    # Find the SKILL_TREES object
    st_start = content.find("SKILL_TREES")
    if st_start == -1:
        print("ERROR: Could not find SKILL_TREES in index.ts", file=sys.stderr)
        sys.exit(1)

    section = content[st_start:]

    # Extract each tree block: "tree_id": [...]
    # We'll parse tree_id keys and their node arrays
    trees: dict[str, dict[str, str]] = {}

    # Find all tree keys
    tree_pattern = re.compile(r'"(\w+)":\s*\[')
    tree_matches = list(tree_pattern.finditer(section))

    for i, m in enumerate(tree_matches):
        tree_id = m.group(1)
        start = m.end()
        # Find the end of this array — look for the next tree key or end of section
        if i + 1 < len(tree_matches):
            end = tree_matches[i + 1].start()
        else:
            end = len(section)
        block = section[start:end]

        # Extract nodes: find name:"..." and iconId:"a-r-..."
        # Each node is an object literal {...}
        nodes: dict[str, str] = {}
        # Match individual node objects
        node_pattern = re.compile(
            r'\{[^}]*?name:"([^"]*)"[^}]*?iconId:"(a-r-\d+)"[^}]*?\}'
            r'|'
            r'\{[^}]*?iconId:"(a-r-\d+)"[^}]*?name:"([^"]*)"[^}]*?\}',
            re.DOTALL,
        )
        for nm in node_pattern.finditer(block):
            if nm.group(1) and nm.group(2):
                name_raw, icon_id = nm.group(1), nm.group(2)
            elif nm.group(3) and nm.group(4):
                icon_id, name_raw = nm.group(3), nm.group(4)
            else:
                continue
            key = normalize_name(name_raw)
            if key:
                nodes[key] = icon_id

        if nodes:
            trees[tree_id] = nodes

    return trees


def load_api_trees(json_path: Path) -> dict[str, dict[str, int]]:
    """Load API skill tree data: {tree_id: {normalized_name: numeric_icon}}.

    Returns a dict mapping tree_id → {normalized_node_name → numeric_icon_int}.
    """
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    trees: dict[str, dict[str, int]] = {}
    for tree in raw:
        tree_id = tree.get("id", "")
        nodes: dict[str, int] = {}
        for node in tree.get("nodes", []):
            icon = node.get("icon")
            name = node.get("name", "")
            if icon and name:
                key = normalize_name(name)
                if key:
                    nodes[key] = icon
        if nodes:
            trees[tree_id] = nodes

    return trees


def main():
    # Load existing sprite map
    with open(SPRITE_MAP_PATH, encoding="utf-8") as f:
        sprite_map: dict[str, list[int]] = json.load(f)

    original_count = len(sprite_map)
    existing_numeric = {k for k in sprite_map if k.isdigit()}
    print(f"Existing sprite map: {original_count} entries ({len(existing_numeric)} numeric)")

    # Parse both data sources
    print("Parsing local skill trees (index.ts)...")
    local_trees = parse_local_trees(LOCAL_TREES_PATH)
    print(f"  Found {len(local_trees)} trees with {sum(len(v) for v in local_trees.values())} nodes with iconIds")

    print("Loading API skill trees (community_skill_trees.json)...")
    api_trees = load_api_trees(API_TREES_PATH)
    print(f"  Found {len(api_trees)} trees with {sum(len(v) for v in api_trees.values())} nodes with icons")

    # Cross-reference
    new_mappings: dict[str, list[int]] = {}
    unmatched_api: list[tuple[str, str, int]] = []  # (tree_id, node_name, numeric_icon)
    already_mapped = 0
    name_not_found = 0
    no_sprite_coords = 0

    # Collect all API numeric icons for coverage stats
    all_api_icons: set[int] = set()
    for nodes in api_trees.values():
        all_api_icons.update(nodes.values())

    for tree_id, api_nodes in api_trees.items():
        local_nodes = local_trees.get(tree_id, {})
        for node_name, numeric_icon in api_nodes.items():
            all_api_icons.add(numeric_icon)
            numeric_key = str(numeric_icon)

            # Skip if already in sprite map
            if numeric_key in sprite_map:
                already_mapped += 1
                continue

            # Try to find matching local node
            icon_id = local_nodes.get(node_name)
            if not icon_id:
                # Try with/without common suffixes
                unmatched_api.append((tree_id, node_name, numeric_icon))
                name_not_found += 1
                continue

            # Look up a-r-* key in sprite map for coordinates
            coords = sprite_map.get(icon_id)
            if not coords:
                unmatched_api.append((tree_id, node_name, numeric_icon))
                no_sprite_coords += 1
                continue

            new_mappings[numeric_key] = coords

    # --- Fuzzy matching pass for unmatched nodes ---
    still_unmatched: list[tuple[str, str, int]] = []
    fuzzy_matched = 0

    for tree_id, node_name, numeric_icon in unmatched_api:
        numeric_key = str(numeric_icon)
        if numeric_key in sprite_map or numeric_key in new_mappings:
            continue

        local_nodes = local_trees.get(tree_id, {})
        if not local_nodes:
            still_unmatched.append((tree_id, node_name, numeric_icon))
            continue

        # Try substring matching: find local node name that contains this name or vice versa
        matched = False
        for local_name, icon_id in local_nodes.items():
            # Check if one is a substring of the other
            if local_name in node_name or node_name in local_name:
                coords = sprite_map.get(icon_id)
                if coords:
                    new_mappings[numeric_key] = coords
                    fuzzy_matched += 1
                    matched = True
                    break
            # Check edit distance for short names (< 3 char difference)
            if abs(len(local_name) - len(node_name)) <= 2:
                # Simple character diff check
                common = sum(1 for a, b in zip(local_name, node_name) if a == b)
                max_len = max(len(local_name), len(node_name))
                if max_len > 0 and common / max_len >= 0.8:
                    coords = sprite_map.get(icon_id)
                    if coords:
                        new_mappings[numeric_key] = coords
                        fuzzy_matched += 1
                        matched = True
                        break

        if not matched:
            still_unmatched.append((tree_id, node_name, numeric_icon))

    # --- Report ---
    print()
    print("=" * 60)
    print("CROSS-REFERENCE RESULTS")
    print("=" * 60)
    print(f"Already mapped (skipped):     {already_mapped}")
    print(f"New exact matches:            {len(new_mappings) - fuzzy_matched}")
    print(f"New fuzzy matches:            {fuzzy_matched}")
    print(f"Total new mappings:           {len(new_mappings)}")
    print(f"Still unmatched:              {len(still_unmatched)}")
    print()

    # Coverage stats
    total_unique_icons = len(all_api_icons)
    mapped_before = sum(1 for i in all_api_icons if str(i) in sprite_map)
    mapped_after = sum(1 for i in all_api_icons if str(i) in sprite_map or str(i) in new_mappings)
    print(f"Total unique API icon IDs:    {total_unique_icons}")
    print(f"Coverage before:              {mapped_before}/{total_unique_icons} ({100*mapped_before/total_unique_icons:.1f}%)")
    print(f"Coverage after:               {mapped_after}/{total_unique_icons} ({100*mapped_after/total_unique_icons:.1f}%)")
    print()

    if still_unmatched:
        print(f"--- {len(still_unmatched)} UNMATCHED NODES ---")
        # Group by reason
        no_local_tree = [(t, n, i) for t, n, i in still_unmatched if t not in local_trees]
        has_local_tree = [(t, n, i) for t, n, i in still_unmatched if t in local_trees]
        if no_local_tree:
            print(f"\n  No local tree data ({len(no_local_tree)} nodes in {len(set(t for t,_,_ in no_local_tree))} trees):")
            for tree_id, node_name, icon in no_local_tree[:20]:
                print(f"    tree={tree_id} node={node_name!r} icon={icon}")
            if len(no_local_tree) > 20:
                print(f"    ... and {len(no_local_tree) - 20} more")
        if has_local_tree:
            print(f"\n  Name mismatch in local tree ({len(has_local_tree)} nodes):")
            for tree_id, node_name, icon in has_local_tree[:20]:
                local_names = list(local_trees[tree_id].keys())[:5]
                print(f"    tree={tree_id} api_name={node_name!r} icon={icon} local_names_sample={local_names}")
            if len(has_local_tree) > 20:
                print(f"    ... and {len(has_local_tree) - 20} more")
        print()

    # Write updated sprite map
    if new_mappings:
        sprite_map.update(new_mappings)
        # Sort: a-r-* keys first (by numeric part), then numeric keys (by value)
        def sort_key(k: str) -> tuple[int, int]:
            if k.startswith("a-r-"):
                return (0, int(k[4:]))
            if k.isdigit():
                return (1, int(k))
            return (2, 0)

        sorted_map = dict(sorted(sprite_map.items(), key=lambda x: sort_key(x[0])))

        with open(SPRITE_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted_map, f, indent=2)
            f.write("\n")

        print(f"Updated {SPRITE_MAP_PATH.relative_to(ROOT)}")
        print(f"  Added {len(new_mappings)} new entries")
        print(f"  Total entries: {len(sorted_map)} (was {original_count})")
    else:
        print("No new mappings found — sprite map unchanged.")


if __name__ == "__main__":
    main()
