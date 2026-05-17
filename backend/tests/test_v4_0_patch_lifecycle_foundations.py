from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.lifecycle_equality import (  # noqa: E402
    patch_identities_equal,
    patch_lifecycle_foundations_equal,
)
from operational_lifecycle.lifecycle_hashing import (  # noqa: E402
    hash_patch_identity,
    hash_patch_lifecycle_foundation,
)
from operational_lifecycle.lifecycle_identity import (  # noqa: E402
    lifecycle_identity_key,
    normalize_patch_identity,
    patch_identity_normalization_report,
)
from operational_lifecycle.lifecycle_lineage import (  # noqa: E402
    lifecycle_lineage_key,
    normalize_lifecycle_lineage,
    validate_lifecycle_lineage_continuity,
)
from operational_lifecycle.lifecycle_models import (  # noqa: E402
    LIFECYCLE_STATE_BLOCKED,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_EXPERIMENTAL,
    LIFECYCLE_STATE_PROHIBITED,
    LIFECYCLE_STATE_SUPPORTED,
    LIFECYCLE_STATE_UNKNOWN,
    LIFECYCLE_STATE_UNSUPPORTED,
    V4_0_PATCH_LIFECYCLE_SCHEMA_VERSION,
    V4_0_PATCH_LIFECYCLE_STATUS_STABLE,
    default_patch_lifecycle_foundation,
)
from operational_lifecycle.lifecycle_provenance import (  # noqa: E402
    lifecycle_provenance_key,
    normalize_lifecycle_provenance,
    validate_lifecycle_provenance_continuity,
)
from operational_lifecycle.lifecycle_serialization import (  # noqa: E402
    export_patch_lifecycle_foundation,
    serialize_patch_lifecycle_foundation,
)
from operational_lifecycle.lifecycle_visibility import (  # noqa: E402
    count_lifecycle_states,
    validate_lifecycle_visibility,
)
from scripts.report_v4_0_patch_lifecycle_foundations import (  # noqa: E402
    build_v4_0_patch_lifecycle_foundations_report,
)


def test_v4_0_patch_lifecycle_models_are_immutable_and_non_executable():
    foundation = default_patch_lifecycle_foundation()

    with pytest.raises(FrozenInstanceError):
        foundation.patch_execution_enabled = True

    assert foundation.patch_identity.schema_version == V4_0_PATCH_LIFECYCLE_SCHEMA_VERSION
    assert foundation.non_executable is True
    assert foundation.descriptive_only is True
    assert foundation.lifecycle_execution_enabled is False
    assert foundation.patch_execution_enabled is False
    assert foundation.patch_application_enabled is False
    assert foundation.deployment_execution_enabled is False
    assert foundation.scheduling_enabled is False
    assert foundation.routing_enabled is False
    assert foundation.dispatch_enabled is False
    assert foundation.optimization_enabled is False
    assert foundation.recommendation_enabled is False
    assert foundation.ranking_enabled is False
    assert foundation.scoring_enabled is False
    assert foundation.selection_enabled is False
    assert foundation.authorization_enabled is False
    assert foundation.approval_enabled is False
    assert foundation.remediation_enabled is False
    assert foundation.repair_enabled is False
    assert foundation.autonomous_behavior_enabled is False
    assert foundation.runtime_mutation_enabled is False
    assert foundation.hidden_lifecycle_state_mutation_enabled is False
    assert foundation.implicit_operational_state_transition_enabled is False
    assert foundation.automatic_patch_transition_logic_enabled is False
    assert foundation.callable_operational_flow_enabled is False
    assert foundation.production_automation_enabled is False
    assert all(not state.executable for state in foundation.lifecycle_states)
    assert all(not state.auto_transition_enabled for state in foundation.lifecycle_states)
    assert all(not record.execution_enabled for record in foundation.lineage_records)
    assert all(not record.execution_enabled for record in foundation.provenance_records)


def test_v4_0_lifecycle_identity_provenance_and_lineage_keys_are_stable():
    foundation = default_patch_lifecycle_foundation()

    assert lifecycle_identity_key(foundation.patch_identity) == (
        "v4_0.patch_lifecycle_foundations.1"
        "|v4_0_phase_1_patch_lifecycle_foundations"
        "|v4.0.0-foundation|v3.9-closeout"
        "|v4_0_patch_lifecycle_provenance_primary"
        "|v4_0_patch_lifecycle_lineage_primary"
    )
    assert lifecycle_provenance_key(foundation.provenance_records[0]) == (
        "patch_lifecycle_provenance_descriptive_only|v4.0.0-foundation"
        "|v3.9-closeout|v4_0.patch_lifecycle_foundations.1"
        "|v4_0_patch_lifecycle_provenance_primary"
    )
    assert lifecycle_lineage_key(foundation.lineage_records[0]) == (
        "patch_lifecycle_lineage_descriptive_only|v4_0_patch_lifecycle_lineage_primary|1"
    )


