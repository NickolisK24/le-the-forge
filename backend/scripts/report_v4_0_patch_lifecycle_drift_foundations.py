"""Generate deterministic v4.0 patch lifecycle drift foundation evidence."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.lifecycle_drift_detection import detect_lifecycle_drift  # noqa: E402
from operational_lifecycle.lifecycle_drift_hashing import deterministic_lifecycle_drift_hash  # noqa: E402
from operational_lifecycle.lifecycle_drift_models import (  # noqa: E402
    LIFECYCLE_DRIFT_TYPES,
    V4_0_PATCH_LIFECYCLE_DRIFT_GENERATED_AT,
    V4_0_PATCH_LIFECYCLE_DRIFT_PHASE_ID,
    V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_BLOCKED,
    V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_STABLE,
)
from operational_lifecycle.lifecycle_drift_serialization import export_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_drift_visibility import (  # noqa: E402
    count_drift_severities,
    count_drift_types,
    validate_lifecycle_drift_visibility,
)
from operational_lifecycle.lifecycle_models import (  # noqa: E402
    LIFECYCLE_SEVERITY_WARNING,
    LIFECYCLE_STATE_UNKNOWN,
    PatchIdentity,
    PatchLifecycleFoundation,
    default_lifecycle_lineage_record,
    default_lifecycle_provenance_record,
    default_lifecycle_states,
    default_lifecycle_visibility_record,
    default_patch_lifecycle_foundation,
    default_patch_operational_metadata,
)


REPORT_PATH = Path("docs/generated/v4_0_patch_lifecycle_drift_foundations_report.json")


def build_representative_lifecycle_drift_pair() -> tuple[PatchLifecycleFoundation, PatchLifecycleFoundation]:
    source = default_patch_lifecycle_foundation()
    target_identity = PatchIdentity(
        patch_version="v4.0.1-foundation",
        extraction_version="v4.0-drift-extraction",
        schema_version="v4_0.patch_lifecycle_foundations.2",
        lifecycle_generation="v4_0_phase_2_patch_lifecycle_drift_foundations",
        lifecycle_timestamp=source.patch_identity.lifecycle_timestamp,
        provenance_reference="v4_0_patch_lifecycle_provenance_drift_target",
        lineage_reference="v4_0_patch_lifecycle_lineage_drift_target",
        trusted_bundle_reference="v4_0_patch_lifecycle_drift_trusted_bundle",
        refresh_chain_reference="v4_0_patch_lifecycle_drift_refresh_chain",
    )
    target_states = list(default_lifecycle_states(target_identity))
    target_states[1] = replace(
        target_states[1],
        state=LIFECYCLE_STATE_UNKNOWN,
        reason="formerly unsupported lifecycle evidence is now explicitly unknown in the target record",
        severity=LIFECYCLE_SEVERITY_WARNING,
    )
    target_lineage = replace(
        default_lifecycle_lineage_record(target_identity),
        continuity_references=(
            "v4_0_patch_lifecycle_drift_replay_reference",
            "v4_0_patch_lifecycle_drift_rollback_reference",
            "v4_0_patch_lifecycle_provenance_continuity_reference",
        ),
        rollback_references=("v4_0_patch_lifecycle_drift_rollback_reference",),
        fail_visible_lineage_gap_ids=(
            "v4_0_future_successor_lifecycle_not_declared",
            "v4_0_patch_lifecycle_drift_lineage_gap",
        ),
    )
    target_provenance = replace(
        default_lifecycle_provenance_record(target_identity),
        continuity_references=(
            "v3_9_closeout_and_v4_readiness_report",
            "v4_0_patch_lifecycle_drift_replay_reference",
            "v4_0_patch_lifecycle_drift_rollback_reference",
        ),
        source_evidence_references=(
            "docs/generated/v4_0_patch_lifecycle_foundations_report.json",
            "docs/migration/V4_0_PATCH_LIFECYCLE_FOUNDATIONS.md",
        ),
    )
    target_visibility = default_lifecycle_visibility_record(tuple(target_states), target_lineage)
    target_visibility = replace(
        target_visibility,
        prohibited_state_visibility=(),
        integrity_warning_visibility=tuple(
            sorted(
                (
                    *target_visibility.integrity_warning_visibility,
                    "v4_0_patch_lifecycle_drift_integrity_warning",
                )
            )
        ),
    )
    target_metadata = default_patch_operational_metadata(target_identity, tuple(target_states), target_visibility)
    target = replace(
        source,
        patch_identity=target_identity,
        lifecycle_states=tuple(target_states),
        provenance_records=(target_provenance,),
        lineage_records=(target_lineage,),
        visibility_records=(target_visibility,),
        operational_metadata=target_metadata,
    )
    return source, target


def build_v4_0_patch_lifecycle_drift_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    source, target = build_representative_lifecycle_drift_pair()
    drift_report = detect_lifecycle_drift(source, target)
    exported = export_lifecycle_drift_report(drift_report)
    visibility_validation = validate_lifecycle_drift_visibility(drift_report)
    drift_type_counts = count_drift_types(drift_report.findings)
    severity_counts = count_drift_severities(drift_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_PATCH_LIFECYCLE_DRIFT_STATUS_BLOCKED
    )
    report = {
        "schema_version": "v4_0.patch_lifecycle_drift_foundations_report.1",
        "generated_at": V4_0_PATCH_LIFECYCLE_DRIFT_GENERATED_AT,
        "phase_id": V4_0_PATCH_LIFECYCLE_DRIFT_PHASE_ID,
        "phase_name": "v4.0_phase_2_patch_lifecycle_drift_foundations",
        "repo_root": str(root),
        "architectural_purpose": "deterministic operational lifecycle drift detection without remediation or execution",
        "drift_detection_mode": "descriptive_only",
        "foundation_status": status,
        "source_lifecycle_identity": drift_report.source_lifecycle_identity,
        "target_lifecycle_identity": drift_report.target_lifecycle_identity,
        "total_drift_findings": drift_report.finding_count,
        "drift_type_counts": drift_type_counts,
        "severity_counts": severity_counts,
        "unsupported_drift_count": drift_report.unsupported_drift_count,
        "prohibited_drift_count": drift_report.prohibited_drift_count,
        "unknown_drift_count": drift_report.unknown_drift_count,
        "blocking_drift_count": drift_report.blocking_drift_count,
        "replay_safety_status": drift_report.replay_safe,
        "rollback_safety_status": drift_report.rollback_safe,
        "provenance_safety_status": drift_report.provenance_safe,
        "deterministic_drift_report_hash": drift_report.deterministic_report_hash,
        "implemented_drift_types": list(LIFECYCLE_DRIFT_TYPES),
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "before_after_values_preserved": all(
                "before_value" in finding and "after_value" in finding for finding in exported["findings"]
            ),
            "provenance_references_preserved": all(
                bool(finding["provenance_reference"]) for finding in exported["findings"]
            ),
            "lineage_references_preserved": all(bool(finding["lineage_reference"]) for finding in exported["findings"]),
            "visibility_references_preserved": all(
                bool(finding["visibility_reference"]) for finding in exported["findings"]
            ),
        },
        "fail_visible_guarantees": {
            "unsupported_drift_visible": drift_report.unsupported_drift_count > 0,
            "prohibited_drift_visible": drift_report.prohibited_drift_count > 0,
            "unknown_drift_visible": drift_report.unknown_drift_count > 0,
            "blocking_drift_visible": drift_report.blocking_drift_count > 0,
            "integrity_warning_drift_visible": drift_type_counts["integrity_warning_drift"] > 0,
            "replay_continuity_drift_visible": drift_type_counts["replay_continuity_drift"] > 0,
            "rollback_continuity_drift_visible": drift_type_counts["rollback_continuity_drift"] > 0,
            "provenance_continuity_drift_visible": drift_type_counts["provenance_drift"] > 0,
            "lineage_continuity_drift_visible": drift_type_counts["lineage_drift"] > 0,
        },
        "non_execution_guarantees": {
            "descriptive_only": drift_report.descriptive_only,
            "remediation_absent": not drift_report.remediation_enabled,
            "correction_absent": not drift_report.correction_enabled,
            "authorization_absent": not drift_report.authorization_enabled,
            "approval_absent": not drift_report.approval_enabled,
            "execution_absent": not drift_report.execution_enabled,
            "routing_absent": not drift_report.routing_enabled,
            "scheduling_absent": not drift_report.scheduling_enabled,
            "dispatch_absent": not drift_report.dispatch_enabled,
            "orchestration_execution_absent": not drift_report.orchestration_execution_enabled,
            "runtime_mutation_absent": not drift_report.runtime_mutation_enabled,
            "callable_operational_workflow_absent": not drift_report.callable_operational_workflow_enabled,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "total_drift_findings": drift_report.finding_count,
            "deterministic_hashing_verified": bool(drift_report.deterministic_report_hash),
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "replay_safe": drift_report.replay_safe,
            "rollback_safe": drift_report.rollback_safe,
            "provenance_safe": drift_report.provenance_safe,
            "drift_detection_remains_descriptive_only": drift_report.descriptive_only,
        },
        "drift_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 2 detects lifecycle drift but does not correct drift.",
            "v4.0 Phase 2 detects lifecycle drift but does not remediate drift.",
            "v4.0 Phase 2 does not authorize lifecycle changes.",
            "v4.0 Phase 2 does not execute patch refresh behavior.",
            "v4.0 Phase 2 does not enable routing, scheduling, dispatch, orchestration, or runtime mutation.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_lifecycle_drift_hash(payload)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_0_patch_lifecycle_drift_foundations_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_drift_report_hash={report['deterministic_drift_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
