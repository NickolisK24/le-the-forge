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
GET  /api/ref/crafting-rules      → FP cost ranges and instability gains from crafting_rules.json
"""

from flask import Blueprint, request, jsonify

from app.models import ItemType, AffixDef, PassiveNode
from app.game_data.game_data_loader import get_all_affixes, get_affix_categories
from app.engines.fp_engine import get_crafting_rules, get_all_fp_ranges, get_fp_range_by_rarity
from app.engines.base_engine import get_all_bases, get_fp_range
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
            "type": a["type"],
            "stat_key": a.get("stat_key", a["id"]),
            "tiers": a["tiers"],
            "applicable": a.get("applicable_to", []),
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

    # Craftable affix types only — skip idol/set/champion types
    CRAFTABLE_TYPES = ["prefix", "suffix", "experimental", "personal"]
    # Map old DB affix_type values to canonical prefix/suffix
    TYPE_NORMALIZE = {"experimental": "prefix", "personal": "prefix"}

    affixes = AffixDef.query.filter(
        AffixDef.affix_type.in_(CRAFTABLE_TYPES)
    ).order_by(AffixDef.name).all()

    if not affixes:
        # Static fallback from canonical JSON
        data = _get_affix_seed_data()
        if category:
            data = [a for a in data if a["type"] == category or category in a.get("tags", [])]
        if item_slot:
            data = [a for a in data if item_slot.lower() in [s.lower() for s in a.get("applicable_to", a.get("applicable", []))]]
        if class_req:
            data = [a for a in data if a.get("class_requirement") in (None, class_req)]
        if tag:
            data = [a for a in data if tag in a.get("tags", [])]
        return ok(data=data)

    result = []
    for a in affixes:
        if item_slot and item_slot.lower() not in [s.lower() for s in (a.applicable_types or [])]:
            continue
        if class_req and a.class_requirement and a.class_requirement != class_req:
            continue

        # Normalize type to prefix/suffix; keep original as a tag if experimental/personal
        raw_type = a.affix_type
        canonical_type = TYPE_NORMALIZE.get(raw_type, raw_type)
        tags = list(a.tags or [])
        if raw_type in TYPE_NORMALIZE and raw_type not in tags:
            tags.append(raw_type)

        if tag and tag not in tags:
            continue
        if category and category not in (canonical_type, raw_type) and category not in tags:
            continue

        # Convert tier_ranges dict {"1": [lo,hi]} to [{tier, min, max}] array
        tier_ranges = a.tier_ranges or {}
        tiers = sorted(
            [{"tier": int(k), "min": v[0], "max": v[1]} for k, v in tier_ranges.items()],
            key=lambda t: t["tier"],
        )
        result.append({
            "id": str(a.id),
            "name": a.name,
            "type": canonical_type,
            "applicable_to": a.applicable_types or [],
            "tiers": tiers,
            "tags": tags,
            "class_requirement": a.class_requirement,
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


@ref_bp.get("/crafting-rules")
def get_crafting_rules_endpoint():
    """Return FP cost ranges and instability gains. Source: data/crafting_rules.json."""
    return ok(data=get_crafting_rules())


@ref_bp.get("/base-items")
def get_base_items_endpoint():
    """Return all base item definitions including FP ranges. Source: data/base_items.json."""
    return ok(data=get_all_bases())


@ref_bp.get("/base-items/<base_type>")
def get_base_item_endpoint(base_type: str):
    """Return FP range and metadata for a specific base type."""
    try:
        bases = get_all_bases()
        key = base_type.lower()
        if key not in bases:
            return ok(data=None, status=404)
        lo, hi = get_fp_range(key)
        return ok(data={**bases[key], "min_fp": lo, "max_fp": hi, "base_type": key})
    except ValueError as e:
        return ok(data=None, status=400)


@ref_bp.get("/fp-ranges")
def get_fp_ranges_endpoint():
    """Return FP ranges by rarity. Source: data/forging_potential_ranges.json."""
    return ok(data=get_all_fp_ranges())


@ref_bp.get("/fp-ranges/<rarity>")
def get_fp_range_endpoint(rarity: str):
    """Return FP range for a specific rarity (+ optional ?ilvl= for Phase 2 tiers)."""
    try:
        item_level = int(request.args.get("ilvl", 84))
        lo, hi = get_fp_range_by_rarity(rarity, item_level)
        return ok(data={"rarity": rarity.lower(), "min_fp": lo, "max_fp": hi, "item_level": item_level})
    except ValueError as e:
        return ok(data={"error": str(e)}, status=400)