def test_v4_0_deterministic_serialization_hashing_and_equality_are_stable():
    first = default_patch_lifecycle_foundation()
    second = default_patch_lifecycle_foundation()

    assert first == second
    assert hash(first) == hash(second)
    assert patch_lifecycle_foundations_equal(first, second)
    assert patch_identities_equal(first.patch_identity, second.patch_identity)
    assert serialize_patch_lifecycle_foundation(first) == serialize_patch_lifecycle_foundation(second)
    assert hash_patch_lifecycle_foundation(first) == hash_patch_lifecycle_foundation(second)
    assert hash_patch_identity(first.patch_identity) == hash_patch_identity(second.patch_identity)
    assert json.loads(serialize_patch_lifecycle_foundation(first))["non_executable"] is True


def test_v4_0_serialization_preserves_deterministic_order_and_visible_states():
    foundation = default_patch_lifecycle_foundation()
    reordered = replace(
        foundation,
        lifecycle_states=tuple(reversed(foundation.lifecycle_states)),
        provenance_records=tuple(reversed(foundation.provenance_records)),
        lineage_records=tuple(reversed(foundation.lineage_records)),
        visibility_records=tuple(reversed(foundation.visibility_records)),
    )

    assert serialize_patch_lifecycle_foundation(foundation) == serialize_patch_lifecycle_foundation(reordered)
    assert hash_patch_lifecycle_foundation(foundation) == hash_patch_lifecycle_foundation(reordered)
    exported = export_patch_lifecycle_foundation(reordered)
    assert [item["state"] for item in exported["lifecycle_states"]] == [
        LIFECYCLE_STATE_SUPPORTED,
        LIFECYCLE_STATE_UNSUPPORTED,
        LIFECYCLE_STATE_BLOCKED,
        LIFECYCLE_STATE_EXPERIMENTAL,
        LIFECYCLE_STATE_UNKNOWN,
        LIFECYCLE_STATE_DEPRECATED,
        LIFECYCLE_STATE_PROHIBITED,
    ]
    visibility = exported["visibility_records"][0]
    assert visibility["unsupported_state_visibility"] == ["v4_0_lifecycle_state_unsupported_source"]
    assert visibility["prohibited_state_visibility"] == ["v4_0_lifecycle_state_prohibited_execution"]
    assert visibility["unknown_state_visibility"] == ["v4_0_lifecycle_state_unknown_successor"]
    assert visibility["integrity_warning_visibility"] == [
        "v4_0_lifecycle_state_blocked_continuity_gap",
        "v4_0_lifecycle_state_deprecated_legacy_patch_context",
        "v4_0_lifecycle_state_experimental_refresh_chain",
    ]


def test_v4_0_lifecycle_identity_lineage_and_provenance_normalization_is_explicit_and_non_corrective():
    foundation = default_patch_lifecycle_foundation()
    identity = normalize_patch_identity(foundation.patch_identity)
    lineage = normalize_lifecycle_lineage(foundation.lineage_records[0])
    provenance = normalize_lifecycle_provenance(foundation.provenance_records[0])
    identity_report = patch_identity_normalization_report(identity)

    assert identity == foundation.patch_identity
    assert lineage == foundation.lineage_records[0]
    assert provenance == foundation.provenance_records[0]
    assert identity_report["normalization_scope"] == "deterministic_field_representation_only"
    assert identity_report["omitted_field_count"] == 0
    assert identity_report["silent_correction_enabled"] is False
    assert identity_report["hidden_fallback_enabled"] is False
    assert identity_report["runtime_mutation_enabled"] is False
    assert identity_report["lifecycle_execution_enabled"] is False


