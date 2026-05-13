"""Non-calculating planner metadata views for v2 trusted data."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from app.normalization.v2 import V2ModifierRegistry
from app.repositories.v2.paths import artifact_path

from .diagnostics import build_planner_adapter_diagnostics
from .eligibility import evaluate_modifier_record


EXPOSED_METADATA_FIELDS = (
    "canonical_id",
    "display_name",
    "domain",
    "source_id",
    "source_path",
    "support_status",
    "trust_level",
    "provenance_summary",
    "warnings",
    "debug_summary",
    "adapter_blocked_reasons",
    "planner_calculable",
    "stable_calculable",
    "display_only_eligible",
)

FORBIDDEN_CALCULATION_FIELDS = (
    "raw_value_min",
    "raw_value_max",
    "normalized_value_min",
    "normalized_value_max",
)


class V2PlannerMetadataRemap:
    """Build read-only, non-calculating metadata views from v2 adapter-visible rows."""

    def __init__(self, *, root: str | Path | None = None, modifier_registry: V2ModifierRegistry | None = None) -> None:
        self.root = Path(root) if root is not None else None
        self._modifier_registry = modifier_registry

    def load_modifier_registry(self) -> V2ModifierRegistry:
        if self._modifier_registry is not None:
            return self._modifier_registry
        return V2ModifierRegistry(artifact_path("modifier_registry", root=self.root)).load()

    def summarize_metadata(self, *, sample_limit: int = 10) -> dict[str, Any]:
        registry = self.load_modifier_registry()
        diagnostics = build_planner_adapter_diagnostics(root=self.root, sample_limit=sample_limit)
        domain_counts: dict[str, Counter[str]] = defaultdict(Counter)
        blocked_reason_counts: Counter[str] = Counter()
        samples: list[dict[str, Any]] = []
        inspected = 0
        display_only = 0
        planner_calculable = 0
        stable = 0

        for record in registry.list_modifiers():
            inspected += 1
            view = build_metadata_view(record)
            domain = view["domain"]
            domain_counts[domain]["inspected_count"] += 1
            if view["display_only_eligible"]:
                display_only += 1
                domain_counts[domain]["display_only_eligible_count"] += 1
            if view["planner_calculable"]:
                planner_calculable += 1
                domain_counts[domain]["planner_calculable_count"] += 1
            if view["stable_calculable"]:
                stable += 1
                domain_counts[domain]["stable_calculable_count"] += 1
            blocked_reason_counts.update(view["adapter_blocked_reasons"])
            if len(samples) < sample_limit:
                samples.append(view)

        domains = [
            {
                "domain": domain,
                "inspected_count": counts["inspected_count"],
                "display_only_eligible_count": counts["display_only_eligible_count"],
                "planner_calculable_count": counts["planner_calculable_count"],
                "stable_calculable_count": counts["stable_calculable_count"],
            }
            for domain, counts in sorted(domain_counts.items())
        ]

        return {
            "summary": {
                "domains_inspected": len(domains),
                "metadata_records_inspected": inspected,
                "display_only_eligible_count": display_only,
                "planner_calculable_count": planner_calculable,
                "stable_calculable_count": stable,
                "production_consumed": False,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "domains": domains,
            "fields_exposed": list(EXPOSED_METADATA_FIELDS),
            "forbidden_calculation_fields": list(FORBIDDEN_CALCULATION_FIELDS),
            "blocked_reason_counts": dict(sorted(blocked_reason_counts.items())),
            "metadata_samples": samples,
            "diagnostics_summary": diagnostics["summary"],
            "display_only_candidates": diagnostics["display_only_candidates"],
            "blocked_mechanical_data": diagnostics["blocked_mechanical_data"],
            "safety_confirmations": {
                "production_consumed": False,
                "planner_remap_performed": False,
                "planner_output_changed": False,
                "crafting_behavior_changed": False,
                "simulation_behavior_changed": False,
                "stat_aggregation_behavior_changed": False,
                "value_normalization_promoted": False,
                "skill_identity_bridge_added": False,
                "stable_calculable_count": stable,
                "planner_calculable_count": planner_calculable,
                "value_normalization_status": "audit_only",
                "skill_identity_bridge_status": "unbridged",
            },
            "metadata_policy": {
                "read_only": True,
                "non_calculating": True,
                "display_only_does_not_imply_planner_calculable": True,
                "values_exposed_for_planner_math": False,
            },
        }


def build_metadata_view(record: dict[str, Any]) -> dict[str, Any]:
    eligibility = evaluate_modifier_record(record)
    provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
    warnings = record.get("warnings") if isinstance(record.get("warnings"), list) else []
    canonical_id = str(record.get("canonical_modifier_id") or "")
    display_name = str(record.get("source_display_name") or record.get("raw_stat_name") or canonical_id)
    source_path = str(provenance.get("source_path") or "")
    display_only_eligible = bool(
        (canonical_id or record.get("source_id"))
        and display_name
        and (provenance or source_path)
    )

    return {
        "canonical_id": canonical_id,
        "display_name": display_name,
        "domain": str(record.get("source_type") or "unknown"),
        "source_id": str(record.get("source_id") or ""),
        "source_path": source_path,
        "support_status": str(record.get("support_status") or "unknown"),
        "trust_level": str(record.get("trust_level") or "unknown"),
        "provenance_summary": _provenance_summary(provenance),
        "warnings": list(warnings),
        "debug_summary": {
            "source_record_status": record.get("source_record_status"),
            "source_identity_status": record.get("source_identity_status"),
            "special_behavior_classification": record.get("special_behavior_classification"),
            "value_scale_status": record.get("value_scale_status"),
            "operation": record.get("operation"),
            "stat_id": record.get("stat_id"),
        },
        "adapter_blocked_reasons": list(eligibility.blocked_reasons),
        "planner_calculable": False,
        "stable_calculable": False,
        "display_only_eligible": display_only_eligible,
    }


def _provenance_summary(provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_path": provenance.get("source_path"),
        "source_type": provenance.get("source_type"),
        "source_id": provenance.get("source_id"),
        "schema_version": provenance.get("schema_version"),
        "extraction_method": provenance.get("extraction_method"),
    }
