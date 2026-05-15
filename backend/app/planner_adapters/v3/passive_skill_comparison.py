"""V3 passive and skill mechanical comparison scaffolding.

Passive and skill rows are intentionally handled more conservatively than
item/affix rows because identity, conditional, triggered, cooldown, duration,
chance, scripted, and text-only behavior can change build output if guessed.
This module only prepares supplied rows for the dry-run comparison boundary.
It does not call production planner, combat, crafting, simulation, optimizer,
or live stat aggregation code.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .mechanical_dry_run import V3ExperimentalMechanicalDryRun, deterministic_hash


PASSIVE_SKILL_COMPONENT_TYPES = frozenset({"passive_node", "skill_node", "skill_modifier"})
KNOWN_SIMPLE_OPERATIONS = frozenset({"flat", "increased", "more", "less", "chance", "duration", "cooldown", "cost"})
APPROVED_VALUE_STATUSES = frozenset({"approved", "normalized"})
GATE_MECHANISM = "explicit_enabled_argument"


class V3PassiveSkillMechanicalComparison:
    """Build passive/skill snapshots and compare them through dry-run mode."""

    def compare(
        self,
        *,
        current_rows: list[dict[str, Any]],
        candidate_rows: list[dict[str, Any]],
        enabled: bool = False,
        baseline_snapshot_id: str | None = None,
        run_id: str = "v3_phase_9_passive_skill_mechanical_comparison",
    ) -> dict[str, Any]:
        if not enabled:
            return _disabled_report(run_id=run_id)

        current_snapshot = _build_snapshot(rows=current_rows, snapshot_id="current_passive_skill_baseline", candidate=False)
        candidate_snapshot = _build_snapshot(rows=candidate_rows, snapshot_id="v3_passive_skill_candidate", candidate=True)
        dry_run = V3ExperimentalMechanicalDryRun().compare(
            current_output=current_snapshot,
            candidate_output=candidate_snapshot,
            enabled=True,
            baseline_snapshot_id=baseline_snapshot_id,
            run_id=run_id,
        )
        report = {
            "schema_version": "v3.passive_skill_mechanical_comparison.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": dry_run["mode"],
            "run": {
                **dry_run["run"],
                "domain": "passive_skill",
                "component_types": sorted(PASSIVE_SKILL_COMPONENT_TYPES),
            },
            "summary": {
                **dry_run["summary"],
                "domain": "passive_skill",
                "current_row_count": len(current_rows),
                "candidate_row_count": len(candidate_rows),
                "candidate_simple_explainable_row_count": _simple_explainable_count(candidate_rows),
                "production_consumed": False,
                "production_planner_output_changed": False,
                "mechanical_calculations_performed": False,
            },
            "component_summary": _component_summary(candidate_rows),
            "operation_summary": _operation_summary(candidate_rows),
            "skill_identity_summary": _skill_identity_summary(candidate_rows),
            "semantic_summary": _semantic_summary(candidate_rows),
            "delta_category_counts": dry_run["delta_category_counts"],
            "blocked_reasons": dry_run["blocked_reasons"],
            "comparison_rows": _attach_passive_skill_metadata(dry_run["comparison_rows"], candidate_snapshot["metadata_by_key"]),
            "candidate_snapshot": {
                "snapshot_id": candidate_snapshot["snapshot_id"],
                "value_count": len(candidate_snapshot["values"]),
                "metadata_by_key": candidate_snapshot["metadata_by_key"],
            },
            "rollback_visibility": dry_run["rollback_visibility"],
            "safety_confirmations": {
                **dry_run["safety_confirmations"],
                "passive_skill_domain_only": True,
                "skill_identity_bridge_added": False,
                "conditional_semantics_implemented": False,
                "triggered_semantics_implemented": False,
                "cooldown_duration_chance_formulas_added": False,
                "tooltip_semantics_inferred": False,
                "runtime_stat_aggregation_changed": False,
            },
            "metadata": {
                "source": "v3_passive_skill_mechanical_comparison",
                "read_only": True,
                "experimental": True,
                "default_enabled": False,
                "production_consumer": False,
                "production_enabled": False,
                "planner_remap_performed": False,
                "domain": "passive_skill",
                "supported_component_types": sorted(PASSIVE_SKILL_COMPONENT_TYPES),
                "deterministic_serializer": "json_sort_keys_sha256",
            },
            "dry_run_envelope": dry_run,
        }
        report["deterministic_hash"] = deterministic_hash(_stable_report(report))
        return report


def build_sample_passive_skill_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic passive/skill samples covering conservative gates."""

    current = [
        _row("acolyte:passive:1", "passive_node", "passive:1", "none", "health", "flat", 10),
        _row("mage:skill:fireball:2", "skill_node", "skill:fireball:2", "fireball", "fire_damage", "increased", 20),
        _row("mage:skill:fireball:3", "skill_modifier", "skill:fireball:3", "fireball", "mana_cost", "flat", -2),
        _row("sentinel:passive:delta", "passive_node", "passive:delta", "none", "armor", "flat", 5),
        _row("skill:rejected-delta", "skill_node", "skill:rejected-delta", "fireball", "fire_damage", "increased", 7),
        _row("sentinel:passive:missing-candidate", "passive_node", "passive:missing-candidate", "none", "block_chance", "increased", 4),
        _row("skill:unresolved", "skill_node", "skill:unresolved", "unknown", "fire_damage", "increased", 3),
        _row("skill:ambiguous", "skill_node", "skill:ambiguous", "ambiguous", "cold_damage", "increased", 3),
        _row("skill:conditional", "skill_node", "skill:conditional", "fireball", "fire_damage", "more", 15),
        _row("skill:triggered", "skill_modifier", "skill:triggered", "fireball", "ignite_chance", "chance", 10),
        _row("skill:unknown-operation", "skill_node", "skill:unknown-operation", "fireball", "void_damage", "unknown", 7),
        _row("skill:unknown-stat", "skill_node", "skill:unknown-stat", "fireball", "unknown_stat", "flat", 2),
        _row("skill:audit-value", "skill_node", "skill:audit-value", "fireball", "minion_damage", "increased", 8),
        _row("skill:unsupported", "skill_node", "skill:unsupported", "fireball", "summon_behavior", "flat", 1),
        _row("skill:text-only", "skill_node", "skill:text-only", "fireball", "display_note", "flat", 1),
        _row("skill:scripted", "skill_modifier", "skill:scripted", "fireball", "scripted_proc", "flat", 1),
        _row("skill:missing-provenance", "skill_node", "skill:missing-provenance", "fireball", "health", "flat", 8),
    ]
    candidate = [
        _row("acolyte:passive:1", "passive_node", "passive:1", "none", "health", "flat", 10),
        _row("mage:skill:fireball:2", "skill_node", "skill:fireball:2", "fireball", "fire_damage", "increased", 20),
        _row("mage:skill:fireball:3", "skill_modifier", "skill:fireball:3", "fireball", "mana_cost", "flat", -2),
        _row(
            "sentinel:passive:delta",
            "passive_node",
            "passive:delta",
            "none",
            "armor",
            "flat",
            7,
            approval_status="accepted_dry_run_delta",
            provenance=("candidate:passive_skill_fixture", "baseline:passive_skill_delta_sample"),
        ),
        _row("skill:rejected-delta", "skill_node", "skill:rejected-delta", "fireball", "fire_damage", "increased", 9),
        _row("skill:unresolved", "skill_node", "skill:unresolved", "unknown", "fire_damage", "increased", 3, skill_identity_status="unresolved"),
        _row("skill:ambiguous", "skill_node", "skill:ambiguous", "ambiguous", "cold_damage", "increased", 3, skill_identity_status="ambiguous"),
        _row("skill:conditional", "skill_node", "skill:conditional", "fireball", "fire_damage", "more", 15, semantic_status="conditional"),
        _row("skill:triggered", "skill_modifier", "skill:triggered", "fireball", "ignite_chance", "chance", 10, semantic_status="triggered"),
        _row("skill:unknown-operation", "skill_node", "skill:unknown-operation", "fireball", "void_damage", "unknown", 7),
        _row("skill:unknown-stat", "skill_node", "skill:unknown-stat", "fireball", "unknown_stat", "flat", 2, stat_identity_status="unresolved"),
        _row("skill:audit-value", "skill_node", "skill:audit-value", "fireball", "minion_damage", "increased", 8, value_normalization_status="audit_only"),
        _row("skill:unsupported", "skill_node", "skill:unsupported", "fireball", "summon_behavior", "flat", 1, support_status="unsupported"),
        _row("skill:text-only", "skill_node", "skill:text-only", "fireball", "display_note", "flat", 1, support_status="text_only"),
        _row("skill:scripted", "skill_modifier", "skill:scripted", "fireball", "scripted_proc", "flat", 1, support_status="scripted"),
        _row("skill:missing-provenance", "skill_node", "skill:missing-provenance", "fireball", "health", "flat", 8, provenance=()),
    ]
    return current, candidate


