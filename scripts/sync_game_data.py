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
from collections import Counter
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
    """Convert 'Void Penetration' → 'void_penetration'. Strips apostrophes before slugifying
    so "Artor's Legacy" → 'artors_legacy' (matching existing data/uniques.json key style)."""
    slug = name.lower().strip()
    slug = slug.replace("'", "")   # strip apostrophes before the regex pass
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
    # Only include equipment-type entries — idol entries use numeric ids now
    # and must not pollute the equipment name→id lookup.
    existing_by_name: dict[str, dict] = {
        a["name"]: a for a in existing
        if a.get("type") != "idol"
        and not str(a.get("id", "")).startswith("idol_")
        and a.get("rolls_on") != "idol"
    }
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
            # Idol affixes: use numeric affix_id from export as the canonical key.
            # Slugs are unreliable because many idol affixes share the same display
            # name (same stat rolling on different idol sizes = different affix_id).
            affix_id = raw_affix["id"]
            canonical_id = f"idol_{affix_id}"
            entry: dict = {
                "id": canonical_id,
                "name": name,
                "type": "idol",
                "tags": cur.get("tags", []),
                "applicable_to": cur.get("applicable_to", ["idol"]),
                "class_requirement": None,
                "tiers": tiers if tiers else cur.get("tiers", []),
                "stat_key": canonical_id,
                "affix_id": affix_id,
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

    # Process equipment affixes — track used IDs to block legacy slug collisions.
    # Some idol-named affixes share the same display name but roll on different
    # idol sizes; use the export's numeric id as a suffix to keep them unique.
    used_ids: set[str] = set()
    for raw_affix in equipment_list:
        entry = _process_affix(raw_affix, is_idol=False)
        if entry["id"] in used_ids:
            numeric = raw_affix.get("id")
            if numeric is not None:
                entry["id"] = f"{entry['id']}_{numeric}"
                if entry.get("stat_key") == entry["id"].rsplit(f"_{numeric}", 1)[0]:
                    entry["stat_key"] = entry["id"]
        result.append(entry)
        updated_names.add(raw_affix["name"])
        used_ids.add(entry["id"])

    # Process idol affixes — each gets a stable numeric id: idol_{affix_id}
    for raw_affix in idol_list:
        entry = _process_affix(raw_affix, is_idol=True)
        used_ids.add(entry["id"])
        result.append(entry)
        updated_names.add(raw_affix["name"])

    # Preserve legacy affixes not in new data — but never if their slug already
    # exists in the export output (game data takes priority).
    # Idol affixes are NEVER preserved from legacy — they all come from the export
    # with stable idol_{id} keys, so old slug-based idol entries are obsolete.
    preserved = 0
    for affix in existing:
        if (affix.get("type") == "idol"
                or str(affix.get("id", "")).startswith("idol_")
                or affix.get("rolls_on") == "idol"):
            continue
        if affix["name"] not in updated_names and affix.get("id") not in used_ids:
            result.append(affix)
            used_ids.add(affix.get("id", ""))
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

    out_path = DATA_DIR / "classes" / "skills_metadata.json"
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
        all_nodes = tree.get("nodes", [])

        # Pass 1: detect raw_node_id collisions (same id used in multiple mastery subtrees)
        raw_id_counts = Counter(n["id"] for n in all_nodes)
        colliding_raw_ids: set[int] = {rid for rid, cnt in raw_id_counts.items() if cnt > 1}

        # Build a lookup: raw_id → mastery_index (for connection ID resolution)
        # When there are collisions, mastery_index is needed to generate the correct id.
        raw_id_to_mastery: dict[int, int] = {}
        for n in all_nodes:
            rid = n["id"]
            mid = n.get("mastery", 0)
            if rid not in colliding_raw_ids:
                raw_id_to_mastery[rid] = 0  # base or unambiguous

        def _node_id(raw_id: int, mastery_idx: int) -> str:
            if raw_id in colliding_raw_ids:
                return f"{prefix}_m{mastery_idx}_{raw_id}"
            return f"{prefix}_{raw_id}"

        for node in all_nodes:
            raw_id: int = node["id"]
            mastery_idx: int = node.get("mastery", 0)
            node_id = _node_id(raw_id, mastery_idx)

            mastery_name: str | None = mastery_map.get(mastery_idx)

            # Connections: requirements is [{nodeId: int, requirement: int}, ...]
            # For colliding raw IDs, resolve the connected node's mastery by scanning.
            connections = []
            for r in node.get("requirements", []):
                req_raw_id = r["nodeId"]
                if req_raw_id in colliding_raw_ids:
                    # Find the actual node in this tree to get its mastery
                    req_node = next((n for n in all_nodes if n["id"] == req_raw_id), None)
                    req_mastery = req_node.get("mastery", 0) if req_node else 0
                    connections.append(_node_id(req_raw_id, req_mastery))
                else:
                    connections.append(f"{prefix}_{req_raw_id}")

            # Stats
            raw_stats = node.get("stats", [])
            stats = [
                {"key": s.get("statName", ""), "value": s.get("value", "")}
                for s in raw_stats
            ]

            ability_granted = node.get("abilityGrantedByNode") or None

            transform = node.get("transform", {})
            x = transform.get("x", 0.0)
            y = transform.get("y", 0.0)

            raw_icon = node.get("icon")
            icon = str(raw_icon) if raw_icon is not None else None

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

        if colliding_raw_ids:
            print(f"  [INFO] {cls}: {len(colliding_raw_ids)} raw node ID(s) shared across masteries — disambiguated with mastery prefix")

    out_path = DATA_DIR / "classes" / "passives.json"
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

    out_path = DATA_DIR / "progression" / "blessings.json"
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

    out_path = DATA_DIR / "combat" / "ailments.json"
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

    out_path = DATA_DIR / "combat" / "monster_mods.json"
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

    out_path = DATA_DIR / "progression" / "timelines.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  timelines: {len(out)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] timelines: would write {len(out)} entries → {out_path.name}")

    return out


