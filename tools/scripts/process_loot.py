"""
process_loot.py
===============
Collects BossLoot ScriptableObjects exported by AssetStudio as JSON.

Sources:
  - extracted_raw/raw_bundles/defaultlocalgroup/MonoBehaviour/   (generic loot tables)
  - extracted_raw/raw_bundles/actors_misc/MonoBehaviour/         (boss-specific loot)

These files use Unity's BossLoot ScriptableObject format:
  {
    "nestedBossLoot": [...],  // references to other BossLoot SOs (by name/path)
    "lootGroups": [
      {
        "dropChance": float,
        "maxDropChance": float,
        "drops": [
          {
            "weight": float,
            "loot": {
              "itemType": int,   // EquipmentType enum value
              "subType": int,    // subTypeID (-1 = any)
              "ilvl": int,
              "rarityType": int, // 0=any, 1=specific, ...
              "rarity": int,
              "uniqueID": int,   // -1 = not a specific unique
              ...
            }
          }
        ]
      }
    ]
  }

Output:
  exports_json/loot_tables.json
"""

import json
import os

ROOT       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR    = os.path.join(ROOT, "exports_json")
OUT_FILE   = os.path.join(OUT_DIR, "loot_tables.json")

SOURCES = [
    ("generic",     os.path.join(ROOT, "extracted_raw", "raw_bundles", "defaultlocalgroup", "MonoBehaviour")),
    ("boss",        os.path.join(ROOT, "extracted_raw", "raw_bundles", "actors_misc",       "MonoBehaviour")),
]

_LOOT_PROPS_KEEP = {
    "itemTypeType", "itemType", "itemTypeGroup", "subType",
    "property", "ilvl", "rarityType", "rarity", "rarityGroup",
    "uniqueID", "requireLegendaryType", "requiredLegendaryType",
    "minimumLegendaryPotential", "hasClassRequirement", "classRequirement",
    "hasSubClassRequirement", "subClassRequirement",
}

_GROUP_KEEP = {
    "dropChance", "maxDropChance", "chanceModifier",
    "chanceMultiplierPerCorruption", "corruptionOffsetForChanceMultiplier",
    "dropAttemptsModifier", "minLevel", "minCorruption", "lootType",
    "dropChancesForTiers",
}


def clean_loot_props(loot: dict) -> dict:
    return {k: v for k, v in loot.items() if k in _LOOT_PROPS_KEEP}


def clean_group(group: dict) -> dict:
    rec = {k: v for k, v in group.items() if k in _GROUP_KEEP}
    drops = []
    for drop in group.get("drops", []):
        loot_raw = drop.get("loot", {})
        drops.append({
            "weight": drop.get("weight", 1.0),
            "loot": clean_loot_props(loot_raw),
        })
    if drops:
        rec["drops"] = drops
    return rec


def process_file(path: str) -> dict | None:
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None

    if "lootGroups" not in d:
        return None

    groups = [clean_group(g) for g in d.get("lootGroups", [])]
    nested = [n.get("m_PathID") for n in d.get("nestedBossLoot", [])
              if isinstance(n, dict) and n.get("m_PathID")]

    rec: dict = {
        "name": d.get("m_Name", os.path.splitext(os.path.basename(path))[0]),
        "lootGroups": groups,
    }
    if nested:
        rec["nestedBossLoot"] = nested
    return rec


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_tables: list[dict] = []
    counts: dict[str, int] = {}

    for category, bundle_dir in SOURCES:
        if not os.path.isdir(bundle_dir):
            print(f"  ⚠️  Skipping '{category}' — dir not found: {bundle_dir}")
            counts[category] = 0
            continue

        tables = []
        for fname in sorted(os.listdir(bundle_dir)):
            if not fname.endswith(".json"):
                continue
            rec = process_file(os.path.join(bundle_dir, fname))
            if rec is not None:
                rec["category"] = category
                tables.append(rec)

        counts[category] = len(tables)
        all_tables.extend(tables)

    total = len(all_tables)
    out = {
        "_meta": {"total": total, "by_category": counts},
        "lootTables": all_tables,
    }
    json.dump(out, open(OUT_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    print(f"\n✅ {total} loot tables → {OUT_FILE}")
    for cat, n in counts.items():
        print(f"   {cat}: {n}")


if __name__ == "__main__":
    main()
