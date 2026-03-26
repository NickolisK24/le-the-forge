"""
process_localization_unified.py
================================
Merges all Last Epoch localization tables into a single unified JSON lookup.

For each table pair (e.g. "Skills_en.json" + "Skills Shared Data.json"):
  - SharedData gives: m_Id → key name (e.g. "Skill_Name_0")
  - en.json gives:    m_Id → localized text (e.g. "Fireball")

Output:
  exports_json/localization/en.json
    { "Skills": { "Skill_Name_0": "Fireball", ... }, ... }

  exports_json/localization/id_lookup.json
    { "80002": "Fireball", ... }   (all IDs → text for fast lookup)

Run from repo root or via run_all.py.
"""

import json
import os
import re

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOC_DIR = os.path.join(ROOT, "extracted_raw", "raw_bundles", "localization_en", "MonoBehaviour")
OUT_DIR = os.path.join(ROOT, "exports_json", "localization")
OUT_EN  = os.path.join(OUT_DIR, "en.json")
OUT_ID  = os.path.join(OUT_DIR, "id_lookup.json")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8", errors="replace") as f:
        return json.load(f)


def table_name_from_filename(fname: str) -> str:
    """Turn 'Skills_en.json' → 'Skills', 'Item_Names_en.json' → 'Item_Names'."""
    base = os.path.splitext(fname)[0]
    base = re.sub(r'_en$', '', base)
    base = re.sub(r' Shared Data$', '', base)
    return base


def process_table(shared_path: str, en_path: str) -> dict[str, str]:
    """
    Merge one SharedData + en table pair.
    Returns {key_name: localized_text}.
    """
    shared = load_json(shared_path)
    en     = load_json(en_path)

    # Build id → key map from SharedData
    id_to_key: dict[int, str] = {}
    for entry in shared.get("m_Entries", []):
        id_to_key[entry["m_Id"]] = entry["m_Key"]

    # Build id → text map from en
    id_to_text: dict[int, str] = {}
    for entry in en.get("m_TableData", []):
        id_to_text[entry["m_Id"]] = entry["m_Localized"]

    # Merge: key → text (skip entries without both key and text)
    result: dict[str, str] = {}
    for id_, key in id_to_key.items():
        text = id_to_text.get(id_)
        if text is not None:
            result[key] = text

    return result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    files = os.listdir(LOC_DIR)
    en_files     = {f for f in files if f.endswith("_en.json")}
    shared_files = {f for f in files if f.endswith(" Shared Data.json")}

    # Map table name → shared data filename
    table_to_shared: dict[str, str] = {}
    for f in shared_files:
        tname = table_name_from_filename(f)
        table_to_shared[tname] = f

    all_tables: dict[str, dict[str, str]] = {}
    id_lookup:  dict[str, str] = {}

    for en_file in sorted(en_files):
        tname = table_name_from_filename(en_file)
        en_path = os.path.join(LOC_DIR, en_file)

        # Find matching shared data
        shared_fname = table_to_shared.get(tname)
        if not shared_fname:
            # Try common suffix variations
            for candidate in shared_files:
                if candidate.startswith(tname.replace("_", " ").replace("_en", "")):
                    shared_fname = candidate
                    break

        if not shared_fname:
            print(f"  WARNING: No SharedData for {en_file} — skipping key names, using IDs")
            en_data = load_json(en_path)
            table: dict[str, str] = {}
            for entry in en_data.get("m_TableData", []):
                id_str = str(entry["m_Id"])
                text   = entry["m_Localized"]
                table[id_str] = text
                id_lookup[id_str] = text
            all_tables[tname] = table
            continue

        shared_path = os.path.join(LOC_DIR, shared_fname)
        try:
            table = process_table(shared_path, en_path)
        except Exception as e:
            print(f"  ERROR processing {en_file}: {e}")
            continue

        # Also build id_lookup from this en file
        en_data = load_json(en_path)
        for entry in en_data.get("m_TableData", []):
            id_lookup[str(entry["m_Id"])] = entry["m_Localized"]

        all_tables[tname] = table
        print(f"  {tname}: {len(table)} entries")

    # Write outputs
    with open(OUT_EN, "w", encoding="utf-8") as f:
        json.dump(all_tables, f, indent=2, ensure_ascii=False)

    with open(OUT_ID, "w", encoding="utf-8") as f:
        json.dump(id_lookup, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in all_tables.values())
    print(f"\n✅ {len(all_tables)} tables, {total} total entries")
    print(f"   → {OUT_EN}")
    print(f"   → {OUT_ID}")


if __name__ == "__main__":
    main()
