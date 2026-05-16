"""Deterministic boundary models for v3.5 orchestration governance planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


ALLOWED_ORCHESTRATION_DOMAINS = (
    "governance_consumption_planning",
    "audit_evidence_collection",
    "readiness_summary_preparation",
)

PROHIBITED_ORCHESTRATION_DOMAINS = (
    "runtime_execution",
    "orchestration_execution",
    "autonomous_orchestration",
    "decision_routing",
    "recommendation_system",
    "production_routing",
    "persistent_mutation",
    "state_write",
    "audit_log_write",
    "external_side_effect",
    "experiment_execution",
    "production_authoritative_manifest",
    "production_runtime_consumption",
    "self_modifying_orchestration",
)

UNSUPPORTED_ORCHESTRATION_STATES = (
    "unknown_governance_dependency",
    "missing_authorization_context",
    "missing_replay_lineage",
    "missing_rollback_lineage",
    "unverified_environment_isolation",
    "unsupported_orchestration_scope",
)


@dataclass(frozen=True)
class OrchestrationBoundaryModel:
    boundary_id: str
    allowed_orchestration_domains: tuple[str, ...]
    prohibited_orchestration_domains: tuple[str, ...]
    isolated_orchestration_scopes: tuple[str, ...]
    unsupported_orchestration_states: tuple[str, ...]
    governance_escalation_required: bool
    manual_review_required: bool
    deterministic_fail_visible_blockers: bool


def default_orchestration_boundary_model() -> OrchestrationBoundaryModel:
    return OrchestrationBoundaryModel(
        boundary_id="v3-5-governance-consumption-boundary",
        allowed_orchestration_domains=ALLOWED_ORCHESTRATION_DOMAINS,
        prohibited_orchestration_domains=PROHIBITED_ORCHESTRATION_DOMAINS,
        isolated_orchestration_scopes=("non_production_governance_planning",),
        unsupported_orchestration_states=UNSUPPORTED_ORCHESTRATION_STATES,
        governance_escalation_required=True,
        manual_review_required=False,
        deterministic_fail_visible_blockers=True,
    )


def export_orchestration_boundary(boundary: OrchestrationBoundaryModel) -> dict[str, Any]:
    return asdict(boundary)


def serialize_orchestration_boundary(boundary: OrchestrationBoundaryModel) -> str:
    return stable_serialize(export_orchestration_boundary(boundary))


def hash_orchestration_boundary(boundary: OrchestrationBoundaryModel) -> str:
    return deterministic_hash(export_orchestration_boundary(boundary))
