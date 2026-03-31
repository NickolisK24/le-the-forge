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

    def _flatten(obj: object, acc: dict[int, dict]) -> None:
        """Recursively walk any nested dict/list to collect nodeId entries."""
        if isinstance(obj, dict):
            if "nodeId" in obj and "rect" in obj:
                acc[obj["nodeId"]] = {
                    "x": obj["rect"][0],
                    "y": obj["rect"][1],
                    "icon": obj.get("icon", ""),
                }
            for v in obj.values():
                _flatten(v, acc)
        elif isinstance(obj, list):
            for item in obj:
                _flatten(item, acc)

    result: dict[str, dict[int, dict]] = {}
    for tree_id, tree_data in layout.items():
        cls = TREE_ID_TO_CLASS.get(tree_id)
        if not cls:
            continue
        node_map: dict[int, dict] = {}
        _flatten(tree_data, node_map)
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

    nodes_out: list[dict] = []

    for tree in raw.get("passiveTrees", []):
        cls = tree.get("class", "")
        if cls not in MASTERY_MAP:
            print(f"  [WARN] Unknown class '{cls}' in passive_trees.json — skipping")
            continue

        prefix = CLASS_PREFIX[cls]
        mastery_map = MASTERY_MAP[cls]

        for node in tree.get("nodes", []):
            raw_id: int = node["id"]
            node_id = f"{prefix}_{raw_id}"

            mastery_idx: int = node.get("mastery", 0)
            mastery_name: str | None = mastery_map.get(mastery_idx)

            # Connections: requirements is [{node: int, requirement: int}, ...]
            connections = [
                f"{prefix}_{r['node']}"
                for r in node.get("requirements", [])
            ]

            # Stats: compact {key, value} pairs; source uses "statName" field
            raw_stats = node.get("stats", [])
            stats = [
                {"key": s.get("statName", ""), "value": s.get("value", "")}
                for s in raw_stats
            ]

            # Ability granted by this node (may be null)
            ability_granted = node.get("abilityGrantedByNode") or None

            # x/y: source provides real coordinates in transform dict
            transform = node.get("transform", {})
            x = transform.get("x", 0.0)
            y = transform.get("y", 0.0)

            # Icon: source stores integer sprite ID; stringify for consistent storage
            raw_icon = node.get("icon")
            icon = str(raw_icon) if raw_icon is not None else None

            # node_type: source has no explicit type field; derive from maxPoints
            # maxPoints==1 → notable (single-point allocatable), >1 → core (investable)
            max_pts = node.get("maxPoints", 1)
            node_type = "core" if max_pts > 1 else "notable"

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


def sync_blessings(dry_run: bool = False) -> list[dict] | None:
    """
    Transform last-epoch-data/exports_json/blessings.json into data/blessings.json.

    Source schema:
      {"blessings": [{
          "name": str,              # internal ID (e.g. "27")
          "displayName": str,       # e.g. "Pride of Rebellion"
          "subTypeID": int,         # 0=normal, 1=grand
          "levelRequirement": int,
          "classRequirement": str,  # "Any" or class name
          "implicits": [{
              "property": str, "tags": [str, ...],
              "modifierType": str, "value": float, "maxValue": float
          }],
          "cannotDrop": bool,
          ...
      }]}

    Output (data/blessings.json): array of blessing entries.
    """
    src_path = SRC_DIR / "blessings.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping blessings sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    blessings_list: list[dict] = raw.get("blessings", [])
    out: list[dict] = []

    for entry in blessings_list:
        display = entry.get("displayName", "")
        if not display:
            continue

        implicits = []
        for imp in entry.get("implicits", []):
            implicits.append({
                "property": imp.get("property", ""),
                "tags": imp.get("tags", []),
                "modifier_type": imp.get("modifierType", ""),
                "value": imp.get("value", 0.0),
                "max_value": imp.get("maxValue", 0.0),
            })

        class_req = entry.get("classRequirement", "Any")
        out.append({
            "id": _slugify(display),
            "name": display,
            "internal_name": entry.get("name", ""),
            "tier": entry.get("subTypeID", 0),
            "level_req": entry.get("levelRequirement", 0),
            "class_req": class_req if class_req != "Any" else None,
            "cannot_drop": entry.get("cannotDrop", False),
            "stats": implicits,
        })

    out_path = DATA_DIR / "blessings.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  blessings: {len(out)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] blessings: would write {len(out)} entries → {out_path.name}")

    return out


