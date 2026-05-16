"""Deterministic integrity policies for v3.7 graph planning evidence."""

from __future__ import annotations

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_integrity_models import (
    V3_7_GRAPH_INTEGRITY_PHASE_ID,
    V37GraphIntegrityPolicy,
    V37GraphIntegrityPolicyIdentity,
    V37GraphIntegrityPolicyMetadata,
    V37GraphIntegrityPolicyRequirement,
)
from .v3_7_graph_models import default_v3_7_graph_provenance


DEFAULT_V37_GRAPH_INTEGRITY_POLICY_ID = "v3_7_graph_integrity_policy_default"


def build_v3_7_graph_integrity_policy_identity() -> V37GraphIntegrityPolicyIdentity:
    key_payload = {
        "policy_id": DEFAULT_V37_GRAPH_INTEGRITY_POLICY_ID,
        "policy_version": "v3.7",
        "phase_id": V3_7_GRAPH_INTEGRITY_PHASE_ID,
    }
    return V37GraphIntegrityPolicyIdentity(
        policy_id=DEFAULT_V37_GRAPH_INTEGRITY_POLICY_ID,
        policy_version="v3.7",
        phase_id=V3_7_GRAPH_INTEGRITY_PHASE_ID,
        stable_identity_key=deterministic_hash(key_payload),
    )


def graph_integrity_policy_identity_key(identity: V37GraphIntegrityPolicyIdentity) -> str:
    return deterministic_hash(
        {
            "policy_id": identity.policy_id,
            "policy_version": identity.policy_version,
            "phase_id": identity.phase_id,
        }
    )


def graph_integrity_policy_identities_are_unique(
    identities: tuple[V37GraphIntegrityPolicyIdentity, ...],
) -> bool:
    keys = [identity.stable_identity_key for identity in identities]
    return len(keys) == len(set(keys))


def build_v3_7_graph_integrity_policy() -> V37GraphIntegrityPolicy:
    identity = build_v3_7_graph_integrity_policy_identity()
    requirements = (
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_graph_evidence",
            "evidence_source",
            "graph_foundations",
            "graph foundation evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_governance_evidence",
            "evidence_source",
            "governance",
            "governance boundary evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_compatibility_evidence",
            "evidence_source",
            "compatibility",
            "compatibility reasoning evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_evaluation_evidence",
            "evidence_source",
            "evaluation",
            "evaluation reasoning evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_session_evidence",
            "evidence_source",
            "session",
            "planning session evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_scenario_evidence",
            "evidence_source",
            "scenario",
            "planning scenario evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_aggregation_evidence",
            "evidence_source",
            "aggregation",
            "planning intelligence aggregation evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_replay_continuity",
            "continuity",
            "replay",
            "replay continuity evidence must remain non-executable and referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_rollback_continuity",
            "continuity",
            "rollback",
            "rollback continuity evidence must remain referenced",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_provenance_continuity",
            "provenance",
            "provenance",
            "provenance continuity must remain complete",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_explainability_continuity",
            "explainability",
            "explainability",
            "explainability continuity must remain complete",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_fail_visible_findings",
            "finding_visibility",
            "fail_visible",
            "prohibited, unsupported, unknown, blocked, and warning evidence must remain visible",
        ),
        V37GraphIntegrityPolicyRequirement(
            "v3_7_integrity_requires_execution_boundary",
            "execution_boundary",
            "non_executable",
            "integrity enforcement must block execution-boundary violations",
        ),
    )
    return V37GraphIntegrityPolicy(
        identity=identity,
        metadata=(
            V37GraphIntegrityPolicyMetadata("policy_semantics", "deterministic_planning_integrity_validation"),
            V37GraphIntegrityPolicyMetadata("runtime_capability", "none"),
            V37GraphIntegrityPolicyMetadata("validity_boundary", "valid_evidence_does_not_authorize_execution"),
        ),
        requirements=requirements,
        provenance=default_v3_7_graph_provenance(identity.policy_id, "graph_planning_integrity_policy"),
        execution_boundary_requirements=(
            "execution_authorization",
            "routing_authorization",
            "scheduling_authorization",
            "dispatch_authorization",
            "traversal_authorization",
            "runtime_path_selection",
            "scenario_execution_selection",
            "optimization_for_execution",
            "recommendation_to_execute",
            "callable_execution_flow_reference",
        ),
    )
