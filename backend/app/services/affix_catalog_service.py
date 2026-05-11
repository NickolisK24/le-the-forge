"""Controlled affix catalog service.

This service is the single selection point between legacy affix data and the
Forge-safe canonical export.  It never mutates the global AffixRegistry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import current_app

from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoaderError
from data.repositories.forge_safe_affix_repository import ForgeSafeAffixRepository

VALID_MODES = {"shadow", "read_only", "active"}


@dataclass(frozen=True)
class AffixCatalogFilters:
    source_type: str | None = None
    item_type: str | None = None


class AffixCatalogUnavailable(RuntimeError):
    pass


class AffixCatalogService:
    def __init__(self, app=None, repository: ForgeSafeAffixRepository | None = None) -> None:
        self.app = app
        self._repository = repository

    @property
    def config(self):
        app = self.app or current_app
        return app.config

    @property
    def consumption_enabled(self) -> bool:
        return bool(self.config.get("FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED", False))

    @property
    def mode(self) -> str:
        mode = str(self.config.get("FORGE_SAFE_AFFIX_CONSUMPTION_MODE", "shadow")).lower()
        return mode if mode in VALID_MODES else "shadow"

    @property
    def active_source(self) -> str:
        if self.consumption_enabled and self.mode in {"read_only", "active"}:
            return "forge_safe"
        return "legacy"

    def list_affixes(self, *, limit: int = 50, offset: int = 0, filters: AffixCatalogFilters | None = None, query: str | None = None) -> dict[str, Any]:
        records = self._active_records()
        filtered = self._filter_records(records, filters or AffixCatalogFilters(), query)
        limit = max(1, min(int(limit), 250))
        offset = max(0, int(offset))
        page = filtered[offset : offset + limit]
        return {
            "affixes": page,
            "total": len(filtered),
            "limit": limit,
            "offset": offset,
            "data_source": self.active_source,
            "mode": self.mode,
            "consumption_enabled": self.consumption_enabled,
            "production_consumer": False,
        }

    def get_affix(self, affix_id: str) -> dict[str, Any] | None:
        affix_id = str(affix_id)
        if self.active_source == "forge_safe":
            return self._repo().get_by_affix_id(affix_id)
        for record in self._legacy_records():
            if str(record.get("id")) == affix_id or str(record.get("affix_id")) == affix_id:
                return record
        return None

    def search_affixes(self, query: str, *, limit: int = 50, offset: int = 0, filters: AffixCatalogFilters | None = None) -> dict[str, Any]:
        return self.list_affixes(limit=limit, offset=offset, filters=filters, query=query)

    def summary(self) -> dict[str, Any]:
        legacy_count = len(self._legacy_records())
        summary = {
            "active_source": self.active_source,
            "mode": self.mode,
            "consumption_enabled": self.consumption_enabled,
            "legacy_count": legacy_count,
            "production_consumer": False,
        }
        if self.consumption_enabled:
            try:
                forge_summary = self._repo().get_summary()
                summary["forge_safe"] = forge_summary
                summary["forge_safe_count"] = forge_summary["loaded_record_count"]
            except ForgeSafeAffixLoaderError as exc:
                summary["forge_safe_error"] = str(exc)
                if self.mode in {"read_only", "active"}:
                    raise AffixCatalogUnavailable(str(exc)) from exc
        else:
            summary["forge_safe_count"] = 0
        return summary

    def _repo(self) -> ForgeSafeAffixRepository:
        if self._repository is not None:
            return self._repository
        path = self.config.get("FORGE_SAFE_AFFIX_EXPORT_PATH")
        if not path:
            raise AffixCatalogUnavailable("FORGE_SAFE_AFFIX_EXPORT_PATH is not configured")
        self._repository = ForgeSafeAffixRepository(path).load()
        return self._repository

    def _active_records(self) -> list[dict[str, Any]]:
        if self.active_source == "forge_safe":
            try:
                return self._repo().list_affixes()
            except ForgeSafeAffixLoaderError as exc:
                raise AffixCatalogUnavailable(str(exc)) from exc
        return self._legacy_records()

    def _legacy_records(self) -> list[dict[str, Any]]:
        app = self.app or current_app
        registry = app.extensions.get("affix_registry")
        if registry is not None:
            return [self._legacy_to_catalog(a) for a in registry.all()]
        return []

    @staticmethod
    def _legacy_to_catalog(affix: Any) -> dict[str, Any]:
        affix_id = getattr(affix, "affix_id", None)
        return {
            "id": str(affix_id if affix_id is not None else getattr(affix, "name", "")),
            "affix_id": affix_id,
            "name": getattr(affix, "name", ""),
            "source_type": getattr(affix, "affix_type", None),
            "item_types": list(getattr(affix, "applicable_to", ()) or ()),
            "data_source": "legacy",
            "production_consumer": False,
        }

    @staticmethod
    def _filter_records(records: list[dict[str, Any]], filters: AffixCatalogFilters, query: str | None) -> list[dict[str, Any]]:
        q = (query or "").strip().lower()
        source_type = (filters.source_type or "").strip().lower()
        item_type = (filters.item_type or "").strip().lower()
        output = []
        for record in records:
            if source_type and str(record.get("source_type") or "").lower() != source_type:
                continue
            # Support both forge-safe records (item_type + eligible_item_types)
            # and legacy records (item_types list)
            if item_type:
                record_item_type = str(record.get("item_type", "")).lower()
                legacy_item_types = [str(v).lower() for v in record.get("item_types", [])]
                eligible = [str(v).lower() for v in (record.get("eligible_item_types") or [])]
                if item_type != record_item_type and item_type not in legacy_item_types and item_type not in eligible:
                    continue
            if q:
                name = str(record.get("name") or record.get("affix_name") or "").lower()
                display = str(record.get("display_name") or "").lower()
                rec_id = str(record.get("id") or record.get("affix_id") or "").lower()
                if q not in name and q not in display and q not in rec_id:
                    continue
            output.append(record)
        return output
