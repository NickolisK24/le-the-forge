#!/usr/bin/env python3
"""
generate_tree_data.py — Enriches passive and skill tree TypeScript data with
real node names and descriptions from last-epoch-data exports.

What it does:
  1. Passive trees: replaces "Node N" names with real names from passive_trees.json
     and fills in description text where missing.
  2. Skill trees: builds a complete SKILL_NAME_TO_CODE mapping (86+ skills) and
     replaces localization-key node names with real names from skills_with_trees.json.

Usage:
    python scripts/generate_tree_data.py [--dry-run]

Requires: last-epoch-data/ to be present in the project root.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "last-epoch-data" / "exports_json"
FRONTEND_DATA = ROOT / "frontend" / "src" / "data"

# ---------------------------------------------------------------------------
# Mastery index → region slug mapping
# ---------------------------------------------------------------------------
MASTERY_REGION: dict[str, list[str]] = {
    "Acolyte":  ["base", "necromancer", "lich", "warlock"],
    "Mage":     ["base", "sorcerer", "spellblade", "runemaster"],
    "Primalist":["base", "beastmaster", "shaman", "druid"],
    "Rogue":    ["base", "bladedancer", "marksman", "falconer"],
    "Sentinel": ["base", "void-knight", "forge-guard", "paladin"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _escape_ts(s: str) -> str:
    """Escape a string for insertion into a TypeScript string literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")


# ---------------------------------------------------------------------------
# Passive trees
# ---------------------------------------------------------------------------

def build_passive_name_lookup() -> dict[str, dict[int, dict]]:
    """
    Returns: className (lower) -> nodeId -> {name, description, stats_summary}
    """
    path = SRC_DIR / "passive_trees.json"
    if not path.exists():
        print(f"  [WARN] {path} not found — skipping passive tree enrichment")
        return {}

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    lookup: dict[str, dict[int, dict]] = {}
    for tree in data["passiveTrees"]:
        cls = tree["class"].lower()
        node_map: dict[int, dict] = {}
        for node in tree["nodes"]:
            nid = node["id"]
            # Build a short description from pointBonusDescription or stats
            desc = node.get("description", "").strip()
            node_map[nid] = {
                "name": node["name"],
                "description": desc,
            }
        lookup[cls] = node_map
    return lookup


