"""Generate deterministic v4.1 replay and rollback visibility evidence."""

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

from operational_refresh.refresh_replay_rollback_visibility_continuity import (  # noqa: E402
    certify_replay_rollback_visibility_continuity,
)
from operational_refresh.refresh_replay_rollback_visibility_diagnostics import (  # noqa: E402
    build_replay_diagnostics,
    build_replay_rollback_diagnostics,
    build_rollback_diagnostics,
)
from operational_refresh.refresh_replay_rollback_visibility_hashing import (  # noqa: E402
    deterministic_replay_rollback_hash,
    hash_refresh_replay_rollback_visibility,
    hash_replay_rollback_continuity,
    hash_replay_rollback_diagnostics,
    hash_replay_rollback_identity,
)
from operational_refresh.refresh_replay_rollback_visibility_integrity import (  # noqa: E402
    refresh_replay_rollback_visibilities_equal,
    replay_rollback_identity_normalization_report,
    validate_replay_rollback_integrity,
    validate_replay_rollback_non_execution,
)
from operational_refresh.refresh_replay_rollback_visibility_models import (  # noqa: E402
    V4_1_REPLAY_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_REPLAY_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_1_REPLAY_ROLLBACK_INTEGRITY_REPORT_SCHEMA_VERSION,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_REPORT_SCHEMA_VERSION,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_BLOCKED,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_STABLE,
    V4_1_ROLLBACK_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_ROLLBACK_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    default_refresh_replay_rollback_visibility,
)
from operational_refresh.refresh_replay_rollback_visibility_serialization import (  # noqa: E402
    export_refresh_replay_rollback_visibility,
    serialize_refresh_replay_rollback_visibility,
)
from operational_refresh.refresh_replay_rollback_visibility_visibility import (  # noqa: E402
    count_replay_rollback_evidence_states,
    validate_refresh_replay_rollback_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_replay_rollback_visibility_report.json")
REPLAY_DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_replay_diagnostics_report.json")
ROLLBACK_DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_rollback_diagnostics_report.json")
REPLAY_CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_replay_continuity_certification_report.json")
ROLLBACK_CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_rollback_continuity_certification_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_replay_rollback_integrity_certification_report.json")


def _reordered_replay_rollback_visibility():
    visibility = default_refresh_replay_rollback_visibility()
    return replace(visibility, evidence=tuple(reversed(visibility.evidence)))


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_replay_rollback_hash(payload)


def _status(valid: bool) -> str:
    return V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_STABLE if valid else V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_BLOCKED


def build_v4_1_refresh_replay_rollback_visibility_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_refresh_replay_rollback_visibility()
    repeated = default_refresh_replay_rollback_visibility()
    reordered = _reordered_replay_rollback_visibility()
    exported = export_refresh_replay_rollback_visibility(visibility)
    visibility_validation = validate_refresh_replay_rollback_visibility(visibility)
    continuity = certify_replay_rollback_visibility_continuity(visibility)
    non_execution = validate_replay_rollback_non_execution(visibility)
    integrity = validate_replay_rollback_integrity(visibility)
    diagnostics = build_replay_rollback_diagnostics(visibility)
    serialization_first = serialize_refresh_replay_rollback_visibility(visibility)
    serialization_second = serialize_refresh_replay_rollback_visibility(repeated)
    serialization_reordered = serialize_refresh_replay_rollback_visibility(reordered)
    visibility_hash = hash_refresh_replay_rollback_visibility(visibility)
    repeated_hash = hash_refresh_replay_rollback_visibility(repeated)
    reordered_hash = hash_refresh_replay_rollback_visibility(reordered)
    validation_error_count = sum(
        [
            0 if visibility_validation["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if visibility_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_replay_rollback_visibilities_equal(visibility, repeated) else 1,
        ]
    )
    status = _status(validation_error_count == 0)
    exported_evidence_order = [item["evidence_id"] for item in exported["evidence"]]
    expected_evidence_order = [
        item["evidence_id"] for item in sorted(exported["evidence"], key=lambda item: (item["deterministic_order"], item["evidence_id"]))
    ]
    report = {
        "schema_version": V4_1_REPLAY_ROLLBACK_VISIBILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_7_refresh_replay_rollback_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic replay and rollback visibility without recovery rollback execution or execution",
        "replay_rollback_visibility_mode": "descriptive_only",
        "foundation_status": status,
        "visibility_model_counts": {
            "identity_count": 1,
            "evidence_count": len(visibility.evidence),
            "evidence_state_counts": count_replay_rollback_evidence_states(visibility.evidence),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_replay_rollback_visibility",
            "payload_length": len(serialization_first),
            "evidence_order_preserved": exported_evidence_order == expected_evidence_order,
            "blocked_replay_preserved": visibility_validation["blocked_replay_visibility_count"] > 0,
            "blocked_rollback_preserved": visibility_validation["blocked_rollback_visibility_count"] > 0,
            "unsupported_state_preserved": visibility_validation["unsupported_replay_visibility_count"] > 0
            and visibility_validation["unsupported_rollback_visibility_count"] > 0,
            "replay_drift_preserved": visibility_validation["replay_drift_conflict_visibility_count"] > 0,
            "rollback_drift_preserved": visibility_validation["rollback_drift_conflict_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": visibility_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_replay_rollback_visibility",
            "replay_rollback_visibility_hash": visibility_hash,
            "identity_hash": hash_replay_rollback_identity(visibility.identity),
            "continuity_hash": hash_replay_rollback_continuity(visibility.continuity_metadata),
            "diagnostics_hash": hash_replay_rollback_diagnostics(visibility.diagnostics),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": visibility == repeated,
            "dataclass_hash_stable": hash(visibility) == hash(repeated),
            "serialized_equality_stable": refresh_replay_rollback_visibilities_equal(visibility, repeated),
            "reordered_serialized_equality_stable": refresh_replay_rollback_visibilities_equal(visibility, reordered),
        },
        "replay_rollback_visibility": visibility_validation,
        "continuity_visibility": continuity,
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_recovery_remediation_and_execution_guarantees": non_execution,
        "replay_rollback_identity_normalization": replay_rollback_identity_normalization_report(visibility.identity),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_replay_rollback_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_replay_rollback_hashing_verified": visibility_hash == repeated_hash == reordered_hash,
            "deterministic_replay_rollback_equality_verified": refresh_replay_rollback_visibilities_equal(visibility, repeated),
            "deterministic_replay_rollback_visibility_verified": visibility_validation["valid"],
            "replay_continuity_validated": continuity["replay_continuity_valid"],
            "rollback_continuity_validated": continuity["rollback_continuity_valid"],
            "replay_lineage_continuity_validated": continuity["replay_lineage_continuity_valid"],
            "rollback_lineage_continuity_validated": continuity["rollback_lineage_continuity_valid"],
            "replay_provenance_continuity_validated": continuity["replay_provenance_continuity_valid"],
            "rollback_provenance_continuity_validated": continuity["rollback_provenance_continuity_valid"],
            "blocked_replay_visibility_validated": visibility_validation["blocked_replay_visible"],
            "blocked_rollback_visibility_validated": visibility_validation["blocked_rollback_visible"],
            "unsupported_state_visibility_validated": visibility_validation["unsupported_replay_visible"]
            and visibility_validation["unsupported_rollback_visible"],
            "replay_drift_validated": visibility_validation["replay_drift_conflict_visible"],
            "rollback_drift_validated": visibility_validation["rollback_drift_conflict_visible"],
            "non_recovery_enforcement_validated": non_execution["recovery_execution_absent"],
            "non_remediation_enforcement_validated": non_execution["remediation_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "certification_validation_verified": continuity["valid"] and integrity["valid"],
            "descriptive_only_verified": visibility.descriptive_only and visibility.non_executable,
        },
        "refresh_replay_rollback_visibility": exported,
        "explicit_limitations": list(visibility.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_replay_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_refresh_replay_rollback_visibility()
    diagnostics = build_replay_diagnostics(visibility)
    non_execution = validate_replay_rollback_non_execution(visibility)
    status = _status(diagnostics["enabled_capability_count"] == 0 and diagnostics["replay_execution_absent"])
    report = {
        "schema_version": V4_1_REPLAY_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_7_refresh_replay_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic replay diagnostics without replay execution recovery or remediation",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_recovery_remediation_and_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "replay_execution_absent": diagnostics["replay_execution_absent"],
            "recovery_execution_absent": diagnostics["recovery_execution_absent"],
            "remediation_absent": diagnostics["remediation_absent"],
            "automatic_correction_absent": diagnostics["automatic_correction_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(visibility.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_rollback_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_refresh_replay_rollback_visibility()
    diagnostics = build_rollback_diagnostics(visibility)
    non_execution = validate_replay_rollback_non_execution(visibility)
    status = _status(diagnostics["enabled_capability_count"] == 0 and diagnostics["rollback_execution_absent"])
    report = {
        "schema_version": V4_1_ROLLBACK_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_7_refresh_rollback_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic rollback diagnostics without rollback execution recovery or remediation",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_recovery_remediation_and_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "rollback_execution_absent": diagnostics["rollback_execution_absent"],
            "recovery_execution_absent": diagnostics["recovery_execution_absent"],
            "remediation_absent": diagnostics["remediation_absent"],
            "automatic_correction_absent": diagnostics["automatic_correction_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(visibility.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_replay_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_refresh_replay_rollback_visibility()
    continuity = certify_replay_rollback_visibility_continuity(visibility)
    status = _status(continuity["replay_continuity_valid"] and continuity["replay_lineage_continuity_valid"])
    report = {
        "schema_version": V4_1_REPLAY_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_7_refresh_replay_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic replay continuity certification without replay execution or recovery",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity["replay_continuity"],
        "lineage_continuity": continuity["lineage_continuity"],
        "provenance_continuity": continuity["provenance_continuity"],
        "summary": {
            "foundation_status": status,
            "replay_continuity_certification_verified": continuity["replay_continuity_valid"],
            "replay_lineage_continuity_verified": continuity["replay_lineage_continuity_valid"],
            "replay_provenance_continuity_verified": continuity["replay_provenance_continuity_valid"],
            "replay_drift_validation_verified": continuity["replay_drift_valid"],
        },
        "explicit_limitations": list(visibility.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_rollback_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_refresh_replay_rollback_visibility()
    continuity = certify_replay_rollback_visibility_continuity(visibility)
    status = _status(continuity["rollback_continuity_valid"] and continuity["rollback_lineage_continuity_valid"])
    report = {
        "schema_version": V4_1_ROLLBACK_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_7_refresh_rollback_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic rollback continuity certification without rollback execution or recovery",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity["rollback_continuity"],
        "lineage_continuity": continuity["lineage_continuity"],
        "provenance_continuity": continuity["provenance_continuity"],
        "summary": {
            "foundation_status": status,
            "rollback_continuity_certification_verified": continuity["rollback_continuity_valid"],
            "rollback_lineage_continuity_verified": continuity["rollback_lineage_continuity_valid"],
            "rollback_provenance_continuity_verified": continuity["rollback_provenance_continuity_valid"],
            "rollback_drift_validation_verified": continuity["rollback_drift_valid"],
        },
        "explicit_limitations": list(visibility.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_replay_rollback_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_refresh_replay_rollback_visibility()
    integrity = validate_replay_rollback_integrity(visibility)
    status = _status(integrity["valid"])
    report = {
        "schema_version": V4_1_REPLAY_ROLLBACK_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_7_refresh_replay_rollback_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic replay rollback integrity auditing without recovery rollback execution or execution",
        "integrity_mode": "descriptive_only_no_recovery_no_repair",
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
            "rollback_execution_disabled_validated": integrity["non_execution_validation"]["rollback_execution_absent"],
            "replay_execution_disabled_validated": integrity["non_execution_validation"]["replay_execution_absent"],
            "recovery_execution_disabled_validated": integrity["non_execution_validation"]["recovery_execution_absent"],
            "remediation_disabled_validated": integrity["non_execution_validation"]["remediation_absent"],
            "automatic_correction_disabled_validated": integrity["non_execution_validation"]["automatic_correction_absent"],
            "production_consumption_disabled_validated": integrity["non_execution_validation"][
                "production_consumption_absent"
            ],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(visibility.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Replay rollback visibility JSON report output path")
    parser.add_argument("--replay-diagnostics-output", default=str(REPLAY_DIAGNOSTICS_REPORT_PATH))
    parser.add_argument("--rollback-diagnostics-output", default=str(ROLLBACK_DIAGNOSTICS_REPORT_PATH))
    parser.add_argument("--replay-continuity-output", default=str(REPLAY_CONTINUITY_REPORT_PATH))
    parser.add_argument("--rollback-continuity-output", default=str(ROLLBACK_CONTINUITY_REPORT_PATH))
    parser.add_argument("--integrity-output", default=str(INTEGRITY_REPORT_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_refresh_replay_rollback_visibility_report()
    replay_diagnostics_report = build_v4_1_refresh_replay_diagnostics_report()
    rollback_diagnostics_report = build_v4_1_refresh_rollback_diagnostics_report()
    replay_continuity_report = build_v4_1_refresh_replay_continuity_certification_report()
    rollback_continuity_report = build_v4_1_refresh_rollback_continuity_certification_report()
    integrity_report = build_v4_1_refresh_replay_rollback_integrity_certification_report()
    write_report(report, Path(args.output))
    write_report(replay_diagnostics_report, Path(args.replay_diagnostics_output))
    write_report(rollback_diagnostics_report, Path(args.rollback_diagnostics_output))
    write_report(replay_continuity_report, Path(args.replay_continuity_output))
    write_report(rollback_continuity_report, Path(args.rollback_continuity_output))
    write_report(integrity_report, Path(args.integrity_output))
    print(f"wrote {Path(args.output)}")
    print(f"wrote {Path(args.replay_diagnostics_output)}")
    print(f"wrote {Path(args.rollback_diagnostics_output)}")
    print(f"wrote {Path(args.replay_continuity_output)}")
    print(f"wrote {Path(args.rollback_continuity_output)}")
    print(f"wrote {Path(args.integrity_output)}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"replay_diagnostics_status={replay_diagnostics_report['foundation_status']}")
    print(f"rollback_diagnostics_status={rollback_diagnostics_report['foundation_status']}")
    print(f"replay_continuity_status={replay_continuity_report['foundation_status']}")
    print(f"rollback_continuity_status={rollback_continuity_report['foundation_status']}")
    print(f"integrity_status={integrity_report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_replay_diagnostics_report_hash={replay_diagnostics_report['deterministic_report_hash']}")
    print(f"deterministic_rollback_diagnostics_report_hash={rollback_diagnostics_report['deterministic_report_hash']}")
    print(f"deterministic_replay_continuity_report_hash={replay_continuity_report['deterministic_report_hash']}")
    print(f"deterministic_rollback_continuity_report_hash={rollback_continuity_report['deterministic_report_hash']}")
    print(f"deterministic_integrity_report_hash={integrity_report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