def _format_tooltip_text(text: str) -> str:
    """
    Convert game tooltip format '[min,max,step]...' → 'min–max...'.

    Examples:
      '[100,150,0]% Chance to Ignite' → '100–150% Chance to Ignite'
      '[0.06,0.12,0]' → '6–12'  (floats < 1 are multiplied × 100 for display)
    """
    def _replace(m: re.Match) -> str:
        parts = m.group(1).split(",")
        try:
            lo = float(parts[0])
            hi = float(parts[1])
            # Values stored as fractions (0–1) → convert to percentage display
            if abs(lo) < 1.0 and abs(hi) < 1.0 and lo != 0.0:
                lo = round(lo * 100)
                hi = round(hi * 100)
            else:
                lo = int(lo) if lo == int(lo) else lo
                hi = int(hi) if hi == int(hi) else hi
            return f"{lo}–{hi}"
        except (ValueError, IndexError):
            return m.group(0)

    return re.sub(r"\[([^\]]+)\]", _replace, text)


def sync_uniques(dry_run: bool = False) -> dict | None:
    """
    Merge exports_json/uniques.json into data/uniques.json.

    Source schema (uniques.json → "uniques" array):
      id, name, displayName, baseType, mods, legendaryType,
      effectiveLevelForLP, canDropRandomly, rerollChance,
      tooltipDescriptions [{text}], loreText

    Merge strategy:
    - Keyed by slug of `name` (matches existing data/uniques.json keys).
    - Curated fields preserved if already set: base, implicit, affixes, tags.
    - Updated from export: slot, lore, unique_effects (from tooltipDescriptions).
    - New raw fields added: legendary_type, effective_level_for_lp,
      can_drop_randomly, reroll_chance.
    """
    src_path = SRC_DIR / "uniques.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping uniques sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    existing_path = DATA_DIR / "items" / "uniques.json"
    existing: dict = {}
    if existing_path.exists():
        with open(existing_path, encoding="utf-8") as f:
            existing = json.load(f)

    export_uniques: list[dict] = raw.get("uniques", [])
    out: dict = {"_meta": existing.get("_meta", {})}
    new_count = 0
    updated_count = 0

    for item in export_uniques:
        name = item.get("name", "")
        display = item.get("displayName", "") or name
        if not name and not display:
            continue

        slug = _slugify(display)
        current = existing.get(slug, {})
        is_new = not bool(current)

        slot = _convert_slot(item.get("baseType", ""))
        unique_effects = [
            _format_tooltip_text(t["text"])
            for t in item.get("tooltipDescriptions", [])
        ]
        lore = item.get("loreText", "") or current.get("lore", "")

        entry = {
            "name": display,
            "slot": slot or current.get("slot", ""),
            # Curated fields: preserve if set, leave empty if not
            "base": current.get("base", ""),
            "implicit": current.get("implicit", ""),
            "affixes": current.get("affixes", []),
            "unique_effects": unique_effects,
            "tags": current.get("tags", []),
            "lore": lore,
            # Raw export fields
            "legendary_type": item.get("legendaryType", "None"),
            "effective_level_for_lp": item.get("effectiveLevelForLP"),
            "can_drop_randomly": item.get("canDropRandomly", True),
            "reroll_chance": item.get("rerollChance", 0.0),
        }

        out[slug] = entry
        if is_new:
            new_count += 1
        else:
            updated_count += 1

    # Preserve any existing entries not in the export
    for slug, val in existing.items():
        if slug not in out:
            out[slug] = val

    out_path = DATA_DIR / "items" / "uniques.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  uniques: {updated_count} updated, {new_count} new → {out_path.name}")
    else:
        print(f"  [DRY RUN] uniques: would update {updated_count}, add {new_count} → {out_path.name}")

    return out


