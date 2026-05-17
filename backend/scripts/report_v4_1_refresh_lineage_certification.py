"""Generate deterministic v4.1 refresh lineage certification evidence."""

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

from operational_refresh.refresh_lineage_certification_continuity import (  # noqa: E402
    certify_refresh_lineage_continuity,
)
from operational_refresh.refresh_lineage_certification_diagnostics import (  # noqa: E402
    build_lineage_certification_diagnostics,
)
from operational_refresh.refresh_lineage_certification_hashing import (  # noqa: E402
    deterministic_refresh_lineage_certification_hash,
    hash_lineage_continuity,
    hash_lineage_diagnostics,
    hash_lineage_identity,
    hash_refresh_lineage_certification,
)
from operational_refresh.refresh_lineage_certification_integrity import (  # noqa: E402
    lineage_identity_normalization_report,
    refresh_lineage_certifications_equal,
    validate_lineage_integrity,
    validate_lineage_non_execution,
)
from operational_refresh.refresh_lineage_certification_models import (  # noqa: E402
    V4_1_REFRESH_LINEAGE_CERTIFICATION_DIAGNOSTICS_SCHEMA_VERSION,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_PHASE_ID,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_BLOCKED,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE,
    V4_1_REFRESH_LINEAGE_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_LINEAGE_INTEGRITY_REPORT_SCHEMA_VERSION,
    default_refresh_lineage_certification,
)
from operational_refresh.refresh_lineage_certification_serialization import (  # noqa: E402
    export_refresh_lineage_certification,
    serialize_refresh_lineage_certification,
)
from operational_refresh.refresh_lineage_certification_visibility import (  # noqa: E402
    count_ancestry_link_states,
    count_ancestry_node_states,
    validate_refresh_lineage_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_lineage_certification_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_lineage_certification_diagnostics_report.json")
CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_lineage_continuity_certification_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_lineage_integrity_certification_report.json")


def _reordered_lineage_certification():
    certification = default_refresh_lineage_certification()
    return replace(
        certification,
        ancestry_nodes=tuple(reversed(certification.ancestry_nodes)),
        ancestry_links=tuple(reversed(certification.ancestry_links)),
        provenance_inheritance=tuple(reversed(certification.provenance_inheritance)),
    )


def build_v4_1_refresh_lineage_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_lineage_certification()
    repeated = default_refresh_lineage_certification()
    reordered = _reordered_lineage_certification()
    exported = export_refresh_lineage_certification(certification)
    visibility = validate_refresh_lineage_visibility(certification)
    continuity = certify_refresh_lineage_continuity(certification)
    non_execution = validate_lineage_non_execution(certification)
    integrity = validate_lineage_integrity(certification)
    diagnostics = build_lineage_certification_diagnostics(certification)
    serialization_first = serialize_refresh_lineage_certification(certification)
    serialization_second = serialize_refresh_lineage_certification(repeated)
    serialization_reordered = serialize_refresh_lineage_certification(reordered)
    certification_hash = hash_refresh_lineage_certification(certification)
    repeated_hash = hash_refresh_lineage_certification(repeated)
    reordered_hash = hash_refresh_lineage_certification(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if certification_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_lineage_certifications_equal(certification, repeated) else 1,
        ]
    )
    status = (
        V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE
        if validation_error_count == 0
        else V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_BLOCKED
    )
    exported_node_order = [item["node_id"] for item in exported["ancestry_nodes"]]
    expected_node_order = [
        item["node_id"]
        for item in sorted(exported["ancestry_nodes"], key=lambda item: (item["deterministic_order"], item["node_id"]))
    ]
    exported_link_order = [item["link_id"] for item in exported["ancestry_links"]]
    expected_link_order = [
        item["link_id"]
        for item in sorted(exported["ancestry_links"], key=lambda item: (item["deterministic_order"], item["link_id"]))
    ]
    report = {
        "schema_version": V4_1_REFRESH_LINEAGE_CERTIFICATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_LINEAGE_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_3_refresh_lineage_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh lineage certification without orchestration or execution",
        "lineage_certification_mode": "descriptive_only",
        "foundation_status": status,
        "lineage_model_counts": {
            "identity_count": 1,
            "ancestry_node_count": len(certification.ancestry_nodes),
            "ancestry_link_count": len(certification.ancestry_links),
            "provenance_inheritance_count": len(certification.provenance_inheritance),
            "ancestry_node_state_counts": count_ancestry_node_states(certification.ancestry_nodes),
            "ancestry_link_state_counts": count_ancestry_link_states(certification.ancestry_links),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_lineage_certification",
            "payload_length": len(serialization_first),
            "node_order_preserved": exported_node_order == expected_node_order,
            "link_order_preserved": exported_link_order == expected_link_order,
            "blocked_states_preserved": visibility["blocked_lineage_link_visibility_count"] > 0,
            "unsupported_states_preserved": visibility["unsupported_lineage_link_visibility_count"] > 0,
            "circular_ancestry_preserved": visibility["circular_ancestry_visibility_count"] > 0,
            "prohibited_lineage_preserved": visibility["prohibited_lineage_link_visibility_count"] > 0,
            "stale_lineage_preserved": visibility["stale_lineage_link_visibility_count"] > 0,
            "schema_discontinuity_preserved": visibility["schema_discontinuity_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": certification_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_lineage_certification",
            "certification_hash": certification_hash,
            "identity_hash": hash_lineage_identity(certification.identity),
            "continuity_hash": hash_lineage_continuity(certification.continuity_metadata),
            "diagnostics_hash": hash_lineage_diagnostics(certification.diagnostics),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": certification == repeated,
            "dataclass_hash_stable": hash(certification) == hash(repeated),
            "serialized_equality_stable": refresh_lineage_certifications_equal(certification, repeated),
            "reordered_serialized_equality_stable": refresh_lineage_certifications_equal(certification, reordered),
        },
        "ancestry_continuity_visibility": continuity["ancestry_continuity"],
        "lineage_continuity_visibility": continuity["lineage_continuity"],
        "provenance_continuity_visibility": continuity["provenance_continuity"],
        "replay_continuity_visibility": continuity["replay_continuity"],
        "rollback_continuity_visibility": continuity["rollback_continuity"],
        "schema_continuity_visibility": continuity["schema_continuity"],
        "fail_visible_visibility": {
            "fail_visible_ancestry_link_count": visibility["fail_visible_ancestry_link_count"],
            "unsupported_lineage_node_visibility_count": visibility["unsupported_lineage_node_visibility_count"],
            "unsupported_lineage_link_visibility_count": visibility["unsupported_lineage_link_visibility_count"],
            "blocked_lineage_link_visibility_count": visibility["blocked_lineage_link_visibility_count"],
            "stale_lineage_link_visibility_count": visibility["stale_lineage_link_visibility_count"],
            "prohibited_lineage_link_visibility_count": visibility["prohibited_lineage_link_visibility_count"],
            "circular_ancestry_visibility_count": visibility["circular_ancestry_visibility_count"],
            "lineage_discontinuity_visibility_count": visibility["lineage_discontinuity_visibility_count"],
            "provenance_discontinuity_visibility_count": visibility["provenance_discontinuity_visibility_count"],
            "schema_discontinuity_visibility_count": visibility["schema_discontinuity_visibility_count"],
            "replay_discontinuity_visibility_count": visibility["replay_discontinuity_visibility_count"],
            "rollback_discontinuity_visibility_count": visibility["rollback_discontinuity_visibility_count"],
            "prohibited_lineage_domain_visibility_count": visibility["prohibited_lineage_domain_visibility_count"],
            "failure_visibility_count": visibility["failure_visibility_count"],
            "diagnostics_warning_visibility_count": visibility["diagnostics_warning_visibility_count"],
            "unsupported_nodes_visible": visibility["unsupported_nodes_visible"],
            "unsupported_links_visible": visibility["unsupported_links_visible"],
            "blocked_links_visible": visibility["blocked_links_visible"],
            "stale_links_visible": visibility["stale_links_visible"],
            "prohibited_links_visible": visibility["prohibited_links_visible"],
            "circular_ancestry_visible": visibility["circular_ancestry_visible"],
            "schema_discontinuity_visible": visibility["schema_discontinuity_visible"],
            "prohibited_lineage_domains_visible": visibility["prohibited_lineage_domains_visible"],
            "visibility_is_descriptive_only": visibility["visibility_is_descriptive_only"],
        },
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_execution_guarantees": non_execution,
        "lineage_identity_normalization": lineage_identity_normalization_report(certification.identity),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_certification_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_certification_hashing_verified": certification_hash == repeated_hash == reordered_hash,
            "deterministic_lineage_equality_verified": refresh_lineage_certifications_equal(certification, repeated),
            "deterministic_lineage_visibility_verified": visibility["valid"],
            "ancestry_continuity_verified": continuity["ancestry_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "schema_continuity_validated": continuity["schema_continuity_valid"],
            "blocked_state_visibility_validated": visibility["blocked_links_visible"],
            "unsupported_state_visibility_validated": visibility["unsupported_links_visible"],
            "circular_ancestry_visibility_validated": visibility["circular_ancestry_visible"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "certification_validation_verified": continuity["valid"] and integrity["valid"],
            "descriptive_only_verified": certification.descriptive_only and certification.non_executable,
        },
        "refresh_lineage_certification": exported,
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_lineage_certification_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_lineage_certification()
    diagnostics = build_lineage_certification_diagnostics(certification)
    non_execution = validate_lineage_non_execution(certification)
    status = (
        V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE
        if diagnostics["visibility_validation"]["valid"] and diagnostics["enabled_capability_count"] == 0
        else V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_LINEAGE_CERTIFICATION_DIAGNOSTICS_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_LINEAGE_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_3_refresh_lineage_certification_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh lineage diagnostics visibility without remediation or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "silent_correction_absent": diagnostics["silent_correction_absent"],
            "automatic_recovery_absent": diagnostics["automatic_recovery_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_lineage_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_lineage_certification()
    continuity = certify_refresh_lineage_continuity(certification)
    status = (
        V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE
        if continuity["valid"]
        else V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_LINEAGE_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_LINEAGE_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_3_refresh_lineage_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh lineage continuity certification without repair or execution",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity,
        "summary": {
            "foundation_status": status,
            "continuity_certification_verified": continuity["valid"],
            "ancestry_continuity_verified": continuity["ancestry_continuity_valid"],
            "lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "schema_continuity_validated": continuity["schema_continuity_valid"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_lineage_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_refresh_lineage_certification()
    integrity = validate_lineage_integrity(certification)
    status = (
        V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE
        if integrity["valid"]
        else V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_LINEAGE_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_1_REFRESH_LINEAGE_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.1_phase_3_refresh_lineage_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh lineage integrity auditing without automatic correction",
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
            "production_consumption_disabled_validated": integrity["non_execution_validation"]["production_consumption_absent"],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(certification.governance.explicit_limitations),
        "explicit_prohibitions": list(certification.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_refresh_lineage_certification_hash(payload)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Lineage certification JSON report output path")
    parser.add_argument(
        "--diagnostics-output",
        default=str(DIAGNOSTICS_REPORT_PATH),
        help="Lineage diagnostics JSON report output path",
    )
    parser.add_argument(
        "--continuity-output",
        default=str(CONTINUITY_REPORT_PATH),
        help="Lineage continuity certification JSON report output path",
    )
    parser.add_argument(
        "--integrity-output",
        default=str(INTEGRITY_REPORT_PATH),
        help="Lineage integrity certification JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_refresh_lineage_certification_report()
    diagnostics_report = build_v4_1_refresh_lineage_certification_diagnostics_report()
    continuity_report = build_v4_1_refresh_lineage_continuity_certification_report()
    integrity_report = build_v4_1_refresh_lineage_integrity_certification_report()
    write_report(report, Path(args.output))
    write_report(diagnostics_report, Path(args.diagnostics_output))
    write_report(continuity_report, Path(args.continuity_output))
    write_report(integrity_report, Path(args.integrity_output))
    print(f"wrote {Path(args.output)}")
    print(f"wrote {Path(args.diagnostics_output)}")
    print(f"wrote {Path(args.continuity_output)}")
    print(f"wrote {Path(args.integrity_output)}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"diagnostics_status={diagnostics_report['foundation_status']}")
    print(f"continuity_status={continuity_report['foundation_status']}")
    print(f"integrity_status={integrity_report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_diagnostics_report_hash={diagnostics_report['deterministic_report_hash']}")
    print(f"deterministic_continuity_report_hash={continuity_report['deterministic_report_hash']}")
    print(f"deterministic_integrity_report_hash={integrity_report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