def _build_snapshot(*, rows: list[dict[str, Any]], snapshot_id: str, candidate: bool) -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {}
    metadata_by_key: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=_row_sort_key):
        output_key = _output_key(row)
        entry = {"value": row.get("value"), "provenance": list(row.get("provenance") or [])}
        if candidate:
            entry.update(
                {
                    "support_status": _support_status(row),
                    "operation_status": _operation_status(row),
                    "stat_identity_status": _stat_identity_status(row),
                    "skill_identity_status": _skill_identity_status(row),
                    "semantic_status": _semantic_status(row),
                    "value_normalization_status": _value_normalization_status(row),
                }
            )
            if row.get("approval_status"):
                entry["approval_status"] = row["approval_status"]
        values[output_key] = entry
        metadata_by_key[output_key] = _row_metadata(row)
    return {"snapshot_id": snapshot_id, "values": values, "metadata_by_key": metadata_by_key}


def _row(
    entity_id: str,
    component_type: str,
    source_id: str,
    skill_id: str,
    stat_id: str,
    operation: str,
    value: int | float,
    *,
    support_status: str = "supported",
    stat_identity_status: str = "resolved",
    skill_identity_status: str = "resolved",
    semantic_status: str = "simple",
    value_normalization_status: str = "approved",
    approval_status: str | None = None,
    provenance: tuple[str, ...] = ("candidate:passive_skill_fixture",),
) -> dict[str, Any]:
    return {
        "entity_id": entity_id,
        "component_type": component_type,
        "source_id": source_id,
        "skill_id": skill_id,
        "stat_id": stat_id,
        "operation": operation,
        "value": value,
        "support_status": support_status,
        "stat_identity_status": stat_identity_status,
        "skill_identity_status": skill_identity_status,
        "semantic_status": semantic_status,
        "value_normalization_status": value_normalization_status,
        "approval_status": approval_status,
        "provenance": list(provenance),
    }


