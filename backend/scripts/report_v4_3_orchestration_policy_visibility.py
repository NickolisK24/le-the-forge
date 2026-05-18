"""Generate deterministic v4.3 orchestration policy visibility evidence."""

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

from orchestration_governance.orchestration_policy_diagnostics import (  # noqa: E402
    build_policy_visibility_diagnostics,
    count_policy_states,
    policy_visibilities_equal,
    policy_visibility_identity_key,
    validate_policy_continuity,
    validate_policy_explainability,
    validate_policy_identity,
    validate_policy_metadata,
    validate_policy_non_execution_and_non_enforcement,
    validate_policy_relationships,
    validate_policy_support_visibility,
    validate_policy_targets,
)
from orchestration_governance.orchestration_policy_hashing import (  # noqa: E402
    deterministic_policy_hash,
    hash_orchestration_policy_visibility,
    hash_policy_diagnostic,
    hash_policy_explainability,
    hash_policy_record,
    hash_policy_relationship,
    hash_policy_target,
    hash_policy_visibility_identity,
)
from orchestration_governance.orchestration_policy_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_POLICY_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_POLICY_PROHIBITIONS,
    V4_3_ORCHESTRATION_POLICY_GENERATED_AT,
    V4_3_ORCHESTRATION_POLICY_PHASE_ID,
    V4_3_ORCHESTRATION_POLICY_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_POLICY_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_POLICY_STATUS_STABLE,
    default_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_policy_serialization import (  # noqa: E402
    export_orchestration_policy_visibility,
    serialize_orchestration_policy_visibility,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_policy_visibility_report.json")


def _reordered_policy_visibility():
    visibility = default_orchestration_policy_visibility()
    return replace(
        visibility,
        policies=tuple(reversed(visibility.policies)),
        targets=tuple(reversed(visibility.targets)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_policy_hash(payload)


def build_v4_3_orchestration_policy_visibility_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_orchestration_policy_visibility()
    repeated = default_orchestration_policy_visibility()
    reordered = _reordered_policy_visibility()
    exported = export_orchestration_policy_visibility(visibility)
    identity = validate_policy_identity(visibility)
    support = validate_policy_support_visibility(visibility)
    targets = validate_policy_targets(visibility)
    metadata = validate_policy_metadata(visibility)
    relationships = validate_policy_relationships(visibility)
    continuity = validate_policy_continuity(visibility)
    explainability = validate_policy_explainability(visibility)
    non_execution = validate_policy_non_execution_and_non_enforcement(visibility)
    diagnostics = build_policy_visibility_diagnostics(visibility)
    serialization_first = serialize_orchestration_policy_visibility(visibility)
    serialization_second = serialize_orchestration_policy_visibility(repeated)
    serialization_reordered = serialize_orchestration_policy_visibility(reordered)
    visibility_hash = hash_orchestration_policy_visibility(visibility)
    repeated_hash = hash_orchestration_policy_visibility(repeated)
    reordered_hash = hash_orchestration_policy_visibility(reordered)
    policy_hashes = [hash_policy_record(policy) for policy in visibility.policies]
    target_hashes = [hash_policy_target(target) for target in visibility.targets]
    relationship_hashes = [
        hash_policy_relationship(relationship) for relationship in visibility.relationships
    ]
    diagnostic_hashes = [hash_policy_diagnostic(diagnostic) for diagnostic in visibility.diagnostics]
    explainability_hashes = [
        hash_policy_explainability(summary) for summary in visibility.explainability_summaries
    ]
    exported_policy_order = [item["policy_id"] for item in exported["policies"]]
    expected_policy_order = [
        item["policy_id"]
        for item in sorted(
            exported["policies"],
            key=lambda item: (item["deterministic_order"], item["policy_id"]),
        )
    ]
    exported_target_order = [item["target_id"] for item in exported["targets"]]
    expected_target_order = [
        item["target_id"]
        for item in sorted(
            exported["targets"],
            key=lambda item: (item["deterministic_order"], item["target_id"]),
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
            0 if targets["valid"] else 1,
            0 if metadata["valid"] else 1,
            0 if relationships["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if visibility_hash == repeated_hash == reordered_hash else 1,
            0 if policy_visibilities_equal(visibility, repeated) else 1,
            0 if exported_policy_order == expected_policy_order else 1,
            0 if exported_target_order == expected_target_order else 1,
            0 if exported_relationship_order == expected_relationship_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_POLICY_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_POLICY_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_3_ORCHESTRATION_POLICY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_POLICY_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_POLICY_PHASE_ID,
        "phase_name": "v4.3_phase_4_orchestration_policy_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration policy visibility without enforcement",
        "policy_mode": "descriptive_only_non_enforcing_non_executable_policy_governance",
        "policy_visibility_status": status,
        "policy_counts": {
            "policy_count": len(visibility.policies),
            "policy_target_count": len(visibility.targets),
            "policy_relationship_count": len(visibility.relationships),
            "prohibited_policy_count": len(diagnostics["prohibited_policy_ids"]),
            "unsupported_policy_count": len(diagnostics["unsupported_policy_ids"]),
            "blocked_policy_count": len(diagnostics["blocked_policy_ids"]),
            "stale_policy_count": len(diagnostics["stale_policy_ids"]),
            "conflicting_policy_count": len(diagnostics["conflicting_policy_ids"]),
            "invalid_target_count": diagnostics["invalid_target_count"],
            "invalid_relationship_count": diagnostics["invalid_relationship_count"],
            "diagnostic_count": len(visibility.diagnostics),
            "explainability_summary_count": len(visibility.explainability_summaries),
            "policy_state_counts": count_policy_states(visibility.policies),
        },
        "identity_visibility": {
            "identity_key": policy_visibility_identity_key(visibility),
            "identity_validation": identity,
            "identity_hash": hash_policy_visibility_identity(visibility.identity),
        },
        "support_state_visibility": {
            "support_visibility_validation": support,
            "prohibited_policy_ids": diagnostics["prohibited_policy_ids"],
            "unsupported_policy_ids": diagnostics["unsupported_policy_ids"],
            "blocked_policy_ids": diagnostics["blocked_policy_ids"],
            "stale_policy_ids": diagnostics["stale_policy_ids"],
            "conflicting_policy_ids": diagnostics["conflicting_policy_ids"],
            "unknown_policy_ids": diagnostics["unknown_policy_ids"],
            "prohibited_policies_visible": support["prohibited_policies_visible"],
            "unsupported_policies_visible": support["unsupported_policies_visible"],
            "blocked_policies_visible": support["blocked_policies_visible"],
            "stale_policies_visible": support["stale_policies_visible"],
            "conflicting_policies_visible": support["conflicting_policies_visible"],
        },
        "target_visibility": {
            "target_validation": targets,
            "target_hashes": target_hashes,
            "policy_target_count": len(visibility.targets),
            "missing_policy_target_ids": targets["missing_policy_target_ids"],
            "invalid_target_count": targets["invalid_target_count"],
        },
        "metadata_visibility": {
            "metadata_validation": metadata,
            "governance_metadata_present": metadata["governance_metadata_present"],
            "policy_scope_metadata_present": metadata["policy_scope_metadata_present"],
            "policy_target_metadata_present": metadata["policy_target_metadata_present"],
            "continuity_metadata_present": metadata["continuity_metadata_present"],
            "provenance_metadata_present": metadata["provenance_metadata_present"],
            "lineage_metadata_present": metadata["lineage_metadata_present"],
            "diagnostics_metadata_present": metadata["diagnostics_metadata_present"],
            "explainability_metadata_present": metadata["explainability_metadata_present"],
            "non_enforcement_metadata_present": metadata["non_enforcement_metadata_present"],
            "non_execution_metadata_present": metadata["non_execution_metadata_present"],
        },
        "relationship_visibility": {
            "relationship_validation": relationships,
            "relationship_hashes": relationship_hashes,
            "invalid_relationship_count": relationships["invalid_relationship_count"],
            "invalid_manifest_relationship_ids": relationships["invalid_manifest_relationship_ids"],
            "invalid_topology_relationship_ids": relationships["invalid_topology_relationship_ids"],
            "invalid_capability_relationship_ids": relationships["invalid_capability_relationship_ids"],
            "invalid_boundary_relationship_ids": relationships["invalid_boundary_relationship_ids"],
            "operational_relationship_ids": relationships["operational_relationship_ids"],
        },
        "continuity_visibility": {
            "continuity_validation": continuity,
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "provenance_continuity_preserved": continuity["provenance_continuity_preserved"],
            "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
            "policy_continuity_visible": continuity["policy_continuity_visible"],
        },
        "diagnostic_aggregation": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "repair_absent": diagnostics["repair_absent"],
            "inference_absent": diagnostics["inference_absent"],
            "authorization_absent": diagnostics["authorization_absent"],
            "operational_mutation_absent": diagnostics["operational_mutation_absent"],
            "policy_enforcement_absent": diagnostics["policy_enforcement_absent"],
            "execution_absent": diagnostics["execution_absent"],
        },
        "explainability_findings": {
            "explainability_validation": explainability,
            "explainability_hashes": explainability_hashes,
            "prohibited_policy_visible": "prohibited_policy" in explainability["explainability_categories"],
            "unsupported_policy_visible": "unsupported_policy" in explainability["explainability_categories"],
            "blocked_policy_visible": "blocked_policy" in explainability["explainability_categories"],
            "stale_policy_visible": "stale_policy" in explainability["explainability_categories"],
            "conflicting_policy_visible": "conflicting_policy" in explainability["explainability_categories"],
            "policy_enforcement_unavailable_visible": (
                "policy_enforcement_unavailable" in explainability["explainability_categories"]
            ),
            "authorization_unavailable_visible": (
                "authorization_unavailable" in explainability["explainability_categories"]
            ),
            "activation_unavailable_visible": "activation_unavailable" in explainability["explainability_categories"],
            "execution_unavailable_visible": "execution_unavailable" in explainability["explainability_categories"],
            "planner_integration_unavailable_visible": (
                "planner_integration_unavailable" in explainability["explainability_categories"]
            ),
            "production_consumption_unavailable_visible": (
                "production_consumption_unavailable" in explainability["explainability_categories"]
            ),
            "governance_constraints_visible": (
                "governance_constraints_exist" in explainability["explainability_categories"]
            ),
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_policy_visibility",
            "payload_length": len(serialization_first),
            "policy_ordering_stable": exported_policy_order == expected_policy_order,
            "target_ordering_stable": exported_target_order == expected_target_order,
            "relationship_ordering_stable": exported_relationship_order == expected_relationship_order,
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
            "prohibited_states_preserved": len(diagnostics["prohibited_policy_ids"]) > 0,
            "unsupported_states_preserved": len(diagnostics["unsupported_policy_ids"]) > 0,
            "blocked_states_preserved": len(diagnostics["blocked_policy_ids"]) > 0,
            "stale_states_preserved": len(diagnostics["stale_policy_ids"]) > 0,
            "conflicting_states_preserved": len(diagnostics["conflicting_policy_ids"]) > 0,
        },
        "hashing_stability_evidence": {
            "stable": visibility_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_policy_visibility",
            "policy_visibility_hash": visibility_hash,
            "repeated_policy_visibility_hash": repeated_hash,
            "reordered_policy_visibility_hash": reordered_hash,
            "identity_hash": hash_policy_visibility_identity(visibility.identity),
            "policy_hashes": policy_hashes,
            "target_hashes": target_hashes,
            "relationship_hashes": relationship_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "non_execution_guarantees": non_execution,
        "non_enforcement_guarantees": {
            "valid": non_execution["valid"],
            "policy_enforcement_disabled": non_execution["policy_enforcement_disabled"],
            "policy_enforcement_execution_disabled": (
                non_execution["policy_enforcement_execution_disabled"]
            ),
            "authorization_disabled": non_execution["orchestration_authorization_disabled"],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "policy_engine_execution_absent": non_execution["policy_engine_execution_absent"],
            "authorization_engine_absent": non_execution["authorization_engine_absent"],
            "enabled_policy_enforcement_count": non_execution["enabled_policy_enforcement_count"],
        },
        "summary": {
            "policy_visibility_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": visibility_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": policy_visibilities_equal(visibility, repeated),
            "policy_ordering_verified": exported_policy_order == expected_policy_order,
            "target_ordering_verified": exported_target_order == expected_target_order,
            "relationship_ordering_verified": exported_relationship_order == expected_relationship_order,
            "identity_visibility_verified": identity["valid"],
            "support_state_visibility_verified": support["valid"],
            "target_visibility_verified": targets["valid"],
            "metadata_visibility_verified": metadata["valid"],
            "relationship_visibility_verified": relationships["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "non_enforcement_guarantees_validated": non_execution["valid"],
            "enabled_policy_enforcement_count": non_execution["enabled_policy_enforcement_count"],
            "enabled_operational_capability_count": non_execution["enabled_operational_capability_count"],
            "policy_enforcement_disabled": non_execution["policy_enforcement_disabled"],
            "policy_enforcement_execution_disabled": (
                non_execution["policy_enforcement_execution_disabled"]
            ),
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "runtime_execution_disabled": non_execution["runtime_execution_disabled"],
            "policy_driven_routing_disabled": non_execution["policy_driven_routing_disabled"],
            "policy_driven_traversal_disabled": non_execution["policy_driven_traversal_disabled"],
            "policy_driven_scheduling_disabled": non_execution["policy_driven_scheduling_disabled"],
            "policy_driven_sequencing_disabled": non_execution["policy_driven_sequencing_disabled"],
            "policy_driven_dependency_resolution_disabled": (
                non_execution["policy_driven_dependency_resolution_disabled"]
            ),
            "policy_driven_activation_disabled": non_execution["policy_driven_activation_disabled"],
            "orchestration_authorization_disabled": non_execution["orchestration_authorization_disabled"],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "policy_engine_execution_absent": non_execution["policy_engine_execution_absent"],
            "orchestration_engine_absent": non_execution["orchestration_engine_absent"],
            "authorization_engine_absent": non_execution["authorization_engine_absent"],
            "activation_pathway_absent": non_execution["activation_pathway_absent"],
        },
        "policy_visibility": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_POLICY_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_POLICY_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Policy visibility JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_policy_visibility_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"policy_visibility_status={report['policy_visibility_status']}")
    print(f"enabled_policy_enforcement_count={report['summary']['enabled_policy_enforcement_count']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
