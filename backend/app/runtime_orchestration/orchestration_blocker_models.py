"""Deterministic blocker models for v3.5 orchestration governance planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


GOVERNANCE_CHAIN_FAILURE = "governance_chain_failure"
AUTHORIZATION_FAILURE = "authorization_failure"
COMPATIBILITY_FAILURE = "compatibility_failure"
REPLAY_LINEAGE_FAILURE = "replay_lineage_failure"
ROLLBACK_LINEAGE_FAILURE = "rollback_lineage_failure"
ENVIRONMENT_FAILURE = "environment_failure"
UNSUPPORTED_ORCHESTRATION_REQUEST = "unsupported_orchestration_request"
PROHIBITED_ORCHESTRATION_REQUEST = "prohibited_orchestration_request"


@dataclass(frozen=True)
class OrchestrationBlockerModel:
    blocker_id: str
    blocker_category: str
    deterministic_rank: int
    fail_visible: bool
    audit_safe: bool
    explicit: bool
    remediation_required: str


def default_orchestration_blockers() -> tuple[OrchestrationBlockerModel, ...]:
    return (
        OrchestrationBlockerModel(
            "governance_chain_dependency_missing",
            GOVERNANCE_CHAIN_FAILURE,
            10,
            True,
            True,
            True,
            "provide explicit governance dependency evidence before orchestration planning",
        ),
        OrchestrationBlockerModel(
            "authorization_state_missing",
            AUTHORIZATION_FAILURE,
            20,
            True,
            True,
            True,
            "provide explicit non-production authorization before orchestration planning",
        ),
        OrchestrationBlockerModel(
            "compatibility_evidence_missing",
            COMPATIBILITY_FAILURE,
            30,
            True,
            True,
            True,
            "provide deterministic compatibility evidence before orchestration planning",
        ),
        OrchestrationBlockerModel(
            "replay_lineage_missing",
            REPLAY_LINEAGE_FAILURE,
            40,
            True,
            True,
            True,
            "provide replay lineage before orchestration planning",
        ),
        OrchestrationBlockerModel(
            "rollback_lineage_missing",
            ROLLBACK_LINEAGE_FAILURE,
            50,
            True,
            True,
            True,
            "provide rollback lineage before orchestration planning",
        ),
        OrchestrationBlockerModel(
            "environment_isolation_missing",
            ENVIRONMENT_FAILURE,
            60,
            True,
            True,
            True,
            "provide isolated non-production environment evidence before orchestration planning",
        ),
        OrchestrationBlockerModel(
            "unsupported_orchestration_state",
            UNSUPPORTED_ORCHESTRATION_REQUEST,
            70,
            True,
            True,
            True,
            "preserve unsupported state visibility and require explicit review",
        ),
        OrchestrationBlockerModel(
            "prohibited_orchestration_domain",
            PROHIBITED_ORCHESTRATION_REQUEST,
            80,
            True,
            True,
            True,
            "block prohibited orchestration domains without fallback",
        ),
    )


def order_orchestration_blockers(blockers: tuple[OrchestrationBlockerModel, ...]) -> tuple[OrchestrationBlockerModel, ...]:
    return tuple(sorted(blockers, key=lambda row: (row.deterministic_rank, row.blocker_id)))


def export_orchestration_blockers(blockers: tuple[OrchestrationBlockerModel, ...]) -> list[dict[str, Any]]:
    return [asdict(row) for row in order_orchestration_blockers(blockers)]


def serialize_orchestration_blockers(blockers: tuple[OrchestrationBlockerModel, ...]) -> str:
    return stable_serialize(export_orchestration_blockers(blockers))


def hash_orchestration_blockers(blockers: tuple[OrchestrationBlockerModel, ...]) -> str:
    return deterministic_hash(export_orchestration_blockers(blockers))
