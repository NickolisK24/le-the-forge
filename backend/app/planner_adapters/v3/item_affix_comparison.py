"""V3 item and affix mechanical comparison scaffolding.

This layer adapts candidate item/base/implicit/standard-affix stat rows into
the generic v3 dry-run comparison envelope. It is intentionally read-only and
does not call production planner, combat, crafting, simulation, optimizer, or
live stat aggregation code.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .mechanical_dry_run import V3ExperimentalMechanicalDryRun, deterministic_hash


ITEM_AFFIX_COMPONENT_TYPES = frozenset({"item_base", "implicit", "affix"})
KNOWN_OPERATIONS = frozenset({"flat", "increased", "more", "less", "chance", "duration", "cooldown", "cost"})
APPROVED_VALUE_STATUSES = frozenset({"approved", "normalized"})
GATE_MECHANISM = "explicit_enabled_argument"


class V3ItemAffixMechanicalComparison:
    """Build item/affix candidate snapshots and compare them through dry-run mode."""

    def compare(
        self,
        *,
        current_rows: list[dict[str, Any]],
        candidate_rows: list[dict[str, Any]],
        enabled: bool = False,
        baseline_snapshot_id: str | None = None,
        run_id: str = "v3_phase_8_item_affix_mechanical_comparison",
    ) -> dict[str, Any]:
        if not enabled:
            return _disabled_report(run_id=run_id)

        current_snapshot = _build_snapshot(
            rows=current_rows,
            snapshot_id="current_item_affix_baseline",
            candidate=False,
        )
        candidate_snapshot = _build_snapshot(
            rows=candidate_rows,
            snapshot_id="v3_item_affix_candidate",
            candidate=True,
        )
        dry_run = V3ExperimentalMechanicalDryRun().compare(
            current_output=current_snapshot,
            candidate_output=candidate_snapshot,
            enabled=True,
            baseline_snapshot_id=baseline_snapshot_id,
            run_id=run_id,
        )
        report = {
            "schema_version": "v3.item_affix_mechanical_comparison.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": dry_run["mode"],
            "run": {
                **dry_run["run"],
                "domain": "item_affix",
                "component_types": sorted(ITEM_AFFIX_COMPONENT_TYPES),
            },
            "summary": {
                **dry_run["summary"],
                "domain": "item_affix",
                "current_row_count": len(current_rows),
                "candidate_row_count": len(candidate_rows),
                "candidate_mechanically_explainable_row_count": _mechanically_explainable_count(candidate_rows),
                "production_consumed": False,
                "production_planner_output_changed": False,
                "mechanical_calculations_performed": False,
            },
            "component_summary": _component_summary(candidate_rows),
            "operation_summary": _operation_summary(candidate_rows),
            "delta_category_counts": dry_run["delta_category_counts"],
            "blocked_reasons": dry_run["blocked_reasons"],
            "comparison_rows": _attach_item_affix_metadata(dry_run["comparison_rows"], candidate_snapshot["metadata_by_key"]),
            "candidate_snapshot": {
                "snapshot_id": candidate_snapshot["snapshot_id"],
                "value_count": len(candidate_snapshot["values"]),
                "metadata_by_key": candidate_snapshot["metadata_by_key"],
            },
            "rollback_visibility": dry_run["rollback_visibility"],
            "safety_confirmations": {
                **dry_run["safety_confirmations"],
                "item_affix_domain_only": True,
                "unique_set_logic_added": False,
                "tooltip_semantics_inferred": False,
                "runtime_stat_aggregation_changed": False,
            },
            "metadata": {
                "source": "v3_item_affix_mechanical_comparison",
                "read_only": True,
                "experimental": True,
                "default_enabled": False,
                "production_consumer": False,
                "production_enabled": False,
                "planner_remap_performed": False,
                "domain": "item_affix",
                "supported_component_types": sorted(ITEM_AFFIX_COMPONENT_TYPES),
                "deterministic_serializer": "json_sort_keys_sha256",
            },
            "dry_run_envelope": dry_run,
        }
        report["deterministic_hash"] = deterministic_hash(_stable_report(report))
        return report


def build_sample_item_affix_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return a deterministic item/affix sample covering supported and blocked gates."""

    current = [
        _row("item:iron-casque", "item_base", "base:iron-casque", "armor", "flat", 42, "resolved"),
        _row("item:ruby-ring", "implicit", "implicit:ruby-ring", "fire_resistance", "flat", 12, "resolved"),
        _row("affix:health-prefix", "affix", "affix:health", "health", "flat", 30, "resolved"),
        _row("affix:fire-damage", "affix", "affix:fire-damage", "fire_damage", "increased", 20, "resolved"),
        _row("affix:armor-delta", "affix", "affix:armor", "armor", "flat", 10, "resolved"),
        _row("affix:missing-candidate", "affix", "affix:missing-candidate", "cold_damage", "increased", 5, "resolved"),
        _row("affix:unknown-operation", "affix", "affix:unknown-operation", "void_damage", "unknown", 7, "resolved"),
        _row("affix:unknown-stat", "affix", "affix:unknown-stat", "unknown_stat", "flat", 3, "unresolved"),
        _row("affix:audit-value", "affix", "affix:audit-value", "minion_damage", "increased", 11, "resolved"),
        _row("affix:unsupported", "affix", "affix:unsupported", "summon_behavior", "flat", 1, "resolved"),
        _row("affix:text-only", "affix", "affix:text-only", "display_only_note", "flat", 1, "resolved"),
        _row("affix:scripted", "affix", "affix:scripted", "scripted_proc", "flat", 1, "resolved"),
        _row("affix:missing-provenance", "affix", "affix:missing-provenance", "health", "flat", 8, "resolved"),
    ]
    candidate = [
        _row("item:iron-casque", "item_base", "base:iron-casque", "armor", "flat", 42, "resolved"),
        _row("item:ruby-ring", "implicit", "implicit:ruby-ring", "fire_resistance", "flat", 12, "resolved"),
        _row("affix:health-prefix", "affix", "affix:health", "health", "flat", 30, "resolved"),
        _row(
            "affix:fire-damage",
            "affix",
            "affix:fire-damage",
            "fire_damage",
            "increased",
            25,
            "resolved",
            approval_status="accepted_dry_run_delta",
            provenance=("candidate:item_affix_fixture", "baseline:item_affix_delta_sample"),
        ),
        _row("affix:armor-delta", "affix", "affix:armor", "armor", "flat", 12, "resolved"),
        _row("affix:unknown-operation", "affix", "affix:unknown-operation", "void_damage", "unknown", 7, "resolved"),
        _row("affix:unknown-stat", "affix", "affix:unknown-stat", "unknown_stat", "flat", 3, "unresolved"),
        _row(
            "affix:audit-value",
            "affix",
            "affix:audit-value",
            "minion_damage",
            "increased",
            11,
            "resolved",
            value_normalization_status="audit_only",
        ),
        _row("affix:unsupported", "affix", "affix:unsupported", "summon_behavior", "flat", 1, "resolved", support_status="unsupported"),
        _row("affix:text-only", "affix", "affix:text-only", "display_only_note", "flat", 1, "resolved", support_status="text_only"),
        _row("affix:scripted", "affix", "affix:scripted", "scripted_proc", "flat", 1, "resolved", support_status="scripted"),
        _row(
            "affix:missing-provenance",
            "affix",
            "affix:missing-provenance",
            "health",
            "flat",
            8,
            "resolved",
            provenance=(),
        ),
        _row("affix:missing-current", "affix", "affix:missing-current", "lightning_damage", "increased", 4, "resolved"),
    ]
    return current, candidate


