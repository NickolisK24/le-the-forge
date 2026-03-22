"""
Admin Blueprint — /api/admin

Endpoints for managing game data files directly.
These are NOT protected by auth in dev; add auth middleware before shipping prod.

GET   /api/admin/affixes          → all affixes from affixes.json
PATCH /api/admin/affixes/<id>     → update one affix by id
"""

import json
import os
from pathlib import Path

from flask import Blueprint, request, jsonify

from app.utils.responses import ok

admin_bp = Blueprint("admin", __name__)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
AFFIXES_PATH = DATA_DIR / "affixes.json"


def _load_affixes() -> list:
    with open(AFFIXES_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_affixes(affixes: list) -> None:
    with open(AFFIXES_PATH, "w", encoding="utf-8") as f:
        json.dump(affixes, f, indent=2, ensure_ascii=False)


@admin_bp.get("/affixes")
def list_affixes():
    """Return all affixes, optionally filtered by name/type/tag."""
    affixes = _load_affixes()

    q = (request.args.get("q") or "").lower().strip()
    type_filter = request.args.get("type", "").lower()
    tag_filter = request.args.get("tag", "").lower()
    slot_filter = request.args.get("slot", "").lower()

    if q:
        affixes = [
            a for a in affixes
            if q in a.get("name", "").lower()
            or q in a.get("id", "").lower()
            or q in (a.get("stat_key") or "").lower()
        ]
    if type_filter:
        affixes = [a for a in affixes if a.get("type", "") == type_filter]
    if tag_filter:
        affixes = [a for a in affixes if tag_filter in (a.get("tags") or [])]
    if slot_filter:
        affixes = [a for a in affixes if slot_filter in (a.get("applicable_to") or [])]

    return ok(affixes, meta={"total": len(affixes)})


@admin_bp.patch("/affixes/<affix_id>")
def update_affix(affix_id: str):
    """Update a single affix by its id field. Writes directly to affixes.json."""
    payload = request.get_json(force=True, silent=True) or {}
    if not payload:
        return jsonify({"errors": [{"message": "Empty payload"}]}), 400

    affixes = _load_affixes()
    idx = next((i for i, a in enumerate(affixes) if a.get("id") == affix_id), None)

    if idx is None:
        return jsonify({"errors": [{"message": f"Affix '{affix_id}' not found"}]}), 404

    # Allowlist of editable fields
    allowed = {"name", "type", "tags", "applicable_to", "class_requirement", "tiers", "stat_key"}
    for key, val in payload.items():
        if key in allowed:
            affixes[idx][key] = val

    _save_affixes(affixes)
    return ok(affixes[idx])
