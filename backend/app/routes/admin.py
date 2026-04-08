"""
Admin Blueprint — /api/admin

Endpoints for managing game data files and monitoring.

GET   /api/admin/affixes            → all affixes from affixes.json
PATCH /api/admin/affixes/<id>       → update one affix by id
GET   /api/admin/import-failures    → paginated import failure log (admin only)
"""

import json
import os
from pathlib import Path

from flask import Blueprint, request

from app import db, limiter
from app.models import ImportFailure
from app.utils.auth import login_required, get_current_user
from app.utils.responses import ok, error, not_found, forbidden, paginate_meta

admin_bp = Blueprint("admin", __name__)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
AFFIXES_PATH = DATA_DIR / "items" / "affixes.json"


def _load_affixes() -> list:
    try:
        with open(AFFIXES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


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
@limiter.limit("30 per minute")
def update_affix(affix_id: str):
    """Update a single affix by its id field. Writes directly to affixes.json."""
    payload = request.get_json(force=True, silent=True) or {}
    if not payload:
        return error("Empty payload", status=400)

    affixes = _load_affixes()
    idx = next((i for i, a in enumerate(affixes) if a.get("id") == affix_id), None)

    if idx is None:
        return not_found(f"Affix '{affix_id}'")

    # Allowlist of editable fields
    allowed = {"name", "type", "tags", "applicable_to", "class_requirement", "tiers", "stat_key"}
    for key, val in payload.items():
        if key in allowed:
            affixes[idx][key] = val

    _save_affixes(affixes)
    return ok(affixes[idx])


# ---------------------------------------------------------------------------
# Import failure tracking
# ---------------------------------------------------------------------------

@admin_bp.get("/import-failures")
@login_required
@limiter.limit("60 per minute")
def list_import_failures():
    """
    GET /api/admin/import-failures
    Query params: page (default 1), per_page (default 20)

    Returns paginated ImportFailure records, sorted by created_at desc.
    Admin-only — returns 403 for non-admin users.
    """
    user = get_current_user()
    if not user or not getattr(user, "is_admin", False):
        return forbidden()

    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
    except (TypeError, ValueError):
        return error("page and per_page must be integers.")

    query = ImportFailure.query.order_by(ImportFailure.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = [
        {
            "id": f.id,
            "source": f.source,
            "raw_url": f.raw_url,
            "missing_fields": f.missing_fields,
            "partial_data": f.partial_data,
            "user_id": f.user_id,
            "error_message": f.error_message,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in pagination.items
    ]

    return ok(
        items,
        meta=paginate_meta(page, per_page, pagination.total, pagination.pages),
    )