def sync_ailments(dry_run: bool = False) -> list[dict] | None:
    """
    Transform last-epoch-data/exports_json/ailments.json into data/ailments.json.

    Source schema:
      {"ailments": [{
          "id": int,
          "name": str,          # CamelCase internal name e.g. "AbyssalDecay"
          "displayName": str,   # e.g. "Abyssal Decay"
          "instanceName": str,  # e.g. "Abyssal Decay"
          "duration": float,    # seconds
          "maxInstances": int,  # 0 = unlimited stacks
          "positive": bool,     # true = buff, false = debuff
          "showsInBuffUI": bool,
          "tags": int,          # bitmask
          "applyPrefix": bool,
          ...
      }]}

    Output (data/ailments.json): array of ailment entries.
    """
    src_path = SRC_DIR / "ailments.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping ailments sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    ailments_list: list[dict] = raw.get("ailments", [])
    out: list[dict] = []

    for entry in ailments_list:
        display = entry.get("displayName", "")
        if not display:
            continue

        out.append({
            "id": entry.get("id"),
            "slug": _slugify(display),
            "name": display,
            "internal_name": entry.get("name", ""),
            "instance_name": entry.get("instanceName", display),
            "duration": entry.get("duration", 0.0),
            "max_instances": entry.get("maxInstances", 0),
            "positive": entry.get("positive", False),
            "shows_in_buff_ui": entry.get("showsInBuffUI", True),
            "tags": entry.get("tags", 0),
        })

    out_path = DATA_DIR / "ailments.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  ailments: {len(out)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] ailments: would write {len(out)} entries → {out_path.name}")

    return out


def sync_monster_mods(dry_run: bool = False) -> list[dict] | None:
    """
    Transform last-epoch-data/exports_json/monster_mods.json into data/monster_mods.json.

    Source schema:
      {"monsterMods": [{
          "name": str,               # e.g. "Increased Health"
          "description": str,        # e.g. "More Health"
          "title": str,              # e.g. "of the Ox"
          "minimumLevel": int,
          "hasBonusDrop": int,       # 0/1
          "bonusDropMin": int,
          "bonusDropMax": int,
          "stats": [{
              "property": int,
              "addedValue": float,
              "increasedValue": float,
              "moreValues": [float, ...]
          }],
          ...
      }]}

    Output (data/monster_mods.json): array of monster mod entries.
    """
    src_path = SRC_DIR / "monster_mods.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping monster_mods sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    mods_list: list[dict] = raw.get("monsterMods", [])
    out: list[dict] = []

    for entry in mods_list:
        name = entry.get("name", "")
        if not name:
            continue

        stats = []
        for s in entry.get("stats", []):
            stats.append({
                "property": s.get("property"),
                "added_value": s.get("addedValue", 0.0),
                "increased_value": s.get("increasedValue", 0.0),
                "more_values": s.get("moreValues", []),
            })

        out.append({
            "id": _slugify(name),
            "name": name,
            "description": entry.get("description", ""),
            "title": entry.get("title", ""),
            "minimum_level": entry.get("minimumLevel", 0),
            "has_bonus_drop": bool(entry.get("hasBonusDrop", 0)),
            "bonus_drop_min": entry.get("bonusDropMin", 0),
            "bonus_drop_max": entry.get("bonusDropMax", 0),
            "stats": stats,
        })

    out_path = DATA_DIR / "monster_mods.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  monster_mods: {len(out)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] monster_mods: would write {len(out)} entries → {out_path.name}")

    return out


