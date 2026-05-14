"""Display/provenance-only affix metadata views backed by v2 affix bundles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from app.repositories.v2.affix_repository import V2AffixRepository
from app.repositories.v2.paths import artifact_path


AFFIX_METADATA_FIELDS = (
    "canonical_id",
    "display_name",
    "domain",
    "affix_type",
    "prefix_suffix",
    "categories",
    "slot_restrictions",
    "item_type_restrictions",
    "class_restrictions",
    "mastery_restrictions",
    "tier_count",
    "modifier_reference_count",
    "modifier_reference_metadata",
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
    "tier_ranges",
    "normalized_fields",
    "raw_value_min",
    "raw_value_max",
    "normalized_value_min",
    "normalized_value_max",
    "min_value",
    "max_value",
)

AFFIX_METADATA_BLOCKED_REASONS = (
    "display_only_metadata",
    "affix_values_not_planner_normalized",
    "stable_calculable_false",
)


class V2AffixDisplayProvenanceMetadata:
    """Read-only display/provenance metadata adapter for v2 affixes."""

    def __init__(self, *, root: str | Path | None = None, repository: V2AffixRepository | None = None) -> None:
        self.root = Path(root) if root is not None else None
        self._repository = repository

    def load_repository(self) -> V2AffixRepository:
        if self._repository is not None:
            return self._repository
        return V2AffixRepository(artifact_path("affix_bundle", root=self.root)).load()

    def summarize_metadata(self, *, sample_limit: int = 10) -> dict[str, Any]:
        repository = self.load_repository()
        records = repository.list_affixes()
        domains: Counter[str] = Counter()
        prefix_suffix_counts: Counter[str] = Counter()
        display_only_count = 0
        planner_calculable_count = 0
        stable_calculable_count = 0
        modifier_reference_metadata_count = 0
        blocked_reason_counts: Counter[str] = Counter()
        samples: list[dict[str, Any]] = []

        for affix in records:
            view = build_affix_metadata_view(affix)
            domains[view["domain"] or "unknown"] += 1
            prefix_suffix_counts[str(view["prefix_suffix"] or "unknown")] += 1
            if view["display_only_eligible"]:
                display_only_count += 1
            if view["planner_calculable"]:
                planner_calculable_count += 1
            if view["stable_calculable"]:
                stable_calculable_count += 1
            modifier_reference_metadata_count += len(view["modifier_reference_metadata"])
            blocked_reason_counts.update(view["blocked_reasons"])
            if len(samples) < sample_limit:
                samples.append(view)

        return {
            "summary": {
                "affix_count": len(records),
                "modifier_reference_metadata_records_exposed": modifier_reference_metadata_count,
                "domains_inspected": len(domains),
                "display_only_eligible_count": display_only_count,
                "planner_calculable_count": planner_calculable_count,
                "stable_calculable_count": stable_calculable_count,
                "production_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "domains": [
                {"domain": domain, "affix_count": count}
                for domain, count in sorted(domains.items())
            ],
            "prefix_suffix_counts": dict(sorted(prefix_suffix_counts.items())),
            "fields_exposed": list(AFFIX_METADATA_FIELDS),
            "fields_excluded_from_calculation": list(EXCLUDED_CALCULATION_FIELDS),
            "blocked_reason_counts": dict(sorted(blocked_reason_counts.items())),
            "metadata_samples": samples,
            "tier_modifier_metadata_treatment": {
                "tier_counts_exposed": True,
                "tier_ranges_exposed": False,
                "modifier_reference_metadata_records_exposed": modifier_reference_metadata_count,
                "modifier_values_exposed_as_planner_stats": False,
                "notes": [
                    "Tier counts and modifier reference labels are display metadata only.",
                    "Tier ranges and source-unit values remain excluded from planner-calculable metadata.",
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


def build_affix_metadata_view(affix: dict[str, Any]) -> dict[str, Any]:
    provenance = affix.get("provenance") if isinstance(affix.get("provenance"), dict) else {}
    warnings = affix.get("warnings") if isinstance(affix.get("warnings"), list) else []
    canonical_id = str(affix.get("canonical_id") or "")
    display_name = str(affix.get("display_name") or canonical_id)
    source_path = str(provenance.get("source_path") or affix.get("source_file") or "")
    modifier_references = affix.get("modifier_references") if isinstance(affix.get("modifier_references"), list) else []
    display_only_eligible = bool(canonical_id and display_name and source_path)

    return {
        "canonical_id": canonical_id,
        "display_name": display_name,
        "domain": affix.get("affix_domain") or affix.get("source_type") or "unknown",
        "affix_type": affix.get("affix_type"),
        "prefix_suffix": affix.get("prefix_suffix"),
        "categories": list(affix.get("categories") or []),
        "slot_restrictions": list(affix.get("slot_restrictions") or []),
        "item_type_restrictions": list(affix.get("item_type_restrictions") or []),
        "class_restrictions": list(affix.get("class_restrictions") or []),
        "mastery_restrictions": list(affix.get("mastery_restrictions") or []),
        "tier_count": int(affix.get("tier_count") or len(affix.get("tier_ranges") or [])),
        "modifier_reference_count": int(affix.get("modifier_reference_count") or len(modifier_references)),
        "modifier_reference_metadata": [_modifier_reference_metadata(record) for record in modifier_references],
        "source_path": source_path,
        "provenance_summary": _provenance_summary(provenance),
        "support_status": str(affix.get("support_status") or "unknown"),
        "trust_level": str(affix.get("trust_level") or "unknown"),
        "warnings": list(warnings),
        "debug_summary": {
            "source_id": affix.get("source_id"),
            "source_type": affix.get("source_type"),
            "source_affix_id": affix.get("source_affix_id"),
            "patch_version": affix.get("patch_version"),
            "value_scale_policy": affix.get("value_scale_policy"),
            "polarity_policy": affix.get("polarity_policy"),
            "stable_calculable_source": bool(affix.get("stable_calculable") is True),
        },
        "display_only_eligible": display_only_eligible,
        "planner_calculable": False,
        "stable_calculable": False,
        "blocked_reasons": list(AFFIX_METADATA_BLOCKED_REASONS),
    }


def _modifier_reference_metadata(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "modifier_id": record.get("modifier_id"),
        "modifier_type": record.get("modifier_type"),
        "property": record.get("property"),
        "property_path": record.get("property_path"),
        "source_record_id": record.get("source_record_id"),
        "tags": list(record.get("tags") or []),
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
