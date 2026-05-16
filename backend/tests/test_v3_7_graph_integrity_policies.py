from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_integrity_models import (
    hash_v3_7_graph_integrity_policy,
    serialize_v3_7_graph_integrity_policy,
)
from app.runtime_orchestration.v3_7_graph_integrity_policies import (
    build_v3_7_graph_integrity_policy,
    graph_integrity_policy_identities_are_unique,
    graph_integrity_policy_identity_key,
)


def test_integrity_policy_identity_is_stable_and_unique():
    policy = build_v3_7_graph_integrity_policy()

    assert policy.identity.stable_identity_key == graph_integrity_policy_identity_key(policy.identity)
    assert graph_integrity_policy_identities_are_unique((policy.identity,)) is True
    assert graph_integrity_policy_identities_are_unique((policy.identity, policy.identity)) is False


def test_integrity_policy_requirements_cover_all_evidence_layers():
    policy = build_v3_7_graph_integrity_policy()
    required_types = {requirement.required_reference_type for requirement in policy.requirements}

    assert {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
        "aggregation",
        "replay",
        "rollback",
        "provenance",
        "explainability",
        "fail_visible",
        "non_executable",
    }.issubset(required_types)
    assert policy.policy_is_non_executable is True
    assert policy.valid_integrity_does_not_authorize_execution is True
    assert policy.execution_boundary_violations_blocked is True


def test_integrity_policy_serialization_and_hash_are_stable():
    policy = build_v3_7_graph_integrity_policy()

    assert serialize_v3_7_graph_integrity_policy(policy) == serialize_v3_7_graph_integrity_policy(policy)
    assert hash_v3_7_graph_integrity_policy(policy) == hash_v3_7_graph_integrity_policy(policy)
    assert policy.execution_authorization_enabled is False
    assert policy.routing_authorization_enabled is False
    assert policy.dispatch_authorization_enabled is False