def sync_timelines(dry_run: bool = False) -> list[dict] | None:
    """
    Transform last-epoch-data/exports_json/timelines.json into data/timelines.json.

    Source schema:
      {"timelines": [{
          "name": str,          # internal name e.g. "Frost Lich Timeline"
          "timelineID": int,
          "displayName": str,   # e.g. "Blood, Frost, and Death"
          "restZone": str,
          "optionRerollCost": int,
          "difficulties": [{
              "level": int,
              "maxStability": int,
              "anySlotBlessings": [int, ...],   # blessing subTypeID references
              "firstSlotBlessings": [int, ...],
              "otherSlotBlessings": [int, ...],
              "minimumCorruption": int,
              "maximumCorruption": int,
              "sufficientRequirements": [{"timelineID": int, "completionType": int}],
              ...
          }],
          ...
      }]}

    Output (data/timelines.json): array of timeline entries.
    """
    src_path = SRC_DIR / "timelines.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping timelines sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    timelines_list: list[dict] = raw.get("timelines", [])
    out: list[dict] = []

    for entry in timelines_list:
        display = entry.get("displayName", "")
        internal = entry.get("name", "")
        if not display and not internal:
            continue

        difficulties = []
        for d in entry.get("difficulties", []):
            # Merge all blessing bucket lists into a single deduplicated list
            blessings = list(dict.fromkeys(
                d.get("anySlotBlessings", [])
                + d.get("firstSlotBlessings", [])
                + d.get("otherSlotBlessings", [])
            ))
            requirements = [
                {"timeline_id": r["timelineID"], "completion_type": r["completionType"]}
                for r in d.get("sufficientRequirements", [])
            ]
            difficulties.append({
                "level": d.get("level", 0),
                "max_stability": d.get("maxStability", 0),
                "blessings": blessings,
                "minimum_corruption": d.get("minimumCorruption", 0),
                "maximum_corruption": d.get("maximumCorruption") if d.get("hasMaxCorruption") else None,
                "sufficient_requirements": requirements,
            })

        out.append({
            "id": _slugify(display or internal),
            "name": display or internal,
            "internal_name": internal,
            "timeline_id": entry.get("timelineID"),
            "rest_zone": entry.get("restZone", ""),
            "option_reroll_cost": entry.get("optionRerollCost", 0),
            "difficulties": difficulties,
        })

    out_path = DATA_DIR / "timelines.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  timelines: {len(out)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] timelines: would write {len(out)} entries → {out_path.name}")

    return out


def main():
    parser = argparse.ArgumentParser(description="Sync game data from last-epoch-data exports.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--all", dest="all", action="store_true", help="Run all sync functions")
    parser.add_argument("--affixes", action="store_true", help="Sync affixes.json")
    parser.add_argument("--skills", action="store_true", help="Sync skills_metadata.json")
    parser.add_argument("--passives", action="store_true", help="Sync passives.json")
    parser.add_argument("--blessings", action="store_true", help="Sync blessings.json")
    parser.add_argument("--ailments", action="store_true", help="Sync ailments.json")
    parser.add_argument("--monster-mods", action="store_true", dest="monster_mods", help="Sync monster_mods.json")
    parser.add_argument("--timelines", action="store_true", help="Sync timelines.json")
    args = parser.parse_args()

    if not SRC_DIR.exists():
        print(f"ERROR: Source directory not found: {SRC_DIR}", file=sys.stderr)
        print("Make sure last-epoch-data is available in the project root.", file=sys.stderr)
        sys.exit(1)

    # If no specific flags given, default to running all
    specific_flags = [args.affixes, args.skills, args.passives, args.blessings,
                      args.ailments, args.monster_mods, args.timelines]
    run_all = args.all or not any(specific_flags)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing game data from {SRC_DIR.name}...\n")

    # --- Affixes ---
    if run_all or args.affixes:
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
    if run_all or args.skills:
        sync_skills_metadata(dry_run=args.dry_run)
        print()

    # --- Passives ---
    if run_all or args.passives:
        sync_passives(dry_run=args.dry_run)
        print()

    # --- Blessings ---
    if run_all or args.blessings:
        sync_blessings(dry_run=args.dry_run)
        print()

    # --- Ailments ---
    if run_all or args.ailments:
        sync_ailments(dry_run=args.dry_run)
        print()

    # --- Monster Mods ---
    if run_all or args.monster_mods:
        sync_monster_mods(dry_run=args.dry_run)
        print()

    # --- Timelines ---
    if run_all or args.timelines:
        sync_timelines(dry_run=args.dry_run)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
