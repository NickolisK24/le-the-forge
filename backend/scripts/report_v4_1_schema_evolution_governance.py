"""Generate deterministic v4.1 schema evolution governance evidence."""

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

from operational_refresh.schema_evolution_governance_continuity import (  # noqa: E402
    certify_schema_evolution_continuity,
)
from operational_refresh.schema_evolution_governance_diagnostics import (  # noqa: E402
    build_schema_evolution_diagnostics,
)
from operational_refresh.schema_evolution_governance_hashing import (  # noqa: E402
    deterministic_schema_evolution_hash,
    hash_schema_continuity,
    hash_schema_diagnostics,
    hash_schema_evolution_governance,
    hash_schema_evolution_identity,
)
from operational_refresh.schema_evolution_governance_integrity import (  # noqa: E402
    schema_evolution_governances_equal,
    schema_evolution_identity_normalization_report,
    validate_schema_evolution_integrity,
    validate_schema_evolution_non_execution,
)
from operational_refresh.schema_evolution_governance_models import (  # noqa: E402
    V4_1_SCHEMA_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_SCHEMA_EVOLUTION_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PHASE_ID,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_REPORT_SCHEMA_VERSION,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_BLOCKED,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE,
    V4_1_SCHEMA_INTEGRITY_REPORT_SCHEMA_VERSION,
    default_schema_evolution_governance,
)
from operational_refresh.schema_evolution_governance_serialization import (  # noqa: E402
    export_schema_evolution_governance,
    serialize_schema_evolution_governance,
)
from operational_refresh.schema_evolution_governance_visibility import (  # noqa: E402
    count_schema_node_states,
    count_schema_transition_states,
    validate_schema_evolution_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_schema_evolution_governance_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_schema_evolution_diagnostics_report.json")
CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_schema_continuity_certification_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_schema_integrity_certification_report.json")


def _reordered_schema_governance():
    governance = default_schema_evolution_governance()
    return replace(
        governance,
        version_nodes=tuple(reversed(governance.version_nodes)),
        version_transitions=tuple(reversed(governance.version_transitions)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_schema_evolution_hash(payload)


def build_v4_1_schema_evolution_governance_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    governance = default_schema_evolution_governance()
    repeated = default_schema_evolution_governance()
    reordered = _reordered_schema_governance()
    exported = export_schema_evolution_governance(governance)
    visibility = validate_schema_evolution_visibility(governance)
    continuity = certify_schema_evolution_continuity(governance)
    non_execution = validate_schema_evolution_non_execution(governance)
    integrity = validate_schema_evolution_integrity(governance)
    diagnostics = build_schema_evolution_diagnostics(governance)
    serialization_first = serialize_schema_evolution_governance(governance)
    serialization_second = serialize_schema_evolution_governance(repeated)
    serialization_reordered = serialize_schema_evolution_governance(reordered)
    governance_hash = hash_schema_evolution_governance(governance)
    repeated_hash = hash_schema_evolution_governance(repeated)
    reordered_hash = hash_schema_evolution_governance(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if governance_hash == repeated_hash == reordered_hash else 1,
            0 if schema_evolution_governances_equal(governance, repeated) else 1,
        ]
    )
    status = (
        V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE
        if validation_error_count == 0
        else V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_BLOCKED
    )
    exported_node_order = [item["node_id"] for item in exported["version_nodes"]]
    expected_node_order = [
        item["node_id"]
        for item in sorted(exported["version_nodes"], key=lambda item: (item["deterministic_order"], item["node_id"]))
    ]
    exported_transition_order = [item["transition_id"] for item in exported["version_transitions"]]
    expected_transition_order = [
        item["transition_id"]
        for item in sorted(
            exported["version_transitions"],
            key=lambda item: (item["deterministic_order"], item["transition_id"]),
        )
    ]
    report = {
        "schema_version": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT,
        "phase_id": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PHASE_ID,
        "phase_name": "v4.1_phase_4_schema_evolution_governance",
        "repo_root": str(root),
        "architectural_purpose": "deterministic schema evolution governance without migration or execution",
        "schema_governance_mode": "descriptive_only",
        "foundation_status": status,
        "schema_model_counts": {
            "identity_count": 1,
            "version_node_count": len(governance.version_nodes),
            "version_transition_count": len(governance.version_transitions),
            "schema_node_state_counts": count_schema_node_states(governance.version_nodes),
            "schema_transition_state_counts": count_schema_transition_states(governance.version_transitions),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_schema_evolution_governance",
            "payload_length": len(serialization_first),
            "node_order_preserved": exported_node_order == expected_node_order,
            "transition_order_preserved": exported_transition_order == expected_transition_order,
            "blocked_states_preserved": visibility["blocked_transition_visibility_count"] > 0,
            "unsupported_states_preserved": visibility["unsupported_transition_visibility_count"] > 0,
            "circular_schema_ancestry_preserved": visibility["circular_schema_ancestry_visibility_count"] > 0,
            "prohibited_schema_preserved": visibility["prohibited_transition_visibility_count"] > 0,
            "stale_schema_preserved": visibility["stale_transition_visibility_count"] > 0,
            "schema_version_discontinuity_preserved": visibility["schema_version_discontinuity_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": governance_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_schema_evolution_governance",
            "schema_governance_hash": governance_hash,
            "identity_hash": hash_schema_evolution_identity(governance.identity),
            "continuity_hash": hash_schema_continuity(governance.continuity_metadata),
            "diagnostics_hash": hash_schema_diagnostics(governance.diagnostics),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": governance == repeated,
            "dataclass_hash_stable": hash(governance) == hash(repeated),
            "serialized_equality_stable": schema_evolution_governances_equal(governance, repeated),
            "reordered_serialized_equality_stable": schema_evolution_governances_equal(governance, reordered),
        },
        "schema_continuity_visibility": continuity["schema_continuity"],
        "lineage_continuity_visibility": continuity["lineage_continuity"],
        "provenance_continuity_visibility": continuity["provenance_continuity"],
        "replay_continuity_visibility": continuity["replay_continuity"],
        "rollback_continuity_visibility": continuity["rollback_continuity"],
        "compatibility_continuity_visibility": continuity["compatibility_continuity"],
        "fail_visible_visibility": {
            "fail_visible_transition_count": visibility["fail_visible_transition_count"],
            "unsupported_node_visibility_count": visibility["unsupported_node_visibility_count"],
            "unsupported_transition_visibility_count": visibility["unsupported_transition_visibility_count"],
            "blocked_transition_visibility_count": visibility["blocked_transition_visibility_count"],
            "stale_transition_visibility_count": visibility["stale_transition_visibility_count"],
            "prohibited_transition_visibility_count": visibility["prohibited_transition_visibility_count"],
            "circular_schema_ancestry_visibility_count": visibility["circular_schema_ancestry_visibility_count"],
            "schema_version_discontinuity_visibility_count": visibility["schema_version_discontinuity_visibility_count"],
            "schema_lineage_discontinuity_visibility_count": visibility["schema_lineage_discontinuity_visibility_count"],
            "schema_provenance_discontinuity_visibility_count": visibility["schema_provenance_discontinuity_visibility_count"],
            "schema_replay_discontinuity_visibility_count": visibility["schema_replay_discontinuity_visibility_count"],
            "schema_rollback_discontinuity_visibility_count": visibility["schema_rollback_discontinuity_visibility_count"],
            "prohibited_schema_domain_visibility_count": visibility["prohibited_schema_domain_visibility_count"],
            "failure_visibility_count": visibility["failure_visibility_count"],
            "compatibility_classification_visibility_count": visibility["compatibility_classification_visibility_count"],
            "diagnostics_warning_visibility_count": visibility["diagnostics_warning_visibility_count"],
            "unsupported_nodes_visible": visibility["unsupported_nodes_visible"],
            "unsupported_transitions_visible": visibility["unsupported_transitions_visible"],
            "blocked_transitions_visible": visibility["blocked_transitions_visible"],
            "stale_transitions_visible": visibility["stale_transitions_visible"],
            "prohibited_transitions_visible": visibility["prohibited_transitions_visible"],
            "circular_schema_ancestry_visible": visibility["circular_schema_ancestry_visible"],
            "schema_version_discontinuity_visible": visibility["schema_version_discontinuity_visible"],
            "prohibited_schema_domains_visible": visibility["prohibited_schema_domains_visible"],
            "compatibility_classifications_visible": visibility["compatibility_classifications_visible"],
            "visibility_is_descriptive_only": visibility["visibility_is_descriptive_only"],
        },
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_migration_and_non_execution_guarantees": non_execution,
        "schema_evolution_identity_normalization": schema_evolution_identity_normalization_report(governance.identity),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_schema_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_schema_hashing_verified": governance_hash == repeated_hash == reordered_hash,
            "deterministic_schema_equality_verified": schema_evolution_governances_equal(governance, repeated),
            "deterministic_schema_visibility_verified": visibility["valid"],
            "schema_lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "schema_provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "schema_replay_continuity_verified": continuity["replay_continuity_valid"],
            "schema_rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "schema_continuity_validated": continuity["schema_continuity_valid"],
            "compatibility_visibility_validated": continuity["compatibility_continuity_valid"],
            "blocked_transition_visibility_validated": visibility["blocked_transitions_visible"],
            "unsupported_state_visibility_validated": visibility["unsupported_transitions_visible"],
            "circular_schema_ancestry_visibility_validated": visibility["circular_schema_ancestry_visible"],
            "non_migration_enforcement_validated": non_execution["schema_migration_execution_absent"]
            and non_execution["automatic_schema_migration_absent"]
            and non_execution["automatic_compatibility_correction_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "certification_validation_verified": continuity["valid"] and integrity["valid"],
            "descriptive_only_verified": governance.descriptive_only and governance.non_executable,
        },
        "schema_evolution_governance": exported,
        "explicit_limitations": list(governance.governance.explicit_limitations),
        "explicit_prohibitions": list(governance.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_schema_evolution_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    governance = default_schema_evolution_governance()
    diagnostics = build_schema_evolution_diagnostics(governance)
    non_execution = validate_schema_evolution_non_execution(governance)
    status = (
        V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE
        if diagnostics["visibility_validation"]["valid"] and diagnostics["enabled_capability_count"] == 0
        else V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_SCHEMA_EVOLUTION_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT,
        "phase_id": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PHASE_ID,
        "phase_name": "v4.1_phase_4_schema_evolution_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic schema evolution diagnostics without correction or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_migration_and_non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "automatic_schema_migration_absent": diagnostics["automatic_schema_migration_absent"],
            "automatic_compatibility_correction_absent": diagnostics["automatic_compatibility_correction_absent"],
            "silent_compatibility_fallback_absent": diagnostics["silent_compatibility_fallback_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(governance.governance.explicit_limitations),
        "explicit_prohibitions": list(governance.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_schema_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    governance = default_schema_evolution_governance()
    continuity = certify_schema_evolution_continuity(governance)
    status = (
        V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE
        if continuity["valid"]
        else V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_SCHEMA_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT,
        "phase_id": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PHASE_ID,
        "phase_name": "v4.1_phase_4_schema_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic schema continuity certification without migration or repair",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity,
        "summary": {
            "foundation_status": status,
            "continuity_certification_verified": continuity["valid"],
            "schema_continuity_verified": continuity["schema_continuity_valid"],
            "lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "compatibility_continuity_verified": continuity["compatibility_continuity_valid"],
        },
        "explicit_limitations": list(governance.governance.explicit_limitations),
        "explicit_prohibitions": list(governance.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_schema_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    governance = default_schema_evolution_governance()
    integrity = validate_schema_evolution_integrity(governance)
    status = (
        V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE
        if integrity["valid"]
        else V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_SCHEMA_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT,
        "phase_id": V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PHASE_ID,
        "phase_name": "v4.1_phase_4_schema_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic schema integrity auditing without migration or correction",
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
            "migration_execution_disabled_validated": integrity["non_execution_validation"][
                "schema_migration_execution_absent"
            ],
            "automatic_compatibility_correction_disabled_validated": integrity["non_execution_validation"][
                "automatic_compatibility_correction_absent"
            ],
            "production_consumption_disabled_validated": integrity["non_execution_validation"][
                "production_consumption_absent"
            ],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(governance.governance.explicit_limitations),
        "explicit_prohibitions": list(governance.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Schema evolution JSON report output path")
    parser.add_argument(
        "--diagnostics-output",
        default=str(DIAGNOSTICS_REPORT_PATH),
        help="Schema evolution diagnostics JSON report output path",
    )
    parser.add_argument(
        "--continuity-output",
        default=str(CONTINUITY_REPORT_PATH),
        help="Schema continuity certification JSON report output path",
    )
    parser.add_argument(
        "--integrity-output",
        default=str(INTEGRITY_REPORT_PATH),
        help="Schema integrity certification JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_schema_evolution_governance_report()
    diagnostics_report = build_v4_1_schema_evolution_diagnostics_report()
    continuity_report = build_v4_1_schema_continuity_certification_report()
    integrity_report = build_v4_1_schema_integrity_certification_report()
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
