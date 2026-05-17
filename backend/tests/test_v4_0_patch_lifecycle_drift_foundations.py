from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.lifecycle_drift_detection import (  # noqa: E402
    compare_lifecycle_states,
    compare_lineage_records,
    compare_patch_identity,
    compare_provenance_records,
    compare_replay_continuity,
    compare_rollback_continuity,
    compare_visibility_records,
    detect_lifecycle_drift,
)
from operational_lifecycle.lifecycle_drift_hashing import hash_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_drift_models import (  # noqa: E402
    DRIFT_TYPE_EXTRACTION_VERSION,
    DRIFT_TYPE_GENERATION,
    DRIFT_TYPE_IDENTITY,
    DRIFT_TYPE_INTEGRITY_WARNING,
    DRIFT_TYPE_LINEAGE,
    DRIFT_TYPE_PATCH_VERSION,
    DRIFT_TYPE_PROVENANCE,
    DRIFT_TYPE_REPLAY_CONTINUITY,
    DRIFT_TYPE_ROLLBACK_CONTINUITY,
    DRIFT_TYPE_SCHEMA_VERSION,
    DRIFT_TYPE_STATE,
    DRIFT_TYPE_VISIBILITY,
    LIFECYCLE_DRIFT_TYPES,
    V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_STABLE,
)
from operational_lifecycle.lifecycle_drift_serialization import (  # noqa: E402
    export_lifecycle_drift_report,
    serialize_lifecycle_drift_report,
)
from operational_lifecycle.lifecycle_drift_visibility import (  # noqa: E402
    count_drift_severities,
    count_drift_types,
    validate_lifecycle_drift_visibility,
)
from operational_lifecycle.lifecycle_serialization import serialize_patch_lifecycle_foundation  # noqa: E402
from scripts.report_v4_0_patch_lifecycle_drift_foundations import (  # noqa: E402
    build_representative_lifecycle_drift_pair,
    build_v4_0_patch_lifecycle_drift_foundations_report,
)


def test_v4_0_drift_detection_ordering_is_deterministic():
    source, target = build_representative_lifecycle_drift_pair()
    first = detect_lifecycle_drift(source, target)
    second = detect_lifecycle_drift(source, target)
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 19
    assert first.finding_count == len(first.findings)


def test_v4_0_drift_report_serialization_and_hashing_are_stable():
    source, target = build_representative_lifecycle_drift_pair()
    first = detect_lifecycle_drift(source, target)
    second = detect_lifecycle_drift(source, target)

    assert serialize_lifecycle_drift_report(first) == serialize_lifecycle_drift_report(second)
    assert hash_lifecycle_drift_report(first) == hash_lifecycle_drift_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_lifecycle_drift_report(first)
    exported = json.loads(serialize_lifecycle_drift_report(first))
    assert exported["finding_count"] == 19
    assert all("before_value" in finding and "after_value" in finding for finding in exported["findings"])
    assert all(finding["provenance_reference"] for finding in exported["findings"])
    assert all(finding["lineage_reference"] for finding in exported["findings"])
    assert all(finding["visibility_reference"] for finding in exported["findings"])


def test_v4_0_identity_patch_extraction_schema_generation_provenance_and_lineage_drift_are_detected():
    source, target = build_representative_lifecycle_drift_pair()
    findings = compare_patch_identity(source.patch_identity, target.patch_identity)
    drift_types = [finding.drift_type for finding in findings]

    assert DRIFT_TYPE_IDENTITY in drift_types
    assert DRIFT_TYPE_PATCH_VERSION in drift_types
    assert DRIFT_TYPE_EXTRACTION_VERSION in drift_types
    assert DRIFT_TYPE_SCHEMA_VERSION in drift_types
    assert DRIFT_TYPE_GENERATION in drift_types
    assert DRIFT_TYPE_PROVENANCE in drift_types
    assert DRIFT_TYPE_LINEAGE in drift_types
    assert any(finding.before_value == "v4.0.0-foundation" for finding in findings)
    assert any(finding.after_value == "v4.0.1-foundation" for finding in findings)
    assert any(finding.before_value == "v3.9-closeout" for finding in findings)
    assert any(finding.after_value == "v4.0-drift-extraction" for finding in findings)
    assert any(finding.before_value == "v4_0.patch_lifecycle_foundations.1" for finding in findings)
    assert any(finding.after_value == "v4_0.patch_lifecycle_foundations.2" for finding in findings)
    assert any(finding.after_value == "v4_0_phase_2_patch_lifecycle_drift_foundations" for finding in findings)


