"""Generate deterministic v4.1 closeout and v4.2 readiness evidence."""

from __future__ import annotations

import argparse
import hashlib
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

from operational_refresh.v4_1_closeout_readiness_continuity import (  # noqa: E402
    certify_v4_1_closeout_continuity,
)
from operational_refresh.v4_1_closeout_readiness_diagnostics import (  # noqa: E402
    build_v4_1_closeout_diagnostics,
    build_v4_1_final_governance_summary,
    build_v4_2_planning_readiness_certification,
)
from operational_refresh.v4_1_closeout_readiness_hashing import (  # noqa: E402
    deterministic_v4_1_closeout_hash,
    hash_v4_1_closeout_identity,
    hash_v4_1_closeout_integrity,
    hash_v4_1_closeout_readiness,
    hash_v4_1_readiness_certification,
    hash_v4_1_warning_aggregation,
)
from operational_refresh.v4_1_closeout_readiness_integrity import (  # noqa: E402
    v4_1_closeout_identity_key,
    v4_1_closeout_identity_normalization_report,
    v4_1_closeout_readiness_equal,
    validate_v4_1_closeout_integrity,
    validate_v4_1_closeout_non_execution,
)
from operational_refresh.v4_1_closeout_readiness_models import (  # noqa: E402
    V4_1_CLOSEOUT_READINESS_GENERATED_AT,
    V4_1_CLOSEOUT_READINESS_PHASE_ID,
    V4_1_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
    V4_1_CLOSEOUT_READINESS_STATUS_BLOCKED,
    V4_1_CLOSEOUT_READINESS_STATUS_STABLE,
    V4_1_CLOSEOUT_REPORT_SCHEMA_VERSION,
    V4_1_CROSS_LAYER_GOVERNANCE_SUMMARY_REPORT_SCHEMA_VERSION,
    V4_1_CROSS_LAYER_INTEGRITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
    V4_1_EXPECTED_MIGRATION_DOC_NAMES,
    V4_1_EXPECTED_REPORT_NAMES,
    V4_1_EXPECTED_TEST_NAMES,
    V4_2_READINESS_CERTIFICATION_REPORT_SCHEMA_VERSION,
    build_v4_1_closeout_readiness,
)
from operational_refresh.v4_1_closeout_readiness_serialization import (  # noqa: E402
    export_v4_1_closeout_readiness,
    serialize_v4_1_closeout_readiness,
)
from operational_refresh.v4_1_closeout_readiness_visibility import (  # noqa: E402
    count_warning_categories,
    validate_v4_1_closeout_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_closeout_and_v4_2_readiness_report.json")
CLOSEOUT_REPORT_PATH = Path("docs/generated/v4_1_closeout_report.json")
READINESS_REPORT_PATH = Path("docs/generated/v4_2_readiness_certification_report.json")
GOVERNANCE_REPORT_PATH = Path("docs/generated/v4_1_cross_layer_governance_summary_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_cross_layer_integrity_certification_report.json")


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_evidence(repo_root: Path) -> tuple[dict[str, str], dict[str, bool], dict[str, bool], dict[str, bool], dict[str, bool]]:
    report_hashes: dict[str, str] = {}
    report_presence: dict[str, bool] = {}
    report_json_validity: dict[str, bool] = {}
    for report_name in V4_1_EXPECTED_REPORT_NAMES:
        path = repo_root / "docs" / "generated" / report_name
        present = path.exists()
        report_presence[report_name] = present
        if present:
            report_hashes[report_name] = _file_hash(path)
            try:
                json.loads(path.read_text(encoding="utf-8"))
                report_json_validity[report_name] = True
            except json.JSONDecodeError:
                report_json_validity[report_name] = False
        else:
            report_hashes[report_name] = ""
            report_json_validity[report_name] = False
    doc_presence = {
        doc_name: (repo_root / "docs" / "migration" / doc_name).exists()
        for doc_name in V4_1_EXPECTED_MIGRATION_DOC_NAMES
    }
    test_presence = {
        test_name: (repo_root / "backend" / "tests" / test_name).exists()
        for test_name in V4_1_EXPECTED_TEST_NAMES
    }
    return report_hashes, report_presence, report_json_validity, doc_presence, test_presence


def build_v4_1_closeout_payload(repo_root: Path | None = None):
    root = repo_root or Path(__file__).resolve().parents[2]
    report_hashes, report_presence, report_json_validity, doc_presence, test_presence = _artifact_evidence(root)
    return build_v4_1_closeout_readiness(
        report_hashes=report_hashes,
        report_presence=report_presence,
        report_json_validity=report_json_validity,
        doc_presence=doc_presence,
        test_presence=test_presence,
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_v4_1_closeout_hash(payload)


def _status(valid: bool) -> str:
    return V4_1_CLOSEOUT_READINESS_STATUS_STABLE if valid else V4_1_CLOSEOUT_READINESS_STATUS_BLOCKED


def _reordered_payload(repo_root: Path | None = None):
    payload = build_v4_1_closeout_payload(repo_root)
    return replace(
        payload,
        phase_coverage=tuple(reversed(payload.phase_coverage)),
        report_coverage=tuple(reversed(payload.report_coverage)),
        warnings=tuple(reversed(payload.warnings)),
    )


def build_v4_1_closeout_and_v4_2_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = build_v4_1_closeout_payload(root)
    repeated = build_v4_1_closeout_payload(root)
    reordered = _reordered_payload(root)
    exported = export_v4_1_closeout_readiness(payload)
    visibility = validate_v4_1_closeout_visibility(payload)
    continuity = certify_v4_1_closeout_continuity(payload)
    non_execution = validate_v4_1_closeout_non_execution(payload)
    integrity = validate_v4_1_closeout_integrity(payload)
    diagnostics = build_v4_1_closeout_diagnostics(payload)
    serialization_first = serialize_v4_1_closeout_readiness(payload)
    serialization_second = serialize_v4_1_closeout_readiness(repeated)
    serialization_reordered = serialize_v4_1_closeout_readiness(reordered)
    payload_hash = hash_v4_1_closeout_readiness(payload)
    repeated_hash = hash_v4_1_closeout_readiness(repeated)
    reordered_hash = hash_v4_1_closeout_readiness(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if payload_hash == repeated_hash == reordered_hash else 1,
            0 if v4_1_closeout_readiness_equal(payload, repeated) else 1,
        ]
    )
    status = _status(validation_error_count == 0)
    summary = {
        "foundation_status": status,
        "validation_error_count": validation_error_count,
        "closeout_status": payload.readiness.closeout_status,
        "v4_2_readiness_status": payload.readiness.v4_2_readiness_status,
        "deterministic_closeout_serialization_verified": serialization_first == serialization_second == serialization_reordered,
        "deterministic_closeout_hashing_verified": payload_hash == repeated_hash == reordered_hash,
        "deterministic_closeout_equality_verified": v4_1_closeout_readiness_equal(payload, repeated),
        "deterministic_closeout_visibility_verified": visibility["valid"],
        "phase_coverage_validated": visibility["phase_coverage_complete"],
        "report_coverage_validated": visibility["report_coverage_complete"],
        "integrity_coverage_validated": continuity["integrity_coverage_valid"],
        "continuity_coverage_validated": continuity["continuity_coverage_valid"],
        "replay_verification_validated": continuity["replay_verification_valid"],
        "rollback_verification_validated": continuity["rollback_verification_valid"],
        "provenance_verification_validated": continuity["provenance_verification_valid"],
        "lineage_verification_validated": continuity["lineage_verification_valid"],
        "readiness_visibility_validated": continuity["readiness_visibility_valid"],
        "warning_aggregation_validated": continuity["warning_aggregation_valid"],
        "unsupported_prohibited_blocked_aggregation_validated": continuity[
            "unsupported_prohibited_blocked_aggregation_valid"
        ],
        "non_remediation_enforcement_validated": non_execution["remediation_absent"],
        "non_correction_enforcement_validated": non_execution["automatic_correction_absent"],
        "non_approval_authorization_enforcement_validated": (
            non_execution["approval_absent"] and non_execution["authorization_absent"]
        ),
        "non_execution_enforcement_validated": non_execution["valid"],
        "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
        "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        "integrity_validation_verified": integrity["valid"],
        "certification_validation_verified": continuity["valid"],
        "closeout_readiness_validation_verified": visibility["valid"] and continuity["valid"],
    }
    report = {
        "schema_version": V4_1_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_CLOSEOUT_READINESS_GENERATED_AT,
        "phase_id": V4_1_CLOSEOUT_READINESS_PHASE_ID,
        "phase_name": "v4.1_phase_10_closeout_and_v4_2_readiness",
        "repo_root": str(root),
        "architectural_purpose": "deterministic v4.1 closeout and v4.2 planning readiness without remediation approval orchestration or execution",
        "closeout_mode": "descriptive_only_non_authorizing",
        "foundation_status": status,
        "model_counts": {
            "phase_count": len(payload.phase_coverage),
            "report_count": len(payload.report_coverage),
            "warning_count": len(payload.warnings),
            "warning_category_counts": count_warning_categories(payload.warnings),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_closeout_readiness",
            "payload_length": len(serialization_first),
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": payload_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_closeout_readiness",
            "closeout_readiness_hash": payload_hash,
            "identity_hash": hash_v4_1_closeout_identity(payload.identity),
            "readiness_hash": hash_v4_1_readiness_certification(payload.readiness),
            "warning_aggregation_hash": hash_v4_1_warning_aggregation(payload.warning_aggregation),
            "integrity_hash": hash_v4_1_closeout_integrity(payload.integrity_boundary),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": payload == repeated,
            "dataclass_hash_stable": hash(payload) == hash(repeated),
            "serialized_equality_stable": v4_1_closeout_readiness_equal(payload, repeated),
            "reordered_serialized_equality_stable": v4_1_closeout_readiness_equal(payload, reordered),
        },
        "closeout_visibility": visibility,
        "closeout_continuity_certification": continuity,
        "closeout_diagnostics": diagnostics,
        "integrity_validation": integrity,
        "non_remediation_approval_and_execution_guarantees": non_execution,
        "identity_key": v4_1_closeout_identity_key(payload.identity),
        "identity_normalization": v4_1_closeout_identity_normalization_report(payload.identity),
        "summary": summary,
        "v4_1_closeout_readiness": exported,
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_closeout_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = build_v4_1_closeout_payload(root)
    report = {
        "schema_version": V4_1_CLOSEOUT_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_CLOSEOUT_READINESS_GENERATED_AT,
        "phase_id": V4_1_CLOSEOUT_READINESS_PHASE_ID,
        "repo_root": str(root),
        "v4_1_closeout": build_v4_1_final_governance_summary(payload),
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_2_readiness_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = build_v4_1_closeout_payload(root)
    report = {
        "schema_version": V4_2_READINESS_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_CLOSEOUT_READINESS_GENERATED_AT,
        "phase_id": V4_1_CLOSEOUT_READINESS_PHASE_ID,
        "repo_root": str(root),
        "v4_2_readiness_certification": build_v4_2_planning_readiness_certification(payload),
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_cross_layer_governance_summary_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = build_v4_1_closeout_payload(root)
    report = {
        "schema_version": V4_1_CROSS_LAYER_GOVERNANCE_SUMMARY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_CLOSEOUT_READINESS_GENERATED_AT,
        "phase_id": V4_1_CLOSEOUT_READINESS_PHASE_ID,
        "repo_root": str(root),
        "cross_layer_governance_summary": build_v4_1_final_governance_summary(payload),
        "governance_scope": "v4_1_refresh_governance_closeout_descriptive_only",
        "approval_enabled": False,
        "authorization_enabled": False,
        "execution_enabled": False,
        "planner_integration_enabled": False,
        "production_consumption_enabled": False,
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_cross_layer_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = build_v4_1_closeout_payload(root)
    report = {
        "schema_version": V4_1_CROSS_LAYER_INTEGRITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_CLOSEOUT_READINESS_GENERATED_AT,
        "phase_id": V4_1_CLOSEOUT_READINESS_PHASE_ID,
        "repo_root": str(root),
        "cross_layer_integrity_certification": validate_v4_1_closeout_integrity(payload),
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
        "approval_enabled": False,
        "authorization_enabled": False,
        "orchestration_enabled": False,
        "execution_enabled": False,
        "planner_integration_enabled": False,
        "production_consumption_enabled": False,
        "runtime_mutation_enabled": False,
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_reports(repo_root: Path) -> dict[str, Path]:
    reports = {
        "v4_1_closeout_and_v4_2_readiness": (
            REPORT_PATH,
            build_v4_1_closeout_and_v4_2_readiness_report(repo_root),
        ),
        "v4_1_closeout": (CLOSEOUT_REPORT_PATH, build_v4_1_closeout_report(repo_root)),
        "v4_2_readiness_certification": (
            READINESS_REPORT_PATH,
            build_v4_2_readiness_certification_report(repo_root),
        ),
        "v4_1_cross_layer_governance_summary": (
            GOVERNANCE_REPORT_PATH,
            build_v4_1_cross_layer_governance_summary_report(repo_root),
        ),
        "v4_1_cross_layer_integrity_certification": (
            INTEGRITY_REPORT_PATH,
            build_v4_1_cross_layer_integrity_certification_report(repo_root),
        ),
    }
    written: dict[str, Path] = {}
    for name, (path, report) in reports.items():
        target = repo_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written[name] = target
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    written = write_reports(args.repo_root)
    for name, path in sorted(written.items()):
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