def _output_key(row: dict[str, Any]) -> str:
    return "::".join(
        str(row.get(part, ""))
        for part in ("entity_id", "component_type", "source_id", "skill_id", "stat_id", "operation")
    )


def _support_status(row: dict[str, Any]) -> str:
    status = str(row.get("support_status") or "unsupported").lower()
    component_type = str(row.get("component_type") or "").lower()
    if component_type not in PASSIVE_SKILL_COMPONENT_TYPES:
        return "unsupported"
    if status in {"supported", "unsupported", "text_only", "scripted"}:
        return status
    return "unsupported"


def _operation_status(row: dict[str, Any]) -> str:
    return "known" if str(row.get("operation") or "").lower() in KNOWN_SIMPLE_OPERATIONS else "unknown"


def _stat_identity_status(row: dict[str, Any]) -> str:
    return "resolved" if str(row.get("stat_identity_status") or "").lower() == "resolved" else "unresolved"


def _skill_identity_status(row: dict[str, Any]) -> str:
    status = str(row.get("skill_identity_status") or "unresolved").lower()
    return status if status in {"resolved", "unresolved", "ambiguous"} else "unresolved"


def _semantic_status(row: dict[str, Any]) -> str:
    status = str(row.get("semantic_status") or "simple").lower()
    return status if status in {"simple", "conditional", "triggered"} else "conditional"