def test_v4_0_record_level_provenance_and_lineage_drift_are_detected():
    source, target = build_representative_lifecycle_drift_pair()
    provenance_findings = compare_provenance_records(source, target)
    lineage_findings = compare_lineage_records(source, target)

    assert len(provenance_findings) == 1
    assert provenance_findings[0].drift_type == DRIFT_TYPE_PROVENANCE
    assert "v4_0_patch_lifecycle_drift_refresh_chain" in str(provenance_findings[0].after_value)
    assert len(lineage_findings) == 1
    assert lineage_findings[0].drift_type == DRIFT_TYPE_LINEAGE
    assert "v4_0_patch_lifecycle_drift_lineage_gap" in str(lineage_findings[0].after_value)


def test_v4_0_state_visibility_replay_rollback_and_integrity_drift_are_detected():
    source, target = build_representative_lifecycle_drift_pair()
    state_findings = compare_lifecycle_states(source, target)
    visibility_findings = compare_visibility_records(source, target)
    replay_findings = compare_replay_continuity(source, target)
    rollback_findings = compare_rollback_continuity(source, target)

    assert len(state_findings) == 1
    assert state_findings[0].drift_type == DRIFT_TYPE_STATE
    assert "unknown" in str(state_findings[0].after_value)
    assert any(finding.drift_type == DRIFT_TYPE_VISIBILITY for finding in visibility_findings)
    assert any(finding.drift_type == DRIFT_TYPE_INTEGRITY_WARNING for finding in visibility_findings)
    assert any("unsupported_state_visibility" in finding.explanation for finding in visibility_findings)
    assert any("prohibited_state_visibility" in finding.explanation for finding in visibility_findings)
    assert any("unknown_state_visibility" in finding.explanation for finding in visibility_findings)
    assert replay_findings[0].drift_type == DRIFT_TYPE_REPLAY_CONTINUITY
    assert rollback_findings[0].drift_type == DRIFT_TYPE_ROLLBACK_CONTINUITY
    assert "v4_0_patch_lifecycle_drift_replay_reference" in str(replay_findings[0].after_value)
    assert "v4_0_patch_lifecycle_drift_rollback_reference" in str(rollback_findings[0].after_value)


def test_v4_0_unsupported_prohibited_unknown_and_blocking_drift_visibility_is_fail_visible():
    source, target = build_representative_lifecycle_drift_pair()
    report = detect_lifecycle_drift(source, target)
    visibility = validate_lifecycle_drift_visibility(report)
    severity_counts = count_drift_severities(report.findings)
    drift_type_counts = count_drift_types(report.findings)

    assert visibility["valid"] is True
    assert report.unsupported_drift_count == 4
    assert report.prohibited_drift_count == 3
    assert report.unknown_drift_count == 3
    assert report.blocking_drift_count == 9
    assert severity_counts["blocking"] == 9
    assert severity_counts["prohibited"] == 2
    assert severity_counts["unknown"] == 1
    assert drift_type_counts[DRIFT_TYPE_INTEGRITY_WARNING] == 1
    assert drift_type_counts[DRIFT_TYPE_REPLAY_CONTINUITY] == 1
    assert drift_type_counts[DRIFT_TYPE_ROLLBACK_CONTINUITY] == 1
    assert visibility["remediation_enabled"] is False
    assert visibility["correction_enabled"] is False
    assert visibility["authorization_enabled"] is False
    assert visibility["execution_enabled"] is False
    assert visibility["capability_enabled_count"] == 0