def _build_snapshot(*, rows: list[dict[str, Any]], snapshot_id: str, candidate: bool) -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {}
    metadata_by_key: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=_row_sort_key):
        output_key = _output_key(row)
        entry = {
            "value": row.get("value"),
            "provenance": list(row.get("provenance") or []),
        }
        if candidate:
            entry.update(
                {
                    "support_status": _support_status(row),
                    "operation_status": _operation_status(row),
                    "stat_identity_status": _stat_identity_status(row),
                    "value_normalization_status": _value_normalization_status(row),
                }
            )
            if row.get("approval_status"):
                entry["approval_status"] = row["approval_status"]
        values[output_key] = entry
        metadata_by_key[output_key] = _row_metadata(row)
    return {
        "snapshot_id": snapshot_id,
        "values": values,
        "metadata_by_key": metadata_by_key,
    }


def _row(
    entity_id: str,
    component_type: str,
    source_id: str,
    stat_id: str,
    operation: str,
    value: int | float,
    stat_identity_status: str,
    *,
    support_status: str = "supported",
    value_normalization_status: str = "approved",
    approval_status: str | None = None,
    provenance: tuple[str, ...] = ("candidate:item_affix_fixture",),
) -> dict[str, Any]:
    return {
        "entity_id": entity_id,
        "component_type": component_type,
        "source_id": source_id,
        "stat_id": stat_id,
        "operation": operation,
        "value": value,
        "stat_identity_status": stat_identity_status,
        "support_status": support_status,
        "value_normalization_status": value_normalization_status,
        "approval_status": approval_status,
        "provenance": list(provenance),
    }


