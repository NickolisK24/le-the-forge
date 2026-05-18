"""Generate deterministic v4.3 orchestration coordination visibility evidence."""

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

from orchestration_governance.orchestration_coordination_diagnostics import (  # noqa: E402
    build_coordination_visibility_diagnostics,
    coordination_visibilities_equal,
    coordination_visibility_identity_key,
    count_coordination_states,
    validate_coordination_continuity,
    validate_coordination_explainability,
    validate_coordination_identity,
    validate_coordination_metadata,
    validate_coordination_non_execution_and_non_coordination,
    validate_coordination_participants,
    validate_coordination_relationships,
    validate_coordination_support_visibility,
)
from orchestration_governance.orchestration_coordination_hashing import (  # noqa: E402
    deterministic_coordination_hash,
    hash_coordination_diagnostic,
    hash_coordination_explainability,
    hash_coordination_participant,
    hash_coordination_record,
    hash_coordination_relationship,
    hash_coordination_visibility_identity,
    hash_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_coordination_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_COORDINATION_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_COORDINATION_PROHIBITIONS,
    V4_3_ORCHESTRATION_COORDINATION_GENERATED_AT,
    V4_3_ORCHESTRATION_COORDINATION_PHASE_ID,
    V4_3_ORCHESTRATION_COORDINATION_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_COORDINATION_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_COORDINATION_STATUS_STABLE,
    default_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_coordination_serialization import (  # noqa: E402
    export_orchestration_coordination_visibility,
    serialize_orchestration_coordination_visibility,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_coordination_visibility_report.json")


def _reordered_coordination_visibility():
    visibility = default_orchestration_coordination_visibility()
    return replace(
        visibility,
        coordinations=tuple(reversed(visibility.coordinations)),
        participants=tuple(reversed(visibility.participants)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_hash(payload)


def build_v4_3_orchestration_coordination_visibility_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_orchestration_coordination_visibility()
    repeated = default_orchestration_coordination_visibility()
    reordered = _reordered_coordination_visibility()
    exported = export_orchestration_coordination_visibility(visibility)

    identity = validate_coordination_identity(visibility)
    support = validate_coordination_support_visibility(visibility)
    participants = validate_coordination_participants(visibility)
    metadata = validate_coordination_metadata(visibility)
    relationships = validate_coordination_relationships(visibility)
    continuity = validate_coordination_continuity(visibility)
    explainability = validate_coordination_explainability(visibility)
    non_execution = validate_coordination_non_execution_and_non_coordination(visibility)
    diagnostics = build_coordination_visibility_diagnostics(visibility)

    serialization_first = serialize_orchestration_coordination_visibility(visibility)
    serialization_second = serialize_orchestration_coordination_visibility(repeated)
    serialization_reordered = serialize_orchestration_coordination_visibility(reordered)
    visibility_hash = hash_orchestration_coordination_visibility(visibility)
    repeated_hash = hash_orchestration_coordination_visibility(repeated)
    reordered_hash = hash_orchestration_coordination_visibility(reordered)
    coordination_hashes = [
        hash_coordination_record(coordination) for coordination in visibility.coordinations
    ]
    participant_hashes = [
        hash_coordination_participant(participant) for participant in visibility.participants
    ]
    relationship_hashes = [
        hash_coordination_relationship(relationship) for relationship in visibility.relationships
    ]
    diagnostic_hashes = [
        hash_coordination_diagnostic(diagnostic) for diagnostic in visibility.diagnostics
    ]
    explainability_hashes = [
        hash_coordination_explainability(summary) for summary in visibility.explainability_summaries
    ]

    exported_coordination_order = [item["coordination_id"] for item in exported["coordinations"]]
    expected_coordination_order = [
        item["coordination_id"]
        for item in sorted(
            exported["coordinations"],
            key=lambda item: (item["deterministic_order"], item["coordination_id"]),
        )
    ]
    exported_participant_order = [item["participant_id"] for item in exported["participants"]]
    expected_participant_order = [
        item["participant_id"]
        for item in sorted(
            exported["participants"],
            key=lambda item: (item["deterministic_order"], item["participant_id"]),
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
            0 if participants["valid"] else 1,
            0 if metadata["valid"] else 1,
            0 if relationships["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if visibility_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_visibilities_equal(visibility, repeated) else 1,
            0 if exported_coordination_order == expected_coordination_order else 1,
            0 if exported_participant_order == expected_participant_order else 1,
            0 if exported_relationship_order == expected_relationship_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_COORDINATION_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_COORDINATION_STATUS_BLOCKED
    )

    report = {
        "schema_version": V4_3_ORCHESTRATION_COORDINATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_COORDINATION_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_COORDINATION_PHASE_ID,
        "phase_name": "v4.3_phase_6_orchestration_coordination_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration coordination visibility without operational coordination",
        "coordination_mode": "descriptive_only_non_executing_non_coordinating_governance",
        "coordination_visibility_status": status,
        "coordination_counts": {
            "coordination_count": len(visibility.coordinations),
            "coordination_relationship_count": len(visibility.relationships),
            "participant_count": len(visibility.participants),
            "prohibited_coordination_count": len(diagnostics["prohibited_coordination_ids"]),
            "unsupported_coordination_count": len(diagnostics["unsupported_coordination_ids"]),
            "blocked_coordination_count": len(diagnostics["blocked_coordination_ids"]),
            "stale_coordination_count": len(diagnostics["stale_coordination_ids"]),
            "conflicting_coordination_count": len(diagnostics["conflicting_coordination_ids"]),
            "invalid_participant_count": diagnostics["invalid_participant_count"],
            "invalid_relationship_count": diagnostics["invalid_relationship_count"],
            "diagnostic_count": len(visibility.diagnostics),
            "explainability_summary_count": len(visibility.explainability_summaries),
            "coordination_state_counts": count_coordination_states(visibility.coordinations),
        },
        "identity_visibility": {
            "identity_key": coordination_visibility_identity_key(visibility),
            "identity_validation": identity,
            "identity_hash": hash_coordination_visibility_identity(visibility.identity),
        },
        "support_state_visibility": {
            "support_visibility_validation": support,
            "prohibited_coordination_ids": diagnostics["prohibited_coordination_ids"],
            "unsupported_coordination_ids": diagnostics["unsupported_coordination_ids"],
            "blocked_coordination_ids": diagnostics["blocked_coordination_ids"],
            "stale_coordination_ids": diagnostics["stale_coordination_ids"],
            "conflicting_coordination_ids": diagnostics["conflicting_coordination_ids"],
            "unknown_coordination_ids": diagnostics["unknown_coordination_ids"],
            "prohibited_coordinations_visible": support["prohibited_coordinations_visible"],
            "unsupported_coordinations_visible": support["unsupported_coordinations_visible"],
            "blocked_coordinations_visible": support["blocked_coordinations_visible"],
            "stale_coordinations_visible": support["stale_coordinations_visible"],
            "conflicting_coordinations_visible": support["conflicting_coordinations_visible"],
        },
        "participant_visibility": {
            "participant_validation": participants,
            "participant_hashes": participant_hashes,
            "invalid_participant_count": participants["invalid_participant_count"],
            "duplicate_participant_ids": participants["duplicate_participant_ids"],
            "missing_participant_ids": participants["missing_participant_ids"],
            "missing_participant_references": participants["missing_participant_references"],
            "unknown_coordination_refs": participants["unknown_coordination_refs"],
            "operational_participant_ids": participants["operational_participant_ids"],
        },
        "metadata_visibility": {
            "metadata_validation": metadata,
            "governance_metadata_present": metadata["governance_metadata_present"],
            "coordination_boundary_metadata_present": metadata[
                "coordination_boundary_metadata_present"
            ],
            "coordination_policy_metadata_present": metadata["coordination_policy_metadata_present"],
            "coordination_transition_metadata_present": metadata[
                "coordination_transition_metadata_present"
            ],
            "continuity_metadata_present": metadata["continuity_metadata_present"],
            "provenance_metadata_present": metadata["provenance_metadata_present"],
            "lineage_metadata_present": metadata["lineage_metadata_present"],
            "diagnostics_metadata_present": metadata["diagnostics_metadata_present"],
            "explainability_metadata_present": metadata["explainability_metadata_present"],
            "non_execution_metadata_present": metadata["non_execution_metadata_present"],
            "non_coordination_metadata_present": metadata["non_coordination_metadata_present"],
        },
        "relationship_visibility": {
            "relationship_validation": relationships,
            "relationship_hashes": relationship_hashes,
            "invalid_relationship_count": relationships["invalid_relationship_count"],
            "invalid_policy_relationship_ids": relationships["invalid_policy_relationship_ids"],
            "invalid_capability_relationship_ids": relationships[
                "invalid_capability_relationship_ids"
            ],
            "invalid_transition_relationship_ids": relationships[
                "invalid_transition_relationship_ids"
            ],
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
            "coordination_continuity_visible": continuity["coordination_continuity_visible"],
        },
        "diagnostic_aggregation": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "execution_absent": diagnostics["execution_absent"],
            "dispatch_absent": diagnostics["dispatch_absent"],
            "repair_absent": diagnostics["repair_absent"],
            "inference_absent": diagnostics["inference_absent"],
            "authorization_absent": diagnostics["authorization_absent"],
            "mutation_absent": diagnostics["mutation_absent"],
        },
        "explainability_findings": {
            "explainability_validation": explainability,
            "explainability_hashes": explainability_hashes,
            "prohibited_coordination_visible": (
                "prohibited_coordination" in explainability["explainability_categories"]
            ),
            "unsupported_coordination_visible": (
                "unsupported_coordination" in explainability["explainability_categories"]
            ),
            "blocked_coordination_visible": (
                "blocked_coordination" in explainability["explainability_categories"]
            ),
            "stale_coordination_visible": (
                "stale_coordination" in explainability["explainability_categories"]
            ),
            "conflicting_coordination_visible": (
                "conflicting_coordination" in explainability["explainability_categories"]
            ),
            "operational_coordination_unavailable_visible": (
                "operational_coordination_unavailable"
                in explainability["explainability_categories"]
            ),
            "orchestration_dispatch_unavailable_visible": (
                "orchestration_dispatch_unavailable"
                in explainability["explainability_categories"]
            ),
            "orchestration_activation_unavailable_visible": (
                "orchestration_activation_unavailable"
                in explainability["explainability_categories"]
            ),
            "planner_integration_unavailable_visible": (
                "planner_integration_unavailable" in explainability["explainability_categories"]
            ),
            "production_consumption_unavailable_visible": (
                "production_consumption_unavailable"
                in explainability["explainability_categories"]
            ),
            "governance_constraints_visible": (
                "governance_constraints_exist" in explainability["explainability_categories"]
            ),
            "runtime_coordination_prohibited_visible": (
                "runtime_coordination_prohibited" in explainability["explainability_categories"]
            ),
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_coordination_visibility",
            "payload_length": len(serialization_first),
            "coordination_ordering_stable": exported_coordination_order == expected_coordination_order,
            "participant_ordering_stable": exported_participant_order == expected_participant_order,
            "relationship_ordering_stable": exported_relationship_order == expected_relationship_order,
            "diagnostics_ordering_stable": [
                item["diagnostic_id"] for item in exported["diagnostics"]
            ]
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
            "prohibited_states_preserved": len(diagnostics["prohibited_coordination_ids"]) > 0,
            "unsupported_states_preserved": len(diagnostics["unsupported_coordination_ids"]) > 0,
            "blocked_states_preserved": len(diagnostics["blocked_coordination_ids"]) > 0,
            "stale_states_preserved": len(diagnostics["stale_coordination_ids"]) > 0,
            "conflicting_states_preserved": len(diagnostics["conflicting_coordination_ids"]) > 0,
        },
        "hashing_stability_evidence": {
            "stable": visibility_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_coordination_visibility",
            "coordination_visibility_hash": visibility_hash,
            "repeated_coordination_visibility_hash": repeated_hash,
            "reordered_coordination_visibility_hash": reordered_hash,
            "identity_hash": hash_coordination_visibility_identity(visibility.identity),
            "coordination_hashes": coordination_hashes,
            "participant_hashes": participant_hashes,
            "relationship_hashes": relationship_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "non_execution_guarantees": non_execution,
        "non_coordination_guarantees": {
            "valid": non_execution["valid"],
            "coordination_execution_disabled": non_execution["coordination_execution_disabled"],
            "operational_coordination_disabled": non_execution[
                "operational_coordination_disabled"
            ],
            "runtime_coordination_disabled": non_execution["runtime_coordination_disabled"],
            "orchestration_dispatch_disabled": non_execution["orchestration_dispatch_disabled"],
            "orchestration_coordination_engine_absent": non_execution[
                "orchestration_coordination_engine_absent"
            ],
            "dispatcher_absent": non_execution["dispatcher_absent"],
            "runtime_coordinator_absent": non_execution["runtime_coordinator_absent"],
            "operational_state_machine_absent": non_execution[
                "operational_state_machine_absent"
            ],
            "enabled_coordination_execution_count": non_execution[
                "enabled_coordination_execution_count"
            ],
        },
        "summary": {
            "coordination_visibility_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first
            == serialization_second
            == serialization_reordered,
            "deterministic_hashing_verified": visibility_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_visibilities_equal(visibility, repeated),
            "coordination_ordering_verified": exported_coordination_order == expected_coordination_order,
            "participant_ordering_verified": exported_participant_order == expected_participant_order,
            "relationship_ordering_verified": exported_relationship_order == expected_relationship_order,
            "identity_visibility_verified": identity["valid"],
            "support_state_visibility_verified": support["valid"],
            "participant_visibility_verified": participants["valid"],
            "metadata_visibility_verified": metadata["valid"],
            "relationship_visibility_verified": relationships["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "non_coordination_guarantees_validated": non_execution["valid"],
            "enabled_coordination_execution_count": non_execution[
                "enabled_coordination_execution_count"
            ],
            "enabled_transition_execution_count": non_execution[
                "enabled_transition_execution_count"
            ],
            "enabled_policy_enforcement_count": non_execution[
                "enabled_policy_enforcement_count"
            ],
            "enabled_operational_capability_count": non_execution[
                "enabled_operational_capability_count"
            ],
            "coordination_execution_disabled": non_execution["coordination_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "operational_coordination_disabled": non_execution[
                "operational_coordination_disabled"
            ],
            "runtime_coordination_disabled": non_execution["runtime_coordination_disabled"],
            "orchestration_dispatch_disabled": non_execution["orchestration_dispatch_disabled"],
            "orchestration_activation_disabled": non_execution[
                "orchestration_activation_disabled"
            ],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "traversal_execution_disabled": non_execution["traversal_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "state_machine_execution_disabled": non_execution["state_machine_execution_disabled"],
            "transition_execution_disabled": non_execution["transition_execution_disabled"],
            "coordination_authorization_disabled": non_execution[
                "coordination_authorization_disabled"
            ],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
            "operational_mutation_disabled": non_execution["operational_mutation_disabled"],
            "planning_engine_absent": non_execution["planning_engine_absent"],
            "decision_engine_absent": non_execution["decision_engine_absent"],
            "hidden_coordination_pathway_absent": non_execution[
                "hidden_coordination_pathway_absent"
            ],
            "implicit_operational_authorization_absent": non_execution[
                "implicit_operational_authorization_absent"
            ],
            "orchestration_coordination_engine_absent": non_execution[
                "orchestration_coordination_engine_absent"
            ],
            "dispatcher_absent": non_execution["dispatcher_absent"],
            "runtime_coordinator_absent": non_execution["runtime_coordinator_absent"],
            "operational_state_machine_absent": non_execution[
                "operational_state_machine_absent"
            ],
            "policy_enforcement_disabled": non_execution["policy_enforcement_disabled"],
        },
        "coordination_visibility": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_COORDINATION_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_COORDINATION_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination visibility JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_coordination_visibility_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"coordination_visibility_status={report['coordination_visibility_status']}")
    print(f"enabled_coordination_execution_count={report['summary']['enabled_coordination_execution_count']}")
    print(f"enabled_transition_execution_count={report['summary']['enabled_transition_execution_count']}")
    print(f"enabled_policy_enforcement_count={report['summary']['enabled_policy_enforcement_count']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
