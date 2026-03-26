"""
process_monster_mods.py
=======================
Collects all MonsterMod ScriptableObjects exported by AssetStudio as JSON
from extracted_raw/raw_bundles/duplicateasset/MonoBehaviour/.

Each file corresponds to one MonsterMod (e.g. "Added Crit Chance", "Enrages").
Key fields extracted:
  - modKey (int) — internal key used by MonolithTimeline, AffixList, etc.
  - title (str)  — affix-style display name  (e.g. "of Loathing")
  - description  — short description         (e.g. "High Critical Strike Chance")
  - minilithDescription — mini-dungeon variant description
  - hideInEndgameUI, displayGroup, monolithIconType
  - effectModifierEffect, effectModifierCap
  - increasedItemRarity, increasedExperience
  - hasBonusDrop / bonusDropChance / bonusDropMin / bonusDropMax
  - canSpawnInArena, incompatibleWithChampions
  - minimumLevel, rarityRequirement
  - stats — raw stats array

Output:
  exports_json/monster_mods.json
"""

import json
import os

ROOT          = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUNDLE_DIR    = os.path.join(ROOT, "extracted_raw", "raw_bundles", "duplicateasset", "MonoBehaviour")
OUT_DIR       = os.path.join(ROOT, "exports_json")
OUT_FILE      = os.path.join(OUT_DIR, "monster_mods.json")

_KEEP = {
    "modKey", "modType", "title", "description", "minilithDescription",
    "hideInEndgameUI", "displayGroup", "monolithIconType",
    "effectModifierEffect", "effectModifierCap",
    "increasedItemRarity", "increasedExperience",
    "hasBonusDrop", "bonusDropChance", "bonusDropMin", "bonusDropMax",
    "bonusDropCondition", "bonusDropProperties",
    "canSpawnInArena", "incompatibleWithChampions",
    "minimumLevel", "rarityRequirement",
    "minilithTooltipTitle", "minilithTooltipText",
    "stats",
}


def process_file(path: str) -> dict | None:
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None

    # Only process files that look like MonsterMod objects (have modKey field)
    if "modKey" not in d:
        return None

    rec: dict = {"name": d.get("m_Name", os.path.splitext(os.path.basename(path))[0])}
    for k in _KEEP:
        if k in d:
            rec[k] = d[k]
    return rec


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.path.isdir(BUNDLE_DIR):
        raise FileNotFoundError(f"duplicateasset MonoBehaviour dir not found: {BUNDLE_DIR}")

    files = sorted(os.listdir(BUNDLE_DIR))
    mods = []
    skipped = 0
    for fname in files:
        if not fname.endswith(".json"):
            continue
        rec = process_file(os.path.join(BUNDLE_DIR, fname))
        if rec is None:
            skipped += 1
        else:
            mods.append(rec)

    # Sort by modKey for stable output
    mods.sort(key=lambda x: x.get("modKey", 0))

    out = {
        "_meta": {"count": len(mods), "skipped": skipped,
                  "source": "extracted_raw/raw_bundles/duplicateasset/MonoBehaviour"},
        "monsterMods": mods,
    }
    json.dump(out, open(OUT_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n✅ {len(mods)} monster mods → {OUT_FILE}")


if __name__ == "__main__":
    main()
