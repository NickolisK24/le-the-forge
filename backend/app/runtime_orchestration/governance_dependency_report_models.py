"""Stable report models for v3.5 governance dependency resolution."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .governance_dependency_models import GovernanceDependencyContract, export_governance_dependency_contract


@dataclass(frozen=True)
class GovernanceDependencyBlocker:
    blocker_id: str
    dependency_status: str
    blocker_category: str
    deterministic_rank: int
    fail_visible: bool
    audit_safe: bool
    explanation: str


@dataclass(frozen=True)
class GovernanceDependencyResolutionResult:
    dependency_id: str
    dependency_status: str
    planning_only: bool
    satisfied_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    blockers: tuple[GovernanceDependencyBlocker, ...]
    unsupported_reasons: tuple[str, ...]
    prohibited_reasons: tuple[str, ...]
    manual_review_reasons: tuple[str, ...]
    compatibility_failures: tuple[str, ...]
    environment_mismatches: tuple[str, ...]
    lineage_gaps: tuple[str, ...]
    lineage_propagation: dict[str, Any]
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool
    orchestration_execution_enabled: bool
    routing_behavior_enabled: bool
    mutation_behavior_enabled: bool
    audit_log_writing_enabled: bool
    production_consumption_enabled: bool
    external_dependency_fetching_enabled: bool
    automatic_remediation_enabled: bool
    contract: GovernanceDependencyContract


def order_dependency_blockers(
    blockers: tuple[GovernanceDependencyBlocker, ...],
) -> tuple[GovernanceDependencyBlocker, ...]:
    return tuple(sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))


def export_dependency_resolution_result(result: GovernanceDependencyResolutionResult) -> dict[str, Any]:
    data = asdict(result)
    data["blockers"] = [asdict(row) for row in order_dependency_blockers(result.blockers)]
    data["contract"] = export_governance_dependency_contract(result.contract)
    for field in (
        "satisfied_evidence",
        "missing_evidence",
        "unsupported_reasons",
        "prohibited_reasons",
        "manual_review_reasons",
        "compatibility_failures",
        "environment_mismatches",
        "lineage_gaps",
    ):
        data[field] = list(data[field])
    data["deterministic_hash"] = hash_dependency_resolution_result(result)
    return data


def serialize_dependency_resolution_result(result: GovernanceDependencyResolutionResult) -> str:
    return stable_serialize(export_dependency_resolution_result(result))


def hash_dependency_resolution_result(result: GovernanceDependencyResolutionResult) -> str:
    payload = asdict(result)
    payload["blockers"] = [asdict(row) for row in order_dependency_blockers(result.blockers)]
    payload["contract"] = export_governance_dependency_contract(result.contract)
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
