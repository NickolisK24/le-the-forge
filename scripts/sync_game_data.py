#!/usr/bin/env python3
"""
sync_game_data.py — Syncs canonical /data/ files from last-epoch-data exports.

Reads raw game exports from last-epoch-data/exports_json/ and transforms them
into the backend schema used by game_data_loader.py and the engine layer.

Usage:
    python scripts/sync_game_data.py [--dry-run]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "last-epoch-data" / "exports_json"
DATA_DIR = ROOT / "data"

# Slot name mapping: raw game UPPER_CASE → backend lowercase slugs
SLOT_MAP = {
    "AMULET": "amulet",
    "BELT": "belt",
    "BODY_ARMOR": "chest",
    "BOOTS": "boots",
    "BOW": "bow",
    "CATALYST": "catalyst",
    "CROSSBOW": "crossbow",
    "GLOVES": "gloves",
    "HELMET": "helm",
    "ONE_HANDED_AXE": "axe_1h",
    "ONE_HANDED_DAGGER": "dagger",
    "ONE_HANDED_FIST": "fist",
    "ONE_HANDED_MACES": "mace_1h",
    "ONE_HANDED_SCEPTRE": "sceptre",
    "ONE_HANDED_SWORD": "sword_1h",
    "QUIVER": "quiver",
    "RELIC": "relic",
    "RING": "ring",
    "SHIELD": "shield",
    "TWO_HANDED_AXE": "axe_2h",
    "TWO_HANDED_MACE": "mace_2h",
    "TWO_HANDED_SPEAR": "spear",
    "TWO_HANDED_STAFF": "staff",
    "TWO_HANDED_SWORD": "sword_2h",
    "WAND": "wand",
}

# Idol slots — kept in applicable_to with their raw names (lowercased) so the
# frontend can filter them separately from equipment.
IDOL_SLOT_PREFIX = "IDOL_"


def _slugify(name: str) -> str:
    """Convert 'Void Penetration' → 'void_penetration'."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


def _class_requirement(specificity: list[str]) -> str | None:
    """Map classSpecificity list to a single class_requirement string or None."""
    filtered = [s for s in specificity if s not in ("None", "NonSpecific")]
    if not filtered:
        return None
    # If multiple classes, join them; engines can extend this later.
    return filtered[0] if len(filtered) == 1 else ",".join(filtered)


def _normalize_tag(tag: str) -> str:
    return tag.lower()


def _convert_slot(raw: str) -> str | None:
    if raw.startswith(IDOL_SLOT_PREFIX):
        return raw.lower()
    return SLOT_MAP.get(raw)


