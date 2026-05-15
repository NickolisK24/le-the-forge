"""Read-only v3 mechanical dry-run comparison envelopes.

This module compares supplied current-planner snapshots with supplied v3
candidate snapshots. It does not import, call, or mutate production planner,
simulation, crafting, combat, optimizer, or stat aggregation code.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any


DELTA_CATEGORIES = frozenset(
    {
        "accepted_unchanged",
        "accepted_explicit_dry_run_delta",
        "rejected_unapproved_delta",
        "blocked_missing_candidate",
        "blocked_missing_current",
        "blocked_missing_provenance",
        "blocked_unsupported_mechanic",
        "blocked_text_only_mechanic",
        "blocked_scripted_mechanic",
        "blocked_unknown_operation",
        "blocked_unresolved_stat_identity",
        "blocked_value_normalization",
    }
)

BLOCKING_CATEGORIES = frozenset(
    {
        "blocked_missing_candidate",
        "blocked_missing_current",
        "blocked_missing_provenance",
        "blocked_unsupported_mechanic",
        "blocked_text_only_mechanic",
        "blocked_scripted_mechanic",
        "blocked_unknown_operation",
        "blocked_unresolved_stat_identity",
        "blocked_value_normalization",
    }
)

REJECTED_CATEGORIES = frozenset({"rejected_unapproved_delta"})
ACCEPTED_CATEGORIES = frozenset({"accepted_unchanged", "accepted_explicit_dry_run_delta"})
GATE_MECHANISM = "explicit_enabled_argument"


class V3ExperimentalMechanicalDryRun:
    """Opt-in comparison layer for current output versus candidate output."""

    def compare(
        self,
        *,
        current_output: dict[str, Any],
        candidate_output: dict[str, Any],
        enabled: bool = False,
        baseline_snapshot_id: str | None = None,
        run_id: str = "v3_phase_7_foundation",
    ) -> dict[str, Any]:
        if not enabled:
            return _disabled_envelope(run_id=run_id)

        current_values = _normalize_output_map(current_output.get("values", {}))
        candidate_values = _normalize_output_map(candidate_output.get("values", {}))
        comparison_rows = [
            _classify_row(
                output_key=output_key,
                current_entry=current_values.get(output_key),
                candidate_entry=candidate_values.get(output_key),
                baseline_snapshot_id=baseline_snapshot_id,
            )
            for output_key in sorted(set(current_values) | set(candidate_values))
        ]
        category_counts = Counter(row["delta_category"] for row in comparison_rows)
        safety = _safety_confirmations(comparison_rows=comparison_rows)

        envelope = {
            "schema_version": "v3.experimental_mechanical_dry_run.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": {
                "enabled": True,
                "active": True,
                "status": "enabled",
                "gate_mechanism": GATE_MECHANISM,
                "default_enabled": False,
                "read_only": True,
                "experimental": True,
                "production_consumer": False,
                "production_enabled": False,
            },
            "run": {
                "run_id": run_id,
                "baseline_snapshot_id": baseline_snapshot_id,
                "current_snapshot_id": current_output.get("snapshot_id"),
                "candidate_snapshot_id": candidate_output.get("snapshot_id"),
                "comparison_row_count": len(comparison_rows),
            },
            "summary": {
                "current_output_count": len(current_values),
                "candidate_output_count": len(candidate_values),
                "accepted_delta_count": sum(category_counts[c] for c in ACCEPTED_CATEGORIES),
                "rejected_delta_count": sum(category_counts[c] for c in REJECTED_CATEGORIES),
                "blocked_delta_count": sum(category_counts[c] for c in BLOCKING_CATEGORIES),
                "production_consumed": False,
                "production_planner_output_changed": False,
                "mechanical_calculations_performed": False,
                "deterministic": True,
            },
            "delta_category_counts": dict(sorted(category_counts.items())),
            "comparison_rows": comparison_rows,
            "blocked_reasons": _blocked_reason_summary(comparison_rows),
            "rollback_visibility": _rollback_visibility(run_id=run_id, baseline_snapshot_id=baseline_snapshot_id),
            "safety_confirmations": safety,
            "metadata": {
                "source": "v3_experimental_mechanical_dry_run",
                "read_only": True,
                "experimental": True,
                "default_enabled": False,
                "production_consumer": False,
                "planner_remap_performed": False,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_without_generated_at(envelope))
        return envelope


def build_sample_v3_dry_run_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a deterministic fixture that exercises each safety category."""

    current = {
        "snapshot_id": "current_planner_baseline_sample",
        "values": {
            "damage.fire.flat": {"value": 10, "provenance": ["current:fixture"]},
            "damage.fire.increased": {"value": 20, "provenance": ["current:fixture"]},
            "defense.armor.flat": {"value": 30, "provenance": ["current:fixture"]},
            "skill.fireball.scripted": {"value": 1, "provenance": ["current:fixture"]},
            "skill.unknown.text": {"value": 1, "provenance": ["current:fixture"]},
            "stat.identity.unknown": {"value": 5, "provenance": ["current:fixture"]},
            "operation.unknown": {"value": 7, "provenance": ["current:fixture"]},
            "value.source_unit": {"value": 2, "provenance": ["current:fixture"]},
            "candidate.missing": {"value": 3, "provenance": ["current:fixture"]},
            "missing.provenance": {"value": 8, "provenance": ["current:fixture"]},
            "unsupported.mechanic": {"value": 9, "provenance": ["current:fixture"]},
        },
    }
    candidate = {
        "snapshot_id": "v3_candidate_sample",
        "values": {
            "damage.fire.flat": {
                "value": 10,
                "provenance": ["candidate:fixture"],
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "damage.fire.increased": {
                "value": 25,
                "provenance": ["candidate:fixture", "baseline:approved_delta_sample"],
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
                "approval_status": "accepted_dry_run_delta",
            },
            "defense.armor.flat": {
                "value": 35,
                "provenance": ["candidate:fixture"],
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "skill.fireball.scripted": {
                "value": 1,
                "provenance": ["candidate:fixture"],
                "support_status": "scripted",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "skill.unknown.text": {
                "value": 1,
                "provenance": ["candidate:fixture"],
                "support_status": "text_only",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "stat.identity.unknown": {
                "value": 5,
                "provenance": ["candidate:fixture"],
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "unresolved",
                "value_normalization_status": "approved",
            },
            "operation.unknown": {
                "value": 7,
                "provenance": ["candidate:fixture"],
                "support_status": "supported",
                "operation_status": "unknown",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "value.source_unit": {
                "value": 2,
                "provenance": ["candidate:fixture"],
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "audit_only",
            },
            "candidate.added": {
                "value": 4,
                "provenance": ["candidate:fixture"],
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "missing.provenance": {
                "value": 8,
                "support_status": "supported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
            "unsupported.mechanic": {
                "value": 9,
                "provenance": ["candidate:fixture"],
                "support_status": "unsupported",
                "operation_status": "known",
                "stat_identity_status": "resolved",
                "value_normalization_status": "approved",
            },
        },
    }
    return current, candidate


def deterministic_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _classify_row(
    *,
    output_key: str,
    current_entry: dict[str, Any] | None,
    candidate_entry: dict[str, Any] | None,
    baseline_snapshot_id: str | None,
) -> dict[str, Any]:
    if current_entry is None:
        category = "blocked_missing_current"
        reasons = ["missing_current_output"]
    elif candidate_entry is None:
        category = "blocked_missing_candidate"
        reasons = ["missing_candidate_output"]
    else:
        category, reasons = _candidate_gate_status(candidate_entry)
        if not reasons:
            current_value = current_entry.get("value")
            candidate_value = candidate_entry.get("value")
            if current_value == candidate_value:
                category = "accepted_unchanged"
            elif (
                candidate_entry.get("approval_status") == "accepted_dry_run_delta"
                and baseline_snapshot_id
                and candidate_entry.get("provenance")
            ):
                category = "accepted_explicit_dry_run_delta"
            else:
                category = "rejected_unapproved_delta"
                reasons = ["candidate_delta_not_approved_for_dry_run"]

    return {
        "output_key": output_key,
        "delta_category": category,
        "status": _status_for_category(category),
        "current_value": None if current_entry is None else current_entry.get("value"),
        "candidate_value": None if candidate_entry is None else candidate_entry.get("value"),
        "provenance": [] if candidate_entry is None else list(candidate_entry.get("provenance") or []),
        "blocked_reasons": reasons,
        "metadata": {
            "current_present": current_entry is not None,
            "candidate_present": candidate_entry is not None,
            "candidate_support_status": None if candidate_entry is None else candidate_entry.get("support_status"),
            "candidate_operation_status": None if candidate_entry is None else candidate_entry.get("operation_status"),
            "candidate_stat_identity_status": None if candidate_entry is None else candidate_entry.get("stat_identity_status"),
            "candidate_value_normalization_status": None
            if candidate_entry is None
            else candidate_entry.get("value_normalization_status"),
        },
    }


def _candidate_gate_status(candidate_entry: dict[str, Any]) -> tuple[str, list[str]]:
    if not candidate_entry.get("provenance"):
        return "blocked_missing_provenance", ["missing_candidate_provenance"]

    support_status = str(candidate_entry.get("support_status") or "unknown").lower()
    if support_status == "unsupported":
        return "blocked_unsupported_mechanic", ["unsupported_mechanic"]
    if support_status == "text_only":
        return "blocked_text_only_mechanic", ["text_only_mechanic"]
    if support_status == "scripted":
        return "blocked_scripted_mechanic", ["scripted_mechanic"]

    operation_status = str(candidate_entry.get("operation_status") or "unknown").lower()
    if operation_status != "known":
        return "blocked_unknown_operation", ["unknown_operation_semantics"]

    stat_identity_status = str(candidate_entry.get("stat_identity_status") or "unresolved").lower()
    if stat_identity_status != "resolved":
        return "blocked_unresolved_stat_identity", ["unresolved_stat_identity"]

    value_status = str(candidate_entry.get("value_normalization_status") or "audit_only").lower()
    if value_status != "approved":
        return "blocked_value_normalization", [f"value_normalization_{value_status}"]

    return "", []


def _normalize_output_map(values: dict[str, Any]) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in values.items():
        if isinstance(value, dict):
            normalized[str(key)] = deepcopy(value)
        else:
            normalized[str(key)] = {"value": value, "provenance": []}
    return normalized


def _blocked_reason_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for row in rows:
        for reason in row["blocked_reasons"]:
            counter[str(reason)] += 1
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _safety_confirmations(*, comparison_rows: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts = Counter(row["delta_category"] for row in comparison_rows)
    return {
        "production_consumed": False,
        "production_enabled": False,
        "production_planner_output_changed": False,
        "planner_remap_performed": False,
        "mechanical_calculations_performed": False,
        "candidate_inputs_only": True,
        "production_planner_imported": False,
        "crafting_behavior_changed": False,
        "simulation_behavior_changed": False,
        "stat_aggregation_behavior_changed": False,
        "value_normalization_promoted": False,
        "unsupported_mechanics_promoted": False,
        "text_only_mechanics_promoted": False,
        "scripted_mechanics_promoted": False,
        "blocked_delta_count": sum(category_counts[c] for c in BLOCKING_CATEGORIES),
        "rejected_delta_count": sum(category_counts[c] for c in REJECTED_CATEGORIES),
        "accepted_delta_count": sum(category_counts[c] for c in ACCEPTED_CATEGORIES),
    }


def _rollback_visibility(*, run_id: str, baseline_snapshot_id: str | None) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "baseline_snapshot_id": baseline_snapshot_id,
        "rollback_required_for_production": False,
        "debug_visibility": [
            "deterministic_hash",
            "delta_category_counts",
            "blocked_reasons",
            "comparison_rows",
            "safety_confirmations",
        ],
    }


def _disabled_envelope(*, run_id: str) -> dict[str, Any]:
    envelope = {
        "schema_version": "v3.experimental_mechanical_dry_run.1",
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
            "baseline_snapshot_id": None,
            "current_snapshot_id": None,
            "candidate_snapshot_id": None,
            "comparison_row_count": 0,
        },
        "summary": {
            "current_output_count": 0,
            "candidate_output_count": 0,
            "accepted_delta_count": 0,
            "rejected_delta_count": 0,
            "blocked_delta_count": 0,
            "production_consumed": False,
            "production_planner_output_changed": False,
            "mechanical_calculations_performed": False,
            "deterministic": True,
        },
        "delta_category_counts": {},
        "comparison_rows": [],
        "blocked_reasons": [],
        "rollback_visibility": _rollback_visibility(run_id=run_id, baseline_snapshot_id=None),
        "safety_confirmations": _safety_confirmations(comparison_rows=[]),
        "metadata": {
            "source": "v3_experimental_mechanical_dry_run",
            "read_only": True,
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(_without_generated_at(envelope))
    return envelope


def _status_for_category(category: str) -> str:
    if category in ACCEPTED_CATEGORIES:
        return "accepted"
    if category in REJECTED_CATEGORIES:
        return "rejected"
    return "blocked"


def _without_generated_at(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
