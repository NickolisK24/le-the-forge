"""Generate deterministic v4.1 refresh drift certification evidence."""

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

from operational_refresh.refresh_drift_certification_continuity import certify_refresh_drift_continuity  # noqa: E402
from operational_refresh.refresh_drift_certification_diagnostics import build_refresh_drift_diagnostics  # noqa: E402
from operational_refresh.refresh_drift_certification_hashing import (  # noqa: E402
    deterministic_refresh_drift_hash,
    hash_refresh_drift_certification,
    hash_refresh_drift_certification_identity,
    hash_refresh_drift_continuity,
    hash_refresh_drift_diagnostics,
)
from operational_refresh.refresh_drift_certification_integrity import (  # noqa: E402
    refresh_drift_certifications_equal,
    refresh_drift_identity_normalization_report,
    validate_refresh_drift_integrity,
    validate_refresh_drift_non_execution,
)
from operational_refresh.refresh_drift_certification_models import (  # noqa: E402
    V4_1_CROSS_LAYER_DRIFT_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
    V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID,
    V4_1_REFRESH_DRIFT_CERTIFICATION_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_BLOCKED,
    V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_STABLE,
    V4_1_REFRESH_DRIFT_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DRIFT_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DRIFT_INTEGRITY_REPORT_SCHEMA_VERSION,
    default_refresh_drift_certification,
)
from operational_refresh.refresh_drift_certification_serialization import (  # noqa: E402
    export_refresh_drift_certification,
    serialize_refresh_drift_certification,
)
from operational_refresh.refresh_drift_certification_visibility import (  # noqa: E402
    count_drift_observation_states,
    validate_refresh_drift_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_drift_certification_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_drift_diagnostics_report.json")
CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_drift_continuity_certification_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_drift_integrity_certification_report.json")
CROSS_LAYER_REPORT_PATH = Path("docs/generated/v4_1_cross_layer_drift_certification_report.json")


def _reordered_refresh_drift_certification():
    certification = default_refresh_drift_certification()
    return replace(certification, drift_observations=tuple(reversed(certification.drift_observations)))


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_refresh_drift_hash(payload)


def _status(valid: bool) -> str:
    return V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_STABLE if valid else V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_BLOCKED


def build_v4_1_refresh_drift_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_drift_certification()
    repeated = default_refresh_drift_certification()
    reordered = _reordered_refresh_drift_certification()
    exported = export_refresh_drift_certification(certification)
    visibility = validate_refresh_drift_visibility(certification)
    continuity = certify_refresh_drift_continuity(certification)
    non_execution = validate_refresh_drift_non_execution(certification)
    integrity = validate_refresh_drift_integrity(certification)
    diagnostics = build_refresh_drift_diagnostics(certification)
    serialization_first = serialize_refresh_drift_certification(certification)
    serialization_second = serialize_refresh_drift_certification(repeated)
    serialization_reordered = serialize_refresh_drift_certification(reordered)
    drift_hash = hash_refresh_drift_certification(certification)
    repeated_hash = hash_refresh_drift_certification(repeated)
    reordered_hash = hash_refresh_drift_certification(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if drift_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_drift_certifications_equal(certification, repeated) else 1,
        ]
    )
    status = _status(validation_error_count == 0)
    exported_observation_order = [item["observation_id"] for item in exported["drift_observations"]]
    expected_observation_order = [
        item["observation_id"]
        for item in sorted(exported["drift_observations"], key=lambda item: (item["deterministic_order"], item["observation_id"]))
    ]
    report = {
        "schema_version": V4_1_REFRESH_DRIFT_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_6_refresh_drift_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh drift certification without remediation correction or execution",
        "drift_certification_mode": "descriptive_only",
        "foundation_status": status,
        "drift_model_counts": {
            "identity_count": 1,
            "drift_observation_count": len(certification.drift_observations),
            "observation_state_counts": count_drift_observation_states(certification.drift_observations),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_drift_certification",
            "payload_length": len(serialization_first),
            "observation_order_preserved": exported_observation_order == expected_observation_order,
            "blocked_drift_preserved": visibility["blocked_drift_visibility_count"] > 0,
            "unsupported_drift_preserved": visibility["unsupported_drift_visibility_count"] > 0,
            "cross_layer_conflict_preserved": visibility["cross_layer_conflict_visibility_count"] > 0,
            "prohibited_drift_preserved": visibility["prohibited_drift_visibility_count"] > 0,
            "stale_drift_preserved": visibility["stale_drift_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": drift_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_drift_certification",
            "drift_certification_hash": drift_hash,
            "identity_hash": hash_refresh_drift_certification_identity(certification.identity),
            "continuity_hash": hash_refresh_drift_continuity(certification.continuity_metadata),
            "diagnostics_hash": hash_refresh_drift_diagnostics(certification.diagnostics),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": certification == repeated,
            "dataclass_hash_stable": hash(certification) == hash(repeated),
            "serialized_equality_stable": refresh_drift_certifications_equal(certification, repeated),
            "reordered_serialized_equality_stable": refresh_drift_certifications_equal(certification, reordered),
        },
        "cross_layer_drift_visibility": {
            "manifest_drift_visible": visibility["manifest_drift_visible"],
            "dependency_drift_visible": visibility["dependency_drift_visible"],
            "lineage_drift_visible": visibility["lineage_drift_visible"],
            "schema_drift_visible": visibility["schema_drift_visible"],
            "sequencing_drift_visible": visibility["sequencing_drift_visible"],
            "cross_layer_conflict_visible": visibility["cross_layer_conflict_visible"],
            "classification_visibility_count": visibility["classification_visibility_count"],
            "severity_visibility_count": visibility["severity_visibility_count"],
        },
        "drift_continuity_visibility": continuity,
        "fail_visible_visibility": visibility,
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_remediation_correction_and_execution_guarantees": non_execution,
        "refresh_drift_identity_normalization": refresh_drift_identity_normalization_report(certification.identity),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_drift_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_drift_hashing_verified": drift_hash == repeated_hash == reordered_hash,
            "deterministic_drift_equality_verified": refresh_drift_certifications_equal(certification, repeated),
            "deterministic_drift_visibility_verified": visibility["valid"],
            "cross_layer_drift_classification_validated": visibility["classifications_visible"],
            "manifest_drift_visibility_validated": visibility["manifest_drift_visible"],
            "dependency_drift_visibility_validated": visibility["dependency_drift_visible"],
            "lineage_drift_visibility_validated": visibility["lineage_drift_visible"],
            "schema_drift_visibility_validated": visibility["schema_drift_visible"],
            "sequencing_drift_visibility_validated": visibility["sequencing_drift_visible"],
            "drift_provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "drift_lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "drift_replay_continuity_verified": continuity["replay_continuity_valid"],
            "drift_rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "blocked_drift_visibility_validated": visibility["blocked_drift_visible"],
            "unsupported_state_visibility_validated": visibility["unsupported_drift_visible"],
            "non_remediation_enforcement_validated": non_execution["drift_remediation_absent"],
            "non_correction_enforcement_validated": non_execution["automatic_drift_correction_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "certification_validation_verified": continuity["valid"] and integrity["valid"],
            "descriptive_only_verified": certification.descriptive_only and certification.non_executable,
        },
        "refresh_drift_certification": exported,
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_drift_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_drift_certification()
    diagnostics = build_refresh_drift_diagnostics(certification)
    non_execution = validate_refresh_drift_non_execution(certification)
    status = _status(diagnostics["visibility_validation"]["valid"] and diagnostics["enabled_capability_count"] == 0)
    report = {
        "schema_version": V4_1_REFRESH_DRIFT_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_6_refresh_drift_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh drift diagnostics without remediation correction or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_remediation_correction_and_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "drift_remediation_absent": diagnostics["drift_remediation_absent"],
            "automatic_drift_correction_absent": diagnostics["automatic_drift_correction_absent"],
            "automatic_repair_absent": diagnostics["automatic_repair_absent"],
            "silent_drift_suppression_absent": diagnostics["silent_drift_suppression_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_drift_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_drift_certification()
    continuity = certify_refresh_drift_continuity(certification)
    status = _status(continuity["valid"])
    report = {
        "schema_version": V4_1_REFRESH_DRIFT_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_6_refresh_drift_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh drift continuity certification without repair correction or execution",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity,
        "summary": {
            "foundation_status": status,
            "continuity_certification_verified": continuity["valid"],
            "drift_continuity_verified": continuity["drift_continuity_valid"],
            "lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_drift_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_drift_certification()
    integrity = validate_refresh_drift_integrity(certification)
    status = _status(integrity["valid"])
    report = {
        "schema_version": V4_1_REFRESH_DRIFT_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_6_refresh_drift_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh drift integrity auditing without remediation correction or execution",
        "integrity_mode": "descriptive_only_no_repair",
        "foundation_status": status,
        "integrity_validation": integrity,
        "summary": {
            "foundation_status": status,
            "integrity_validation_verified": integrity["valid"],
            "visibility_valid": integrity["visibility_valid"],
            "continuity_valid": integrity["continuity_valid"],
            "non_execution_valid": integrity["non_execution_valid"],
            "prohibited_leakage_visible": integrity["prohibited_leakage_visible"],
            "enabled_capability_count": integrity["non_execution_validation"]["enabled_capability_count"],
            "drift_remediation_disabled_validated": integrity["non_execution_validation"]["drift_remediation_absent"],
            "automatic_correction_disabled_validated": integrity["non_execution_validation"][
                "automatic_drift_correction_absent"
            ],
            "production_consumption_disabled_validated": integrity["non_execution_validation"][
                "production_consumption_absent"
            ],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_cross_layer_drift_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_drift_certification()
    visibility = validate_refresh_drift_visibility(certification)
    diagnostics = build_refresh_drift_diagnostics(certification)
    status = _status(
        visibility["manifest_drift_visible"]
        and visibility["dependency_drift_visible"]
        and visibility["lineage_drift_visible"]
        and visibility["schema_drift_visible"]
        and visibility["sequencing_drift_visible"]
        and visibility["cross_layer_conflict_visible"]
        and diagnostics["enabled_capability_count"] == 0
    )
    report = {
        "schema_version": V4_1_CROSS_LAYER_DRIFT_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_6_cross_layer_drift_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic cross-layer drift certification without remediation correction or execution",
        "cross_layer_mode": "descriptive_certification_only",
        "foundation_status": status,
        "cross_layer_visibility": {
            "manifest_drift_visible": visibility["manifest_drift_visible"],
            "dependency_drift_visible": visibility["dependency_drift_visible"],
            "lineage_drift_visible": visibility["lineage_drift_visible"],
            "schema_drift_visible": visibility["schema_drift_visible"],
            "sequencing_drift_visible": visibility["sequencing_drift_visible"],
            "cross_layer_conflict_visible": visibility["cross_layer_conflict_visible"],
            "blocked_drift_visible": visibility["blocked_drift_visible"],
            "unsupported_drift_visible": visibility["unsupported_drift_visible"],
            "stale_drift_visible": visibility["stale_drift_visible"],
            "prohibited_drift_visible": visibility["prohibited_drift_visible"],
        },
        "summary": {
            "foundation_status": status,
            "cross_layer_drift_certification_verified": status == V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_STABLE,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "manifest_drift_visibility_validated": visibility["manifest_drift_visible"],
            "dependency_drift_visibility_validated": visibility["dependency_drift_visible"],
            "lineage_drift_visibility_validated": visibility["lineage_drift_visible"],
            "schema_drift_visibility_validated": visibility["schema_drift_visible"],
            "sequencing_drift_visibility_validated": visibility["sequencing_drift_visible"],
            "cross_layer_drift_classification_validated": visibility["classifications_visible"],
            "non_remediation_enforcement_validated": diagnostics["drift_remediation_absent"],
            "non_correction_enforcement_validated": diagnostics["automatic_drift_correction_absent"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Refresh drift JSON report output path")
    parser.add_argument("--diagnostics-output", default=str(DIAGNOSTICS_REPORT_PATH), help="Drift diagnostics JSON report output path")
    parser.add_argument("--continuity-output", default=str(CONTINUITY_REPORT_PATH), help="Drift continuity JSON report output path")
    parser.add_argument("--integrity-output", default=str(INTEGRITY_REPORT_PATH), help="Drift integrity JSON report output path")
    parser.add_argument("--cross-layer-output", default=str(CROSS_LAYER_REPORT_PATH), help="Cross-layer drift JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_refresh_drift_certification_report()
    diagnostics_report = build_v4_1_refresh_drift_diagnostics_report()
    continuity_report = build_v4_1_refresh_drift_continuity_certification_report()
    integrity_report = build_v4_1_refresh_drift_integrity_certification_report()
    cross_layer_report = build_v4_1_cross_layer_drift_certification_report()
    write_report(report, Path(args.output))
    write_report(diagnostics_report, Path(args.diagnostics_output))
    write_report(continuity_report, Path(args.continuity_output))
    write_report(integrity_report, Path(args.integrity_output))
    write_report(cross_layer_report, Path(args.cross_layer_output))
    print(f"wrote {Path(args.output)}")
    print(f"wrote {Path(args.diagnostics_output)}")
    print(f"wrote {Path(args.continuity_output)}")
    print(f"wrote {Path(args.integrity_output)}")
    print(f"wrote {Path(args.cross_layer_output)}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"diagnostics_status={diagnostics_report['foundation_status']}")
    print(f"continuity_status={continuity_report['foundation_status']}")
    print(f"integrity_status={integrity_report['foundation_status']}")
    print(f"cross_layer_status={cross_layer_report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_diagnostics_report_hash={diagnostics_report['deterministic_report_hash']}")
    print(f"deterministic_continuity_report_hash={continuity_report['deterministic_report_hash']}")
    print(f"deterministic_integrity_report_hash={integrity_report['deterministic_report_hash']}")
    print(f"deterministic_cross_layer_report_hash={cross_layer_report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
