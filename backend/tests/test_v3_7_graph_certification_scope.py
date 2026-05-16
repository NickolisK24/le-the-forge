from __future__ import annotations

from dataclasses import replace

from app.runtime_orchestration.v3_7_graph_certification_models import (
    hash_v3_7_graph_certification_scope,
    serialize_v3_7_graph_certification_scope,
)
from app.runtime_orchestration.v3_7_graph_certification_scope import (
    build_v3_7_graph_certification_identity,
    build_v3_7_graph_certification_scope,
    certification_scope_is_complete,
    graph_certification_identities_are_unique,
    graph_certification_identity_key,
    graph_certification_scope_identities_are_unique,
    graph_certification_scope_identity_key,
)


def test_certification_and_scope_identity_are_stable():
    identity = build_v3_7_graph_certification_identity()
    scope = build_v3_7_graph_certification_scope(identity)

    assert identity.stable_identity_key == graph_certification_identity_key(identity)
    assert scope.identity.stable_identity_key == graph_certification_scope_identity_key(scope.identity)
    assert graph_certification_identities_are_unique((identity,)) is True
    assert graph_certification_identities_are_unique((identity, identity)) is False
    assert graph_certification_scope_identities_are_unique((scope.identity,)) is True
    assert graph_certification_scope_identities_are_unique((scope.identity, scope.identity)) is False


def test_certification_scope_covers_full_stack():
    scope = build_v3_7_graph_certification_scope()
    reference_types = {reference.reference_type for reference in scope.references}

    assert reference_types == {
        "graph_foundations",
        "governance",
        "compatibility",
        "evaluation",
        "session",
        "scenario",
        "aggregation",
        "integrity",
    }
    assert certification_scope_is_complete(scope) is True
    assert scope.scope_is_non_executable is True
    assert scope.scope_does_not_mark_runtime_readiness is True


def test_certification_scope_detects_incomplete_references():
    scope = build_v3_7_graph_certification_scope()
    incomplete = replace(scope, references=tuple(reference for reference in scope.references if reference.reference_type != "integrity"))

    assert certification_scope_is_complete(incomplete) is False


def test_certification_scope_serialization_and_hash_are_stable():
    scope = build_v3_7_graph_certification_scope()
    reordered = replace(scope, references=tuple(reversed(scope.references)), metadata=tuple(reversed(scope.metadata)))

    assert serialize_v3_7_graph_certification_scope(scope) == serialize_v3_7_graph_certification_scope(reordered)
    assert hash_v3_7_graph_certification_scope(scope) == hash_v3_7_graph_certification_scope(reordered)