def _output_key(row: dict[str, Any]) -> str:
    return "::".join(
        str(row.get(part, ""))
        for part in ("entity_id", "component_type", "source_id", "stat_id", "operation")
    )


def _support_status(row: dict[str, Any]) -> str:
    status = str(row.get("support_status") or "unsupported").lower()
    component_type = str(row.get("component_type") or "").lower()
    if component_type not in ITEM_AFFIX_COMPONENT_TYPES:
        return "unsupported"
    if status in {"supported", "unsupported", "text_only", "scripted"}:
        return status
    return "unsupported"


def _operation_status(row: dict[str, Any]) -> str:
    return "known" if str(row.get("operation") or "").lower() in KNOWN_OPERATIONS else "unknown"


def _stat_identity_status(row: dict[str, Any]) -> str:
    return "resolved" if str(row.get("stat_identity_status") or "").lower() == "resolved" else "unresolved"


def _value_normalization_status(row: dict[str, Any]) -> str:
    status = str(row.get("value_normalization_status") or "audit_only").lower()
    return "approved" if status in APPROVED_VALUE_STATUSES else status


def _row_metadata(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "entity_id": row.get("entity_id"),
        "component_type": row.get("component_type"),
        "source_id": row.get("source_id"),
        "stat_id": row.get("stat_id"),
        "operation": row.get("operation"),
        "support_status": row.get("support_status"),
        "stat_identity_status": row.get("stat_identity_status"),
        "value_normalization_status": row.get("value_normalization_status"),
        "approval_status": row.get("approval_status"),
    }


def _attach_item_affix_metadata(
    rows: list[dict[str, Any]],
    metadata_by_key: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        enriched = deepcopy(row)
        enriched["item_affix_metadata"] = metadata_by_key.get(row["output_key"], {})
        output.append(enriched)
    return output


def _component_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("component_type")) for row in rows).items()))


def _operation_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("operation")) for row in rows).items()))


def _mechanically_explainable_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        if _support_status(row) == "supported"
        and _operation_status(row) == "known"
        and _stat_identity_status(row) == "resolved"
        and _value_normalization_status(row) == "approved"
        and bool(row.get("provenance"))
    )


def _disabled_report(*, run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v3.item_affix_mechanical_comparison.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": {
            "enabled": False,
            "active": False,
            "status": "disabled",
            "gate_mechanism": GATE_MECHANISM,
            "default_enabled": False,
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_enabled": False,
        },
        "run": {
            "run_id": run_id,
            "domain": "item_affix",
            "component_types": sorted(ITEM_AFFIX_COMPONENT_TYPES),
            "comparison_row_count": 0,
        },
        "summary": {
            "domain": "item_affix",
            "current_row_count": 0,
            "candidate_row_count": 0,
            "candidate_mechanically_explainable_row_count": 0,
            "accepted_delta_count": 0,
            "rejected_delta_count": 0,
            "blocked_delta_count": 0,
            "production_consumed": False,
            "production_planner_output_changed": False,
            "mechanical_calculations_performed": False,
            "deterministic": True,
        },
        "component_summary": {},
        "operation_summary": {},
        "delta_category_counts": {},
        "blocked_reasons": [],
        "comparison_rows": [],
        "candidate_snapshot": {"snapshot_id": None, "value_count": 0, "metadata_by_key": {}},
        "rollback_visibility": {
            "run_id": run_id,
            "rollback_required_for_production": False,
            "debug_visibility": ["deterministic_hash", "delta_category_counts", "blocked_reasons", "comparison_rows"],
        },
        "safety_confirmations": {
            "production_consumed": False,
            "production_enabled": False,
            "production_planner_output_changed": False,
            "planner_remap_performed": False,
            "mechanical_calculations_performed": False,
            "item_affix_domain_only": True,
            "unique_set_logic_added": False,
            "tooltip_semantics_inferred": False,
            "runtime_stat_aggregation_changed": False,
        },
        "metadata": {
            "source": "v3_item_affix_mechanical_comparison",
            "read_only": True,
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "production_enabled": False,
            "planner_remap_performed": False,
            "domain": "item_affix",
            "supported_component_types": sorted(ITEM_AFFIX_COMPONENT_TYPES),
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }


def _stable_report(report: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(report)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    if isinstance(stable.get("dry_run_envelope"), dict):
        stable["dry_run_envelope"].pop("generated_at", None)
    return stable


def _row_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(row.get("entity_id") or ""),
        str(row.get("component_type") or ""),
        str(row.get("source_id") or ""),
        str(row.get("stat_id") or ""),
        str(row.get("operation") or ""),
    )