def sync_set_items(dry_run: bool = False) -> dict | None:
    """
    Merge set item data from exports into data/set_items.json.

    Sources:
      - exports_json/uniques.json → "setItems" array (47 items with mods/tooltips)
      - exports_json/set_bonuses.json → "setBonuses" array (7 sets with bonus tiers)

    Merge strategy:
    - Individual set items keyed by slug of displayName (or name).
    - Curated fields preserved: base, affixes, tags, lore.
    - Updated: slot, unique_effects (from tooltipDescriptions).
    - "sets" dict updated with set_name and bonus tier descriptions from set_bonuses.json.
    """
    uniques_src = SRC_DIR / "uniques.json"
    bonuses_src = SRC_DIR / "set_bonuses.json"

    if not uniques_src.exists():
        print(f"  [WARN] {uniques_src} not found — skipping set_items sync")
        return None

    with open(uniques_src, encoding="utf-8") as f:
        uniques_raw = json.load(f)

    set_bonuses_by_id: dict[int, dict] = {}
    if bonuses_src.exists():
        with open(bonuses_src, encoding="utf-8") as f:
            bonuses_raw = json.load(f)
        for entry in bonuses_raw.get("setBonuses", []):
            set_bonuses_by_id[entry["setId"]] = entry
    else:
        print(f"  [WARN] {bonuses_src} not found — set bonus descriptions will be skipped")

    existing_path = DATA_DIR / "items" / "set_items.json"
    existing: dict = {}
    if existing_path.exists():
        with open(existing_path, encoding="utf-8") as f:
            existing = json.load(f)

    export_set_items: list[dict] = uniques_raw.get("setItems", [])

    # Rebuild sets dict: setId → {name, items[], bonuses[]}
    sets: dict[str, dict] = existing.get("sets", {})
    set_id_to_slugs: dict[int, list[str]] = {}

    out: dict = {"_meta": existing.get("_meta", {})}
    new_count = 0
    updated_count = 0

    for item in export_set_items:
        display = item.get("displayName", "") or item.get("name", "")
        if not display:
            continue

        slug = _slugify(display)
        current = existing.get(slug, {})
        is_new = not bool(current)

        slot = _convert_slot(item.get("baseType", ""))
        unique_effects = [
            _format_tooltip_text(t["text"])
            for t in item.get("tooltipDescriptions", [])
        ]
        set_id: int = item.get("setId", 0)

        entry = {
            "name": display,
            "slot": slot or current.get("slot", ""),
            "set_id": set_id,
            "set": set_bonuses_by_id.get(set_id, {}).get("setName", current.get("set", "")),
            "base": current.get("base", ""),
            "affixes": current.get("affixes", []),
            "unique_effects": unique_effects,
            "tags": current.get("tags", []),
            "lore": item.get("loreText", "") or current.get("lore", ""),
        }

        out[slug] = entry
        set_id_to_slugs.setdefault(set_id, []).append(slug)

        if is_new:
            new_count += 1
        else:
            updated_count += 1

    # Rebuild sets dict with bonus tier data
    for set_id, slugs in set_id_to_slugs.items():
        bonus_entry = set_bonuses_by_id.get(set_id, {})
        set_name = bonus_entry.get("setName", sets.get(str(set_id), {}).get("name", ""))
        bonuses = [
            {
                "pieces_required": b["piecesRequired"],
                "text": b.get("text", ""),
                "alt_text": b.get("altText", ""),
            }
            for b in bonus_entry.get("bonuses", [])
        ]
        sets[str(set_id)] = {
            "name": set_name,
            "items": slugs,
            "bonuses": bonuses,
        }

    out["sets"] = sets

    # Preserve any existing item entries not in the export
    for slug, val in existing.items():
        if slug not in out and slug not in ("_meta", "sets"):
            out[slug] = val

    out_path = DATA_DIR / "items" / "set_items.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  set_items: {updated_count} updated, {new_count} new, {len(sets)} sets → {out_path.name}")
    else:
        print(f"  [DRY RUN] set_items: would update {updated_count}, add {new_count}, {len(sets)} sets → {out_path.name}")

    return out


