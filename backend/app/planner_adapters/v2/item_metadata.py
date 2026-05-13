"""Display-only item/base metadata views backed by v2 item bundles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from app.repositories.v2.item_repository import V2ItemRepository
from app.repositories.v2.paths import artifact_path


ITEM_METADATA_FIELDS = (
    "canonical_id",
    "display_name",
    "domain",
    "item_category",
    "item_type",
    "subtype",
    "slot",
    "classification",
    "level_requirement",
    "class_restrictions",
    "mastery_restrictions",
    "implicit_count",
    "implicit_metadata",
    "source_path",
    "provenance_summary",
    "support_status",
    "trust_level",
    "warnings",
    "debug_summary",
    "display_only_eligible",
    "planner_calculable",
    "stable_calculable",
    "blocked_reasons",
)

EXCLUDED_CALCULATION_FIELDS = (
    "base_stats",
    "modifier_rows",
    "value_range",
    "value_min",
    "value_max",
    "raw_value_min",
    "raw_value_max",
    "normalized_value_min",
    "normalized_value_max",
)

ITEM_METADATA_BLOCKED_REASONS = (
    "display_only_metadata",
    "implicit_values_not_planner_normalized",
    "stable_calculable_false",
)


class V2ItemBaseDisplayMetadata:
    """Read-only display metadata adapter for v2 item bases and implicits."""

    def __init__(self, *, root: str | Path | None = None, repository: V2ItemRepository | None = None) -> None:
        self.root = Path(root) if root is not None else None
        self._repository = repository

    def load_repository(self) -> V2ItemRepository:
        if self._repository is not None:
            return self._repository
        return V2ItemRepository(
            artifact_path("item_base_bundle", root=self.root),
            artifact_path("item_implicit_bundle", root=self.root),
        ).load()

    def summarize_metadata(self, *, sample_limit: int = 10) -> dict[str, Any]:
        repository = self.load_repository()
        records = repository.list_bases()
        domains: Counter[str] = Counter()
        display_only_count = 0
        planner_calculable_count = 0
        stable_calculable_count = 0
        implicit_metadata_count = 0
        blocked_reason_counts: Counter[str] = Counter()
        samples: list[dict[str, Any]] = []

        for base in records:
            implicits = repository.get_implicits_for_base(base["canonical_id"])
            view = build_item_base_metadata_view(base, implicits)
            domains[view["classification"] or view["item_category"] or "unknown"] += 1
            if view["display_only_eligible"]:
                display_only_count += 1
            if view["planner_calculable"]:
                planner_calculable_count += 1
            if view["stable_calculable"]:
                stable_calculable_count += 1
            implicit_metadata_count += len(view["implicit_metadata"])
            blocked_reason_counts.update(view["blocked_reasons"])
            if len(samples) < sample_limit:
                samples.append(view)

        return {
            "summary": {
                "item_base_count": len(records),
                "implicit_record_count": repository.count_implicits(),
                "implicit_metadata_records_exposed": implicit_metadata_count,
                "domains_inspected": len(domains),
                "display_only_eligible_count": display_only_count,
                "planner_calculable_count": planner_calculable_count,
                "stable_calculable_count": stable_calculable_count,
                "production_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "domains": [
                {"domain": domain, "item_base_count": count}
                for domain, count in sorted(domains.items())
            ],
            "fields_exposed": list(ITEM_METADATA_FIELDS),
            "fields_excluded_from_calculation": list(EXCLUDED_CALCULATION_FIELDS),
            "blocked_reason_counts": dict(sorted(blocked_reason_counts.items())),
            "metadata_samples": samples,
            "implicit_metadata_treatment": {
                "implicit_records_loaded": repository.count_implicits(),
                "implicit_metadata_records_exposed": implicit_metadata_count,
                "modifier_values_exposed_as_planner_stats": False,
                "modifier_rows_exposed": False,
                "notes": [
                    "Implicit links are exposed as display/provenance metadata only.",
                    "Implicit modifier row values remain excluded from planner-calculable metadata.",
                ],
            },
            "safety_confirmations": {
                "production_consumed": False,
                "planner_remap_performed": False,
                "planner_output_changed": False,
                "crafting_behavior_changed": False,
                "simulation_behavior_changed": False,
                "stat_aggregation_behavior_changed": False,
                "value_normalization_promoted": False,
                "skill_identity_bridge_added": False,
                "planner_calculable_count": planner_calculable_count,
                "stable_calculable_count": stable_calculable_count,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
        }


def build_item_base_metadata_view(base: dict[str, Any], implicits: list[dict[str, Any]]) -> dict[str, Any]:
    provenance = base.get("provenance") if isinstance(base.get("provenance"), dict) else {}
    warnings = base.get("warnings") if isinstance(base.get("warnings"), list) else []
    implicit_metadata = [_implicit_metadata_view(record) for record in implicits]
    canonical_id = str(base.get("canonical_id") or "")
    display_name = str(base.get("display_name") or canonical_id)
    source_path = str(provenance.get("source_path") or base.get("source_file") or "")
    display_only_eligible = bool(canonical_id and display_name and source_path)

    return {
        "canonical_id": canonical_id,
        "display_name": display_name,
        "domain": "item_base",
        "item_category": base.get("item_category"),
        "item_type": base.get("item_type"),
        "subtype": base.get("subtype"),
        "slot": base.get("slot") or base.get("equipment_slot"),
        "classification": base.get("classification"),
        "level_requirement": base.get("level_requirement"),
        "class_restrictions": list(base.get("class_restrictions") or []),
        "mastery_restrictions": list(base.get("mastery_restrictions") or []),
        "implicit_count": len(implicit_metadata),
        "implicit_metadata": implicit_metadata,
        "source_path": source_path,
        "provenance_summary": _provenance_summary(provenance),
        "support_status": str(base.get("support_status") or "unknown"),
        "trust_level": str(base.get("trust_level") or "unknown"),
        "warnings": list(warnings),
        "debug_summary": {
            "source_id": base.get("source_id"),
            "patch_version": base.get("patch_version"),
            "maximum_affixes": base.get("maximum_affixes"),
            "cannot_drop": base.get("cannot_drop"),
            "stable_calculable_source": bool(base.get("stable_calculable") is True),
        },
        "display_only_eligible": display_only_eligible,
        "planner_calculable": False,
        "stable_calculable": False,
        "blocked_reasons": list(ITEM_METADATA_BLOCKED_REASONS),
    }


def _implicit_metadata_view(record: dict[str, Any]) -> dict[str, Any]:
    provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
    references = record.get("modifier_references") if isinstance(record.get("modifier_references"), list) else []
    return {
        "canonical_id": record.get("canonical_id"),
        "display_name": record.get("display_name"),
        "item_base_id": record.get("item_base_id"),
        "item_type": record.get("item_type"),
        "source_path": provenance.get("source_path") or record.get("source_file"),
        "provenance_summary": _provenance_summary(provenance),
        "support_status": record.get("support_status"),
        "trust_level": record.get("trust_level"),
        "warnings": list(record.get("warnings") or []),
        "modifier_reference_count": len(references),
        "planner_calculable": False,
        "stable_calculable": False,
    }


def _provenance_summary(provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_path": provenance.get("source_path"),
        "source_type": provenance.get("source_type"),
        "source_id": provenance.get("source_id"),
        "schema_version": provenance.get("schema_version"),
        "extraction_method": provenance.get("extraction_method"),
        "patch_version": provenance.get("patch_version"),
    }
