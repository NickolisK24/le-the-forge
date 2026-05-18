"""Generate deterministic v4.3 orchestration continuity and integrity certification evidence."""

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

from orchestration_governance.orchestration_continuity_certification import (  # noqa: E402
    build_continuity_integrity_certification_diagnostics,
    continuity_certification_identity_key,
    continuity_certifications_equal,
    default_orchestration_continuity_integrity_certification,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_orchestration_authorization_count,
    enabled_orchestration_decision_count,
    enabled_orchestration_recommendation_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    validate_continuity_certification_identity,
    validate_continuity_certifications,
    validate_continuity_explainability,
    validate_continuity_non_execution_authorization_decision,
    validate_integrity_certifications,
    validate_state_certification_visibility,
)
from orchestration_governance.orchestration_continuity_hashing import (  # noqa: E402
    deterministic_continuity_hash,
    hash_certification_state_summary,
    hash_continuity_certification_diagnostic,
    hash_continuity_certification_explainability,
    hash_continuity_certification_identity,
    hash_continuity_certification_record,
    hash_integrity_certification_record,
    hash_orchestration_continuity_integrity_certification,
)
from orchestration_governance.orchestration_continuity_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_CONTINUITY_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_CONTINUITY_PROHIBITIONS,
    V4_3_ORCHESTRATION_CONTINUITY_GENERATED_AT,
    V4_3_ORCHESTRATION_CONTINUITY_PHASE_ID,
    V4_3_ORCHESTRATION_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_CONTINUITY_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_CONTINUITY_STATUS_STABLE,
)
from orchestration_governance.orchestration_continuity_serialization import (  # noqa: E402
    export_orchestration_continuity_integrity_certification,
    serialize_orchestration_continuity_integrity_certification,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_continuity_and_integrity_certification_report.json")


def _reordered_continuity_certification():
    certification = default_orchestration_continuity_integrity_certification()
    return replace(
        certification,
        continuity_certifications=tuple(reversed(certification.continuity_certifications)),
        integrity_certifications=tuple(reversed(certification.integrity_certifications)),
        state_certification_summaries=tuple(reversed(certification.state_certification_summaries)),
        diagnostics=tuple(reversed(certification.diagnostics)),
        explainability_summaries=tuple(reversed(certification.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_continuity_hash(payload)


def build_v4_3_orchestration_continuity_and_integrity_certification_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_orchestration_continuity_integrity_certification()
    repeated = default_orchestration_continuity_integrity_certification()
    reordered = _reordered_continuity_certification()
    exported = export_orchestration_continuity_integrity_certification(certification)

    identity = validate_continuity_certification_identity(certification)
    continuity = validate_continuity_certifications(certification)
    integrity = validate_integrity_certifications(certification)
    states = validate_state_certification_visibility(certification)
    explainability = validate_continuity_explainability(certification)
    non_execution = validate_continuity_non_execution_authorization_decision(certification)
    diagnostics = build_continuity_integrity_certification_diagnostics(certification)

    serialization_first = serialize_orchestration_continuity_integrity_certification(certification)
    serialization_second = serialize_orchestration_continuity_integrity_certification(repeated)
    serialization_reordered = serialize_orchestration_continuity_integrity_certification(reordered)
    certification_hash = hash_orchestration_continuity_integrity_certification(certification)
    repeated_hash = hash_orchestration_continuity_integrity_certification(repeated)
    reordered_hash = hash_orchestration_continuity_integrity_certification(reordered)
    continuity_hashes = [
        hash_continuity_certification_record(item) for item in certification.continuity_certifications
    ]
    integrity_hashes = [
        hash_integrity_certification_record(item) for item in certification.integrity_certifications
    ]
    state_hashes = [
        hash_certification_state_summary(item) for item in certification.state_certification_summaries
    ]
    diagnostic_hashes = [
        hash_continuity_certification_diagnostic(item) for item in certification.diagnostics
    ]
    explainability_hashes = [
        hash_continuity_certification_explainability(item)
        for item in certification.explainability_summaries
    ]

    exported_continuity_order = [
        item["certification_id"] for item in exported["continuity_certifications"]
    ]
    expected_continuity_order = [
        item["certification_id"]
        for item in sorted(
            exported["continuity_certifications"],
            key=lambda item: (item["deterministic_order"], item["certification_id"]),
        )
    ]
    exported_integrity_order = [item["integrity_id"] for item in exported["integrity_certifications"]]
    expected_integrity_order = [
        item["integrity_id"]
        for item in sorted(
            exported["integrity_certifications"],
            key=lambda item: (item["deterministic_order"], item["integrity_id"]),
        )
    ]
    exported_state_order = [
        item["state_summary_id"] for item in exported["state_certification_summaries"]
    ]
    expected_state_order = [
        item["state_summary_id"]
        for item in sorted(
            exported["state_certification_summaries"],
            key=lambda item: (item["deterministic_order"], item["state_summary_id"]),
        )
    ]
    exported_diagnostic_order = [item["diagnostic_id"] for item in exported["diagnostics"]]
    expected_diagnostic_order = [
        item["diagnostic_id"]
        for item in sorted(
            exported["diagnostics"],
            key=lambda item: (item["deterministic_order"], item["diagnostic_id"]),
        )
    ]
    exported_explainability_order = [
        item["explanation_id"] for item in exported["explainability_summaries"]
    ]
    expected_explainability_order = [
        item["explanation_id"]
        for item in sorted(
            exported["explainability_summaries"],
            key=lambda item: (item["deterministic_order"], item["explanation_id"]),
        )
    ]

    validation_error_count = sum(
        [
            0 if identity["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if states["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if certification_hash == repeated_hash == reordered_hash else 1,
            0 if continuity_certifications_equal(certification, repeated) else 1,
            0 if exported_continuity_order == expected_continuity_order else 1,
            0 if exported_integrity_order == expected_integrity_order else 1,
            0 if exported_state_order == expected_state_order else 1,
            0 if exported_diagnostic_order == expected_diagnostic_order else 1,
            0 if exported_explainability_order == expected_explainability_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_CONTINUITY_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_CONTINUITY_STATUS_BLOCKED
    )

    report = {
        "schema_version": V4_3_ORCHESTRATION_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_CONTINUITY_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_CONTINUITY_PHASE_ID,
        "phase_name": "v4.3_phase_8_orchestration_continuity_and_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration continuity and integrity certification without operational orchestration certification",
        "certification_mode": "descriptive_only_non_executing_non_authorizing_non_decisioning_governance",
        "continuity_integrity_certification_status": status,
        "certification_counts": {
            "continuity_certification_count": len(certification.continuity_certifications),
            "integrity_certification_count": len(certification.integrity_certifications),
            "continuity_gap_count": diagnostics["continuity_gap_count"],
            "integrity_failure_count": diagnostics["integrity_failure_count"],
            "prohibited_state_certification_count": states[
                "prohibited_state_certification_count"
            ],
            "unsupported_state_certification_count": states[
                "unsupported_state_certification_count"
            ],
            "blocked_state_certification_count": states["blocked_state_certification_count"],
            "stale_state_certification_count": states["stale_state_certification_count"],
            "conflicting_state_certification_count": states[
                "conflicting_state_certification_count"
            ],
            "diagnostic_count": len(certification.diagnostics),
            "explainability_summary_count": len(certification.explainability_summaries),
        },
        "identity_visibility": {
            "identity_key": continuity_certification_identity_key(certification),
            "identity_validation": identity,
            "identity_hash": hash_continuity_certification_identity(certification.identity),
        },
        "continuity_certification_visibility": {
            "continuity_validation": continuity,
            "continuity_certification_hashes": continuity_hashes,
            "continuity_gap_count": continuity["continuity_gap_count"],
            "replay_safe_certification_status": continuity["replay_safe_certification_status"],
            "rollback_safe_certification_status": continuity[
                "rollback_safe_certification_status"
            ],
            "lineage_consistency_visible": continuity["lineage_consistency_visible"],
            "provenance_consistency_visible": continuity["provenance_consistency_visible"],
            "governance_consistency_visible": continuity["governance_consistency_visible"],
        },
        "integrity_certification_visibility": {
            "integrity_validation": integrity,
            "integrity_certification_hashes": integrity_hashes,
            "integrity_failure_count": integrity["integrity_failure_count"],
            "continuity_gap_count": integrity["continuity_gap_count"],
            "cross_layer_integrity_visible": integrity["cross_layer_integrity_visible"],
            "replay_safe_certification_status": integrity["replay_safe_certification_status"],
            "rollback_safe_certification_status": integrity[
                "rollback_safe_certification_status"
            ],
            "governance_consistency_visible": integrity["governance_consistency_visible"],
        },
        "state_certification_visibility": {
            "state_certification_validation": states,
            "state_certification_hashes": state_hashes,
            "prohibited_state_certification_visible": states[
                "prohibited_state_certification_visible"
            ],
            "unsupported_state_certification_visible": states[
                "unsupported_state_certification_visible"
            ],
            "blocked_state_certification_visible": states["blocked_state_certification_visible"],
            "stale_state_certification_visible": states["stale_state_certification_visible"],
            "conflicting_state_certification_visible": states[
                "conflicting_state_certification_visible"
            ],
        },
        "diagnostics_findings": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "phase_7_diagnostics_validation": diagnostics["phase_7_diagnostics_validation"],
        },
        "explainability_findings": {
            "explainability_validation": explainability,
            "explainability_categories": diagnostics["explainability_categories"],
            "explainability_hashes": explainability_hashes,
            "explainability_is_descriptive_only": diagnostics["explainability_is_descriptive_only"],
            "orchestration_non_executable_visible": (
                "orchestration_non_executable" in explainability["explainability_categories"]
            ),
            "orchestration_authorization_unavailable_visible": (
                "orchestration_authorization_unavailable"
                in explainability["explainability_categories"]
            ),
            "governance_consistency_visible": (
                "governance_consistency_matters" in explainability["explainability_categories"]
            ),
            "lineage_continuity_visible": (
                "lineage_continuity_matters" in explainability["explainability_categories"]
            ),
            "provenance_continuity_visible": (
                "provenance_continuity_matters" in explainability["explainability_categories"]
            ),
            "replay_safe_evidence_visible": (
                "replay_safe_evidence_matters" in explainability["explainability_categories"]
            ),
            "rollback_safe_evidence_visible": (
                "rollback_safe_evidence_matters" in explainability["explainability_categories"]
            ),
            "fail_visible_inconsistencies_visible": (
                "fail_visible_inconsistencies_exist"
                in explainability["explainability_categories"]
            ),
            "operational_orchestration_prohibited_visible": (
                "operational_orchestration_prohibited"
                in explainability["explainability_categories"]
            ),
        },
        "replay_safe_certification_status": continuity["replay_safe_certification_status"]
        and integrity["replay_safe_certification_status"],
        "rollback_safe_certification_status": continuity["rollback_safe_certification_status"]
        and integrity["rollback_safe_certification_status"],
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_continuity_integrity_certification",
            "payload_length": len(serialization_first),
            "continuity_ordering_stable": exported_continuity_order == expected_continuity_order,
            "integrity_ordering_stable": exported_integrity_order == expected_integrity_order,
            "state_certification_ordering_stable": exported_state_order == expected_state_order,
            "diagnostics_ordering_stable": exported_diagnostic_order == expected_diagnostic_order,
            "explainability_ordering_stable": exported_explainability_order == expected_explainability_order,
            "deterministic_fail_visible_serialization": states["valid"],
        },
        "hashing_stability_evidence": {
            "stable": certification_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_continuity_integrity_certification",
            "continuity_integrity_certification_hash": certification_hash,
            "repeated_continuity_integrity_certification_hash": repeated_hash,
            "reordered_continuity_integrity_certification_hash": reordered_hash,
            "identity_hash": hash_continuity_certification_identity(certification.identity),
            "continuity_certification_hashes": continuity_hashes,
            "integrity_certification_hashes": integrity_hashes,
            "state_certification_hashes": state_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "non_execution_guarantees": non_execution,
        "non_authorization_guarantees": {
            "valid": non_execution["valid"],
            "orchestration_authorization_disabled": non_execution[
                "orchestration_authorization_disabled"
            ],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "implicit_authorization_absent": non_execution["implicit_authorization_absent"],
            "enabled_orchestration_authorization_count": non_execution[
                "enabled_orchestration_authorization_count"
            ],
        },
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
            "enabled_orchestration_decision_count": non_execution[
                "enabled_orchestration_decision_count"
            ],
            "enabled_orchestration_recommendation_count": non_execution[
                "enabled_orchestration_recommendation_count"
            ],
        },
        "summary": {
            "continuity_integrity_certification_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first
            == serialization_second
            == serialization_reordered,
            "deterministic_hashing_verified": certification_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": continuity_certifications_equal(certification, repeated),
            "continuity_ordering_verified": exported_continuity_order == expected_continuity_order,
            "integrity_ordering_verified": exported_integrity_order == expected_integrity_order,
            "state_certification_ordering_verified": exported_state_order == expected_state_order,
            "diagnostics_ordering_verified": exported_diagnostic_order == expected_diagnostic_order,
            "explainability_ordering_verified": exported_explainability_order == expected_explainability_order,
            "identity_visibility_verified": identity["valid"],
            "continuity_certification_verified": continuity["valid"],
            "integrity_certification_verified": integrity["valid"],
            "state_certification_visibility_verified": states["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_certification_status": continuity["replay_safe_certification_status"]
            and integrity["replay_safe_certification_status"],
            "rollback_safe_certification_status": continuity["rollback_safe_certification_status"]
            and integrity["rollback_safe_certification_status"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "non_authorization_guarantees_validated": non_execution["valid"],
            "non_decision_guarantees_validated": non_execution["valid"],
            "enabled_coordination_execution_count": enabled_coordination_execution_count(certification),
            "enabled_transition_execution_count": enabled_transition_execution_count(certification),
            "enabled_policy_enforcement_count": enabled_policy_enforcement_count(certification),
            "enabled_operational_capability_count": enabled_operational_capability_count(certification),
            "enabled_orchestration_decision_count": enabled_orchestration_decision_count(certification),
            "enabled_orchestration_recommendation_count": enabled_orchestration_recommendation_count(
                certification
            ),
            "enabled_orchestration_authorization_count": enabled_orchestration_authorization_count(
                certification
            ),
            "orchestration_activation_disabled": non_execution[
                "orchestration_activation_disabled"
            ],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
            "operational_mutation_disabled": non_execution["operational_mutation_disabled"],
        },
        "continuity_integrity_certification": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_CONTINUITY_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_CONTINUITY_PROHIBITIONS),
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
        help="Continuity and integrity certification JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_continuity_and_integrity_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"continuity_integrity_certification_status={report['continuity_integrity_certification_status']}")
    print(f"enabled_coordination_execution_count={report['summary']['enabled_coordination_execution_count']}")
    print(f"enabled_transition_execution_count={report['summary']['enabled_transition_execution_count']}")
    print(f"enabled_policy_enforcement_count={report['summary']['enabled_policy_enforcement_count']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"enabled_orchestration_decision_count={report['summary']['enabled_orchestration_decision_count']}")
    print(
        "enabled_orchestration_recommendation_count="
        f"{report['summary']['enabled_orchestration_recommendation_count']}"
    )
    print(
        "enabled_orchestration_authorization_count="
        f"{report['summary']['enabled_orchestration_authorization_count']}"
    )
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