def enrich_passive_trees(dry_run: bool = False) -> None:
    """Update passiveTrees/index.ts with real node names from passive_trees.json."""
    lookup = build_passive_name_lookup()
    if not lookup:
        return

    ts_path = FRONTEND_DATA / "passiveTrees" / "index.ts"
    with open(ts_path, encoding="utf-8") as f:
        content = f.read()

    # Detect which class block we're in by scanning for the constant declarations.
    # Map const name fragment → class name
    # E.g. "_PRIMALIST_BASE" → primalist, "_PRIMALIST_BEASTMASTER" → primalist
    # We do a single-pass replacement: for each node literal, look up its real name.

    # Pattern: {id:NNN,...,name:"...",regionId:"REGION",...}
    node_pattern = re.compile(
        r'\{id:(\d+),x:[^,]+,y:[^,]+,type:"[^"]+",name:"([^"]*)",regionId:"([^"]+)"'
        r',maxPoints:\d+,parentId:[^,}]+(?:,description:"([^"]*)")?(?:,iconId:"[^"]*")?\}'
    )

    # Also determine class from surrounding const name
    # We'll do a block-by-block scan
    # Find all const declarations and their positions
    const_pattern = re.compile(r'const _([A-Z]+)_([A-Z_]+): N\[\] = \[')

    # Build a map: position range -> (class_lower, region_slug)
    blocks: list[tuple[int, int, str]] = []  # (start, end, class_lower)
    const_matches = list(const_pattern.finditer(content))
    for i, m in enumerate(const_matches):
        class_raw = m.group(1).lower()  # e.g. "primalist"
        end = const_matches[i + 1].start() if i + 1 < len(const_matches) else len(content)
        blocks.append((m.start(), end, class_raw))

    replacements: list[tuple[int, int, str]] = []  # (start, end, new_text)
    stats = {"updated": 0, "missing": 0}

    for node_match in node_pattern.finditer(content):
        node_id = int(node_match.group(1))
        old_name = node_match.group(2)
        region_id = node_match.group(3)
        old_desc = node_match.group(4) or ""
        pos = node_match.start()

        # Find which class block this node is in
        cls = None
        for bstart, bend, class_lower in blocks:
            if bstart <= pos < bend:
                cls = class_lower
                break

        if cls is None:
            continue

        node_data = lookup.get(cls, {}).get(node_id)
        if not node_data:
            stats["missing"] += 1
            continue

        new_name = node_data["name"]
        new_desc = node_data["description"] or old_desc

        if new_name == old_name and new_desc == old_desc:
            continue  # nothing to update

        # Rebuild the matched string with updated name/description
        old_text = node_match.group(0)
        new_text = old_text.replace(
            f'name:"{old_name}"', f'name:"{_escape_ts(new_name)}"', 1
        )
        if ',description:"' in new_text:
            new_text = re.sub(
                r',description:"[^"]*"',
                f',description:"{_escape_ts(new_desc)}"',
                new_text,
                count=1,
            )
        replacements.append((node_match.start(), node_match.end(), new_text))
        stats["updated"] += 1

    # Apply replacements in reverse order to preserve positions
    for start, end, new_text in sorted(replacements, key=lambda r: r[0], reverse=True):
        content = content[:start] + new_text + content[end:]

    print(f"  passive trees: {stats['updated']} nodes updated, "
          f"{stats['missing']} node IDs not found in source")

    if not dry_run:
        with open(ts_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  → Written: {ts_path}")
    else:
        print(f"  [DRY RUN] Would write {ts_path}")


# ---------------------------------------------------------------------------
# Skill trees
# ---------------------------------------------------------------------------

def build_skill_tree_lookups() -> tuple[dict[str, str], dict[str, dict[int, str]]]:
    """
    Returns:
      name_to_code: skill display name (lower) → tree code
      node_names:   tree code → {nodeId: real name}
    """
    path = SRC_DIR / "skills_with_trees.json"
    if not path.exists():
        print(f"  [WARN] {path} not found — skipping skill tree enrichment")
        return {}, {}

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    name_to_code: dict[str, str] = {}
    node_names: dict[str, dict[int, str]] = {}

    for skill in data["skills"]:
        tree = skill.get("skillTree")
        if not tree or not isinstance(tree, dict):
            continue
        nodes = tree.get("nodes")
        if not nodes:
            continue

        skill_id = skill["id"]
        skill_name = skill["name"]

        # Map lowercase name → tree code id
        name_to_code[skill_name.lower()] = skill_id

        # Map nodeId → real name (skip node 0 — it's just the skill name used as entry)
        node_map: dict[int, str] = {}
        for node in nodes:
            nid = node["id"]
            name = node.get("name", "").strip()
            if name:
                node_map[nid] = name
        node_names[skill_id] = node_map

    return name_to_code, node_names


def enrich_skill_trees(dry_run: bool = False) -> None:
    """Update skillTrees/index.ts with full name mapping and real node names."""
    name_to_code, node_names = build_skill_tree_lookups()
    if not name_to_code:
        return

    ts_path = FRONTEND_DATA / "skillTrees" / "index.ts"
    with open(ts_path, encoding="utf-8") as f:
        content = f.read()

    # ---- 1. Replace SKILL_NAME_TO_CODE block ----
    old_map_pattern = re.compile(
        r'const SKILL_NAME_TO_CODE: Record<string, string> = \{[^}]+\};',
        re.DOTALL,
    )

    # Build sorted mapping lines
    map_lines = []
    for skill_name, code in sorted(name_to_code.items()):
        map_lines.append(f'  "{skill_name}": "{code}",')

    new_map = (
        "const SKILL_NAME_TO_CODE: Record<string, string> = {\n"
        + "\n".join(map_lines)
        + "\n};"
    )

    if old_map_pattern.search(content):
        content = old_map_pattern.sub(new_map, content)
        print(f"  skill trees: SKILL_NAME_TO_CODE updated with {len(name_to_code)} entries")
    else:
        print("  [WARN] Could not find SKILL_NAME_TO_CODE block to replace")

    # ---- 2. Replace node name localization keys with real names ----
    # Pattern: name:"Skills.Skill_TREEID_NODEID_Name"
    loc_key_pattern = re.compile(r'name:"(Skills\.Skill_([a-zA-Z0-9\-]+)_(\d+)_Name)"')

    updated_nodes = 0
    unfound_nodes = 0

    def replace_node_name(m: re.Match) -> str:
        nonlocal updated_nodes, unfound_nodes
        orig = m.group(1)
        tree_code = m.group(2)
        node_id = int(m.group(3))
        real_name = node_names.get(tree_code, {}).get(node_id)
        if real_name:
            updated_nodes += 1
            return f'name:"{_escape_ts(real_name)}"'
        unfound_nodes += 1
        return m.group(0)  # keep original

    content = loc_key_pattern.sub(replace_node_name, content)
    print(f"  skill trees: {updated_nodes} node names resolved, "
          f"{unfound_nodes} localization keys kept (no source match)")

    # ---- 3. Update cleanNodeName to handle real names gracefully ----
    # The function currently strips "Skills.Skill_xxx_N_Name" → "Node N"
    # With real names, the function should just return the name directly.
    old_fn = re.compile(
        r'export function cleanNodeName\(name: string \| undefined\): string \{.*?\n\}',
        re.DOTALL,
    )
    new_fn = (
        'export function cleanNodeName(name: string | undefined): string {\n'
        '  if (!name) return "";\n'
        '  // Legacy localization key format → numbered fallback\n'
        r'  const m = name.match(/Skills\.Skill_\w+_(\d+)_Name$/);'
        '\n'
        '  if (m) return `Node ${m[1]}`;\n'
        '  return name;\n'
        '}'
    )
    if old_fn.search(content):
        content = old_fn.sub(lambda _: new_fn, content)

    if not dry_run:
        with open(ts_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  → Written: {ts_path}")
    else:
        print(f"  [DRY RUN] Would write {ts_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich passive and skill tree TypeScript data with real node names."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing files")
    args = parser.parse_args()

    if not SRC_DIR.exists():
        print(f"ERROR: {SRC_DIR} not found.", file=sys.stderr)
        print("Clone last-epoch-data into the project root first.", file=sys.stderr)
        sys.exit(1)

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"{prefix}Enriching tree data from {SRC_DIR.name}...\n")

    print("── Passive Trees ──")
    enrich_passive_trees(dry_run=args.dry_run)

    print("\n── Skill Trees ──")
    enrich_skill_trees(dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
