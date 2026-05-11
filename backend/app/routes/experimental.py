"""Experimental feature-gated endpoints preserved for migration debugging."""

from __future__ import annotations

from flask import Blueprint, request

from app.services.affix_catalog_service import AffixCatalogService, AffixCatalogUnavailable
from app.utils.responses import error, ok

experimental_bp = Blueprint("experimental", __name__)


@experimental_bp.get("/forge-safe-affixes")
def forge_safe_affixes():
    service = AffixCatalogService()
    if not service.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return error("Experimental Forge-safe affix catalog is disabled", status=404)
    try:
        result = service.list_affixes(limit=int(request.args.get("limit", 100)), offset=int(request.args.get("offset", 0)))
    except AffixCatalogUnavailable as exc:
        return error(str(exc), status=503)
    return ok(data=result["affixes"], meta={k: result[k] for k in ("total", "limit", "offset", "data_source", "mode", "production_consumer")})
