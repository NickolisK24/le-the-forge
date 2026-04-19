"""
Passives Blueprint — /api/passives

Read-only endpoints for passive tree data seeded from game exports.

GET /api/passives                         → All nodes; filterable via ?class= and ?mastery=
GET /api/passives/<character_class>       → Full tree for one class (base + all masteries)
GET /api/passives/<character_class>/<mastery> → Mastery-specific nodes + base class nodes

All responses share the same envelope:
  { "class": str|null, "mastery": str|null, "count": int, "nodes": [...] }
"""

import json
from pathlib import Path

from flask import Blueprint, current_app, request

from app.models import PassiveNode
from app.utils.responses import ok, error

passives_bp = Blueprint("passives", __name__)

_PASSIVES_JSON = Path(__file__).resolve().parents[3] / "data" / "classes" / "passives.json"


def _load_json_fallback(character_class: str | None = None, mastery: str | None = None) -> list[dict]:
    """Read passive nodes from the JSON export when the DB is empty."""
    with open(_PASSIVES_JSON, encoding="utf-8") as f:
        nodes: list[dict] = json.load(f)
    if character_class:
        nodes = [n for n in nodes if n.get("character_class") == character_class]
        if mastery:
            nodes = [n for n in nodes if n.get("mastery") == mastery or n.get("mastery") is None]
    return nodes

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

from app.constants import BASE_CLASSES, CLASS_MASTERIES

VALID_CLASSES = BASE_CLASSES
VALID_MASTERIES: dict[str, list[str]] = CLASS_MASTERIES


# ---------------------------------------------------------------------------
# Serialization helper
# ---------------------------------------------------------------------------

def _serialize(node: PassiveNode) -> dict:
    return {
        "id": node.id,
        "raw_node_id": node.raw_node_id,
        "character_class": node.character_class,
        "mastery": node.mastery,
        "mastery_index": node.mastery_index,
        "mastery_requirement": node.mastery_requirement,
        "name": node.name,
        "description": node.description,
        "node_type": node.node_type,
        "x": node.x,
        "y": node.y,
        "max_points": node.max_points,
        "connections": node.connections,
        "requires": node.requires or [],
        "stats": node.stats,
        "ability_granted": node.ability_granted,
        "icon": node.icon,
    }


def _nodes_response(nodes: list[PassiveNode], character_class=None, mastery=None) -> tuple:
    serialized = [_serialize(n) for n in nodes]
    if not serialized:
        # DB table empty — fall back to the JSON export so the page still works
        serialized = _load_json_fallback(character_class, mastery)

    # Group nodes by tree section (base vs each mastery)
    grouped: dict[str, list[dict]] = {}
    for n in serialized:
        key = n.get("mastery") or "__base__"
        grouped.setdefault(key, []).append(n)

    return ok(data={
        "class": character_class,
        "mastery": mastery,
        "count": len(serialized),
        "nodes": serialized,
        "grouped": grouped,
    })


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@passives_bp.get("")
def list_passives():
    """
    Return all passive nodes, optionally filtered by ?class= and/or ?mastery=.

    When ?mastery= is supplied without ?class= it is ignored (mastery names are
    not globally unique — they require a class for context).
    """
    cls = request.args.get("class")
    mastery = request.args.get("mastery")

    if cls and cls not in VALID_CLASSES:
        return error(f"Unknown class: {cls}")

    if mastery and cls:
        if mastery not in VALID_MASTERIES.get(cls, []):
            return error(f"Unknown mastery '{mastery}' for class {cls}")

    q = PassiveNode.query
    if cls:
        q = q.filter_by(character_class=cls)
        if mastery:
            # mastery-specific nodes + base class nodes (mastery IS NULL)
            q = q.filter(
                (PassiveNode.mastery == mastery) | (PassiveNode.mastery.is_(None))
            )
    try:
        nodes = q.order_by(PassiveNode.mastery_index, PassiveNode.raw_node_id).all()
    except Exception:
        current_app.logger.exception("DB query failed in list_passives")
        nodes = []
    return _nodes_response(nodes, character_class=cls, mastery=mastery)


@passives_bp.get("/<character_class>")
def get_class_tree(character_class: str):
    """Return the full passive tree for one class (base nodes + all three masteries)."""
    if character_class not in VALID_CLASSES:
        return error(f"Unknown class: {character_class}")

    try:
        nodes = (
            PassiveNode.query
            .filter_by(character_class=character_class)
            .order_by(PassiveNode.mastery_index, PassiveNode.raw_node_id)
            .all()
        )
    except Exception:
        current_app.logger.exception("DB query failed in get_class_tree")
        nodes = []
    return _nodes_response(nodes, character_class=character_class)


@passives_bp.get("/<character_class>/<mastery>")
def get_mastery_tree(character_class: str, mastery: str):
    """
    Return mastery-specific nodes plus base class nodes (mastery IS NULL).
    This is the minimal set needed to render a single mastery panel.
    """
    if character_class not in VALID_CLASSES:
        return error(f"Unknown class: {character_class}")

    if mastery not in VALID_MASTERIES.get(character_class, []):
        return error(f"Unknown mastery '{mastery}' for class {character_class}")

    try:
        nodes = (
            PassiveNode.query
            .filter_by(character_class=character_class)
            .filter(
                (PassiveNode.mastery == mastery) | (PassiveNode.mastery.is_(None))
            )
            .order_by(PassiveNode.mastery_index, PassiveNode.raw_node_id)
            .all()
        )
    except Exception:
        current_app.logger.exception("DB query failed in get_mastery_tree")
        nodes = []
    return _nodes_response(nodes, character_class=character_class, mastery=mastery)
