from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from orchestration_governance.v4_5a_1_drift_foundation_audit import (  # noqa: E402
    build_v4_5a_1_drift_foundations,
    build_v4_5a_1_drift_foundations_report,
    contaminate_v4_5a_1_drift_foundations_for_non_operational_validation,
    drift_foundation_capability_counter_values,
    drift_foundations_equal,
    enabled_drift_foundation_capability_flags,
    validate_descriptive_only_drift_guarantees,
    validate_drift_evidence_continuity,
    validate_drift_identity_integrity,
    validate_drift_lineage_continuity,
    validate_drift_ordering_stability,
    validate_drift_serialization_and_hashing,
    validate_fail_visible_unsupported_state_visibility,
    validate_v4_5a_1_drift_foundations,
)
from orchestration_governance.v4_5a_1_drift_foundation_hashing import (  # noqa: E402
    hash_drift_classification_record,
    hash_drift_continuity_visibility,
    hash_drift_evidence_reference,
    hash_drift_foundation_identity,
    hash_drift_identity_record,
    hash_v4_5a_1_drift_foundations,
)
from orchestration_governance.v4_5a_1_drift_foundation_models import (  # noqa: E402
    DRIFT_CLASSIFICATION_CATEGORIES,
    DRIFT_CONTINUITY_TYPES,
    DRIFT_DIAGNOSTIC_TYPES,
    DRIFT_EVIDENCE_TYPES,
    DRIFT_SEVERITY_LEVELS,
    UNSUPPORTED_DRIFT_OPERATIONAL_STATES,
    V4_5A_1_DRIFT_FOUNDATION_SCHEMA_VERSION,
    V4_5A_1_DRIFT_FOUNDATION_STATUS_STABLE,
)
from orchestration_governance.v4_5a_1_drift_foundation_serialization import (  # noqa: E402
    serialize_v4_5a_1_drift_foundations,
)
from orchestration_governance.v4_5a_1_drift_foundation_visibility import (  # noqa: E402
    continuity_summary_visibility,
    descriptive_only_visibility_summary,
    drift_summary_visibility,
    evidence_summary_visibility,
    fail_visible_diagnostic_summaries,
    severity_summary_visibility,
    unsupported_state_visibility_summaries,
    validate_required_drift_visibility,
)


def test_v4_5a_1_drift_foundation_models_are_immutable_and_descriptive_only():
    foundations = build_v4_5a_1_drift_foundations()

    with pytest.raises(FrozenInstanceError):
        foundations.runtime_execution_enabled = True

    assert foundations.foundation_identity.schema_version == V4_5A_1_DRIFT_FOUNDATION_SCHEMA_VERSION
    assert foundations.descriptive_only is True
    assert foundations.non_operational is True
    assert foundations.non_executing is True
    assert foundations.non_authorizing is True
    assert foundations.non_remediating is True
    assert foundations.non_runtime_mutating is True
    assert foundations.planner_integration_enabled is False
    assert foundations.production_consumption_enabled is False
    assert foundations.runtime_execution_enabled is False
    assert foundations.runtime_mutation_enabled is False
    assert enabled_drift_foundation_capability_flags(foundations) == {}
    assert all(
        value == 0
        for value in drift_foundation_capability_counter_values(foundations).values()
    )