def test_v4_0_drift_detection_does_not_mutate_source_or_target_records():
    source, target = build_representative_lifecycle_drift_pair()
    source_before = serialize_patch_lifecycle_foundation(source)
    target_before = serialize_patch_lifecycle_foundation(target)

    detect_lifecycle_drift(source, target)
    detect_lifecycle_drift(source, target)

    assert serialize_patch_lifecycle_foundation(source) == source_before
    assert serialize_patch_lifecycle_foundation(target) == target_before


def test_v4_0_drift_hash_changes_when_before_or_after_evidence_changes():
    source, target = build_representative_lifecycle_drift_pair()
    baseline = detect_lifecycle_drift(source, target)
    alternate_target = replace(
        target,
        patch_identity=replace(target.patch_identity, patch_version="v4.0.2-foundation"),
    )
    alternate = detect_lifecycle_drift(source, alternate_target)

    assert baseline.deterministic_report_hash != alternate.deterministic_report_hash
    assert baseline.target_lifecycle_identity != alternate.target_lifecycle_identity


def test_v4_0_drift_generated_report_contains_required_counts_and_boundaries():
    report = build_v4_0_patch_lifecycle_drift_foundations_report()
    drift_report = report["drift_report"]

    assert report["foundation_status"] == V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_STABLE
    assert report["drift_detection_mode"] == "descriptive_only"
    assert report["total_drift_findings"] == 19
    assert report["unsupported_drift_count"] == 4
    assert report["prohibited_drift_count"] == 3
    assert report["unknown_drift_count"] == 3
    assert report["blocking_drift_count"] == 9
    assert report["replay_safety_status"] is True
    assert report["rollback_safety_status"] is True
    assert report["provenance_safety_status"] is True
    assert set(report["implemented_drift_types"]) == set(LIFECYCLE_DRIFT_TYPES)
    assert report["drift_type_counts"][DRIFT_TYPE_PATCH_VERSION] == 1
    assert report["drift_type_counts"][DRIFT_TYPE_EXTRACTION_VERSION] == 1
    assert report["drift_type_counts"][DRIFT_TYPE_SCHEMA_VERSION] == 1
    assert report["drift_type_counts"][DRIFT_TYPE_GENERATION] == 1
    assert report["drift_type_counts"][DRIFT_TYPE_PROVENANCE] == 2
    assert report["drift_type_counts"][DRIFT_TYPE_LINEAGE] == 3
    assert report["drift_type_counts"][DRIFT_TYPE_STATE] == 1
    assert report["drift_type_counts"][DRIFT_TYPE_VISIBILITY] == 5
    assert report["drift_type_counts"][DRIFT_TYPE_REPLAY_CONTINUITY] == 1
    assert report["drift_type_counts"][DRIFT_TYPE_ROLLBACK_CONTINUITY] == 1
    assert report["deterministic_drift_report_hash"] == drift_report["deterministic_report_hash"]
    assert report["non_execution_guarantees"]["remediation_absent"] is True
    assert report["non_execution_guarantees"]["execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["summary"]["capability_enabled_count"] == 0
    assert "v4.0 Phase 2 detects lifecycle drift but does not remediate drift." in report["explicit_limitations"]


def test_v4_0_drift_export_preserves_before_after_and_visible_findings():
    source, target = build_representative_lifecycle_drift_pair()
    report = detect_lifecycle_drift(source, target)
    exported = export_lifecycle_drift_report(report)

    assert exported["finding_count"] == len(exported["findings"])
    assert [finding["deterministic_key"] for finding in exported["findings"]] == sorted(
        finding["deterministic_key"] for finding in exported["findings"]
    )
    assert all(finding["before_value"] != finding["after_value"] for finding in exported["findings"])
    assert any("unsupported" in str(finding["before_value"]) for finding in exported["findings"])
    assert any("prohibited" in str(finding["before_value"]) for finding in exported["findings"])
    assert any("unknown" in str(finding["after_value"]) for finding in exported["findings"])
