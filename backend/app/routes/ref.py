"""
Reference Data Blueprint — /api/ref

Read-only endpoints that serve game data (seeded, not user-created).
These are heavily cacheable — in production, add a Redis cache layer
or serve them from a CDN-backed static JSON file.

GET  /api/ref/item-types          → All item type definitions
GET  /api/ref/affixes             → All affix definitions (filterable by type/slot)
GET  /api/ref/passives            → Passive tree nodes (filterable by class/mastery)
GET  /api/ref/skills              → Skill definitions (filterable by class)
GET  /api/ref/classes             → Class + mastery metadata
"""

from flask import Blueprint, request, jsonify

from app.models import ItemType, AffixDef, PassiveNode
from app.utils.responses import ok

ref_bp = Blueprint("ref", __name__)


# ---------------------------------------------------------------------------
# Static class metadata (no DB needed)
# ---------------------------------------------------------------------------

CLASS_META = {
    "Acolyte": {
        "color": "#9a7ac8",
        "masteries": ["Necromancer", "Lich", "Warlock"],
        "skills": [
            "Summon Skeleton", "Bone Curse", "Transplant",
            "Rip Blood", "Marrow Shards",
        ],
    },
    "Mage": {
        "color": "#6a9ec8",
        "masteries": ["Runemaster", "Sorcerer", "Spellblade"],
        "skills": [
            "Glacier", "Fireball", "Shatter Strike",
            "Mana Strike", "Teleport",
        ],
    },
    "Primalist": {
        "color": "#7cb87a",
        "masteries": ["Druid", "Beastmaster", "Shaman"],
        "skills": [
            "Summon Wolf", "Warcry", "Entangling Roots",
            "Avalanche", "Serpent Strike",
        ],
    },
    "Sentinel": {
        "color": "#e8891a",
        "masteries": ["Forge Guard", "Paladin", "Void Knight"],
        "skills": [
            "Lunge", "Rive", "Warpath",
            "Shield Rush", "Volatile Reversal",
        ],
    },
    "Rogue": {
        "color": "#e05050",
        "masteries": ["Bladedancer", "Marksman", "Falconer"],
        "skills": [
            "Shift", "Flurry", "Puncture",
            "Shadow Cascade", "Smoke Bomb",
        ],
    },
}