def test_v4_5a_1_drift_foundation_preserves_required_visibility_sets():
    foundations = build_v4_5a_1_drift_foundations()
    visibility = validate_required_drift_visibility(foundations)

    assert visibility["valid"] is True
    assert set(visibility["category_counts"]) == set(DRIFT_CLASSIFICATION_CATEGORIES)
    assert set(visibility["severity_counts"]) == set(DRIFT_SEVERITY_LEVELS)
    assert set(visibility["evidence_counts"]) == set(DRIFT_EVIDENCE_TYPES)
    assert set(visibility["continuity_counts"]) == set(DRIFT_CONTINUITY_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(DRIFT_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_DRIFT_OPERATIONAL_STATES
    )
    assert visibility["missing_categories"] == []
    assert visibility["missing_severities"] == []
    assert visibility["missing_evidence_types"] == []
    assert visibility["missing_continuity_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_1_drift_foundation_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_1_drift_foundations()
    second = build_v4_5a_1_drift_foundations()
    serialization = validate_drift_serialization_and_hashing(first)

    assert first == second
    assert drift_foundations_equal(first, second)
    assert serialize_v4_5a_1_drift_foundations(first) == serialize_v4_5a_1_drift_foundations(second)
    assert hash_v4_5a_1_drift_foundations(first) == hash_v4_5a_1_drift_foundations(second)
    assert serialization["valid"] is True
    assert len(hash_drift_foundation_identity(first.foundation_identity)) == 64
    assert len(hash_drift_identity_record(first.drift_identities[0])) == 64
    assert len(hash_drift_classification_record(first.classifications[0])) == 64
    assert len(hash_drift_evidence_reference(first.evidence_references[0])) == 64
    assert len(hash_drift_continuity_visibility(first.continuity_visibility[0])) == 64


def test_v4_5a_1_drift_foundation_ordering_survives_reordered_collections():
    foundations = build_v4_5a_1_drift_foundations()
    reordered = replace(
        foundations,
        drift_identities=tuple(reversed(foundations.drift_identities)),
        classifications=tuple(reversed(foundations.classifications)),
        evidence_references=tuple(reversed(foundations.evidence_references)),
        continuity_visibility=tuple(reversed(foundations.continuity_visibility)),
        diagnostics=tuple(reversed(foundations.diagnostics)),
        severity_visibility=tuple(reversed(foundations.severity_visibility)),
        unsupported_state_visibility=tuple(
            reversed(foundations.unsupported_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(foundations.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(foundations.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(foundations.inherited_constraints)),
        explicit_limitations=tuple(reversed(foundations.explicit_limitations)),
    )

    assert validate_drift_ordering_stability(foundations)["valid"] is True
    assert serialize_v4_5a_1_drift_foundations(foundations) == serialize_v4_5a_1_drift_foundations(reordered)
    assert hash_v4_5a_1_drift_foundations(foundations) == hash_v4_5a_1_drift_foundations(reordered)


def test_v4_5a_1_drift_identity_evidence_lineage_and_provenance_are_preserved():
    foundations = build_v4_5a_1_drift_foundations()
    identity = validate_drift_identity_integrity(foundations)
    evidence = validate_drift_evidence_continuity(foundations)
    lineage = validate_drift_lineage_continuity(foundations)

    assert identity["valid"] is True
    assert identity["drift_identity_count"] == 8
    assert evidence["valid"] is True
    assert evidence["replay_safe_evidence_count"] == len(foundations.evidence_references)
    assert evidence["provenance_safe_evidence_count"] == len(foundations.evidence_references)
    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True


def test_v4_5a_1_fail_visible_unsupported_states_and_diagnostics_are_explicit():
    foundations = build_v4_5a_1_drift_foundations()
    unsupported = validate_fail_visible_unsupported_state_visibility(foundations)

    assert unsupported["valid"] is True
    assert unsupported["fail_visible"] is True
    assert unsupported["hidden_fallback_used_count"] == 0
    assert unsupported["remediation_enabled_count"] == 0
    assert unsupported["missing_diagnostic_types"] == []
    assert unsupported["missing_unsupported_states"] == []
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_diagnostic_summaries(foundations.diagnostics)
    )
    assert all(
        summary["operational_enabled"] is False
        for summary in unsupported_state_visibility_summaries(
            foundations.unsupported_state_visibility
        )
    )


def test_v4_5a_1_visibility_helpers_remain_descriptive_only_and_non_operational():
    foundations = build_v4_5a_1_drift_foundations()

    assert len(drift_summary_visibility(foundations)) == 8
    assert len(evidence_summary_visibility(foundations.evidence_references)) == 8
    assert len(continuity_summary_visibility(foundations.continuity_visibility)) == 8
    assert len(severity_summary_visibility(foundations.severity_visibility)) == 5
    descriptive = descriptive_only_visibility_summary(foundations)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["planner_integration_enabled"] is False
    assert descriptive["remediation_enabled"] is False
    assert descriptive["auto_correction_enabled"] is False


def test_v4_5a_1_descriptive_only_guarantees_detect_operational_contamination():
    foundations = build_v4_5a_1_drift_foundations()
    contaminated = contaminate_v4_5a_1_drift_foundations_for_non_operational_validation(
        foundations
    )

    assert validate_descriptive_only_drift_guarantees(foundations)["valid"] is True
    contaminated_validation = validate_descriptive_only_drift_guarantees(contaminated)
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_runtime_execution_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert contaminated_validation["counters"]["enabled_runtime_mutation_count"] > 0
    assert enabled_drift_foundation_capability_flags(contaminated) != {}


def test_v4_5a_1_report_generation_is_replay_safe_and_contains_required_repository_state():
    first_report = build_v4_5a_1_drift_foundations_report()
    second_report = build_v4_5a_1_drift_foundations_report()
    validation = validate_v4_5a_1_drift_foundations(
        build_v4_5a_1_drift_foundations()
    )

    assert first_report == second_report
    assert first_report["foundation_status"] == V4_5A_1_DRIFT_FOUNDATION_STATUS_STABLE
    assert first_report["deterministic_report_hash"] == second_report["deterministic_report_hash"]
    assert len(first_report["deterministic_report_hash"]) == 64
    assert validation["valid"] is True
    assert first_report["summary"]["validation_error_count"] == 0
    assert first_report["summary"]["repository_remains"] == [
        "NON-operational",
        "NON-authorizing",
        "NON-executing",
        "NON-remediating",
        "NON-runtime-mutating",
    ]
