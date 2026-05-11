"""Stable affix catalog endpoints gated behind Forge-safe consumption config."""

from __future__ import annotations

from flask import Blueprint, request

from app.services.affix_catalog_service import AffixCatalogFilters, AffixCatalogService, AffixCatalogUnavailable
from app.utils.responses import error, not_found, ok

affixes_bp = Blueprint("affixes", __name__)


def _service() -> AffixCatalogService:
    return AffixCatalogService()


def _require_enabled(service: AffixCatalogService):
    if not service.consumption_enabled:
        return error("Forge-safe affix consumption is disabled", status=404)
    if service.mode == "shadow":
        return error("Forge-safe affix catalog is in shadow mode and is not user-facing", status=409)
    return None


@affixes_bp.get("/catalog")
def list_catalog_affixes():
    service = _service()
    disabled = _require_enabled(service)
    if disabled:
        return disabled
    try:
        result = service.list_affixes(
            limit=int(request.args.get("limit", 50)),
            offset=int(request.args.get("offset", 0)),
            query=request.args.get("q") or request.args.get("query"),
            filters=AffixCatalogFilters(
                source_type=request.args.get("source_type"),
                item_type=request.args.get("item_type"),
            ),
        )
    except (ValueError, AffixCatalogUnavailable) as exc:
        return error(str(exc), status=503)
    meta = {k: result[k] for k in ("total", "limit", "offset", "data_source", "mode", "consumption_enabled", "production_consumer")}
    return ok(data=result["affixes"], meta=meta)


@affixes_bp.get("/catalog/summary")
def catalog_summary():
    service = _service()
    disabled = _require_enabled(service)
    if disabled:
        return disabled
    try:
        return ok(data=service.summary())
    except AffixCatalogUnavailable as exc:
        return error(str(exc), status=503)


@affixes_bp.get("/catalog/<affix_id>")
def catalog_affix_detail(affix_id: str):
    service = _service()
    disabled = _require_enabled(service)
    if disabled:
        return disabled
    try:
        affix = service.get_affix(affix_id)
    except AffixCatalogUnavailable as exc:
        return error(str(exc), status=503)
    if affix is None:
        return not_found("Affix")
    return ok(data=affix, meta={"data_source": service.active_source, "production_consumer": False})


@affixes_bp.get("/experimental/forge-safe-affixes")
def experimental_forge_safe_affixes():
    service = _service()
    if not service.config.get("FORGE_SAFE_AFFIX_CATALOG_ENABLED", False):
        return error("Experimental Forge-safe affix catalog is disabled", status=404)
    try:
        result = service.list_affixes(limit=int(request.args.get("limit", 100)), offset=int(request.args.get("offset", 0)))
    except AffixCatalogUnavailable as exc:
        return error(str(exc), status=503)
    return ok(data=result["affixes"], meta={k: result[k] for k in ("total", "limit", "offset", "data_source", "mode", "production_consumer")})
