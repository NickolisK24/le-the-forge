"""Generate deterministic v4.1 refresh sequencing visibility evidence."""

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

from operational_refresh.refresh_sequencing_visibility_continuity import (  # noqa: E402
    certify_refresh_sequencing_continuity,
)
from operational_refresh.refresh_sequencing_visibility_diagnostics import (  # noqa: E402
    build_refresh_sequencing_diagnostics,
)
from operational_refresh.refresh_sequencing_visibility_hashing import (  # noqa: E402
    deterministic_refresh_sequencing_hash,
    hash_refresh_sequencing_continuity,
    hash_refresh_sequencing_diagnostics,
    hash_refresh_sequencing_identity,
    hash_refresh_sequencing_visibility,
)
from operational_refresh.refresh_sequencing_visibility_integrity import (  # noqa: E402
    refresh_sequencing_identity_normalization_report,
    refresh_sequencing_visibilities_equal,
    validate_refresh_sequencing_integrity,
    validate_refresh_sequencing_non_execution,
)
from operational_refresh.refresh_sequencing_visibility_models import (  # noqa: E402
    V4_1_REFRESH_SEQUENCING_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_SEQUENCING_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_SEQUENCING_INTEGRITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_PHASE_ID,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_BLOCKED,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE,
    default_refresh_sequencing_visibility,
)
from operational_refresh.refresh_sequencing_visibility_serialization import (  # noqa: E402
    export_refresh_sequencing_visibility,
    serialize_refresh_sequencing_visibility,
)
from operational_refresh.refresh_sequencing_visibility_visibility import (  # noqa: E402
    count_refresh_ordering_node_states,
    count_refresh_ordering_relationship_states,
    validate_refresh_sequencing_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_sequencing_visibility_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_sequencing_diagnostics_report.json")
CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_sequencing_continuity_certification_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_sequencing_integrity_certification_report.json")


def _reordered_refresh_sequencing_visibility():
    visibility = default_refresh_sequencing_visibility()
    return replace(
        visibility,
        ordering_nodes=tuple(reversed(visibility.ordering_nodes)),
        ordering_relationships=tuple(reversed(visibility.ordering_relationships)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_refresh_sequencing_hash(payload)


def build_v4_1_refresh_sequencing_visibility_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility_model = default_refresh_sequencing_visibility()
    repeated = default_refresh_sequencing_visibility()
    reordered = _reordered_refresh_sequencing_visibility()
    exported = export_refresh_sequencing_visibility(visibility_model)
    visibility = validate_refresh_sequencing_visibility(visibility_model)
    continuity = certify_refresh_sequencing_continuity(visibility_model)
    non_execution = validate_refresh_sequencing_non_execution(visibility_model)
    integrity = validate_refresh_sequencing_integrity(visibility_model)
    diagnostics = build_refresh_sequencing_diagnostics(visibility_model)
    serialization_first = serialize_refresh_sequencing_visibility(visibility_model)
    serialization_second = serialize_refresh_sequencing_visibility(repeated)
    serialization_reordered = serialize_refresh_sequencing_visibility(reordered)
    sequencing_hash = hash_refresh_sequencing_visibility(visibility_model)
    repeated_hash = hash_refresh_sequencing_visibility(repeated)
    reordered_hash = hash_refresh_sequencing_visibility(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if sequencing_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_sequencing_visibilities_equal(visibility_model, repeated) else 1,
        ]
    )
    status = (
        V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE
        if validation_error_count == 0
        else V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_BLOCKED
    )
    exported_node_order = [item["node_id"] for item in exported["ordering_nodes"]]
    expected_node_order = [
        item["node_id"]
        for item in sorted(exported["ordering_nodes"], key=lambda item: (item["deterministic_order"], item["node_id"]))
    ]
    exported_relationship_order = [item["relationship_id"] for item in exported["ordering_relationships"]]
    expected_relationship_order = [
        item["relationship_id"]
        for item in sorted(
            exported["ordering_relationships"],
            key=lambda item: (item["deterministic_order"], item["relationship_id"]),
        )
    ]
    report = {
        "schema_version": V4_1_REFRESH_SEQUENCING_VISIBILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_SEQUENCING_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_5_refresh_sequencing_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh sequencing visibility without orchestration or execution",
        "sequencing_visibility_mode": "descriptive_only",
        "foundation_status": status,
        "sequencing_model_counts": {
            "identity_count": 1,
            "ordering_node_count": len(visibility_model.ordering_nodes),
            "ordering_relationship_count": len(visibility_model.ordering_relationships),
            "ordering_node_state_counts": count_refresh_ordering_node_states(visibility_model.ordering_nodes),
            "ordering_relationship_state_counts": count_refresh_ordering_relationship_states(
                visibility_model.ordering_relationships
            ),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_sequencing_visibility",
            "payload_length": len(serialization_first),
            "node_order_preserved": exported_node_order == expected_node_order,
            "relationship_order_preserved": exported_relationship_order == expected_relationship_order,
            "blocked_order_preserved": visibility["blocked_relationship_visibility_count"] > 0,
            "unsupported_state_preserved": visibility["unsupported_relationship_visibility_count"] > 0,
            "circular_sequencing_preserved": visibility["circular_sequencing_visibility_count"] > 0,
            "prohibited_sequencing_preserved": visibility["prohibited_relationship_visibility_count"] > 0,
            "stale_sequencing_preserved": visibility["stale_relationship_visibility_count"] > 0,
            "dependency_ordering_discontinuity_preserved": (
                visibility["dependency_ordering_discontinuity_visibility_count"] > 0
            ),
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": sequencing_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_sequencing_visibility",
            "sequencing_visibility_hash": sequencing_hash,
            "identity_hash": hash_refresh_sequencing_identity(visibility_model.identity),
            "continuity_hash": hash_refresh_sequencing_continuity(visibility_model.continuity_metadata),
            "diagnostics_hash": hash_refresh_sequencing_diagnostics(visibility_model.diagnostics),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": visibility_model == repeated,
            "dataclass_hash_stable": hash(visibility_model) == hash(repeated),
            "serialized_equality_stable": refresh_sequencing_visibilities_equal(visibility_model, repeated),
            "reordered_serialized_equality_stable": refresh_sequencing_visibilities_equal(visibility_model, reordered),
        },
        "sequencing_continuity_visibility": continuity["sequencing_continuity"],
        "dependency_ordering_continuity_visibility": continuity["dependency_ordering_continuity"],
        "lineage_continuity_visibility": continuity["lineage_continuity"],
        "provenance_continuity_visibility": continuity["provenance_continuity"],
        "replay_continuity_visibility": continuity["replay_continuity"],
        "rollback_continuity_visibility": continuity["rollback_continuity"],
        "fail_visible_visibility": {
            "fail_visible_relationship_count": visibility["fail_visible_relationship_count"],
            "unsupported_node_visibility_count": visibility["unsupported_node_visibility_count"],
            "unsupported_relationship_visibility_count": visibility["unsupported_relationship_visibility_count"],
            "blocked_relationship_visibility_count": visibility["blocked_relationship_visibility_count"],
            "stale_relationship_visibility_count": visibility["stale_relationship_visibility_count"],
            "prohibited_relationship_visibility_count": visibility["prohibited_relationship_visibility_count"],
            "circular_sequencing_visibility_count": visibility["circular_sequencing_visibility_count"],
            "sequencing_discontinuity_visibility_count": visibility["sequencing_discontinuity_visibility_count"],
            "dependency_ordering_discontinuity_visibility_count": (
                visibility["dependency_ordering_discontinuity_visibility_count"]
            ),
            "lineage_discontinuity_visibility_count": visibility["lineage_discontinuity_visibility_count"],
            "provenance_discontinuity_visibility_count": visibility["provenance_discontinuity_visibility_count"],
            "replay_discontinuity_visibility_count": visibility["replay_discontinuity_visibility_count"],
            "rollback_discontinuity_visibility_count": visibility["rollback_discontinuity_visibility_count"],
            "prohibited_sequencing_domain_visibility_count": visibility["prohibited_sequencing_domain_visibility_count"],
            "failure_visibility_count": visibility["failure_visibility_count"],
            "dependency_ordering_reference_visibility_count": visibility["dependency_ordering_reference_visibility_count"],
            "diagnostics_warning_visibility_count": visibility["diagnostics_warning_visibility_count"],
            "unsupported_nodes_visible": visibility["unsupported_nodes_visible"],
            "unsupported_relationships_visible": visibility["unsupported_relationships_visible"],
            "blocked_relationships_visible": visibility["blocked_relationships_visible"],
            "stale_relationships_visible": visibility["stale_relationships_visible"],
            "prohibited_relationships_visible": visibility["prohibited_relationships_visible"],
            "circular_sequencing_visible": visibility["circular_sequencing_visible"],
            "dependency_ordering_discontinuity_visible": visibility["dependency_ordering_discontinuity_visible"],
            "prohibited_sequencing_domains_visible": visibility["prohibited_sequencing_domains_visible"],
            "dependency_references_visible": visibility["dependency_references_visible"],
            "visibility_is_descriptive_only": visibility["visibility_is_descriptive_only"],
        },
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_orchestration_and_non_execution_guarantees": non_execution,
        "refresh_sequencing_identity_normalization": refresh_sequencing_identity_normalization_report(
            visibility_model.identity
        ),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_sequencing_serialization_verified": (
                serialization_first == serialization_second == serialization_reordered
            ),
            "deterministic_sequencing_hashing_verified": sequencing_hash == repeated_hash == reordered_hash,
            "deterministic_sequencing_equality_verified": refresh_sequencing_visibilities_equal(
                visibility_model,
                repeated,
            ),
            "deterministic_sequencing_visibility_verified": visibility["valid"],
            "sequencing_lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "sequencing_provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "sequencing_replay_continuity_verified": continuity["replay_continuity_valid"],
            "sequencing_rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "sequencing_continuity_validated": continuity["sequencing_continuity_valid"],
            "dependency_ordering_continuity_validated": continuity["dependency_ordering_continuity_valid"],
            "blocked_order_visibility_validated": visibility["blocked_relationships_visible"],
            "unsupported_state_visibility_validated": visibility["unsupported_relationships_visible"],
            "circular_sequencing_visibility_validated": visibility["circular_sequencing_visible"],
            "non_orchestration_enforcement_validated": (
                non_execution["orchestration_absent"]
                and non_execution["automatic_sequencing_absent"]
                and non_execution["automatic_dependency_resolution_absent"]
            ),
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "certification_validation_verified": continuity["valid"] and integrity["valid"],
            "descriptive_only_verified": visibility_model.descriptive_only and visibility_model.non_executable,
        },
        "refresh_sequencing_visibility": exported,
        "explicit_limitations": list(visibility_model.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility_model.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_sequencing_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility_model = default_refresh_sequencing_visibility()
    diagnostics = build_refresh_sequencing_diagnostics(visibility_model)
    non_execution = validate_refresh_sequencing_non_execution(visibility_model)
    status = (
        V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE
        if diagnostics["visibility_validation"]["valid"] and diagnostics["enabled_capability_count"] == 0
        else V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_SEQUENCING_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_SEQUENCING_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_5_refresh_sequencing_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh sequencing diagnostics without remediation or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_orchestration_and_non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "automatic_sequencing_absent": diagnostics["automatic_sequencing_absent"],
            "automatic_dependency_resolution_absent": diagnostics["automatic_dependency_resolution_absent"],
            "silent_ordering_correction_absent": diagnostics["silent_ordering_correction_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(visibility_model.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility_model.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_sequencing_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility_model = default_refresh_sequencing_visibility()
    continuity = certify_refresh_sequencing_continuity(visibility_model)
    status = (
        V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE
        if continuity["valid"]
        else V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_SEQUENCING_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_SEQUENCING_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_5_refresh_sequencing_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh sequencing continuity certification without sequencing or repair",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity,
        "summary": {
            "foundation_status": status,
            "continuity_certification_verified": continuity["valid"],
            "sequencing_continuity_verified": continuity["sequencing_continuity_valid"],
            "dependency_ordering_continuity_verified": continuity["dependency_ordering_continuity_valid"],
            "lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
        },
        "explicit_limitations": list(visibility_model.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility_model.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_sequencing_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility_model = default_refresh_sequencing_visibility()
    integrity = validate_refresh_sequencing_integrity(visibility_model)
    status = (
        V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE
        if integrity["valid"]
        else V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_SEQUENCING_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_SEQUENCING_VISIBILITY_PHASE_ID,
        "phase_name": "v4.1_phase_5_refresh_sequencing_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh sequencing integrity auditing without orchestration or correction",
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
            "orchestration_disabled_validated": integrity["non_execution_validation"]["orchestration_absent"],
            "automatic_sequencing_disabled_validated": integrity["non_execution_validation"][
                "automatic_sequencing_absent"
            ],
            "production_consumption_disabled_validated": integrity["non_execution_validation"][
                "production_consumption_absent"
            ],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(visibility_model.governance.explicit_limitations),
        "explicit_prohibitions": list(visibility_model.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Refresh sequencing JSON report output path")
    parser.add_argument(
        "--diagnostics-output",
        default=str(DIAGNOSTICS_REPORT_PATH),
        help="Refresh sequencing diagnostics JSON report output path",
    )
    parser.add_argument(
        "--continuity-output",
        default=str(CONTINUITY_REPORT_PATH),
        help="Refresh sequencing continuity certification JSON report output path",
    )
    parser.add_argument(
        "--integrity-output",
        default=str(INTEGRITY_REPORT_PATH),
        help="Refresh sequencing integrity certification JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_refresh_sequencing_visibility_report()
    diagnostics_report = build_v4_1_refresh_sequencing_diagnostics_report()
    continuity_report = build_v4_1_refresh_sequencing_continuity_certification_report()
    integrity_report = build_v4_1_refresh_sequencing_integrity_certification_report()
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
