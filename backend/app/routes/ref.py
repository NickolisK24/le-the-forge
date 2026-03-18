"""
Reference Data Blueprint — /api/ref

Read-only endpoints that serve game data (seeded, not user-created).
These are heavily cacheable — in production, add a Redis cache layer
or serve them from a CDN-backed static JSON file.

GET  /api/ref/item-types          → All item type definitions
GET  /api/ref/affixes             → All affix definitions (filterable by category/slot/class/tags)
GET  /api/ref/passives            → Passive tree nodes (filterable by class/mastery)
GET  /api/ref/skills              → Skill definitions (filterable by class)
GET  /api/ref/classes             → Class + mastery metadata
GET  /api/ref/affix-categories    → Available affix category descriptions
"""

from flask import Blueprint, request, jsonify

from app.models import ItemType, AffixDef, PassiveNode
from app.game_data.game_data_loader import get_all_affixes, get_affix_categories
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

def _get_affix_seed_data() -> list[dict]:
    """Build seed-compatible dicts from the canonical affixes.json."""
    return [
        {
            "id": a["id"],
            "name": a["name"],
            "type": a["category"],
            "modifier_type": a.get("type", "flat"),
            "stat": a.get("stat", a.get("stat_key", "")),
            "tiers": a["tiers"],
            "applicable": a.get("applicable", []),
            "class_requirement": a.get("class_requirement"),
            "tags": a.get("tags", []),
        }
        for a in get_all_affixes()
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
    category = request.args.get("category") or request.args.get("type")
    item_slot = request.args.get("slot")
    class_req = request.args.get("class")
    tag = request.args.get("tag")

    affixes = AffixDef.query
    if category:
        affixes = affixes.filter_by(affix_type=category)
    affixes = affixes.order_by(AffixDef.name).all()

    if not affixes:
        # Static fallback from canonical JSON
        data = _get_affix_seed_data()
        if category:
            data = [a for a in data if a["type"] == category]
        if item_slot:
            data = [a for a in data if item_slot in a.get("applicable", [])]
        if class_req:
            data = [a for a in data if a.get("class_requirement") in (None, class_req)]
        if tag:
            data = [a for a in data if tag in a.get("tags", [])]
        return ok(data=data)

    result = []
    for a in affixes:
        if item_slot and item_slot not in (a.applicable_types or []):
            continue
        if class_req and a.class_requirement and a.class_requirement != class_req:
            continue
        if tag and tag not in (a.tags or []):
            continue
        result.append({
            "id": a.id,
            "name": a.name,
            "type": a.affix_type,
            "stat_key": a.stat_key,
            "tier_ranges": a.tier_ranges,
            "applicable_types": a.applicable_types,
            "class_requirement": a.class_requirement,
            "tags": a.tags,
        })
    return ok(data=result)


@ref_bp.get("/affix-categories")
def get_affix_categories_endpoint():
    return ok(data=get_affix_categories())


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
