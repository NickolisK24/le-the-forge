"""
process_localization.py
=======================
Processes all Unity Localization string table exports from the localization_en bundle.
Builds lookup tables and enriched JSON outputs for:
  - Skill tree node descriptions (Skills_en)
  - Ability names/descriptions (Abilities_en + Abilities Shared Data)
  - Item base type names (Item_Names_en + Item_Names Shared Data)
  - Affix names (Item_Affixes_en)
  - Stat property descriptions (Properties_en)
  - Affix stat descriptors (Descriptors_en)
  - Ailment names (Ailments_en)
  - Common UI strings (Common_en)

Outputs:
  exports_json/localization/skill_tree_strings.json
  exports_json/localization/ability_strings.json
  exports_json/localization/item_strings.json
  exports_json/localization/affix_strings.json
  exports_json/localization/property_strings.json
  exports_json/localization/descriptor_strings.json
  exports_json/localization/ailment_strings.json
"""

import os
import json
import re

ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOC_DIR   = os.path.join(ROOT, "extracted_raw", "raw_bundles", "localization_en", "MonoBehaviour")
OLD_DIR   = os.path.join(ROOT, "extracted_raw")  # affixes/items/ailments already exported
OUT_DIR   = os.path.join(ROOT, "exports_json", "localization")


def load_table(path: str) -> list[dict]:
    """Load m_TableData from a localization JSON file."""
    if not os.path.exists(path):
        return []
    data = json.load(open(path, encoding="utf-8"))
    return data.get("m_TableData", [])


def load_shared_entries(path: str) -> list[dict]:
    """Load m_Entries from a Shared Data JSON file."""
    if not os.path.exists(path):
        return []
    data = json.load(open(path, encoding="utf-8"))
    return data.get("m_Entries", [])


def table_to_dict(table: list[dict]) -> dict[int, str]:
    """Convert m_TableData list to {id: localized_string} dict."""
    return {e["m_Id"]: e["m_Localized"] for e in table if "m_Id" in e}


def shared_to_key_dict(entries: list[dict]) -> dict[int, str]:
    """Convert m_Entries list to {id: key_string} dict."""
    return {e["m_Id"]: e["m_Key"] for e in entries if "m_Id" in e and "m_Key" in e}