# ---------------------------------------------------------------------------
# Passthrough syncs — copy export data into data/ with light normalization
# ---------------------------------------------------------------------------

def sync_actors(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/actors.json → data/actors.json.
    Source: {"meta": {...}, "actors": [{id, name, level, actorType, monsterForgeCategory, tags, ...}]}
    """
    src_path = SRC_DIR / "actors.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping actors sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    actors_raw = raw.get("actors", [])
    # Deduplicate by id (export can contain exact duplicate entries)
    seen_ids: set = set()
    actors = []
    for a in actors_raw:
        if a["id"] not in seen_ids:
            seen_ids.add(a["id"])
            actors.append(a)
    dupes_removed = len(actors_raw) - len(actors)
    out_path = DATA_DIR / "entities" / "actors.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(actors, f, indent=2, ensure_ascii=False)
        print(f"  actors: {len(actors)} entries → {out_path.name}" + (f" ({dupes_removed} duplicates removed)" if dupes_removed else ""))
    else:
        print(f"  [DRY RUN] actors: would write {len(actors)} entries → {out_path.name}" + (f" ({dupes_removed} duplicates removed)" if dupes_removed else ""))
    return actors


def sync_classes(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/classes.json → data/classes.json.
    Source: {"meta": {...}, "classes": [{id, name, treeID, baseHealth, baseMana, masteries, ...}]}
    """
    src_path = SRC_DIR / "classes.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping classes sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    classes = raw.get("classes", [])
    out_path = DATA_DIR / "classes" / "classes.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(classes, f, indent=2, ensure_ascii=False)
        print(f"  classes: {len(classes)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] classes: would write {len(classes)} entries → {out_path.name}")
    return classes


def sync_community_skill_trees(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/community_skill_trees.json → data/community_skill_trees.json.
    Source: {"meta": {...}, "skillTrees": [{id, ability, nodes: [...]}]}
    """
    src_path = SRC_DIR / "community_skill_trees.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping community_skill_trees sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    trees = raw.get("skillTrees", [])
    out_path = DATA_DIR / "classes" / "community_skill_trees.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(trees, f, indent=2, ensure_ascii=False)
        print(f"  community_skill_trees: {len(trees)} skill trees → {out_path.name}")
    else:
        print(f"  [DRY RUN] community_skill_trees: would write {len(trees)} skill trees → {out_path.name}")
    return trees


def sync_dungeons(dry_run: bool = False) -> dict | None:
    """
    Copy exports_json/dungeons.json → data/dungeons.json.
    Source: {"meta": {...}, "dungeons": [{id, name, mods}], "vaultModStrings": [{id, text}]}
    """
    src_path = SRC_DIR / "dungeons.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping dungeons sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    out = {
        "dungeons": raw.get("dungeons", []),
        "vault_mod_strings": raw.get("vaultModStrings", []),
    }
    out_path = DATA_DIR / "world" / "dungeons.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  dungeons: {len(out['dungeons'])} dungeons, {len(out['vault_mod_strings'])} vault mods → {out_path.name}")
    else:
        print(f"  [DRY RUN] dungeons: would write {len(out['dungeons'])} dungeons → {out_path.name}")
    return out


def sync_items(dry_run: bool = False) -> dict | None:
    """
    Copy exports_json/items.json → data/items.json.
    Source: {"_meta": {...}, "equippable": [{name, displayName, baseTypeID, ...}], "nonEquippable": [...]}
    This is raw base item type data, distinct from the curated data/base_items.json.
    """
    src_path = SRC_DIR / "items.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping items sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    out = {
        "equippable": raw.get("equippable", []),
        "non_equippable": raw.get("nonEquippable", []),
    }
    out_path = DATA_DIR / "items" / "items.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  items: {len(out['equippable'])} equippable, {len(out['non_equippable'])} non-equippable → {out_path.name}")
    else:
        print(f"  [DRY RUN] items: would write {len(out['equippable'])} equippable base types → {out_path.name}")
    return out


def sync_loot_tables(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/loot_tables.json → data/loot_tables.json.
    Source: {"_meta": {...}, "lootTables": [{name, lootGroups, category}]}
    """
    src_path = SRC_DIR / "loot_tables.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping loot_tables sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    tables = raw.get("lootTables", [])
    out_path = DATA_DIR / "world" / "loot_tables.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(tables, f, indent=2, ensure_ascii=False)
        print(f"  loot_tables: {len(tables)} tables → {out_path.name}")
    else:
        print(f"  [DRY RUN] loot_tables: would write {len(tables)} tables → {out_path.name}")
    return tables


def sync_quests(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/quests.json → data/quests.json.
    Source: {"meta": {...}, "quests": [{id, displayName, chapter, mainLine, ...}]}
    """
    src_path = SRC_DIR / "quests.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping quests sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    quests = raw.get("quests", [])
    out_path = DATA_DIR / "world" / "quests.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(quests, f, indent=2, ensure_ascii=False)
        print(f"  quests: {len(quests)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] quests: would write {len(quests)} entries → {out_path.name}")
    return quests


def sync_skills_with_trees(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/skills_with_trees.json → data/skills_with_trees.json.
    Source: {"meta": {...}, "skills": [{id, name, description, tags, nodes, ...}]}
    Full skill data including tree node definitions for all 182 skills.
    """
    src_path = SRC_DIR / "skills_with_trees.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping skills_with_trees sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    skills = raw.get("skills", [])
    out_path = DATA_DIR / "classes" / "skills_with_trees.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(skills, f, indent=2, ensure_ascii=False)
        print(f"  skills_with_trees: {len(skills)} skills → {out_path.name}")
    else:
        print(f"  [DRY RUN] skills_with_trees: would write {len(skills)} skills → {out_path.name}")
    return skills


def sync_unmatched_trees(dry_run: bool = False) -> list[dict] | None:
    """
    Copy exports_json/unmatched_trees.json → data/unmatched_trees.json.
    Source: array of skill tree entries that couldn't be matched to a known skill.
    """
    src_path = SRC_DIR / "unmatched_trees.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping unmatched_trees sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        trees = json.load(f)

    if not isinstance(trees, list):
        trees = []

    out_path = DATA_DIR / "classes" / "unmatched_trees.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(trees, f, indent=2, ensure_ascii=False)
        print(f"  unmatched_trees: {len(trees)} entries → {out_path.name}")
    else:
        print(f"  [DRY RUN] unmatched_trees: would write {len(trees)} entries → {out_path.name}")
    return trees


def sync_zones(dry_run: bool = False) -> dict | None:
    """
    Copy exports_json/zones.json → data/zones.json.
    Source: {"meta": {...}, "zones": [{id, name}], "mapObjects": [{id, name}]}
    """
    src_path = SRC_DIR / "zones.json"
    if not src_path.exists():
        print(f"  [WARN] {src_path} not found — skipping zones sync")
        return None

    with open(src_path, encoding="utf-8") as f:
        raw = json.load(f)

    out = {
        "zones": raw.get("zones", []),
        "map_objects": raw.get("mapObjects", []),
    }
    out_path = DATA_DIR / "world" / "zones.json"
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"  zones: {len(out['zones'])} zones, {len(out['map_objects'])} map objects → {out_path.name}")
    else:
        print(f"  [DRY RUN] zones: would write {len(out['zones'])} zones → {out_path.name}")
    return out


def sync_localization(dry_run: bool = False) -> dict[str, int] | None:
    """
    Copy all files from exports_json/localization/ → data/localization/.
    Handles all 20+ localization files as direct passthroughs.
    Returns a dict of {filename: entry_count} for reporting.
    """
    src_dir = SRC_DIR / "localization"
    if not src_dir.exists():
        print(f"  [WARN] {src_dir} not found — skipping localization sync")
        return None

    out_dir = DATA_DIR / "localization"
    if not dry_run:
        out_dir.mkdir(exist_ok=True)

    results: dict[str, int] = {}
    for src_file in sorted(src_dir.glob("*.json")):
        with open(src_file, encoding="utf-8") as f:
            data = json.load(f)

        count = len(data) if isinstance(data, list) else len(data)
        results[src_file.name] = count

        out_path = out_dir / src_file.name
        if not dry_run:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    total_files = len(results)
    total_entries = sum(results.values())
    if not dry_run:
        print(f"  localization: {total_files} files, {total_entries} total entries → data/localization/")
        for fname, count in results.items():
            print(f"    {fname}: {count} entries")
    else:
        print(f"  [DRY RUN] localization: would write {total_files} files, {total_entries} total entries → data/localization/")
    return results


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
    parser.add_argument("--uniques", action="store_true", help="Sync uniques.json")
    parser.add_argument("--set-items", action="store_true", dest="set_items", help="Sync set_items.json")
    parser.add_argument("--actors", action="store_true", help="Sync actors.json")
    parser.add_argument("--classes", action="store_true", help="Sync classes.json")
    parser.add_argument("--community-skill-trees", action="store_true", dest="community_skill_trees", help="Sync community_skill_trees.json")
    parser.add_argument("--dungeons", action="store_true", help="Sync dungeons.json")
    parser.add_argument("--items", action="store_true", help="Sync items.json (base item types)")
    parser.add_argument("--loot-tables", action="store_true", dest="loot_tables", help="Sync loot_tables.json")
    parser.add_argument("--quests", action="store_true", help="Sync quests.json")
    parser.add_argument("--skills-with-trees", action="store_true", dest="skills_with_trees", help="Sync skills_with_trees.json")
    parser.add_argument("--unmatched-trees", action="store_true", dest="unmatched_trees", help="Sync unmatched_trees.json")
    parser.add_argument("--zones", action="store_true", help="Sync zones.json")
    parser.add_argument("--localization", action="store_true", help="Sync all localization/ files")
    args = parser.parse_args()

    if not SRC_DIR.exists():
        print(f"ERROR: Source directory not found: {SRC_DIR}", file=sys.stderr)
        print("Make sure last-epoch-data is available in the project root.", file=sys.stderr)
        sys.exit(1)

    # If no specific flags given, default to running all
    specific_flags = [args.affixes, args.skills, args.passives, args.blessings,
                      args.ailments, args.monster_mods, args.timelines,
                      args.uniques, args.set_items, args.actors, args.classes,
                      args.community_skill_trees, args.dungeons, args.items,
                      args.loot_tables, args.quests, args.skills_with_trees,
                      args.unmatched_trees, args.zones, args.localization]
    run_all = args.all or not any(specific_flags)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing game data from {SRC_DIR.name}...\n")

    # --- Affixes ---
    if run_all or args.affixes:
        affixes_path = DATA_DIR / "items" / "affixes.json"
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

    # --- Uniques ---
    if run_all or args.uniques:
        sync_uniques(dry_run=args.dry_run)
        print()

    # --- Set Items ---
    if run_all or args.set_items:
        sync_set_items(dry_run=args.dry_run)
        print()

    # --- Actors ---
    if run_all or args.actors:
        sync_actors(dry_run=args.dry_run)
        print()

    # --- Classes ---
    if run_all or args.classes:
        sync_classes(dry_run=args.dry_run)
        print()

    # --- Community Skill Trees ---
    if run_all or args.community_skill_trees:
        sync_community_skill_trees(dry_run=args.dry_run)
        print()

    # --- Dungeons ---
    if run_all or args.dungeons:
        sync_dungeons(dry_run=args.dry_run)
        print()

    # --- Items (base types) ---
    if run_all or args.items:
        sync_items(dry_run=args.dry_run)
        print()

    # --- Loot Tables ---
    if run_all or args.loot_tables:
        sync_loot_tables(dry_run=args.dry_run)
        print()

    # --- Quests ---
    if run_all or args.quests:
        sync_quests(dry_run=args.dry_run)
        print()

    # --- Skills With Trees ---
    if run_all or args.skills_with_trees:
        sync_skills_with_trees(dry_run=args.dry_run)
        print()

    # --- Unmatched Trees ---
    if run_all or args.unmatched_trees:
        sync_unmatched_trees(dry_run=args.dry_run)
        print()

    # --- Zones ---
    if run_all or args.zones:
        sync_zones(dry_run=args.dry_run)
        print()

    # --- Localization ---
    if run_all or args.localization:
        sync_localization(dry_run=args.dry_run)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
