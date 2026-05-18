"""Generate deterministic v4.3 orchestration transition visibility evidence."""

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

from orchestration_governance.orchestration_transition_diagnostics import (  # noqa: E402
    build_transition_visibility_diagnostics,
    count_transition_states,
    transition_visibilities_equal,
    transition_visibility_identity_key,
    validate_transition_continuity,
    validate_transition_explainability,
    validate_transition_identity,
    validate_transition_metadata,
    validate_transition_non_execution_and_non_activation,
    validate_transition_relationships,
    validate_transition_state_visibility,
    validate_transition_support_visibility,
)
from orchestration_governance.orchestration_transition_hashing import (  # noqa: E402
    deterministic_transition_hash,
    hash_orchestration_transition_visibility,
    hash_transition_diagnostic,
    hash_transition_explainability,
    hash_transition_record,
    hash_transition_relationship,
    hash_transition_visibility_identity,
)
from orchestration_governance.orchestration_transition_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_TRANSITION_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_TRANSITION_PROHIBITIONS,
    V4_3_ORCHESTRATION_TRANSITION_GENERATED_AT,
    V4_3_ORCHESTRATION_TRANSITION_PHASE_ID,
    V4_3_ORCHESTRATION_TRANSITION_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_TRANSITION_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_TRANSITION_STATUS_STABLE,
    default_orchestration_transition_visibility,
)
from orchestration_governance.orchestration_transition_serialization import (  # noqa: E402
    export_orchestration_transition_visibility,
    serialize_orchestration_transition_visibility,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_transition_visibility_report.json")


def _reordered_transition_visibility():
    visibility = default_orchestration_transition_visibility()
    return replace(
        visibility,
        transitions=tuple(reversed(visibility.transitions)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_transition_hash(payload)


def build_v4_3_orchestration_transition_visibility_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_orchestration_transition_visibility()
    repeated = default_orchestration_transition_visibility()
    reordered = _reordered_transition_visibility()
    exported = export_orchestration_transition_visibility(visibility)
    identity = validate_transition_identity(visibility)
    support = validate_transition_support_visibility(visibility)
    states = validate_transition_state_visibility(visibility)
    metadata = validate_transition_metadata(visibility)
    relationships = validate_transition_relationships(visibility)
    continuity = validate_transition_continuity(visibility)
    explainability = validate_transition_explainability(visibility)
    non_execution = validate_transition_non_execution_and_non_activation(visibility)
    diagnostics = build_transition_visibility_diagnostics(visibility)
    serialization_first = serialize_orchestration_transition_visibility(visibility)
    serialization_second = serialize_orchestration_transition_visibility(repeated)
    serialization_reordered = serialize_orchestration_transition_visibility(reordered)
    visibility_hash = hash_orchestration_transition_visibility(visibility)
    repeated_hash = hash_orchestration_transition_visibility(repeated)
    reordered_hash = hash_orchestration_transition_visibility(reordered)
    transition_hashes = [hash_transition_record(transition) for transition in visibility.transitions]
    relationship_hashes = [
        hash_transition_relationship(relationship) for relationship in visibility.relationships
    ]
    diagnostic_hashes = [hash_transition_diagnostic(diagnostic) for diagnostic in visibility.diagnostics]
    explainability_hashes = [
        hash_transition_explainability(summary) for summary in visibility.explainability_summaries
    ]
    exported_transition_order = [item["transition_id"] for item in exported["transitions"]]
    expected_transition_order = [
        item["transition_id"]
        for item in sorted(
            exported["transitions"],
            key=lambda item: (item["deterministic_order"], item["transition_id"]),
        )
    ]
    exported_relationship_order = [item["relationship_id"] for item in exported["relationships"]]
    expected_relationship_order = [
        item["relationship_id"]
        for item in sorted(
            exported["relationships"],
            key=lambda item: (item["deterministic_order"], item["relationship_id"]),
        )
    ]
    validation_error_count = sum(
        [
            0 if identity["valid"] else 1,
            0 if support["valid"] else 1,
            0 if states["valid"] else 1,
            0 if metadata["valid"] else 1,
            0 if relationships["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if visibility_hash == repeated_hash == reordered_hash else 1,
            0 if transition_visibilities_equal(visibility, repeated) else 1,
            0 if exported_transition_order == expected_transition_order else 1,
            0 if exported_relationship_order == expected_relationship_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_TRANSITION_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_TRANSITION_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_3_ORCHESTRATION_TRANSITION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_TRANSITION_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_TRANSITION_PHASE_ID,
        "phase_name": "v4.3_phase_5_orchestration_transition_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration transition visibility without execution",
        "transition_mode": "descriptive_only_non_executing_non_activating_transition_governance",
        "transition_visibility_status": status,
        "transition_counts": {
            "transition_count": len(visibility.transitions),
            "prohibited_transition_count": len(diagnostics["prohibited_transition_ids"]),
            "unsupported_transition_count": len(diagnostics["unsupported_transition_ids"]),
            "blocked_transition_count": len(diagnostics["blocked_transition_ids"]),
            "stale_transition_count": len(diagnostics["stale_transition_ids"]),
            "conflicting_transition_count": len(diagnostics["conflicting_transition_ids"]),
            "relationship_count": len(visibility.relationships),
            "invalid_source_to_target_count": diagnostics["invalid_source_to_target_count"],
            "invalid_relationship_count": diagnostics["invalid_relationship_count"],
            "diagnostic_count": len(visibility.diagnostics),
            "explainability_summary_count": len(visibility.explainability_summaries),
            "transition_state_counts": count_transition_states(visibility.transitions),
        },
        "identity_visibility": {
            "identity_key": transition_visibility_identity_key(visibility),
            "identity_validation": identity,
            "identity_hash": hash_transition_visibility_identity(visibility.identity),
        },
        "support_state_visibility": {
            "support_visibility_validation": support,
            "prohibited_transition_ids": diagnostics["prohibited_transition_ids"],
            "unsupported_transition_ids": diagnostics["unsupported_transition_ids"],
            "blocked_transition_ids": diagnostics["blocked_transition_ids"],
            "stale_transition_ids": diagnostics["stale_transition_ids"],
            "conflicting_transition_ids": diagnostics["conflicting_transition_ids"],
            "unknown_transition_ids": diagnostics["unknown_transition_ids"],
            "prohibited_transitions_visible": support["prohibited_transitions_visible"],
            "unsupported_transitions_visible": support["unsupported_transitions_visible"],
            "blocked_transitions_visible": support["blocked_transitions_visible"],
            "stale_transitions_visible": support["stale_transitions_visible"],
            "conflicting_transitions_visible": support["conflicting_transitions_visible"],
        },
        "source_target_state_visibility": {
            "state_visibility_validation": states,
            "invalid_source_to_target_count": states["invalid_source_to_target_count"],
            "missing_source_state_ids": states["missing_source_state_ids"],
            "missing_target_state_ids": states["missing_target_state_ids"],
            "self_referential_transition_ids": states["self_referential_transition_ids"],
        },
        "metadata_visibility": {
            "metadata_validation": metadata,
            "governance_metadata_present": metadata["governance_metadata_present"],
            "transition_boundary_metadata_present": metadata["transition_boundary_metadata_present"],
            "transition_policy_metadata_present": metadata["transition_policy_metadata_present"],
            "continuity_metadata_present": metadata["continuity_metadata_present"],
            "provenance_metadata_present": metadata["provenance_metadata_present"],
            "lineage_metadata_present": metadata["lineage_metadata_present"],
            "diagnostics_metadata_present": metadata["diagnostics_metadata_present"],
            "explainability_metadata_present": metadata["explainability_metadata_present"],
            "non_execution_metadata_present": metadata["non_execution_metadata_present"],
            "non_activation_metadata_present": metadata["non_activation_metadata_present"],
        },
        "relationship_visibility": {
            "relationship_validation": relationships,
            "relationship_hashes": relationship_hashes,
            "invalid_relationship_count": relationships["invalid_relationship_count"],
            "invalid_policy_relationship_ids": relationships["invalid_policy_relationship_ids"],
            "invalid_capability_relationship_ids": relationships["invalid_capability_relationship_ids"],
            "invalid_boundary_relationship_ids": relationships["invalid_boundary_relationship_ids"],
            "invalid_topology_relationship_ids": relationships["invalid_topology_relationship_ids"],
            "invalid_manifest_relationship_ids": relationships["invalid_manifest_relationship_ids"],
            "operational_relationship_ids": relationships["operational_relationship_ids"],
        },
        "continuity_visibility": {
            "continuity_validation": continuity,
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "provenance_continuity_preserved": continuity["provenance_continuity_preserved"],
            "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
            "transition_continuity_visible": continuity["transition_continuity_visible"],
        },
        "diagnostic_aggregation": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "execution_absent": diagnostics["execution_absent"],
            "repair_absent": diagnostics["repair_absent"],
            "inference_absent": diagnostics["inference_absent"],
            "authorization_absent": diagnostics["authorization_absent"],
            "mutation_absent": diagnostics["mutation_absent"],
            "activation_absent": diagnostics["activation_absent"],
        },
        "explainability_findings": {
            "explainability_validation": explainability,
            "explainability_hashes": explainability_hashes,
            "prohibited_transition_visible": "prohibited_transition" in explainability["explainability_categories"],
            "unsupported_transition_visible": "unsupported_transition" in explainability["explainability_categories"],
            "blocked_transition_visible": "blocked_transition" in explainability["explainability_categories"],
            "stale_transition_visible": "stale_transition" in explainability["explainability_categories"],
            "conflicting_transition_visible": "conflicting_transition" in explainability["explainability_categories"],
            "transition_execution_unavailable_visible": (
                "transition_execution_unavailable" in explainability["explainability_categories"]
            ),
            "orchestration_activation_unavailable_visible": (
                "orchestration_activation_unavailable" in explainability["explainability_categories"]
            ),
            "state_progression_unavailable_visible": (
                "state_progression_unavailable" in explainability["explainability_categories"]
            ),
            "planner_integration_unavailable_visible": (
                "planner_integration_unavailable" in explainability["explainability_categories"]
            ),
            "production_consumption_unavailable_visible": (
                "production_consumption_unavailable" in explainability["explainability_categories"]
            ),
            "governance_constraints_visible": (
                "governance_constraints_exist" in explainability["explainability_categories"]
            ),
            "operational_orchestration_prohibited_visible": (
                "operational_orchestration_prohibited" in explainability["explainability_categories"]
            ),
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_transition_visibility",
            "payload_length": len(serialization_first),
            "transition_ordering_stable": exported_transition_order == expected_transition_order,
            "relationship_ordering_stable": exported_relationship_order == expected_relationship_order,
            "source_state_ordering_stable": [
                item["source_state_id"] for item in exported["transitions"]
            ]
            == [
                item["source_state_id"]
                for item in sorted(
                    exported["transitions"],
                    key=lambda item: (item["deterministic_order"], item["transition_id"]),
                )
            ],
            "target_state_ordering_stable": [
                item["target_state_id"] for item in exported["transitions"]
            ]
            == [
                item["target_state_id"]
                for item in sorted(
                    exported["transitions"],
                    key=lambda item: (item["deterministic_order"], item["transition_id"]),
                )
            ],
            "diagnostics_ordering_stable": [item["diagnostic_id"] for item in exported["diagnostics"]]
            == [
                item["diagnostic_id"]
                for item in sorted(
                    exported["diagnostics"],
                    key=lambda item: (item["deterministic_order"], item["diagnostic_id"]),
                )
            ],
            "explainability_ordering_stable": [
                item["explanation_id"] for item in exported["explainability_summaries"]
            ]
            == [
                item["explanation_id"]
                for item in sorted(
                    exported["explainability_summaries"],
                    key=lambda item: (item["deterministic_order"], item["explanation_id"]),
                )
            ],
            "prohibited_states_preserved": len(diagnostics["prohibited_transition_ids"]) > 0,
            "unsupported_states_preserved": len(diagnostics["unsupported_transition_ids"]) > 0,
            "blocked_states_preserved": len(diagnostics["blocked_transition_ids"]) > 0,
            "stale_states_preserved": len(diagnostics["stale_transition_ids"]) > 0,
            "conflicting_states_preserved": len(diagnostics["conflicting_transition_ids"]) > 0,
        },
        "hashing_stability_evidence": {
            "stable": visibility_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_transition_visibility",
            "transition_visibility_hash": visibility_hash,
            "repeated_transition_visibility_hash": repeated_hash,
            "reordered_transition_visibility_hash": reordered_hash,
            "identity_hash": hash_transition_visibility_identity(visibility.identity),
            "transition_hashes": transition_hashes,
            "relationship_hashes": relationship_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "non_execution_guarantees": non_execution,
        "non_activation_guarantees": {
            "valid": non_execution["valid"],
            "transition_execution_disabled": non_execution["transition_execution_disabled"],
            "orchestration_activation_disabled": non_execution["orchestration_activation_disabled"],
            "state_progression_disabled": non_execution["state_progression_disabled"],
            "transition_engine_absent": non_execution["transition_engine_absent"],
            "orchestration_runtime_absent": non_execution["orchestration_runtime_absent"],
            "executable_state_machine_absent": non_execution["executable_state_machine_absent"],
            "orchestration_dispatcher_absent": non_execution["orchestration_dispatcher_absent"],
            "enabled_transition_execution_count": non_execution["enabled_transition_execution_count"],
        },
        "summary": {
            "transition_visibility_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": visibility_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": transition_visibilities_equal(visibility, repeated),
            "transition_ordering_verified": exported_transition_order == expected_transition_order,
            "relationship_ordering_verified": exported_relationship_order == expected_relationship_order,
            "identity_visibility_verified": identity["valid"],
            "support_state_visibility_verified": support["valid"],
            "state_visibility_verified": states["valid"],
            "metadata_visibility_verified": metadata["valid"],
            "relationship_visibility_verified": relationships["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "non_activation_guarantees_validated": non_execution["valid"],
            "enabled_transition_execution_count": non_execution["enabled_transition_execution_count"],
            "enabled_operational_capability_count": non_execution["enabled_operational_capability_count"],
            "enabled_policy_enforcement_count": non_execution["enabled_policy_enforcement_count"],
            "transition_execution_disabled": non_execution["transition_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "state_machine_execution_disabled": non_execution["state_machine_execution_disabled"],
            "runtime_execution_disabled": non_execution["runtime_execution_disabled"],
            "orchestration_activation_disabled": non_execution["orchestration_activation_disabled"],
            "state_progression_disabled": non_execution["state_progression_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "traversal_execution_disabled": non_execution["traversal_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "transition_authorization_disabled": non_execution["transition_authorization_disabled"],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "transition_dispatch_disabled": non_execution["transition_dispatch_disabled"],
            "operational_coordination_disabled": non_execution["operational_coordination_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "transition_engine_absent": non_execution["transition_engine_absent"],
            "orchestration_runtime_absent": non_execution["orchestration_runtime_absent"],
            "executable_state_machine_absent": non_execution["executable_state_machine_absent"],
            "orchestration_dispatcher_absent": non_execution["orchestration_dispatcher_absent"],
        },
        "transition_visibility": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_TRANSITION_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_TRANSITION_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Transition visibility JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_transition_visibility_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"transition_visibility_status={report['transition_visibility_status']}")
    print(f"enabled_transition_execution_count={report['summary']['enabled_transition_execution_count']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"enabled_policy_enforcement_count={report['summary']['enabled_policy_enforcement_count']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