def _value_normalization_status(row: dict[str, Any]) -> str:
    status = str(row.get("value_normalization_status") or "audit_only").lower()
    return "approved" if status in APPROVED_VALUE_STATUSES else status


def _row_metadata(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "entity_id": row.get("entity_id"),
        "component_type": row.get("component_type"),
        "source_id": row.get("source_id"),
        "skill_id": row.get("skill_id"),
        "stat_id": row.get("stat_id"),
        "operation": row.get("operation"),
        "support_status": row.get("support_status"),
        "stat_identity_status": row.get("stat_identity_status"),
        "skill_identity_status": row.get("skill_identity_status"),
        "semantic_status": row.get("semantic_status"),
        "value_normalization_status": row.get("value_normalization_status"),
        "approval_status": row.get("approval_status"),
    }


def _attach_passive_skill_metadata(rows: list[dict[str, Any]], metadata_by_key: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        enriched = deepcopy(row)
        enriched["passive_skill_metadata"] = metadata_by_key.get(row["output_key"], {})
        output.append(enriched)
    return output


def _component_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("component_type")) for row in rows).items()))


def _operation_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("operation")) for row in rows).items()))


def _skill_identity_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_skill_identity_status(row) for row in rows).items()))


def _semantic_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_semantic_status(row) for row in rows).items()))


def _simple_explainable_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        if _support_status(row) == "supported"
        and _operation_status(row) == "known"
        and _stat_identity_status(row) == "resolved"
        and _skill_identity_status(row) == "resolved"
        and _semantic_status(row) == "simple"
        and _value_normalization_status(row) == "approved"
        and bool(row.get("provenance"))
    )


def _disabled_report(*, run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v3.passive_skill_mechanical_comparison.1",
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
        "run": {"run_id": run_id, "domain": "passive_skill", "component_types": sorted(PASSIVE_SKILL_COMPONENT_TYPES), "comparison_row_count": 0},
        "summary": {
            "domain": "passive_skill",
            "current_row_count": 0,
            "candidate_row_count": 0,
            "candidate_simple_explainable_row_count": 0,
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
        "skill_identity_summary": {},
        "semantic_summary": {},
        "delta_category_counts": {},
        "blocked_reasons": [],
        "comparison_rows": [],
        "candidate_snapshot": {"snapshot_id": None, "value_count": 0, "metadata_by_key": {}},
        "rollback_visibility": {"run_id": run_id, "rollback_required_for_production": False, "debug_visibility": ["deterministic_hash", "delta_category_counts", "blocked_reasons", "comparison_rows"]},
        "safety_confirmations": {
            "production_consumed": False,
            "production_enabled": False,
            "production_planner_output_changed": False,
            "planner_remap_performed": False,
            "mechanical_calculations_performed": False,
            "passive_skill_domain_only": True,
            "skill_identity_bridge_added": False,
            "conditional_semantics_implemented": False,
            "triggered_semantics_implemented": False,
            "cooldown_duration_chance_formulas_added": False,
            "tooltip_semantics_inferred": False,
            "runtime_stat_aggregation_changed": False,
        },
        "metadata": {
            "source": "v3_passive_skill_mechanical_comparison",
            "read_only": True,
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "production_enabled": False,
            "planner_remap_performed": False,
            "domain": "passive_skill",
            "supported_component_types": sorted(PASSIVE_SKILL_COMPONENT_TYPES),
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


def _row_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    return (
        str(row.get("entity_id") or ""),
        str(row.get("component_type") or ""),
        str(row.get("source_id") or ""),
        str(row.get("skill_id") or ""),
        str(row.get("stat_id") or ""),
        str(row.get("operation") or ""),
    )