def sync_affixes(existing: list[dict], dry_run: bool = False) -> list[dict]:
    """
    Merge raw export affixes with existing curated data.

    Strategy:
    - All 946 equipment affixes from new data are matched by name to existing.
    - stat_key, id (slug) preserved from existing data.
    - Tier values: new data uses normalized floats (0.10), multiply × 100 for backend.
    - New fields added: title, group, reroll_chance, t6_compatible, modifier_type.
    - Affixes present in existing but not in new export are kept unchanged.
    """
    src_path = SRC_DIR / "affixes.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping affixes sync")
        return existing

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    equipment_list: list[dict] = raw.get("equipment", [])
    idol_list: list[dict] = raw.get("idol", [])

    # Build lookup from existing curated data (by name for best match)
    existing_by_name: dict[str, dict] = {a["name"]: a for a in existing}
    updated_names: set[str] = set()

    result: list[dict] = []

    def _process_affix(raw_affix: dict, is_idol: bool = False) -> dict:
        name = raw_affix["name"]
        cur = existing_by_name.get(name, {})

        # Derive slug id from name if not in existing
        slug_id = cur.get("id") or _slugify(name)

        # Tier conversion: multiply normalized floats × 100 → integers
        tiers = []
        for t in raw_affix.get("tiers", []):
            lo = round(t["minRoll"] * 100, 4)
            hi = round(t["maxRoll"] * 100, 4)
            # Use integers when values are whole numbers
            lo = int(lo) if lo == int(lo) else lo
            hi = int(hi) if hi == int(hi) else hi
            tiers.append({"tier": t["tier"], "min": lo, "max": hi})

        if is_idol:
            # Idol affixes have a simplified schema
            entry: dict = {
                "id": slug_id,
                "name": name,
                "type": "idol",
                "tags": cur.get("tags", []),
                "applicable_to": cur.get("applicable_to", ["idol"]),
                "class_requirement": None,
                "tiers": tiers if tiers else cur.get("tiers", []),
                "stat_key": cur.get("stat_key", slug_id),
                "affix_id": raw_affix["id"],
                "rolls_on": "idol",
                "level_requirement": raw_affix.get("levelRequirement", 0),
                "special_affix_type": 0,
                "title": raw_affix.get("shardName", ""),
                "group": "",
                "modifier_type": "",
                "reroll_chance": 1.0,
                "t6_compatible": False,
            }
            return entry

        # Slot mapping (equipment only)
        applicable_to = []
        for raw_slot in raw_affix.get("canRollOn", []):
            mapped = _convert_slot(raw_slot)
            if mapped:
                applicable_to.append(mapped)

        # Tags: lowercase
        tags = [_normalize_tag(t) for t in raw_affix.get("tags", []) if t.lower() != "none"]

        # Class requirement
        class_req = _class_requirement(raw_affix.get("classSpecificity", ["None"]))

        # t6 compatibility flag
        t6_compat = raw_affix.get("t6Compatibility", "Normal") == "Normal"

        entry = {
            "id": slug_id,
            "name": name,
            "type": raw_affix["type"].lower(),
            "tags": tags,
            "applicable_to": applicable_to if applicable_to else cur.get("applicable_to", []),
            "class_requirement": class_req,
            "tiers": tiers if tiers else cur.get("tiers", []),
            "stat_key": cur.get("stat_key", slug_id),
            "affix_id": raw_affix["id"],
            "rolls_on": raw_affix.get("rollsOn", "Equipment").lower(),
            "level_requirement": raw_affix.get("levelRequirement", 0),
            "special_affix_type": 0 if raw_affix.get("specialAffixType") == "Standard" else 1,
            # Enriched fields from new data
            "title": raw_affix.get("title", ""),
            "group": raw_affix.get("group", ""),
            "modifier_type": raw_affix.get("modifierType", ""),
            "reroll_chance": round(raw_affix.get("rerollChance", 1.0), 4),
            "t6_compatible": t6_compat,
        }
        return entry

    # Process equipment affixes
    for raw_affix in equipment_list:
        entry = _process_affix(raw_affix, is_idol=False)
        result.append(entry)
        updated_names.add(raw_affix["name"])

    # Process idol affixes (kept separate, rolls_on=idol)
    for raw_affix in idol_list:
        entry = _process_affix(raw_affix, is_idol=True)
        result.append(entry)
        updated_names.add(raw_affix["name"])

    # Preserve any existing affixes not found in new data (manual entries, etc.)
    preserved = 0
    for affix in existing:
        if affix["name"] not in updated_names:
            result.append(affix)
            preserved += 1

    print(f"  affixes: {len(equipment_list)} equipment + {len(idol_list)} idol updated, "
          f"{preserved} legacy entries preserved → {len(result)} total")
    return result


def sync_skills_metadata(dry_run: bool = False) -> dict | None:
    """
    Load skills metadata (id, name, description) from last-epoch-data.
    Returns a dict keyed by skill name for use in game_data_loader enrichment.
    """
    src_path = SRC_DIR / "skills.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping skills metadata")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    skills_list: list[dict] = raw.get("skills", [])
    metadata = {}
    for skill in skills_list:
        name = skill.get("name", "")
        if name:
            metadata[name] = {
                "id": skill.get("id", ""),
                "name": name,
                "description": skill.get("description", ""),
                "lore": skill.get("lore", ""),
                "class": skill.get("class", ""),
            }

    out_path = DATA_DIR / "skills_metadata.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  skills_metadata: {len(metadata)} skills → {out_path.name}")
    else:
        print(f"  [DRY RUN] skills_metadata: would write {len(metadata)} skills → {out_path.name}")

    return metadata