def test_v4_0_provenance_lineage_replay_and_rollback_continuity_are_preserved():
    foundation = default_patch_lifecycle_foundation()
    provenance_validation = validate_lifecycle_provenance_continuity(foundation.provenance_records[0])
    lineage_validation = validate_lifecycle_lineage_continuity(foundation.lineage_records[0])

    with pytest.raises(FrozenInstanceError):
        foundation.provenance_records[0].inferred_provenance_allowed = True

    assert provenance_validation["valid"] is True
    assert provenance_validation["provenance_preserved"] is True
    assert provenance_validation["no_inferred_provenance"] is True
    assert provenance_validation["provenance_continuity_visible"] is True
    assert provenance_validation["trusted_bundle_reference_present"] is True
    assert provenance_validation["refresh_chain_reference_present"] is True
    assert lineage_validation["valid"] is True
    assert lineage_validation["lineage_preserved"] is True
    assert lineage_validation["replay_safe"] is True
    assert lineage_validation["rollback_safe"] is True
    assert lineage_validation["prior_bundle_reference_count"] == 3
    assert lineage_validation["continuity_reference_count"] == 3
    assert lineage_validation["rollback_reference_count"] == 1
    assert lineage_validation["fail_visible_lineage_gap_count"] == 1


def test_v4_0_fail_visible_unsupported_prohibited_unknown_and_integrity_visibility_are_preserved():
    foundation = default_patch_lifecycle_foundation()
    validation = validate_lifecycle_visibility(foundation)
    counts = count_lifecycle_states(foundation.lifecycle_states)

    assert counts[LIFECYCLE_STATE_SUPPORTED] == 1
    assert counts[LIFECYCLE_STATE_UNSUPPORTED] == 1
    assert counts[LIFECYCLE_STATE_BLOCKED] == 1
    assert counts[LIFECYCLE_STATE_EXPERIMENTAL] == 1
    assert counts[LIFECYCLE_STATE_UNKNOWN] == 1
    assert counts[LIFECYCLE_STATE_DEPRECATED] == 1
    assert counts[LIFECYCLE_STATE_PROHIBITED] == 1
    assert counts["invalid"] == 0
    assert validation["valid"] is True
    assert validation["unsupported_states_visible"] is True
    assert validation["prohibited_states_visible"] is True
    assert validation["unknown_states_visible"] is True
    assert validation["unsupported_state_visibility_count"] == 1
    assert validation["prohibited_state_visibility_count"] == 1
    assert validation["unknown_state_visibility_count"] == 1
    assert validation["integrity_warning_visibility_count"] == 3
    assert validation["lifecycle_continuity_visibility_count"] == 4
    assert validation["lineage_gap_visibility_count"] == 1
    assert validation["hidden_state_count"] == 0
    assert validation["corrective_visibility_count"] == 0
    assert validation["state_execution_semantics_count"] == 0


def test_v4_0_visibility_validation_blocks_hidden_correction_and_execution_semantics():
    foundation = default_patch_lifecycle_foundation()
    hidden_state = replace(
        foundation.lifecycle_states[1],
        hidden=True,
        fail_visible=False,
        auto_transition_enabled=True,
    )
    corrective_visibility = replace(
        foundation.visibility_records[0],
        automatic_resolution_enabled=True,
        silent_omission_enabled=True,
    )
    contaminated = replace(
        foundation,
        lifecycle_states=(foundation.lifecycle_states[0], hidden_state, *foundation.lifecycle_states[2:]),
        visibility_records=(corrective_visibility,),
    )
    validation = validate_lifecycle_visibility(contaminated)

    assert validation["valid"] is False
    assert validation["hidden_state_count"] == 1
    assert validation["corrective_visibility_count"] == 1
    assert validation["state_execution_semantics_count"] == 1


def test_v4_0_patch_lifecycle_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_patch_lifecycle_foundations_report()

    assert report["foundation_status"] == V4_0_PATCH_LIFECYCLE_STATUS_STABLE
    assert report["operational_lifecycle_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["execution_boundary_enabled_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["deterministic_equality_verified"] is True
    assert report["summary"]["provenance_continuity_verified"] is True
    assert report["summary"]["lineage_continuity_verified"] is True
    assert report["summary"]["replay_continuity_verified"] is True
    assert report["summary"]["rollback_continuity_verified"] is True
    assert report["summary"]["integrity_safe_visibility_preserved"] is True
    assert report["lifecycle_model_counts"]["patch_identity_count"] == 1
    assert report["lifecycle_model_counts"]["lifecycle_state_count"] == 7
    assert report["lifecycle_model_counts"]["lifecycle_lineage_record_count"] == 1
    assert report["lifecycle_model_counts"]["lifecycle_visibility_record_count"] == 1
    assert report["non_execution_guarantees"]["patch_execution_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
    assert report["non_execution_guarantees"]["callable_operational_flow_absent"] is True
    assert "v4.0 Phase 1 does not enable orchestration execution." in report["explicit_limitations"]
