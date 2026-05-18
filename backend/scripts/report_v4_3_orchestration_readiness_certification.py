"""Generate deterministic v4.3 orchestration readiness certification evidence."""

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

from orchestration_governance.orchestration_readiness_certification import (  # noqa: E402
    build_readiness_certification_diagnostics,
    default_orchestration_readiness_certification,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_orchestration_approval_count,
    enabled_orchestration_authorization_count,
    enabled_orchestration_decision_count,
    enabled_orchestration_recommendation_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    readiness_certification_identity_key,
    readiness_certifications_equal,
    validate_readiness_certification_identity,
    validate_readiness_certifications,
    validate_readiness_explainability,
    validate_readiness_non_execution_authorization_approval_decision,
    validate_state_readiness_visibility,
)
from orchestration_governance.orchestration_readiness_hashing import (  # noqa: E402
    deterministic_readiness_hash,
    hash_orchestration_readiness_certification,
    hash_readiness_certification_identity,
    hash_readiness_certification_record,
    hash_readiness_diagnostic,
    hash_readiness_explainability,
    hash_readiness_state_summary,
)
from orchestration_governance.orchestration_readiness_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_READINESS_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_READINESS_PROHIBITIONS,
    V4_3_ORCHESTRATION_READINESS_GENERATED_AT,
    V4_3_ORCHESTRATION_READINESS_PHASE_ID,
    V4_3_ORCHESTRATION_READINESS_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_READINESS_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_READINESS_STATUS_STABLE,
)
from orchestration_governance.orchestration_readiness_serialization import (  # noqa: E402
    export_orchestration_readiness_certification,
    serialize_orchestration_readiness_certification,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_readiness_certification_report.json")


def _reordered_readiness_certification():
    certification = default_orchestration_readiness_certification()
    return replace(
        certification,
        readiness_certifications=tuple(reversed(certification.readiness_certifications)),
        state_readiness_summaries=tuple(reversed(certification.state_readiness_summaries)),
        diagnostics=tuple(reversed(certification.diagnostics)),
        explainability_summaries=tuple(reversed(certification.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_readiness_hash(payload)


def build_v4_3_orchestration_readiness_certification_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    certification = default_orchestration_readiness_certification()
    repeated = default_orchestration_readiness_certification()
    reordered = _reordered_readiness_certification()
    exported = export_orchestration_readiness_certification(certification)

    identity = validate_readiness_certification_identity(certification)
    readiness = validate_readiness_certifications(certification)
    states = validate_state_readiness_visibility(certification)
    explainability = validate_readiness_explainability(certification)
    non_execution = validate_readiness_non_execution_authorization_approval_decision(certification)
    diagnostics = build_readiness_certification_diagnostics(certification)

    serialization_first = serialize_orchestration_readiness_certification(certification)
    serialization_second = serialize_orchestration_readiness_certification(repeated)
    serialization_reordered = serialize_orchestration_readiness_certification(reordered)
    readiness_hash = hash_orchestration_readiness_certification(certification)
    repeated_hash = hash_orchestration_readiness_certification(repeated)
    reordered_hash = hash_orchestration_readiness_certification(reordered)
    readiness_hashes = [
        hash_readiness_certification_record(item) for item in certification.readiness_certifications
    ]
    state_hashes = [
        hash_readiness_state_summary(item) for item in certification.state_readiness_summaries
    ]
    diagnostic_hashes = [hash_readiness_diagnostic(item) for item in certification.diagnostics]
    explainability_hashes = [
        hash_readiness_explainability(item) for item in certification.explainability_summaries
    ]

    exported_readiness_order = [item["readiness_id"] for item in exported["readiness_certifications"]]
    expected_readiness_order = [
        item["readiness_id"]
        for item in sorted(
            exported["readiness_certifications"],
            key=lambda item: (item["deterministic_order"], item["readiness_id"]),
        )
    ]
    exported_state_order = [item["state_summary_id"] for item in exported["state_readiness_summaries"]]
    expected_state_order = [
        item["state_summary_id"]
        for item in sorted(
            exported["state_readiness_summaries"],
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
            0 if readiness["valid"] else 1,
            0 if states["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if readiness_hash == repeated_hash == reordered_hash else 1,
            0 if readiness_certifications_equal(certification, repeated) else 1,
            0 if exported_readiness_order == expected_readiness_order else 1,
            0 if exported_state_order == expected_state_order else 1,
            0 if exported_diagnostic_order == expected_diagnostic_order else 1,
            0 if exported_explainability_order == expected_explainability_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_READINESS_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_READINESS_STATUS_BLOCKED
    )

    report = {
        "schema_version": V4_3_ORCHESTRATION_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_READINESS_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_READINESS_PHASE_ID,
        "phase_name": "v4.3_phase_9_orchestration_readiness_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration readiness certification for architectural closeout planning without operational readiness approval",
        "certification_mode": "descriptive_only_non_executing_non_authorizing_non_approving_non_decisioning_governance",
        "readiness_certification_status": status,
        "certification_counts": {
            "readiness_certification_count": len(certification.readiness_certifications),
            "readiness_gap_count": diagnostics["readiness_gap_count"],
            "governance_instability_count": diagnostics["governance_instability_count"],
            "continuity_failure_count": diagnostics["continuity_failure_count"],
            "integrity_failure_count": diagnostics["integrity_failure_count"],
            "prohibited_state_readiness_count": states["prohibited_state_readiness_count"],
            "unsupported_state_readiness_count": states["unsupported_state_readiness_count"],
            "blocked_state_readiness_count": states["blocked_state_readiness_count"],
            "stale_state_readiness_count": states["stale_state_readiness_count"],
            "conflicting_state_readiness_count": states["conflicting_state_readiness_count"],
            "diagnostic_count": len(certification.diagnostics),
            "explainability_summary_count": len(certification.explainability_summaries),
        },
        "identity_visibility": {
            "identity_key": readiness_certification_identity_key(certification),
            "identity_validation": identity,
            "identity_hash": hash_readiness_certification_identity(certification.identity),
        },
        "readiness_certification_visibility": {
            "readiness_validation": readiness,
            "readiness_certification_hashes": readiness_hashes,
            "readiness_gap_count": readiness["readiness_gap_count"],
            "governance_instability_count": readiness["governance_instability_count"],
            "continuity_failure_count": readiness["continuity_failure_count"],
            "integrity_failure_count": readiness["integrity_failure_count"],
            "readiness_classification": readiness["readiness_classification"],
            "replay_safe_readiness_status": readiness["replay_safe_readiness_status"],
            "rollback_safe_readiness_status": readiness["rollback_safe_readiness_status"],
            "governance_readiness_visible": readiness["governance_readiness_visible"],
            "continuity_readiness_visible": readiness["continuity_readiness_visible"],
            "integrity_readiness_visible": readiness["integrity_readiness_visible"],
        },
        "state_readiness_visibility": {
            "state_readiness_validation": states,
            "state_readiness_hashes": state_hashes,
            "prohibited_state_readiness_visible": states["prohibited_state_readiness_visible"],
            "unsupported_state_readiness_visible": states["unsupported_state_readiness_visible"],
            "blocked_state_readiness_visible": states["blocked_state_readiness_visible"],
            "stale_state_readiness_visible": states["stale_state_readiness_visible"],
            "conflicting_state_readiness_visible": states["conflicting_state_readiness_visible"],
        },
        "diagnostics_findings": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "phase_8_continuity_diagnostics": diagnostics["phase_8_continuity_diagnostics"],
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
            "orchestration_approval_unavailable_visible": (
                "orchestration_approval_unavailable" in explainability["explainability_categories"]
            ),
            "governance_readiness_visible": (
                "governance_readiness_matters" in explainability["explainability_categories"]
            ),
            "continuity_readiness_visible": (
                "continuity_readiness_matters" in explainability["explainability_categories"]
            ),
            "integrity_readiness_visible": (
                "integrity_readiness_matters" in explainability["explainability_categories"]
            ),
            "replay_safe_evidence_visible": (
                "replay_safe_evidence_matters" in explainability["explainability_categories"]
            ),
            "rollback_safe_evidence_visible": (
                "rollback_safe_evidence_matters" in explainability["explainability_categories"]
            ),
            "fail_visible_readiness_states_visible": (
                "fail_visible_readiness_states_exist"
                in explainability["explainability_categories"]
            ),
            "operational_orchestration_prohibited_visible": (
                "operational_orchestration_prohibited"
                in explainability["explainability_categories"]
            ),
        },
        "replay_safe_readiness_status": readiness["replay_safe_readiness_status"],
        "rollback_safe_readiness_status": readiness["rollback_safe_readiness_status"],
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_readiness_certification",
            "payload_length": len(serialization_first),
            "readiness_ordering_stable": exported_readiness_order == expected_readiness_order,
            "state_readiness_ordering_stable": exported_state_order == expected_state_order,
            "diagnostics_ordering_stable": exported_diagnostic_order == expected_diagnostic_order,
            "explainability_ordering_stable": exported_explainability_order == expected_explainability_order,
            "deterministic_fail_visible_serialization": states["valid"],
        },
        "hashing_stability_evidence": {
            "stable": readiness_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_readiness_certification",
            "readiness_certification_hash": readiness_hash,
            "repeated_readiness_certification_hash": repeated_hash,
            "reordered_readiness_certification_hash": reordered_hash,
            "identity_hash": hash_readiness_certification_identity(certification.identity),
            "readiness_certification_hashes": readiness_hashes,
            "state_readiness_hashes": state_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "non_execution_guarantees": non_execution,
        "non_authorization_guarantees": {
            "valid": non_execution["valid"],
            "orchestration_authorization_disabled": non_execution[
                "orchestration_authorization_disabled"
            ],
            "implicit_authorization_absent": non_execution["implicit_authorization_absent"],
            "enabled_orchestration_authorization_count": non_execution[
                "enabled_orchestration_authorization_count"
            ],
        },
        "non_approval_guarantees": {
            "valid": non_execution["valid"],
            "orchestration_approval_disabled": non_execution["orchestration_approval_disabled"],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "readiness_operational_approval_disabled": non_execution[
                "readiness_operational_approval_disabled"
            ],
            "enabled_orchestration_approval_count": non_execution[
                "enabled_orchestration_approval_count"
            ],
        },
        "non_decision_guarantees": {
            "valid": non_execution["valid"],
            "orchestration_decision_disabled": non_execution["orchestration_decision_disabled"],
            "orchestration_recommendation_disabled": non_execution[
                "orchestration_recommendation_disabled"
            ],
            "orchestration_planning_engine_disabled": non_execution[
                "orchestration_planning_engine_disabled"
            ],
            "orchestration_decision_engine_disabled": non_execution[
                "orchestration_decision_engine_disabled"
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
            "readiness_certification_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first
            == serialization_second
            == serialization_reordered,
            "deterministic_hashing_verified": readiness_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": readiness_certifications_equal(certification, repeated),
            "readiness_ordering_verified": exported_readiness_order == expected_readiness_order,
            "state_readiness_ordering_verified": exported_state_order == expected_state_order,
            "diagnostics_ordering_verified": exported_diagnostic_order == expected_diagnostic_order,
            "explainability_ordering_verified": exported_explainability_order == expected_explainability_order,
            "identity_visibility_verified": identity["valid"],
            "readiness_certification_verified": readiness["valid"],
            "state_readiness_visibility_verified": states["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_readiness_status": readiness["replay_safe_readiness_status"],
            "rollback_safe_readiness_status": readiness["rollback_safe_readiness_status"],
            "readiness_classification": readiness["readiness_classification"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "non_authorization_guarantees_validated": non_execution["valid"],
            "non_approval_guarantees_validated": non_execution["valid"],
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
            "enabled_orchestration_approval_count": enabled_orchestration_approval_count(certification),
            "orchestration_activation_disabled": non_execution["orchestration_activation_disabled"],
            "orchestration_approval_disabled": non_execution["orchestration_approval_disabled"],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
            "operational_mutation_disabled": non_execution["operational_mutation_disabled"],
        },
        "readiness_certification": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_READINESS_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_READINESS_PROHIBITIONS),
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
        help="Readiness certification JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_readiness_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"readiness_certification_status={report['readiness_certification_status']}")
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
    print(
        "enabled_orchestration_approval_count="
        f"{report['summary']['enabled_orchestration_approval_count']}"
    )
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
