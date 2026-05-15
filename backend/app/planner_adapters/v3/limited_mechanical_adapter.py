"""Limited v3 candidate mechanical adapter execution.

This module executes only supplied rows that already passed the v3 dry-run
comparison boundary. It does not import, call, or mutate production planner,
combat, crafting, simulation, optimizer, or live stat aggregation code.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .mechanical_dry_run import ACCEPTED_CATEGORIES, BLOCKING_CATEGORIES, REJECTED_CATEGORIES, deterministic_hash


EXECUTED_CATEGORIES = frozenset({"executed_accepted_unchanged", "executed_accepted_dry_run_delta"})
NON_EXECUTED_CATEGORIES = frozenset(
    {
        "rejected_unapproved_delta",
        "blocked_domain_not_allowed",
        "blocked_dry_run_not_accepted",
        "blocked_missing_candidate",
        "blocked_missing_current",
        "blocked_missing_provenance",
        "blocked_unsupported_mechanic",
        "blocked_text_only_mechanic",
        "blocked_scripted_mechanic",
        "blocked_unknown_operation",
        "blocked_unresolved_stat_identity",
        "blocked_unresolved_skill_identity",
        "blocked_ambiguous_skill_identity",
        "blocked_value_normalization",
        "blocked_conditional_semantics",
        "blocked_triggered_semantics",
    }
)
SUPPORTED_DOMAINS = frozenset({"item_affix", "passive_skill"})
GATE_MECHANISM = "explicit_enabled_argument_and_allowed_domains"


class V3LimitedMechanicalAdapter:
    """Execute only accepted dry-run candidate rows behind explicit gates."""

    def execute(
        self,
        *,
        comparison_reports: list[dict[str, Any]],
        enabled: bool = False,
        allowed_domains: set[str] | frozenset[str] | tuple[str, ...] | list[str] | None = None,
        run_id: str = "v3_phase_10_limited_mechanical_adapter",
    ) -> dict[str, Any]:
        normalized_domains = _normalize_allowed_domains(allowed_domains)
        if not enabled:
            return _disabled_envelope(run_id=run_id, allowed_domains=normalized_domains)

        execution_rows: list[dict[str, Any]] = []
        for report in comparison_reports:
            domain = _report_domain(report)
            for row in report.get("comparison_rows", []):
                execution_rows.append(_execution_row(row=row, domain=domain, allowed_domains=normalized_domains))

        execution_rows.sort(key=lambda row: (row["domain"], row["output_key"]))
        aggregates = _aggregate_executed_rows(execution_rows)
        category_counts = Counter(row["execution_category"] for row in execution_rows)
        domain_counts = Counter(row["domain"] for row in execution_rows)

        envelope = {
            "schema_version": "v3.limited_mechanical_adapter.1",
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": {
                "enabled": True,
                "active": True,
                "status": "enabled",
                "gate_mechanism": GATE_MECHANISM,
                "default_enabled": False,
                "experimental": True,
                "production_consumer": False,
                "production_enabled": False,
                "read_only": True,
                "allowed_domains": sorted(normalized_domains),
            },
            "run": {
                "run_id": run_id,
                "comparison_report_count": len(comparison_reports),
                "execution_row_count": len(execution_rows),
                "allowed_domains": sorted(normalized_domains),
            },
            "summary": {
                "executed_row_count": sum(category_counts[c] for c in EXECUTED_CATEGORIES),
                "rejected_row_count": sum(category_counts[c] for c in REJECTED_CATEGORIES),
                "blocked_row_count": sum(category_counts[c] for c in NON_EXECUTED_CATEGORIES if c not in REJECTED_CATEGORIES),
                "aggregate_count": len(aggregates),
                "production_consumed": False,
                "production_planner_output_changed": False,
                "candidate_execution_performed": bool(sum(category_counts[c] for c in EXECUTED_CATEGORIES)),
                "deterministic": True,
            },
            "execution_gate_summary": _execution_gate_summary(normalized_domains),
            "domain_summary": dict(sorted(domain_counts.items())),
            "execution_category_counts": dict(sorted(category_counts.items())),
            "execution_rows": execution_rows,
            "candidate_aggregates": aggregates,
            "blocked_reasons": _blocked_reason_summary(execution_rows),
            "rollback_visibility": _rollback_visibility(run_id=run_id),
            "safety_confirmations": _safety_confirmations(category_counts=category_counts),
            "metadata": {
                "source": "v3_limited_mechanical_adapter",
                "experimental": True,
                "default_enabled": False,
                "production_consumer": False,
                "production_enabled": False,
                "planner_remap_performed": False,
                "live_stat_aggregation_changed": False,
                "deterministic_serializer": "json_sort_keys_sha256",
            },
        }
        envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
        return envelope


def build_sample_limited_adapter_inputs() -> list[dict[str, Any]]:
    from .item_affix_comparison import V3ItemAffixMechanicalComparison, build_sample_item_affix_rows
    from .passive_skill_comparison import V3PassiveSkillMechanicalComparison, build_sample_passive_skill_rows

    item_current, item_candidate = build_sample_item_affix_rows()
    passive_current, passive_candidate = build_sample_passive_skill_rows()
    return [
        V3ItemAffixMechanicalComparison().compare(
            current_rows=item_current,
            candidate_rows=item_candidate,
            enabled=True,
            baseline_snapshot_id="baseline:v3_phase_8_item_affix_sample",
        ),
        V3PassiveSkillMechanicalComparison().compare(
            current_rows=passive_current,
            candidate_rows=passive_candidate,
            enabled=True,
            baseline_snapshot_id="baseline:v3_phase_9_passive_skill_sample",
        ),
    ]


def _execution_row(*, row: dict[str, Any], domain: str, allowed_domains: frozenset[str]) -> dict[str, Any]:
    comparison_category = str(row.get("delta_category"))
    blocked_reasons = list(row.get("blocked_reasons") or [])
    if domain not in allowed_domains:
        execution_category = "blocked_domain_not_allowed"
        blocked_reasons = ["domain_not_allowed_for_limited_adapter"]
        status = "blocked"
    elif comparison_category == "accepted_unchanged":
        execution_category = "executed_accepted_unchanged"
        status = "executed"
    elif comparison_category == "accepted_explicit_dry_run_delta":
        execution_category = "executed_accepted_dry_run_delta"
        status = "executed"
    elif comparison_category in REJECTED_CATEGORIES:
        execution_category = comparison_category
        status = "rejected"
    elif comparison_category in BLOCKING_CATEGORIES:
        execution_category = comparison_category
        status = "blocked"
    else:
        execution_category = "blocked_dry_run_not_accepted"
        blocked_reasons = ["dry_run_category_not_executable"]
        status = "blocked"

    return {
        "domain": domain,
        "output_key": row.get("output_key"),
        "execution_category": execution_category,
        "comparison_category": comparison_category,
        "status": status,
        "candidate_value": row.get("candidate_value"),
        "current_value": row.get("current_value"),
        "provenance": list(row.get("provenance") or []),
        "blocked_reasons": blocked_reasons,
        "gate_evidence": {
            "dry_run_accepted": comparison_category in ACCEPTED_CATEGORIES,
            "domain_allowed": domain in allowed_domains,
            "stable_calculable": comparison_category in ACCEPTED_CATEGORIES,
            "approved_normalization_required": True,
            "approved_operation_semantics_required": True,
            "approved_identity_resolution_required": True,
            "provenance_required": True,
            "comparison_backed": True,
        },
        "metadata": deepcopy(row.get("metadata") or {}),
        "domain_metadata": deepcopy(row.get("item_affix_metadata") or row.get("passive_skill_metadata") or {}),
    }


def _aggregate_executed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], float] = defaultdict(float)
    provenance_by_group: dict[tuple[str, str], set[str]] = defaultdict(set)
    row_keys_by_group: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in rows:
        if row["execution_category"] not in EXECUTED_CATEGORIES:
            continue
        aggregate_key = _aggregate_key(row)
        value = row.get("candidate_value")
        if not isinstance(value, int | float):
            continue
        grouped[(row["domain"], aggregate_key)] += value
        provenance_by_group[(row["domain"], aggregate_key)].update(str(item) for item in row.get("provenance") or [])
        row_keys_by_group[(row["domain"], aggregate_key)].append(str(row.get("output_key")))

    return [
        {
            "domain": domain,
            "aggregate_key": aggregate_key,
            "value": value,
            "source_row_count": len(row_keys_by_group[(domain, aggregate_key)]),
            "source_output_keys": sorted(row_keys_by_group[(domain, aggregate_key)]),
            "provenance": sorted(provenance_by_group[(domain, aggregate_key)]),
        }
        for (domain, aggregate_key), value in sorted(grouped.items())
    ]


def _aggregate_key(row: dict[str, Any]) -> str:
    metadata = row.get("domain_metadata") or row.get("metadata") or {}
    stat_id = metadata.get("stat_id") or row.get("output_key")
    operation = metadata.get("operation") or "unknown"
    return f"{stat_id}::{operation}"


def _report_domain(report: dict[str, Any]) -> str:
    run = report.get("run") or {}
    metadata = report.get("metadata") or {}
    return str(run.get("domain") or metadata.get("domain") or "unknown")


def _normalize_allowed_domains(allowed_domains: set[str] | frozenset[str] | tuple[str, ...] | list[str] | None) -> frozenset[str]:
    if allowed_domains is None:
        return frozenset()
    return frozenset(str(domain) for domain in allowed_domains if str(domain) in SUPPORTED_DOMAINS)


def _execution_gate_summary(allowed_domains: frozenset[str]) -> dict[str, Any]:
    return {
        "dry_run_enabled_required": True,
        "domain_gate_required": True,
        "allowed_domains": sorted(allowed_domains),
        "stable_calculable_required": True,
        "approved_normalization_required": True,
        "approved_operation_semantics_required": True,
        "approved_identity_resolution_required": True,
        "provenance_required": True,
        "accepted_dry_run_category_required": True,
        "unsupported_text_only_scripted_blocked": True,
        "production_consumption_allowed": False,
    }


def _blocked_reason_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for row in rows:
        if row["status"] == "executed":
            continue
        for reason in row["blocked_reasons"] or [row["execution_category"]]:
            counter[str(reason)] += 1
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _rollback_visibility(*, run_id: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "rollback_required_for_production": False,
        "debug_visibility": [
            "deterministic_hash",
            "execution_category_counts",
            "execution_rows",
            "candidate_aggregates",
            "blocked_reasons",
            "safety_confirmations",
        ],
    }


def _safety_confirmations(*, category_counts: Counter[str]) -> dict[str, Any]:
    return {
        "production_consumed": False,
        "production_enabled": False,
        "production_planner_output_changed": False,
        "planner_remap_performed": False,
        "live_stat_aggregation_changed": False,
        "combat_simulation_changed": False,
        "crafting_behavior_changed": False,
        "optimizer_behavior_changed": False,
        "unsupported_mechanics_promoted": False,
        "text_only_mechanics_promoted": False,
        "scripted_mechanics_promoted": False,
        "unknown_operations_promoted": False,
        "unresolved_identities_promoted": False,
        "candidate_execution_default_enabled": False,
        "executed_row_count": sum(category_counts[c] for c in EXECUTED_CATEGORIES),
    }


def _disabled_envelope(*, run_id: str, allowed_domains: frozenset[str]) -> dict[str, Any]:
    envelope = {
        "schema_version": "v3.limited_mechanical_adapter.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": {
            "enabled": False,
            "active": False,
            "status": "disabled",
            "gate_mechanism": GATE_MECHANISM,
            "default_enabled": False,
            "experimental": True,
            "production_consumer": False,
            "production_enabled": False,
            "read_only": True,
            "allowed_domains": sorted(allowed_domains),
        },
        "run": {
            "run_id": run_id,
            "comparison_report_count": 0,
            "execution_row_count": 0,
            "allowed_domains": sorted(allowed_domains),
        },
        "summary": {
            "executed_row_count": 0,
            "rejected_row_count": 0,
            "blocked_row_count": 0,
            "aggregate_count": 0,
            "production_consumed": False,
            "production_planner_output_changed": False,
            "candidate_execution_performed": False,
            "deterministic": True,
        },
        "execution_gate_summary": _execution_gate_summary(allowed_domains),
        "domain_summary": {},
        "execution_category_counts": {},
        "execution_rows": [],
        "candidate_aggregates": [],
        "blocked_reasons": [],
        "rollback_visibility": _rollback_visibility(run_id=run_id),
        "safety_confirmations": _safety_confirmations(category_counts=Counter()),
        "metadata": {
            "source": "v3_limited_mechanical_adapter",
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "production_enabled": False,
            "planner_remap_performed": False,
            "live_stat_aggregation_changed": False,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    envelope["deterministic_hash"] = deterministic_hash(_stable_envelope(envelope))
    return envelope


def _stable_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(envelope)
    stable.pop("generated_at", None)
    stable.pop("deterministic_hash", None)
    return stable
