"""
Game constants package for the Python/Flask layer.
Mirrors backend/src/constants/ for the Python layer.

Prefer importing from the domain module directly for clarity:
    from app.constants.defense import RES_CAP

Or import from this package for convenience:
    from app.constants import RES_CAP
"""

from app.constants.classes import BASE_CLASSES, CLASS_MASTERIES
from app.constants.damage_types import DAMAGE_TYPES
from app.constants.equipment_slots import EQUIPMENT_SLOTS
from app.constants.item_rarities import ITEM_RARITIES
from app.constants.item_type_ids import ITEM_TYPE_IDS
from app.constants.base_type_id_to_item_type_id import BASE_TYPE_ID_TO_ITEM_TYPE_ID
from app.constants.game_type_to_item_type_id import GAME_TYPE_TO_ITEM_TYPE_ID
from app.constants.item_type_to_slot import ITEM_TYPE_TO_SLOT
from app.constants.sub_type_id_to_item_type_id import SUBTYPE_ID_TO_ITEM_TYPE_ID
from app.constants.defense import (
    RES_CAP,
    WARD_BASE_DECAY_RATE,
    ENDURANCE_CAP,
    ARMOR_DIVISOR,
    DODGE_DIVISOR,
    BLOCK_DIVISOR,
    STUN_AVOIDANCE_DIVISOR,
    ENEMY_CRIT_RATE,
    ENEMY_CRIT_MULTIPLIER,
)
from app.constants.combat import (
    CRIT_CHANCE_CAP,
    BASE_CRIT_CHANCE,
    BASE_CRIT_MULTIPLIER,
    BLEED_BASE_RATIO,
    BLEED_DURATION,
    IGNITE_DPS_RATIO,
    IGNITE_DURATION,
    POISON_DPS_RATIO,
    POISON_DURATION,
)
from app.constants.crafting import (
    MAX_PREFIXES,
    MAX_SUFFIXES,
    PERFECT_ROLL_THRESHOLD,
    TARGET_TIER,
)
from app.constants.cache import REF_STATIC_CACHE_TTL, REF_SEMISTATIC_CACHE_TTL

__all__ = [
    # classes
    "BASE_CLASSES",
    "CLASS_MASTERIES",
    # damage_types
    "DAMAGE_TYPES",
    # equipment_slots
    "EQUIPMENT_SLOTS",
    # item_rarities
    "ITEM_RARITIES",
    # item_type_ids
    "ITEM_TYPE_IDS",
    # base_type_id_to_item_type_id
    "BASE_TYPE_ID_TO_ITEM_TYPE_ID",
    # game_type_to_item_type_id
    "GAME_TYPE_TO_ITEM_TYPE_ID",
    # item_type_to_slot
    "ITEM_TYPE_TO_SLOT",
    # sub_type_id_to_item_type_id
    "SUBTYPE_ID_TO_ITEM_TYPE_ID",
    # defense
    "RES_CAP",
    "WARD_BASE_DECAY_RATE",
    "ENDURANCE_CAP",
    "ARMOR_DIVISOR",
    "DODGE_DIVISOR",
    "BLOCK_DIVISOR",
    "STUN_AVOIDANCE_DIVISOR",
    "ENEMY_CRIT_RATE",
    "ENEMY_CRIT_MULTIPLIER",
    # combat
    "CRIT_CHANCE_CAP",
    "BASE_CRIT_CHANCE",
    "BASE_CRIT_MULTIPLIER",
    "BLEED_BASE_RATIO",
    "BLEED_DURATION",
    "IGNITE_DPS_RATIO",
    "IGNITE_DURATION",
    "POISON_DPS_RATIO",
    "POISON_DURATION",
    # crafting
    "MAX_PREFIXES",
    "MAX_SUFFIXES",
    "PERFECT_ROLL_THRESHOLD",
    "TARGET_TIER",
    # cache
    "REF_STATIC_CACHE_TTL",
    "REF_SEMISTATIC_CACHE_TTL",
]
