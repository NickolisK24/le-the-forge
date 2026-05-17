"""Generate deterministic v4.1 refresh continuity certification evidence."""

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

from operational_refresh.refresh_continuity_certification_continuity import (  # noqa: E402
    certify_refresh_continuity,
)
from operational_refresh.refresh_continuity_certification_diagnostics import (  # noqa: E402
    build_cross_layer_continuity_diagnostics,
    build_cross_layer_continuity_explainability,
    build_refresh_continuity_certification_diagnostics,
    build_unified_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_hashing import (  # noqa: E402
    deterministic_continuity_certification_hash,
    hash_continuity_certification_identity,
    hash_continuity_diagnostics,
    hash_continuity_explainability,
    hash_continuity_integrity,
    hash_continuity_metadata,
    hash_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_integrity import (  # noqa: E402
    continuity_certification_identity_normalization_report,
    refresh_continuity_certifications_equal,
    validate_continuity_certification_integrity,
    validate_continuity_certification_non_execution,
)
from operational_refresh.refresh_continuity_certification_models import (  # noqa: E402
    V4_1_CROSS_LAYER_CONTINUITY_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_1_CROSS_LAYER_CONTINUITY_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
    V4_1_CROSS_LAYER_CONTINUITY_INTEGRITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_BLOCKED,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_STABLE,
    V4_1_UNIFIED_REFRESH_CONTINUITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
    default_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_serialization import (  # noqa: E402
    export_refresh_continuity_certification,
    serialize_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_visibility import (  # noqa: E402
    count_continuity_states,
    validate_refresh_continuity_certification_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_continuity_certification_report.json")
UNIFIED_REPORT_PATH = Path("docs/generated/v4_1_unified_refresh_continuity_certification_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_cross_layer_continuity_diagnostics_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_cross_layer_continuity_integrity_certification_report.json")
EXPLAINABILITY_REPORT_PATH = Path("docs/generated/v4_1_cross_layer_continuity_explainability_report.json")


def _reordered_continuity_certification():
    payload = default_refresh_continuity_certification()
    return replace(payload, certifications=tuple(reversed(payload.certifications)))


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_continuity_certification_hash(payload)


def _status(valid: bool) -> str:
    return V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_STABLE if valid else V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_BLOCKED


def build_v4_1_refresh_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_continuity_certification()
    repeated = default_refresh_continuity_certification()
    reordered = _reordered_continuity_certification()
    exported = export_refresh_continuity_certification(payload)
    visibility = validate_refresh_continuity_certification_visibility(payload)
    continuity = certify_refresh_continuity(payload)
    non_execution = validate_continuity_certification_non_execution(payload)
    integrity = validate_continuity_certification_integrity(payload)
    diagnostics = build_refresh_continuity_certification_diagnostics(payload)
    serialization_first = serialize_refresh_continuity_certification(payload)
    serialization_second = serialize_refresh_continuity_certification(repeated)
    serialization_reordered = serialize_refresh_continuity_certification(reordered)
    payload_hash = hash_refresh_continuity_certification(payload)
    repeated_hash = hash_refresh_continuity_certification(repeated)
    reordered_hash = hash_refresh_continuity_certification(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if payload_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_continuity_certifications_equal(payload, repeated) else 1,
        ]
    )
    status = _status(validation_error_count == 0)
    exported_order = [item["certification_id"] for item in exported["certifications"]]
    expected_order = [
        item["certification_id"]
        for item in sorted(
            exported["certifications"],
            key=lambda item: (item["deterministic_order"], item["certification_id"]),
        )
    ]
    summary = {
        "foundation_status": status,
        "validation_error_count": validation_error_count,
        "enabled_capability_count": diagnostics["enabled_capability_count"],
        "deterministic_continuity_serialization_verified": (
            serialization_first == serialization_second == serialization_reordered
        ),
        "deterministic_continuity_hashing_verified": payload_hash == repeated_hash == reordered_hash,
        "deterministic_continuity_equality_verified": refresh_continuity_certifications_equal(payload, repeated),
        "deterministic_continuity_visibility_verified": visibility["valid"],
        "manifest_continuity_validated": continuity["manifest_continuity_valid"],
        "dependency_continuity_validated": continuity["dependency_continuity_valid"],
        "lineage_continuity_validated": continuity["lineage_continuity_valid"],
        "schema_continuity_validated": continuity["schema_continuity_valid"],
        "sequencing_continuity_validated": continuity["sequencing_continuity_valid"],
        "drift_continuity_validated": continuity["drift_continuity_valid"],
        "replay_continuity_validated": continuity["replay_continuity_valid"],
        "rollback_continuity_validated": continuity["rollback_continuity_valid"],
        "diagnostics_continuity_validated": continuity["diagnostics_continuity_valid"],
        "explainability_continuity_validated": continuity["explainability_continuity_valid"],
        "cross_layer_continuity_aggregation_validated": continuity["cross_layer_continuity_valid"],
        "unsupported_continuity_state_validated": visibility["unsupported_continuity_state_visible"],
        "blocked_continuity_state_validated": visibility["blocked_continuity_state_visible"],
        "prohibited_continuity_state_validated": visibility["prohibited_continuity_state_visible"],
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
        "cross_layer_continuity_validation_verified": continuity["cross_layer_continuity_valid"],
    }
    report = {
        "schema_version": V4_1_REFRESH_CONTINUITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_9_refresh_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh continuity certification without remediation approval orchestration or execution",
        "continuity_certification_mode": "descriptive_only_non_authorizing",
        "foundation_status": status,
        "model_counts": {
            "identity_count": 1,
            "certification_count": len(payload.certifications),
            "continuity_state_counts": count_continuity_states(payload.certifications),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_continuity_certification",
            "payload_length": len(serialization_first),
            "certification_order_preserved": exported_order == expected_order,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": payload_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_continuity_certification",
            "continuity_certification_hash": payload_hash,
            "identity_hash": hash_continuity_certification_identity(payload.identity),
            "continuity_metadata_hash": hash_continuity_metadata(payload.continuity_metadata),
            "diagnostics_hash": hash_continuity_diagnostics(payload.diagnostics),
            "explainability_hash": hash_continuity_explainability(payload.explainability),
            "integrity_hash": hash_continuity_integrity(payload.integrity_boundary),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": payload == repeated,
            "dataclass_hash_stable": hash(payload) == hash(repeated),
            "serialized_equality_stable": refresh_continuity_certifications_equal(payload, repeated),
            "reordered_serialized_equality_stable": refresh_continuity_certifications_equal(payload, reordered),
        },
        "continuity_visibility": visibility,
        "continuity_certification": continuity,
        "continuity_diagnostics": diagnostics,
        "integrity_validation": integrity,
        "non_remediation_approval_and_execution_guarantees": non_execution,
        "identity_normalization": continuity_certification_identity_normalization_report(payload.identity),
        "summary": summary,
        "refresh_continuity_certification": exported,
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_unified_refresh_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_continuity_certification()
    body = build_unified_refresh_continuity_certification(payload)
    report = {
        "schema_version": V4_1_UNIFIED_REFRESH_CONTINUITY_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID,
        "repo_root": str(root),
        "unified_refresh_continuity_certification": body,
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_cross_layer_continuity_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_continuity_certification()
    report = {
        "schema_version": V4_1_CROSS_LAYER_CONTINUITY_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID,
        "repo_root": str(root),
        "cross_layer_continuity_diagnostics": build_cross_layer_continuity_diagnostics(payload),
        "diagnostics_are_descriptive_only": True,
        "automatic_correction_enabled": False,
        "execution_enabled": False,
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_cross_layer_continuity_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_continuity_certification()
    integrity = validate_continuity_certification_integrity(payload)
    report = {
        "schema_version": V4_1_CROSS_LAYER_CONTINUITY_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID,
        "repo_root": str(root),
        "cross_layer_continuity_integrity_certification": integrity,
        "remediation_enabled": False,
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


def build_v4_1_cross_layer_continuity_explainability_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_continuity_certification()
    report = {
        "schema_version": V4_1_CROSS_LAYER_CONTINUITY_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID,
        "repo_root": str(root),
        "cross_layer_continuity_explainability": build_cross_layer_continuity_explainability(payload),
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_reports(repo_root: Path) -> dict[str, Path]:
    reports = {
        "refresh_continuity_certification": (
            REPORT_PATH,
            build_v4_1_refresh_continuity_certification_report(repo_root),
        ),
        "unified_refresh_continuity_certification": (
            UNIFIED_REPORT_PATH,
            build_v4_1_unified_refresh_continuity_certification_report(repo_root),
        ),
        "cross_layer_continuity_diagnostics": (
            DIAGNOSTICS_REPORT_PATH,
            build_v4_1_cross_layer_continuity_diagnostics_report(repo_root),
        ),
        "cross_layer_continuity_integrity_certification": (
            INTEGRITY_REPORT_PATH,
            build_v4_1_cross_layer_continuity_integrity_certification_report(repo_root),
        ),
        "cross_layer_continuity_explainability": (
            EXPLAINABILITY_REPORT_PATH,
            build_v4_1_cross_layer_continuity_explainability_report(repo_root),
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
