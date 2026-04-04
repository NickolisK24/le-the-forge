"""
Maps baseTypeID (from items.json equippable[].baseTypeID) to canonical
item type ID slugs.

IMPORTANT: Per-item subTypeID values are NOT globally unique — they restart
at 0 for each base type. Only baseTypeID is globally unique and safe to use
as a flat numeric key. Use GAME_TYPE_TO_ITEM_TYPE_ID for string-based lookups.

Non-equipment base types (BLESSING=34, *_LENS=35-39) are omitted.
"""

BASE_TYPE_ID_TO_ITEM_TYPE_ID: dict[int, str] = {
    0:  "helm",      # HELMET
    1:  "chest",     # BODY_ARMOR
    2:  "belt",      # BELT
    3:  "boots",     # BOOTS
    4:  "gloves",    # GLOVES
    5:  "axe",       # ONE_HANDED_AXE
    6:  "dagger",    # ONE_HANDED_DAGGER
    7:  "mace",      # ONE_HANDED_MACES
    8:  "sceptre",   # ONE_HANDED_SCEPTRE
    9:  "sword",     # ONE_HANDED_SWORD
    10: "wand",      # WAND
    11: "fist",      # ONE_HANDED_FIST
    12: "axe",       # TWO_HANDED_AXE
    13: "mace",      # TWO_HANDED_MACE
    14: "polearm",   # TWO_HANDED_SPEAR
    15: "staff",     # TWO_HANDED_STAFF
    16: "sword",     # TWO_HANDED_SWORD
    17: "quiver",    # QUIVER
    18: "shield",    # SHIELD
    19: "catalyst",  # CATALYST
    20: "amulet",    # AMULET
    21: "ring",      # RING
    22: "relic",     # RELIC
    23: "bow",       # BOW
    24: "crossbow",  # CROSSBOW
    25: "idol_1x1",  # IDOL_1x1_ETERRA
    26: "idol_1x1",  # IDOL_1x1_LAGON
    27: "idol_2x1",  # IDOL_2x1
    28: "idol_1x2",  # IDOL_1x2
    29: "idol_3x1",  # IDOL_3x1
    30: "idol_1x3",  # IDOL_1x3
    31: "idol_4x1",  # IDOL_4x1
    32: "idol_1x4",  # IDOL_1x4
    33: "idol_2x2",  # IDOL_2x2
}
