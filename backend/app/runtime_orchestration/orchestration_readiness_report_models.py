"""Stable report models for v3.5 orchestration readiness evaluation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


@dataclass(frozen=True)
class OrchestrationReadinessBlocker:
    blocker_id: str
    readiness_status: str
    blocker_category: str
    deterministic_rank: int
    fail_visible: bool
    audit_safe: bool
    explanation: str


@dataclass(frozen=True)
class OrchestrationReadinessResult:
    readiness_status: str
    planning_ready: bool
    planning_only: bool
    blockers: tuple[OrchestrationReadinessBlocker, ...]
    unsupported_states: tuple[str, ...]
    prohibited_domains: tuple[str, ...]
    missing_governance_dependencies: tuple[str, ...]
    missing_replay_requirements: tuple[str, ...]
    missing_rollback_requirements: tuple[str, ...]
    compatibility_failures: tuple[str, ...]
    environment_failures: tuple[str, ...]
    manual_review_reasons: tuple[str, ...]
    deterministic_explanation_summary: str
    runtime_execution_enabled: bool
    orchestration_execution_enabled: bool
    routing_behavior_enabled: bool
    mutation_behavior_enabled: bool
    audit_log_writing_enabled: bool
    production_consumption_enabled: bool


def order_readiness_blockers(
    blockers: tuple[OrchestrationReadinessBlocker, ...],
) -> tuple[OrchestrationReadinessBlocker, ...]:
    return tuple(sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))


def export_readiness_result(result: OrchestrationReadinessResult) -> dict[str, Any]:
    data = asdict(result)
    data["blockers"] = [asdict(row) for row in order_readiness_blockers(result.blockers)]
    for field in (
        "unsupported_states",
        "prohibited_domains",
        "missing_governance_dependencies",
        "missing_replay_requirements",
        "missing_rollback_requirements",
        "compatibility_failures",
        "environment_failures",
        "manual_review_reasons",
    ):
        data[field] = list(data[field])
    data["deterministic_hash"] = hash_readiness_result(result)
    return data


def serialize_readiness_result(result: OrchestrationReadinessResult) -> str:
    return stable_serialize(export_readiness_result(result))


def hash_readiness_result(result: OrchestrationReadinessResult) -> str:
    payload = asdict(result)
    payload["blockers"] = [asdict(row) for row in order_readiness_blockers(result.blockers)]
    return deterministic_hash(_without_hash(payload))


def _without_hash(payload: dict[str, Any]) -> dict[str, Any]:
    stable = deepcopy(payload)
    stable.pop("deterministic_hash", None)
    return stable