AFFIX_SEED_DATA = [
    # --- Damage prefixes ---
    {"name": "Spell Damage",         "type": "prefix", "stat_key": "spell_damage_pct",
     "tiers": {"T1": [1, 7], "T2": [8, 15], "T3": [16, 25], "T4": [26, 38], "T5": [39, 55]},
     "applicable": ["Wand", "Staff", "Helm", "Chest"]},
    {"name": "Necrotic Damage",      "type": "prefix", "stat_key": "necrotic_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Wand", "Staff", "Amulet"]},
    {"name": "Fire Damage",          "type": "prefix", "stat_key": "fire_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Wand", "Staff", "Amulet"]},
    {"name": "Cold Damage",          "type": "prefix", "stat_key": "cold_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Wand", "Staff", "Amulet"]},
    {"name": "Lightning Damage",     "type": "prefix", "stat_key": "lightning_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Wand", "Staff", "Amulet"]},
    {"name": "Physical Damage",      "type": "prefix", "stat_key": "physical_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Axe", "Sword", "Mace", "Dagger", "Bow", "Amulet"]},
    {"name": "Void Damage",          "type": "prefix", "stat_key": "void_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Wand", "Staff", "Amulet"]},
    {"name": "Poison Damage",        "type": "prefix", "stat_key": "poison_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Dagger", "Bow", "Amulet"]},
    {"name": "Minion Damage",        "type": "prefix", "stat_key": "minion_damage_pct",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 49], "T4": [50, 69], "T5": [70, 90]},
     "applicable": ["Wand", "Staff", "Helm", "Amulet"]},
    # --- Speed prefixes ---
    {"name": "Cast Speed",           "type": "prefix", "stat_key": "cast_speed",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 14], "T4": [15, 19], "T5": [20, 25]},
     "applicable": ["Wand", "Staff", "Sceptre"]},
    {"name": "Attack Speed",         "type": "prefix", "stat_key": "attack_speed_pct",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 14], "T4": [15, 19], "T5": [20, 25]},
     "applicable": ["Axe", "Sword", "Dagger", "Bow", "Gloves"]},
    # --- Defense prefixes ---
    {"name": "Health",               "type": "prefix", "stat_key": "max_health",
     "tiers": {"T1": [20, 35], "T2": [36, 55], "T3": [56, 80], "T4": [81, 110], "T5": [111, 150]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet"]},
    {"name": "Armour",               "type": "prefix", "stat_key": "armour",
     "tiers": {"T1": [40, 79], "T2": [80, 129], "T3": [130, 199], "T4": [200, 299], "T5": [300, 420]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Shield"]},
    {"name": "Ward",                 "type": "prefix", "stat_key": "ward",
     "tiers": {"T1": [5, 14], "T2": [15, 29], "T3": [30, 49], "T4": [50, 79], "T5": [80, 120]},
     "applicable": ["Helm", "Chest", "Amulet", "Ring"]},
    {"name": "Endurance",            "type": "prefix", "stat_key": "max_health",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 54], "T4": [55, 79], "T5": [80, 110]},
     "applicable": ["Belt", "Boots"]},
    # --- Resistance suffixes ---
    {"name": "Fire Resistance",      "type": "suffix", "stat_key": "fire_res",
     "tiers": {"T1": [12, 19], "T2": [20, 29], "T3": [30, 39], "T4": [40, 49], "T5": [50, 60]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet", "Shield"]},
    {"name": "Cold Resistance",      "type": "suffix", "stat_key": "cold_res",
     "tiers": {"T1": [12, 19], "T2": [20, 29], "T3": [30, 39], "T4": [40, 49], "T5": [50, 60]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet", "Shield"]},
    {"name": "Lightning Resistance", "type": "suffix", "stat_key": "lightning_res",
     "tiers": {"T1": [12, 19], "T2": [20, 29], "T3": [30, 39], "T4": [40, 49], "T5": [50, 60]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet", "Shield"]},
    {"name": "Void Resistance",      "type": "suffix", "stat_key": "void_res",
     "tiers": {"T1": [12, 19], "T2": [20, 29], "T3": [30, 39], "T4": [40, 49], "T5": [50, 60]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet", "Shield"]},
    {"name": "Necrotic Resistance",  "type": "suffix", "stat_key": "necrotic_res",
     "tiers": {"T1": [12, 19], "T2": [20, 29], "T3": [30, 39], "T4": [40, 49], "T5": [50, 60]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet", "Shield"]},
    {"name": "Poison Resistance",    "type": "suffix", "stat_key": "poison_res",
     "tiers": {"T1": [12, 19], "T2": [20, 29], "T3": [30, 39], "T4": [40, 49], "T5": [50, 60]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots", "Belt", "Ring", "Amulet", "Shield"]},
    # --- Defense suffixes ---
    {"name": "Ward Retention",       "type": "suffix", "stat_key": "ward_retention_pct",
     "tiers": {"T1": [5, 9], "T2": [10, 14], "T3": [15, 19], "T4": [20, 24], "T5": [25, 30]},
     "applicable": ["Helm", "Chest", "Ring", "Amulet"]},
    {"name": "Dodge Rating",         "type": "suffix", "stat_key": "dodge_rating",
     "tiers": {"T1": [25, 49], "T2": [50, 79], "T3": [80, 119], "T4": [120, 179], "T5": [180, 260]},
     "applicable": ["Helm", "Chest", "Gloves", "Boots"]},
    # --- Crit suffixes ---
    {"name": "Critical Strike Chance",     "type": "suffix", "stat_key": "crit_chance_pct",
     "tiers": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 8], "T5": [9, 12]},
     "applicable": ["Wand", "Dagger", "Sword", "Axe", "Ring", "Amulet"]},
    {"name": "Critical Strike Multiplier", "type": "suffix", "stat_key": "crit_multiplier_pct",
     "tiers": {"T1": [3, 7], "T2": [8, 14], "T3": [15, 24], "T4": [25, 39], "T5": [40, 60]},
     "applicable": ["Ring", "Amulet", "Gloves"]},
    # --- Attribute suffixes ---
    {"name": "Strength",     "type": "suffix", "stat_key": "strength",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 13], "T4": [14, 17], "T5": [18, 24]},
     "applicable": ["Helm", "Gloves", "Ring", "Amulet", "Belt"]},
    {"name": "Intelligence", "type": "suffix", "stat_key": "intelligence",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 13], "T4": [14, 17], "T5": [18, 24]},
     "applicable": ["Helm", "Gloves", "Ring", "Amulet", "Belt"]},
    {"name": "Dexterity",    "type": "suffix", "stat_key": "dexterity",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 13], "T4": [14, 17], "T5": [18, 24]},
     "applicable": ["Helm", "Gloves", "Ring", "Amulet", "Belt"]},
    {"name": "Vitality",     "type": "suffix", "stat_key": "vitality",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 13], "T4": [14, 17], "T5": [18, 24]},
     "applicable": ["Helm", "Gloves", "Ring", "Amulet", "Belt"]},
    {"name": "Attunement",   "type": "suffix", "stat_key": "attunement",
     "tiers": {"T1": [3, 5], "T2": [6, 9], "T3": [10, 13], "T4": [14, 17], "T5": [18, 24]},
     "applicable": ["Helm", "Gloves", "Ring", "Amulet", "Belt"]},
    # --- Resource suffixes ---
    {"name": "Mana",         "type": "suffix", "stat_key": "max_mana",
     "tiers": {"T1": [10, 19], "T2": [20, 34], "T3": [35, 54], "T4": [55, 79], "T5": [80, 110]},
     "applicable": ["Helm", "Amulet", "Ring", "Belt"]},
    {"name": "Mana Regen",   "type": "suffix", "stat_key": "mana_regen",
     "tiers": {"T1": [1, 2], "T2": [3, 4], "T3": [5, 6], "T4": [7, 9], "T5": [10, 15]},
     "applicable": ["Helm", "Amulet", "Ring", "Belt"]},
    {"name": "Health Regen", "type": "suffix", "stat_key": "health_regen",
     "tiers": {"T1": [1, 2], "T2": [3, 5], "T3": [6, 9], "T4": [10, 14], "T5": [15, 25]},
     "applicable": ["Helm", "Chest", "Belt", "Amulet"]},
]


@ref_bp.get("/classes")
def get_classes():
    return ok(data=CLASS_META)


@ref_bp.get("/item-types")
def get_item_types():
    item_types = ItemType.query.order_by(ItemType.category, ItemType.name).all()
    if not item_types:
        # Return static fallback if DB not seeded yet
        return ok(data=[
            {"name": n, "category": c} for n, c in [
                ("Wand", "weapon"), ("Staff", "weapon"), ("Sword", "weapon"),
                ("Axe", "weapon"), ("Dagger", "weapon"), ("Mace", "weapon"),
                ("Sceptre", "weapon"), ("Bow", "weapon"),
                ("Shield", "off_hand"),
                ("Helm", "armour"), ("Chest", "armour"), ("Gloves", "armour"),
                ("Boots", "armour"),
                ("Belt", "accessory"), ("Ring", "accessory"), ("Amulet", "accessory"),
            ]
        ])
    return ok(data=[
        {"id": it.id, "name": it.name, "category": it.category,
         "base_implicit": it.base_implicit}
        for it in item_types
    ])


@ref_bp.get("/affixes")
def get_affixes():
    affix_type = request.args.get("type")   # "prefix" | "suffix"
    item_slot = request.args.get("slot")    # "Wand", "Helm", etc.

    affixes = AffixDef.query
    if affix_type:
        affixes = affixes.filter_by(affix_type=affix_type)
    affixes = affixes.order_by(AffixDef.name).all()

    if not affixes:
        # Static fallback
        data = AFFIX_SEED_DATA
        if affix_type:
            data = [a for a in data if a["type"] == affix_type]
        if item_slot:
            data = [a for a in data if item_slot in a.get("applicable", [])]
        return ok(data=data)

    result = []
    for a in affixes:
        if item_slot and item_slot not in (a.applicable_types or []):
            continue
        result.append({
            "id": a.id,
            "name": a.name,
            "type": a.affix_type,
            "stat_key": a.stat_key,
            "tier_ranges": a.tier_ranges,
            "applicable_types": a.applicable_types,
        })
    return ok(data=result)


@ref_bp.get("/passives")
def get_passives():
    char_class = request.args.get("class")
    mastery = request.args.get("mastery")

    q = PassiveNode.query
    if char_class:
        q = q.filter_by(character_class=char_class)
    if mastery:
        q = q.filter(
            (PassiveNode.mastery == mastery) | (PassiveNode.mastery.is_(None))
        )

    nodes = q.all()
    return ok(data=[
        {
            "id": n.id,
            "name": n.name,
            "description": n.description,
            "node_type": n.node_type,
            "x": n.x,
            "y": n.y,
            "max_points": n.max_points,
            "connections": n.connections,
            "mastery": n.mastery,
        }
        for n in nodes
    ])


@ref_bp.get("/skills")
def get_skills():
    char_class = request.args.get("class")
    if char_class and char_class in CLASS_META:
        return ok(data={
            "class": char_class,
            "skills": CLASS_META[char_class]["skills"],
        })
    all_skills = {}
    for cls, meta in CLASS_META.items():
        all_skills[cls] = meta["skills"]
    return ok(data=all_skills)