def write(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {os.path.relpath(path, ROOT)}  ({len(data) if isinstance(data, (list,dict)) else '?'} entries)")


# ── 1. Skill tree node strings ─────────────────────────────────────────────────
def process_skills_en():
    table = load_table(os.path.join(LOC_DIR, "Skills_en.json"))
    id_map = table_to_dict(table)

    # Pair up: IDs come in runs of (name, description, stat_label, stat_tooltip, ...)
    # Key structure: consecutive IDs, even = name, odd = description (not always)
    # Just export as flat id→string lookup + try to group into nodes
    entries = []
    ids = sorted(id_map.keys())

    i = 0
    while i < len(ids):
        entry_id = ids[i]
        text = id_map[entry_id]
        entries.append({"id": entry_id, "text": text})
        i += 1

    write(os.path.join(OUT_DIR, "skill_tree_strings.json"), entries)
    return id_map


# ── 2. Ability strings ─────────────────────────────────────────────────────────
def process_abilities():
    table     = load_table(os.path.join(LOC_DIR, "Abilities_en.json"))
    id_map    = table_to_dict(table)
    shared    = load_shared_entries(os.path.join(LOC_DIR, "Abilities Shared Data.json"))
    key_map   = shared_to_key_dict(shared)

    # Build structured: key → {id, key, text}
    abilities: dict[str, dict] = {}
    for entry_id, key in key_map.items():
        text = id_map.get(entry_id, "")
        # Parse key: Ability_<InternalName>_<Field>
        parts = key.split("_", 2)
        if len(parts) >= 3:
            internal = parts[1]
            field    = parts[2].lower()  # name, description, lore, alttext
        else:
            internal = key
            field    = "text"

        if internal not in abilities:
            abilities[internal] = {"internalName": internal}
        abilities[internal][field] = text
        abilities[internal][f"{field}_id"] = entry_id

    result = sorted(abilities.values(), key=lambda x: x["internalName"])
    write(os.path.join(OUT_DIR, "ability_strings.json"), result)
    return abilities


# ── 3. Item name strings ───────────────────────────────────────────────────────
def process_item_names():
    table     = load_table(os.path.join(LOC_DIR, "Item_Names_en.json"))
    id_map    = table_to_dict(table)
    shared    = load_shared_entries(os.path.join(LOC_DIR, "Item_Names Shared Data.json"))

    # Build: index → {id, key, name}
    items_by_index: dict[int, dict] = {}
    key_to_id: dict[str, int] = {}

    for entry in shared:
        entry_id = entry.get("m_Id")
        key      = entry.get("m_Key", "")
        rid_list = entry.get("m_Metadata", {}).get("m_Items", [])
        rid      = rid_list[0].get("rid") if rid_list else None
        name     = id_map.get(entry_id, "")

        rec = {"id": entry_id, "key": key, "name": name}
        if rid is not None:
            rec["index"] = rid
            items_by_index[rid] = rec

    result = sorted(items_by_index.values(), key=lambda x: x.get("index", 0))
    write(os.path.join(OUT_DIR, "item_strings.json"), result)

    # Also write flat id→name lookup
    flat = {str(k): v for k, v in id_map.items()}
    write(os.path.join(OUT_DIR, "item_id_to_name.json"), flat)
    return items_by_index


# ── 4. Affix name strings ──────────────────────────────────────────────────────
def process_affix_names():
    # Try localization_en folder first, fall back to old location
    path = os.path.join(LOC_DIR, "Item_Affixes_en.json")
    if not os.path.exists(path):
        path = os.path.join(OLD_DIR, "affixes", "MonoBehaviour", "Item_Affixes_en.json")

    table  = load_table(path)
    id_map = table_to_dict(table)

    result = [{"id": k, "name": v} for k, v in sorted(id_map.items())]
    write(os.path.join(OUT_DIR, "affix_strings.json"), result)

    flat = {str(k): v for k, v in id_map.items()}
    write(os.path.join(OUT_DIR, "affix_id_to_name.json"), flat)
    return id_map


# ── 5. Property (stat) descriptions ───────────────────────────────────────────
def process_properties():
    table  = load_table(os.path.join(LOC_DIR, "Properties_en.json"))
    id_map = table_to_dict(table)

    # Properties come in pairs: even ID = stat name, odd ID = tooltip
    result = []
    ids = sorted(id_map.keys())
    i = 0
    while i < len(ids):
        name_id = ids[i]
        name_text = id_map[name_id]
        tooltip_id = ids[i+1] if i+1 < len(ids) else None
        tooltip_text = id_map.get(tooltip_id, "") if tooltip_id else ""

        result.append({
            "nameId":    name_id,
            "name":      name_text,
            "tooltipId": tooltip_id,
            "tooltip":   tooltip_text,
        })
        i += 2  # advance by 2 (name + tooltip pairs)

    write(os.path.join(OUT_DIR, "property_strings.json"), result)
    return id_map


# ── 6. Descriptor strings (affix stat labels) ──────────────────────────────────
def process_descriptors():
    table  = load_table(os.path.join(LOC_DIR, "Descriptors_en.json"))
    id_map = table_to_dict(table)
    result = [{"id": k, "text": v} for k, v in sorted(id_map.items())]
    write(os.path.join(OUT_DIR, "descriptor_strings.json"), result)
    return id_map


# ── 7. Ailment strings ─────────────────────────────────────────────────────────
def process_ailments():
    path = os.path.join(LOC_DIR, "Ailments_en.json")
    if not os.path.exists(path):
        path = os.path.join(OLD_DIR, "ailments", "MonoBehaviour", "Ailments_en.json")
    table  = load_table(path)
    id_map = table_to_dict(table)
    result = [{"id": k, "text": v} for k, v in sorted(id_map.items())]
    write(os.path.join(OUT_DIR, "ailment_strings.json"), result)
    return id_map


# ── 8. Common strings ──────────────────────────────────────────────────────────
def process_common():
    table  = load_table(os.path.join(LOC_DIR, "Common_en.json"))
    id_map = table_to_dict(table)
    result = [{"id": k, "text": v} for k, v in sorted(id_map.items())]
    write(os.path.join(OUT_DIR, "common_strings.json"), result)


# ── 9. Enrich skills.json with skill tree strings ─────────────────────────────
def enrich_skills_with_localization(skill_tree_id_map: dict, ability_strings: dict):
    """Cross-reference existing skills.json with ability_strings to add tree node data."""
    skills_path = os.path.join(ROOT, "exports_json", "skills.json")
    if not os.path.exists(skills_path):
        print("  [SKIP] skills.json not found — run process_skills.py first")
        return

    skills_data = json.load(open(skills_path, encoding="utf-8"))
    skills = skills_data.get("skills", [])
    enriched = 0

    for skill in skills:
        internal_name = skill.get("name", "").replace(" ", "")
        # Try to find matching ability strings by name similarity
        match = ability_strings.get(internal_name)
        if match:
            if "description" in match and not skill.get("description"):
                skill["description"] = match["description"]
            enriched += 1

    skills_data["meta"]["localization_enriched"] = enriched
    with open(skills_path, "w", encoding="utf-8") as f:
        json.dump(skills_data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ skills.json enriched ({enriched} skills matched)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Processing localization from:\n  {LOC_DIR}\n")

    print("1. Skill tree strings...")
    skill_tree_map = process_skills_en()

    print("2. Ability strings...")
    ability_strings = process_abilities()

    print("3. Item name strings...")
    process_item_names()

    print("4. Affix name strings...")
    process_affix_names()

    print("5. Property (stat) descriptions...")
    process_properties()

    print("6. Descriptor strings...")
    process_descriptors()

    print("7. Ailment strings...")
    process_ailments()

    print("8. Common UI strings...")
    process_common()

    print("9. Enriching skills.json...")
    enrich_skills_with_localization(skill_tree_map, ability_strings)

    print(f"\n✅ All localization data written to exports_json/localization/")


if __name__ == "__main__":
    main()