# ---------------------------------------------------------------------------
# Class / mastery metadata for passive tree sync
# ---------------------------------------------------------------------------

# Integer mastery index → mastery name (None = base class tree)
MASTERY_MAP: dict[str, dict[int, str | None]] = {
    "Acolyte":  {0: None, 1: "Necromancer", 2: "Lich",      3: "Warlock"},
    "Mage":     {0: None, 1: "Sorcerer",    2: "Runemaster", 3: "Spellblade"},
    "Primalist":{0: None, 1: "Shaman",      2: "Beastmaster",3: "Druid"},
    "Rogue":    {0: None, 1: "Bladedancer", 2: "Marksman",   3: "Falconer"},
    "Sentinel": {0: None, 1: "Paladin",     2: "Forge Guard",3: "Void Knight"},
}

# Class name → two-letter prefix used in namespaced IDs (e.g. "ac_0")
CLASS_PREFIX: dict[str, str] = {
    "Acolyte":  "ac",
    "Mage":     "mg",
    "Primalist":"pr",
    "Rogue":    "rg",
    "Sentinel": "sn",
}

# Tree ID (from char-tree-layout.json) → class name
TREE_ID_TO_CLASS: dict[str, str] = {
    "ac-1": "Acolyte",
    "mg-1": "Mage",
    "pr-1": "Primalist",
    "rg-1": "Rogue",
    "kn-1": "Sentinel",
}


def _build_layout_lookup() -> dict[str, dict[int, dict]]:
    """
    Parse char-tree-layout.json from the frontend raw data directory and return
    a nested lookup: class_name → raw_node_id → {x, y, icon}.

    The layout file uses real game coordinates stored as rect[x, y, w, h].
    """
    layout_path = ROOT / "frontend" / "src" / "data" / "raw" / "char-tree-layout.json"
    if not layout_path.exists():
        return {}

    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)

    def _flatten(children: list[dict], acc: dict[int, dict]) -> None:
        for child in children:
            if "nodeId" in child and "rect" in child:
                acc[child["nodeId"]] = {
                    "x": child["rect"][0],
                    "y": child["rect"][1],
                    "icon": child.get("icon", ""),
                }
            if "children" in child:
                _flatten(child["children"], acc)

    result: dict[str, dict[int, dict]] = {}
    for tree_id, tree_data in layout.items():
        cls = TREE_ID_TO_CLASS.get(tree_id)
        if not cls:
            continue
        node_map: dict[int, dict] = {}
        for section in tree_data.get("nodes", []):
            if "children" in section:
                _flatten(section["children"], node_map)
        result[cls] = node_map

    return result


