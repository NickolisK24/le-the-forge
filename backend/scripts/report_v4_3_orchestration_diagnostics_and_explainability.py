"""Generate deterministic v4.3 orchestration diagnostics and explainability evidence."""

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

from orchestration_governance.orchestration_diagnostics_aggregation import (  # noqa: E402
    build_orchestration_diagnostics_aggregation_diagnostics,
    diagnostics_aggregation_identity_key,
    diagnostics_aggregations_equal,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_orchestration_decision_count,
    enabled_orchestration_recommendation_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    validate_diagnostics_aggregation_explainability,
    validate_diagnostics_aggregation_identity,
    validate_diagnostics_aggregation_layers,
    validate_diagnostics_aggregation_non_execution_and_non_decision,
    validate_diagnostics_aggregation_state_visibility,
)
from orchestration_governance.orchestration_diagnostics_hashing import (  # noqa: E402
    deterministic_diagnostics_hash,
    hash_aggregated_diagnostic_finding,
    hash_aggregated_explainability_summary,
    hash_cross_layer_state_summary,
    hash_diagnostics_aggregation_identity,
    hash_governance_layer_diagnostic_summary,
    hash_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_diagnostics_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_DIAGNOSTICS_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS,
    V4_3_ORCHESTRATION_DIAGNOSTICS_GENERATED_AT,
    V4_3_ORCHESTRATION_DIAGNOSTICS_PHASE_ID,
    V4_3_ORCHESTRATION_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_STABLE,
)
from orchestration_governance.orchestration_diagnostics_aggregation import (  # noqa: E402
    default_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_diagnostics_serialization import (  # noqa: E402
    export_orchestration_diagnostics_aggregation,
    serialize_orchestration_diagnostics_aggregation,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_diagnostics_and_explainability_report.json")


def _reordered_diagnostics_aggregation():
    aggregation = default_orchestration_diagnostics_aggregation()
    return replace(
        aggregation,
        governance_layer_summaries=tuple(reversed(aggregation.governance_layer_summaries)),
        diagnostics=tuple(reversed(aggregation.diagnostics)),
        explainability_summaries=tuple(reversed(aggregation.explainability_summaries)),
        cross_layer_state_summaries=tuple(reversed(aggregation.cross_layer_state_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_diagnostics_hash(payload)


def build_v4_3_orchestration_diagnostics_and_explainability_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    aggregation = default_orchestration_diagnostics_aggregation()
    repeated = default_orchestration_diagnostics_aggregation()
    reordered = _reordered_diagnostics_aggregation()
    exported = export_orchestration_diagnostics_aggregation(aggregation)

    identity = validate_diagnostics_aggregation_identity(aggregation)
    layers = validate_diagnostics_aggregation_layers(aggregation)
    state_visibility = validate_diagnostics_aggregation_state_visibility(aggregation)
    explainability = validate_diagnostics_aggregation_explainability(aggregation)
    non_execution = validate_diagnostics_aggregation_non_execution_and_non_decision(aggregation)
    diagnostics = build_orchestration_diagnostics_aggregation_diagnostics(aggregation)

    serialization_first = serialize_orchestration_diagnostics_aggregation(aggregation)
    serialization_second = serialize_orchestration_diagnostics_aggregation(repeated)
    serialization_reordered = serialize_orchestration_diagnostics_aggregation(reordered)
    aggregation_hash = hash_orchestration_diagnostics_aggregation(aggregation)
    repeated_hash = hash_orchestration_diagnostics_aggregation(repeated)
    reordered_hash = hash_orchestration_diagnostics_aggregation(reordered)
    layer_hashes = [
        hash_governance_layer_diagnostic_summary(summary)
        for summary in aggregation.governance_layer_summaries
    ]
    diagnostic_hashes = [
        hash_aggregated_diagnostic_finding(diagnostic) for diagnostic in aggregation.diagnostics
    ]
    explainability_hashes = [
        hash_aggregated_explainability_summary(summary)
        for summary in aggregation.explainability_summaries
    ]
    state_summary_hashes = [
        hash_cross_layer_state_summary(summary)
        for summary in aggregation.cross_layer_state_summaries
    ]

    exported_layer_order = [item["layer_id"] for item in exported["governance_layer_summaries"]]
    expected_layer_order = [
        item["layer_id"]
        for item in sorted(
            exported["governance_layer_summaries"],
            key=lambda item: (item["deterministic_order"], item["layer_id"]),
        )
    ]
    exported_diagnostic_order = [item["aggregated_diagnostic_id"] for item in exported["diagnostics"]]
    expected_diagnostic_order = [
        item["aggregated_diagnostic_id"]
        for item in sorted(
            exported["diagnostics"],
            key=lambda item: (item["deterministic_order"], item["aggregated_diagnostic_id"]),
        )
    ]
    exported_explainability_order = [
        item["aggregated_explanation_id"] for item in exported["explainability_summaries"]
    ]
    expected_explainability_order = [
        item["aggregated_explanation_id"]
        for item in sorted(
            exported["explainability_summaries"],
            key=lambda item: (item["deterministic_order"], item["aggregated_explanation_id"]),
        )
    ]
    exported_state_order = [
        item["state_summary_id"] for item in exported["cross_layer_state_summaries"]
    ]
    expected_state_order = [
        item["state_summary_id"]
        for item in sorted(
            exported["cross_layer_state_summaries"],
            key=lambda item: (item["deterministic_order"], item["state_summary_id"]),
        )
    ]

    validation_error_count = sum(
        [
            0 if identity["valid"] else 1,
            0 if layers["valid"] else 1,
            0 if state_visibility["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if aggregation_hash == repeated_hash == reordered_hash else 1,
            0 if diagnostics_aggregations_equal(aggregation, repeated) else 1,
            0 if exported_layer_order == expected_layer_order else 1,
            0 if exported_diagnostic_order == expected_diagnostic_order else 1,
            0 if exported_explainability_order == expected_explainability_order else 1,
            0 if exported_state_order == expected_state_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_BLOCKED
    )

    report = {
        "schema_version": V4_3_ORCHESTRATION_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_DIAGNOSTICS_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_DIAGNOSTICS_PHASE_ID,
        "phase_name": "v4.3_phase_7_orchestration_diagnostics_and_explainability",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration diagnostics and explainability aggregation without operational orchestration intelligence",
        "aggregation_mode": "descriptive_only_non_executing_non_decisioning_governance",
        "diagnostics_aggregation_status": status,
        "aggregation_counts": {
            "aggregated_diagnostics_count": len(aggregation.diagnostics),
            "aggregated_explainability_count": len(aggregation.explainability_summaries),
            "cross_layer_blocked_state_count": state_visibility["blocked_state_count"],
            "cross_layer_prohibited_state_count": state_visibility["prohibited_state_count"],
            "cross_layer_unsupported_state_count": state_visibility["unsupported_state_count"],
            "cross_layer_stale_state_count": state_visibility["stale_state_count"],
            "cross_layer_conflicting_state_count": state_visibility["conflicting_state_count"],
            "governance_layer_summary_count": len(aggregation.governance_layer_summaries),
        },
        "identity_visibility": {
            "identity_key": diagnostics_aggregation_identity_key(aggregation),
            "identity_validation": identity,
            "identity_hash": hash_diagnostics_aggregation_identity(aggregation.identity),
        },
        "governance_layer_visibility": {
            "governance_layer_validation": layers,
            "governance_layer_hashes": layer_hashes,
            "layer_ordering_stable": exported_layer_order == expected_layer_order,
            "continuity_diagnostics_visible": layers["continuity_diagnostics_visible"],
            "provenance_diagnostics_visible": layers["provenance_diagnostics_visible"],
            "lineage_diagnostics_visible": layers["lineage_diagnostics_visible"],
        },
        "cross_layer_state_visibility": {
            "state_visibility_validation": state_visibility,
            "state_summary_hashes": state_summary_hashes,
            "prohibited_state_visibility": state_visibility["prohibited_states_visible"],
            "unsupported_state_visibility": state_visibility["unsupported_states_visible"],
            "blocked_state_visibility": state_visibility["blocked_states_visible"],
            "stale_state_visibility": state_visibility["stale_states_visible"],
            "conflicting_state_visibility": state_visibility["conflicting_states_visible"],
        },
        "diagnostics_findings": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "aggregated_diagnostics_count": diagnostics["aggregated_diagnostics_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
        },
        "explainability_findings": {
            "explainability_validation": explainability,
            "explainability_categories": diagnostics["explainability_categories"],
            "explainability_hashes": explainability_hashes,
            "aggregated_explainability_count": diagnostics["aggregated_explainability_count"],
            "explainability_is_descriptive_only": diagnostics["explainability_is_descriptive_only"],
            "orchestration_non_executable_visible": (
                "orchestration_non_executable" in explainability["explainability_categories"]
            ),
            "orchestration_activation_unavailable_visible": (
                "orchestration_activation_unavailable" in explainability["explainability_categories"]
            ),
            "orchestration_coordination_unavailable_visible": (
                "orchestration_coordination_unavailable" in explainability["explainability_categories"]
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
            "fail_visible_governance_evidence_visible": (
                "fail_visible_governance_evidence_exists"
                in explainability["explainability_categories"]
            ),
            "orchestration_decision_making_prohibited_visible": (
                "orchestration_decision_making_prohibited"
                in explainability["explainability_categories"]
            ),
            "orchestration_recommendations_prohibited_visible": (
                "orchestration_recommendations_prohibited"
                in explainability["explainability_categories"]
            ),
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_diagnostics_aggregation",
            "payload_length": len(serialization_first),
            "governance_layer_ordering_stable": exported_layer_order == expected_layer_order,
            "diagnostics_ordering_stable": exported_diagnostic_order == expected_diagnostic_order,
            "explainability_ordering_stable": exported_explainability_order == expected_explainability_order,
            "state_summary_ordering_stable": exported_state_order == expected_state_order,
            "prohibited_states_preserved": state_visibility["prohibited_states_visible"],
            "unsupported_states_preserved": state_visibility["unsupported_states_visible"],
            "blocked_states_preserved": state_visibility["blocked_states_visible"],
            "stale_states_preserved": state_visibility["stale_states_visible"],
            "conflicting_states_preserved": state_visibility["conflicting_states_visible"],
        },
        "hashing_stability_evidence": {
            "stable": aggregation_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_diagnostics_aggregation",
            "diagnostics_aggregation_hash": aggregation_hash,
            "repeated_diagnostics_aggregation_hash": repeated_hash,
            "reordered_diagnostics_aggregation_hash": reordered_hash,
            "identity_hash": hash_diagnostics_aggregation_identity(aggregation.identity),
            "governance_layer_hashes": layer_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
            "state_summary_hashes": state_summary_hashes,
        },
        "replay_safe_status": True,
        "rollback_safe_status": True,
        "non_execution_guarantees": non_execution,
        "non_decision_guarantees": {
            "valid": non_execution["valid"],
            "orchestration_decision_disabled": non_execution["orchestration_decision_disabled"],
            "orchestration_recommendation_disabled": non_execution[
                "orchestration_recommendation_disabled"
            ],
            "ranking_disabled": non_execution["ranking_disabled"],
            "scoring_disabled": non_execution["scoring_disabled"],
            "selection_disabled": non_execution["selection_disabled"],
            "optimization_disabled": non_execution["optimization_disabled"],
            "planning_engine_absent": non_execution["planning_engine_absent"],
            "decision_engine_absent": non_execution["decision_engine_absent"],
            "enabled_orchestration_decision_count": non_execution[
                "enabled_orchestration_decision_count"
            ],
            "enabled_orchestration_recommendation_count": non_execution[
                "enabled_orchestration_recommendation_count"
            ],
        },
        "summary": {
            "diagnostics_aggregation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first
            == serialization_second
            == serialization_reordered,
            "deterministic_hashing_verified": aggregation_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": diagnostics_aggregations_equal(aggregation, repeated),
            "governance_layer_ordering_verified": exported_layer_order == expected_layer_order,
            "diagnostics_ordering_verified": exported_diagnostic_order == expected_diagnostic_order,
            "explainability_ordering_verified": exported_explainability_order == expected_explainability_order,
            "state_summary_ordering_verified": exported_state_order == expected_state_order,
            "identity_visibility_verified": identity["valid"],
            "governance_layer_visibility_verified": layers["valid"],
            "cross_layer_state_visibility_verified": state_visibility["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_status": True,
            "rollback_safe_status": True,
            "non_execution_enforcement_validated": non_execution["valid"],
            "non_decision_guarantees_validated": non_execution["valid"],
            "enabled_coordination_execution_count": enabled_coordination_execution_count(aggregation),
            "enabled_transition_execution_count": enabled_transition_execution_count(aggregation),
            "enabled_policy_enforcement_count": enabled_policy_enforcement_count(aggregation),
            "enabled_operational_capability_count": enabled_operational_capability_count(aggregation),
            "enabled_orchestration_decision_count": enabled_orchestration_decision_count(aggregation),
            "enabled_orchestration_recommendation_count": enabled_orchestration_recommendation_count(
                aggregation
            ),
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "orchestration_intelligence_execution_disabled": non_execution[
                "orchestration_intelligence_execution_disabled"
            ],
            "orchestration_recommendation_disabled": non_execution[
                "orchestration_recommendation_disabled"
            ],
            "orchestration_decision_disabled": non_execution["orchestration_decision_disabled"],
            "orchestration_authorization_disabled": non_execution[
                "orchestration_authorization_disabled"
            ],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "orchestration_dispatch_disabled": non_execution["orchestration_dispatch_disabled"],
            "orchestration_activation_disabled": non_execution[
                "orchestration_activation_disabled"
            ],
            "runtime_coordination_disabled": non_execution["runtime_coordination_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "traversal_execution_disabled": non_execution["traversal_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "repair_disabled": non_execution["repair_disabled"],
            "inference_disabled": non_execution["inference_disabled"],
            "ranking_disabled": non_execution["ranking_disabled"],
            "scoring_disabled": non_execution["scoring_disabled"],
            "selection_disabled": non_execution["selection_disabled"],
            "optimization_disabled": non_execution["optimization_disabled"],
            "planning_engine_absent": non_execution["planning_engine_absent"],
            "decision_engine_absent": non_execution["decision_engine_absent"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
            "operational_mutation_disabled": non_execution["operational_mutation_disabled"],
            "hidden_orchestration_pathway_absent": non_execution[
                "hidden_orchestration_pathway_absent"
            ],
            "implicit_operational_authorization_absent": non_execution[
                "implicit_operational_authorization_absent"
            ],
        },
        "diagnostics_aggregation": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_DIAGNOSTICS_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="Diagnostics and explainability JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_diagnostics_and_explainability_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"diagnostics_aggregation_status={report['diagnostics_aggregation_status']}")
    print(f"enabled_coordination_execution_count={report['summary']['enabled_coordination_execution_count']}")
    print(f"enabled_transition_execution_count={report['summary']['enabled_transition_execution_count']}")
    print(f"enabled_policy_enforcement_count={report['summary']['enabled_policy_enforcement_count']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"enabled_orchestration_decision_count={report['summary']['enabled_orchestration_decision_count']}")
    print(
        "enabled_orchestration_recommendation_count="
        f"{report['summary']['enabled_orchestration_recommendation_count']}"
    )
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
