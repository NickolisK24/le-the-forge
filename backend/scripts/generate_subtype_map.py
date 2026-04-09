"""
generateSubtypeMap.py

Generates SUBTYPE_ID_TO_ITEM_TYPE_ID.ts from data/items/items.json.

The key insight: per-item subTypeID values are NOT globally unique (they
restart at 0 for each base type). Only baseTypeID is globally unique.
This script maps baseTypeID → ItemTypeId.

Usage:
    python backend/scripts/generateSubtypeMap.py
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ITEMS_PATH = os.path.join(BASE_DIR, "..", "data", "items", "items.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "src", "constants", "SUBTYPE_ID_TO_ITEM_TYPE_ID.ts")

# Maps raw game type string → canonical ItemTypeId slug
GAME_TYPE_TO_ITEM_TYPE_ID = {
    "HELMET":             "helm",
    "BODY_ARMOR":         "chest",
    "BELT":               "belt",
    "BOOTS":              "boots",
    "GLOVES":             "gloves",
    "ONE_HANDED_AXE":     "axe",
    "ONE_HANDED_DAGGER":  "dagger",
    "ONE_HANDED_FIST":    "fist",
    "ONE_HANDED_MACES":   "mace",
    "ONE_HANDED_SCEPTRE": "sceptre",
    "ONE_HANDED_SWORD":   "sword",
    "WAND":               "wand",
    "TWO_HANDED_AXE":     "axe",
    "TWO_HANDED_MACE":    "mace",
    "TWO_HANDED_SPEAR":   "polearm",
    "TWO_HANDED_STAFF":   "staff",
    "TWO_HANDED_SWORD":   "sword",
    "BOW":                "bow",
    "CROSSBOW":           "crossbow",
    "QUIVER":             "quiver",
    "SHIELD":             "shield",
    "CATALYST":           "catalyst",
    "AMULET":             "amulet",
    "RING":               "ring",
    "RELIC":              "relic",
    "IDOL_1x1_ETERRA":    "idol_1x1",
    "IDOL_1x1_LAGON":     "idol_1x1",
    "IDOL_2x1":           "idol_2x1",
    "IDOL_1x2":           "idol_1x2",
    "IDOL_3x1":           "idol_3x1",
    "IDOL_1x3":           "idol_1x3",
    "IDOL_4x1":           "idol_4x1",
    "IDOL_1x4":           "idol_1x4",
    "IDOL_2x2":           "idol_2x2",
}

with open(ITEMS_PATH) as f:
    data = json.load(f)

equippable = data.get("equippable", [])
mapping = {}  # baseTypeID → itemTypeId

for base_type in equippable:
    game_type = base_type.get("type", "")
    base_type_id = base_type.get("baseTypeID")
    item_type_id = GAME_TYPE_TO_ITEM_TYPE_ID.get(game_type)

    if base_type_id is not None and item_type_id:
        mapping[base_type_id] = (item_type_id, game_type)

lines = []
for base_type_id in sorted(mapping.keys()):
    item_type_id, game_type = mapping[base_type_id]
    lines.append(f'  {base_type_id}: "{item_type_id}",  // {game_type}')

output = f'''import type {{ ItemTypeId }} from "./itemTypeIds";

/**
 * Maps `baseTypeID` (from items.json equippable[].baseTypeID) to canonical
 * ItemTypeId slugs.
 *
 * IMPORTANT: Per-item `subTypeID` values are NOT globally unique — they restart
 * at 0 for each base type. Only `baseTypeID` is globally unique and safe to use
 * as a flat numeric key. Use GAME_TYPE_TO_ITEM_TYPE_ID for string-based lookups.
 *
 * Non-equipment base types (BLESSING=34, *_LENS=35-39) are omitted.
 */
export const SUBTYPE_ID_TO_ITEM_TYPE_ID: Record<number, ItemTypeId> = {{
{chr(10).join(lines)}
}};

export type BaseTypeId = keyof typeof SUBTYPE_ID_TO_ITEM_TYPE_ID;
'''

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    f.write(output)

print(f"✓ Generated SUBTYPE_ID_TO_ITEM_TYPE_ID.ts ({len(mapping)} entries)")
print(f"  Output: {OUTPUT_PATH}")