def sync_passives(dry_run: bool = False) -> list[dict] | None:
    """
    Transform last-epoch-data/exports_json/passive_trees.json into
    data/passives.json, with namespaced IDs and resolved mastery names.

    Source schema (passive_trees.json):
      {"passiveTrees": [{"class": "Acolyte", "nodes": [{
          "id": int, "name": str, "description": str,
          "mastery": int,            # 0=base, 1/2/3=mastery subtrees
          "masteryRequirement": int, # points needed to unlock
          "maxPoints": int,
          "requirements": [int, ...],  # connected node IDs
          "stats": [{"statNameKey": str, "value": str, ...}, ...],
          "relatedAbilities": [str, ...],
          "type": str,               # "core"|"notable"|"keystone"|"mastery_gate"
          "icon": str,               # sprite ID e.g. "a-r-42"
      }, ...]}]}

    Output per node (data/passives.json array):
      id, raw_node_id, character_class, mastery, mastery_index,
      mastery_requirement, name, description, node_type, x, y,
      max_points, connections, stats, ability_granted, icon
    """
    src_path = SRC_DIR / "passive_trees.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping passives sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    layout_lookup = _build_layout_lookup()

    nodes_out: list[dict] = []

    for tree in raw.get("passiveTrees", []):
        cls = tree.get("class", "")
        if cls not in MASTERY_MAP:
            print(f"  [WARN] Unknown class '{cls}' in passive_trees.json — skipping")
            continue

        prefix = CLASS_PREFIX[cls]
        mastery_map = MASTERY_MAP[cls]
        cls_layout = layout_lookup.get(cls, {})

        for node in tree.get("nodes", []):
            raw_id: int = node["id"]
            node_id = f"{prefix}_{raw_id}"

            mastery_idx: int = node.get("mastery", 0)
            mastery_name: str | None = mastery_map.get(mastery_idx)

            # Connections: unpack requirements → namespaced IDs
            connections = [f"{prefix}_{r}" for r in node.get("requirements", [])]

            # Stats: compact {key, value} pairs (drop localization keys)
            raw_stats = node.get("stats", [])
            stats = [
                {"key": s.get("statNameKey", ""), "value": s.get("value", "")}
                for s in raw_stats
            ]

            # First related ability name, if any
            related = node.get("relatedAbilities", [])
            ability_granted = related[0] if related else None

            # x/y from layout lookup; fall back to 0.0
            layout_node = cls_layout.get(raw_id, {})
            x = layout_node.get("x", 0.0)
            y = layout_node.get("y", 0.0)

            # Icon: prefer layout sprite (more reliable), fall back to node field
            icon = layout_node.get("icon") or node.get("icon", "")

            # node_type: normalise to snake_case backend convention
            raw_type = node.get("type", "core")
            node_type = raw_type.lower().replace("-", "_").replace(" ", "_")
            if node_type not in ("core", "notable", "keystone", "mastery_gate"):
                node_type = "core"

            nodes_out.append({
                "id": node_id,
                "raw_node_id": raw_id,
                "character_class": cls,
                "mastery": mastery_name,
                "mastery_index": mastery_idx,
                "mastery_requirement": node.get("masteryRequirement", 0),
                "name": node.get("name", ""),
                "description": node.get("description", ""),
                "node_type": node_type,
                "x": x,
                "y": y,
                "max_points": node.get("maxPoints", 1),
                "connections": connections,
                "stats": stats,
                "ability_granted": ability_granted,
                "icon": icon or None,
            })

    out_path = DATA_DIR / "passives.json"
    total = len(nodes_out)

    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(nodes_out, f, indent=2, ensure_ascii=False)
        print(f"  passives: {total} nodes → {out_path.name}")
    else:
        print(f"  [DRY RUN] passives: would write {total} nodes → {out_path.name}")

    return nodes_out


def main():
    parser = argparse.ArgumentParser(description="Sync game data from last-epoch-data exports.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    args = parser.parse_args()

    if not SRC_DIR.exists():
        print(f"ERROR: Source directory not found: {SRC_DIR}", file=sys.stderr)
        print("Make sure last-epoch-data is available in the project root.", file=sys.stderr)
        sys.exit(1)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing game data from {SRC_DIR.name}...\n")

    # --- Affixes ---
    affixes_path = DATA_DIR / "affixes.json"
    with open(affixes_path, encoding="utf-8") as f:
        existing_affixes = json.load(f)

    updated_affixes = sync_affixes(existing_affixes, dry_run=args.dry_run)

    if not args.dry_run:
        with open(affixes_path, "w", encoding="utf-8") as f:
            json.dump(updated_affixes, f, indent=2, ensure_ascii=False)
        print(f"  → Written: {affixes_path}")
    else:
        print(f"  [DRY RUN] Would write {len(updated_affixes)} affixes → {affixes_path}")

    print()

    # --- Skills metadata ---
    sync_skills_metadata(dry_run=args.dry_run)

    print()

    # --- Passives ---
    sync_passives(dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
