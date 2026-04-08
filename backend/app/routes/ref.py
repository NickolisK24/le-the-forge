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
GET  /api/ref/crafting-rules      → FP cost ranges from crafting_rules.json
"""

from flask import Blueprint, current_app, request, jsonify

from app.constants.cache import REF_STATIC_CACHE_TTL, REF_SEMISTATIC_CACHE_TTL
from app.models import ItemType, AffixDef, PassiveNode
from app.game_data.game_data_loader import get_all_affixes, get_affix_categories
from app.engines.fp_engine import get_crafting_rules, get_all_fp_ranges, get_fp_range_by_rarity
from app.engines.base_engine import get_all_bases, get_bases_for_slot, get_fp_range
from app.utils.responses import ok, error, not_found
from app.utils.cache import cached_route, delete_pattern

ref_bp = Blueprint("ref", __name__)


# ---------------------------------------------------------------------------
# Slot name normalization — maps frontend-friendly names to DB values
# ---------------------------------------------------------------------------
# Frontend/UI may use human-readable names (helmet, chest, boots) while the
# database applicable_to arrays use game-internal names (helm, chest, feet).
# This mapping is applied at the API boundary so callers can use either form.

_SLOT_ALIASES: dict[str, list[str]] = {
    # Frontend name  →  DB applicable_to values to match against
    "helmet":         ["helm"],
    "head":           ["helm"],
    "body":           ["chest"],
    "feet":           ["boots"],
    "hands":          ["gloves"],
    "neck":           ["amulet"],
    "finger":         ["ring"],
    "waist":          ["belt"],
    "weapon":         ["sword_1h", "sword_2h", "axe_1h", "axe_2h", "mace_1h", "mace_2h",
                       "dagger", "sceptre", "wand", "staff", "bow", "polearm", "spear",
                       "crossbow", "fist"],
    "offhand":        ["shield", "quiver", "catalyst"],
    "off_hand":       ["shield", "quiver", "catalyst"],
    "idol":           ["idol", "idol_1x1_eterra", "idol_1x1_lagon", "idol_1x2", "idol_1x3",
                       "idol_1x4", "idol_2x1", "idol_2x2", "idol_3x1", "idol_4x1"],
}


def _normalize_slot(raw_slot: str) -> list[str]:
    """Convert a frontend slot name to a list of DB applicable_to values.

    If the slot is already a valid DB value, returns it as a single-item list.
    If it's an alias, returns all mapped DB values.
    """
    key = raw_slot.strip().lower()
    if key in _SLOT_ALIASES:
        return _SLOT_ALIASES[key]
    # Already a DB value — return as-is
    return [key]


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
    """Build seed-compatible dicts directly from the canonical affixes.json.

    Reads the raw JSON so we get every field (tags, class_requirement, id,
    modifier_type, applicable_to) without depending on the ORM or domain layer.
    """
    import json
    from pathlib import Path

    affixes_path = Path(__file__).resolve().parents[3] / "data" / "items" / "affixes.json"
    with open(affixes_path, encoding="utf-8") as f:
        raw_list: list[dict] = json.load(f)

    # Normalize experimental/personal → prefix to match the DB path
    type_normalize = {"experimental": "prefix", "personal": "prefix"}
    result = []
    for a in raw_list:
        raw_type = a.get("type", "")
        if raw_type not in ("prefix", "suffix", "experimental", "personal"):
            continue
        canonical_type = type_normalize.get(raw_type, raw_type)
        tags = list(a.get("tags", []))
        if raw_type in type_normalize and raw_type not in tags:
            tags.append(raw_type)
        result.append({
            "id": a.get("id", a.get("affix_id", a.get("name", ""))),
            "name": a.get("name", ""),
            "type": canonical_type,
            "stat_key": a.get("stat_key", ""),
            "tiers": a.get("tiers", []),
            "applicable_to": a.get("applicable_to", []),
            "class_requirement": a.get("class_requirement"),
            "tags": tags,
        })
    return result


@ref_bp.get("/classes")
@cached_route("ref:classes", ttl=REF_STATIC_CACHE_TTL)
def get_classes():
    return ok(data=CLASS_META)


@ref_bp.get("/item-types")
@cached_route("ref:item-types", ttl=REF_STATIC_CACHE_TTL)
def get_item_types():
    try:
        item_types = ItemType.query.order_by(ItemType.category, ItemType.name).all()
    except Exception:
        current_app.logger.exception("DB query failed in get_item_types")
        item_types = []
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
@cached_route("ref:affixes", ttl=REF_SEMISTATIC_CACHE_TTL)
def get_affixes():
    try:
        return _get_affixes_inner()
    except Exception:
        current_app.logger.exception("Unhandled error in get_affixes — falling back to JSON")
        try:
            return ok(data=_get_affix_seed_data())
        except Exception:
            current_app.logger.exception("JSON fallback also failed in get_affixes")
            return ok(data=[])


def _get_affixes_inner():
    category = request.args.get("category") or request.args.get("type")
    item_slot = request.args.get("slot")
    class_req = request.args.get("class")
    tag = request.args.get("tag")

    # Craftable affix types only — skip idol/set/champion types
    CRAFTABLE_TYPES = ["prefix", "suffix", "experimental", "personal"]
    # Map old DB affix_type values to canonical prefix/suffix
    TYPE_NORMALIZE = {"experimental": "prefix", "personal": "prefix"}

    try:
        affixes = AffixDef.query.filter(
            AffixDef.affix_type.in_(CRAFTABLE_TYPES)
        ).order_by(AffixDef.name).all()
    except Exception:
        current_app.logger.exception("DB query failed in get_affixes")
        affixes = []

    # Normalize slot parameter to DB vocabulary
    slot_matches = _normalize_slot(item_slot) if item_slot else []

    if not affixes:
        # Static fallback from canonical JSON
        data = _get_affix_seed_data()
        if category:
            data = [a for a in data if a["type"] == category or category in a.get("tags", [])]
        if slot_matches:
            data = [a for a in data if any(
                s.lower() in slot_matches for s in a.get("applicable_to", [])
            )]
        if class_req:
            data = [a for a in data if a.get("class_requirement") in (None, class_req)]
        if tag:
            data = [a for a in data if tag in a.get("tags", [])]
        return ok(data=data)

    result = []
    for a in affixes:
        if slot_matches and not any(
            s.lower() in slot_matches for s in (a.applicable_types or [])
        ):
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
            "stat_key": a.stat_key or "",
            "applicable_to": a.applicable_types or [],
            "tiers": tiers,
            "tags": tags,
            "class_requirement": a.class_requirement,
        })
    return ok(data=result)


@ref_bp.get("/affix-categories")
@cached_route("ref:affix-categories", ttl=REF_STATIC_CACHE_TTL)
def get_affix_categories_endpoint():
    return ok(data=get_affix_categories())


@ref_bp.get("/passives")
@cached_route("ref:passives", ttl=REF_SEMISTATIC_CACHE_TTL)
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
@cached_route("ref:skills", ttl=REF_STATIC_CACHE_TTL)
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
@cached_route("ref:crafting-rules", ttl=REF_STATIC_CACHE_TTL)
def get_crafting_rules_endpoint():
    """Return FP cost ranges. Source: data/crafting_rules.json."""
    return ok(data=get_crafting_rules())


@ref_bp.get("/base-items")
def get_base_items_endpoint():
    """
    Return base item definitions.

    ?slot=helmet   → flat list of named items for that slot
    ?slot=weapon   → merged list across all weapon slots
    ?slot=offhand  → merged list across shield/quiver/catalyst
    (no param)     → full dict keyed by slot category
    """
    slot = request.args.get("slot", "").strip().lower()
    if slot:
        expanded = _SLOT_CATEGORIES.get(slot)
        if expanded:
            all_bases = get_all_bases()
            items = []
            for s in expanded:
                items.extend(all_bases.get(s, []))
        else:
            # Try normalized slot names, then fall back to direct lookup
            all_bases = get_all_bases()
            normalized = _normalize_slot(slot)
            items = []
            for s in normalized:
                items.extend(all_bases.get(s, []))
            if not items:
                items = get_bases_for_slot(slot)
        return ok(data=items)
    return ok(data=get_all_bases())


@ref_bp.get("/base-items/<base_type>")
def get_base_item_endpoint(base_type: str):
    """Return all named base items for a specific slot category."""
    key = base_type.lower()
    items = get_bases_for_slot(key)
    if not items:
        return ok(data=None, status=404)
    return ok(data=items)


@ref_bp.get("/fp-ranges")
@cached_route("ref:fp-ranges", ttl=REF_STATIC_CACHE_TTL)
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
        return error(str(e), status=400)


# ---------------------------------------------------------------------------
# New dataset endpoints
# ---------------------------------------------------------------------------

@ref_bp.get("/enemy-profiles")
@cached_route("ref:enemy-profiles", ttl=REF_STATIC_CACHE_TTL)
def get_enemy_profiles_endpoint():
    """Return all enemy profiles from data/enemy_profiles.json."""
    from app.game_data.game_data_loader import get_enemy_profiles
    return ok(data=[e.to_dict() for e in get_enemy_profiles()])


@ref_bp.get("/enemy-profiles/<enemy_id>")
def get_enemy_profile_endpoint(enemy_id: str):
    """Return a single enemy profile by id."""
    from app.game_data.game_data_loader import get_enemy_profile
    profile = get_enemy_profile(enemy_id)
    if not profile:
        return not_found(f"Enemy profile '{enemy_id}'")
    return ok(data=profile.to_dict())


@ref_bp.get("/damage-types")
@cached_route("ref:damage-types", ttl=REF_STATIC_CACHE_TTL)
def get_damage_types_endpoint():
    """Return all damage type definitions from data/damage_types.json."""
    from app.game_data.game_data_loader import get_damage_types
    return ok(data=get_damage_types())


@ref_bp.get("/rarities")
@cached_route("ref:rarities", ttl=REF_STATIC_CACHE_TTL)
def get_rarities_endpoint():
    """Return all rarity tier definitions from data/rarities.json."""
    from app.game_data.game_data_loader import get_rarities
    return ok(data=get_rarities())


@ref_bp.get("/implicit-stats")
@cached_route("ref:implicit-stats", ttl=REF_STATIC_CACHE_TTL)
def get_implicit_stats_endpoint():
    """Return all implicit stat definitions keyed by item type."""
    from app.game_data.game_data_loader import get_all_implicit_stats
    return ok(data=get_all_implicit_stats())


@ref_bp.get("/implicit-stats/<item_type>")
def get_implicit_stat_endpoint(item_type: str):
    """Return implicit stat for a specific item type."""
    from app.game_data.game_data_loader import get_implicit_stat
    stat = get_implicit_stat(item_type.lower())
    if stat is None:
        return ok(data=None)
    return ok(data=stat)


# ---------------------------------------------------------------------------
# Unique items
# ---------------------------------------------------------------------------


# Meta-slot categories for the paper-doll picker
_WEAPON_SLOTS = frozenset([
    "sword", "axe", "mace", "dagger", "sceptre",
    "wand", "staff", "bow", "two_handed_spear",
])
_OFFHAND_SLOTS = frozenset(["shield", "quiver", "catalyst"])
_IDOL_SLOTS = frozenset([
    "idol_1x1_eterra", "idol_1x3", "idol_1x4", "idol_2x2",
])
_SLOT_CATEGORIES: dict = {
    "weapon":  _WEAPON_SLOTS,
    "offhand": _OFFHAND_SLOTS,
    "idol":    _IDOL_SLOTS,
}


@ref_bp.get("/uniques")
@cached_route("ref:uniques", ttl=REF_STATIC_CACHE_TTL)
def get_uniques_endpoint():
    """
    GET /api/ref/uniques
    Optional query params:
      ?slot=helmet       — exact slot name, OR meta-category:
                           weapon  → all 1H/2H weapon slots
                           offhand → shield, quiver, catalyst
                           idol    → all idol sizes
      ?q=exsang          — case-insensitive name/tag search
    """
    from app.game_data.game_data_loader import get_all_uniques
    uniques = get_all_uniques()

    slot = request.args.get("slot", "").strip().lower()
    query = request.args.get("q", "").strip().lower()

    if slot:
        expanded = _SLOT_CATEGORIES.get(slot)
        if expanded:
            slot_set = expanded
        else:
            slot_set = frozenset(_normalize_slot(slot))
        uniques = [u for u in uniques if u.get("slot", "").lower() in slot_set]

    if query:
        uniques = [
            u for u in uniques
            if query in u.get("name", "").lower()
            or any(query in t.lower() for t in u.get("tags", []))
        ]

    return ok(data=uniques)


@ref_bp.get("/uniques/<slug>")
def get_unique_endpoint(slug: str):
    """Return a single unique item by slug."""
    from app.game_data.game_data_loader import get_unique_by_id
    item = get_unique_by_id(slug)
    if item is None:
        return not_found(f"Unique '{slug}'")
    return ok(data=item)
