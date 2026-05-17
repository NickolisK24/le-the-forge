"""Generate deterministic v4.1 refresh diagnostics explainability evidence."""

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

from operational_refresh.refresh_diagnostics_explainability_continuity import (  # noqa: E402
    certify_diagnostics_explainability_continuity,
)
from operational_refresh.refresh_diagnostics_explainability_diagnostics import (  # noqa: E402
    build_refresh_diagnostics_explainability_diagnostics,
    build_unified_refresh_diagnostics,
    build_unified_refresh_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_hashing import (  # noqa: E402
    deterministic_diagnostics_explainability_hash,
    hash_diagnostics_continuity,
    hash_diagnostics_explainability_identity,
    hash_diagnostics_integrity,
    hash_refresh_diagnostics_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_integrity import (  # noqa: E402
    diagnostics_explainability_identity_normalization_report,
    refresh_diagnostics_explainabilities_equal,
    validate_diagnostics_explainability_integrity,
    validate_diagnostics_explainability_non_execution,
)
from operational_refresh.refresh_diagnostics_explainability_models import (  # noqa: E402
    V4_1_REFRESH_DIAGNOSTICS_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_BLOCKED,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_STABLE,
    V4_1_REFRESH_DIAGNOSTICS_INTEGRITY_REPORT_SCHEMA_VERSION,
    V4_1_UNIFIED_REFRESH_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_1_UNIFIED_REFRESH_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
    default_refresh_diagnostics_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_serialization import (  # noqa: E402
    export_refresh_diagnostics_explainability,
    serialize_refresh_diagnostics_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_visibility import (  # noqa: E402
    count_diagnostic_states,
    count_explanation_states,
    validate_refresh_diagnostics_explainability_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_diagnostics_explainability_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_unified_refresh_diagnostics_report.json")
EXPLAINABILITY_REPORT_PATH = Path("docs/generated/v4_1_unified_refresh_explainability_report.json")
CONTINUITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_diagnostics_continuity_certification_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_diagnostics_integrity_certification_report.json")


def _reordered_diagnostics_explainability():
    payload = default_refresh_diagnostics_explainability()
    return replace(
        payload,
        diagnostic_summaries=tuple(reversed(payload.diagnostic_summaries)),
        explanation_summaries=tuple(reversed(payload.explanation_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_diagnostics_explainability_hash(payload)


def _status(valid: bool) -> str:
    return V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_STABLE if valid else V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_BLOCKED


def build_v4_1_refresh_diagnostics_explainability_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_diagnostics_explainability()
    repeated = default_refresh_diagnostics_explainability()
    reordered = _reordered_diagnostics_explainability()
    exported = export_refresh_diagnostics_explainability(payload)
    visibility = validate_refresh_diagnostics_explainability_visibility(payload)
    continuity = certify_diagnostics_explainability_continuity(payload)
    non_execution = validate_diagnostics_explainability_non_execution(payload)
    integrity = validate_diagnostics_explainability_integrity(payload)
    diagnostics = build_refresh_diagnostics_explainability_diagnostics(payload)
    serialization_first = serialize_refresh_diagnostics_explainability(payload)
    serialization_second = serialize_refresh_diagnostics_explainability(repeated)
    serialization_reordered = serialize_refresh_diagnostics_explainability(reordered)
    payload_hash = hash_refresh_diagnostics_explainability(payload)
    repeated_hash = hash_refresh_diagnostics_explainability(repeated)
    reordered_hash = hash_refresh_diagnostics_explainability(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if payload_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_diagnostics_explainabilities_equal(payload, repeated) else 1,
        ]
    )
    status = _status(validation_error_count == 0)
    exported_diagnostic_order = [item["diagnostic_id"] for item in exported["diagnostic_summaries"]]
    expected_diagnostic_order = [
        item["diagnostic_id"]
        for item in sorted(
            exported["diagnostic_summaries"],
            key=lambda item: (item["deterministic_order"], item["diagnostic_id"]),
        )
    ]
    exported_explanation_order = [item["explanation_id"] for item in exported["explanation_summaries"]]
    expected_explanation_order = [
        item["explanation_id"]
        for item in sorted(
            exported["explanation_summaries"],
            key=lambda item: (item["deterministic_order"], item["explanation_id"]),
        )
    ]
    report = {
        "schema_version": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID,
        "phase_name": "v4.1_phase_8_refresh_diagnostics_explainability",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh diagnostics and explainability without remediation recommendation approval orchestration or execution",
        "diagnostics_explainability_mode": "descriptive_only",
        "foundation_status": status,
        "model_counts": {
            "identity_count": 1,
            "diagnostic_summary_count": len(payload.diagnostic_summaries),
            "explanation_summary_count": len(payload.explanation_summaries),
            "diagnostic_state_counts": count_diagnostic_states(payload.diagnostic_summaries),
            "explanation_state_counts": count_explanation_states(payload.explanation_summaries),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_diagnostics_explainability",
            "payload_length": len(serialization_first),
            "diagnostic_order_preserved": exported_diagnostic_order == expected_diagnostic_order,
            "explanation_order_preserved": exported_explanation_order == expected_explanation_order,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": payload_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_diagnostics_explainability",
            "diagnostics_explainability_hash": payload_hash,
            "identity_hash": hash_diagnostics_explainability_identity(payload.identity),
            "continuity_hash": hash_diagnostics_continuity(payload.continuity_metadata),
            "integrity_hash": hash_diagnostics_integrity(payload.integrity_boundary),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": payload == repeated,
            "dataclass_hash_stable": hash(payload) == hash(repeated),
            "serialized_equality_stable": refresh_diagnostics_explainabilities_equal(payload, repeated),
            "reordered_serialized_equality_stable": refresh_diagnostics_explainabilities_equal(payload, reordered),
        },
        "diagnostic_visibility": visibility,
        "continuity_certification": continuity,
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_remediation_recommendation_approval_and_execution_guarantees": non_execution,
        "identity_normalization": diagnostics_explainability_identity_normalization_report(payload.identity),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_diagnostics_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_diagnostics_hashing_verified": payload_hash == repeated_hash == reordered_hash,
            "deterministic_diagnostics_equality_verified": refresh_diagnostics_explainabilities_equal(payload, repeated),
            "deterministic_diagnostics_visibility_verified": visibility["valid"],
            "deterministic_explanation_visibility_verified": visibility["explanation_category_coverage_complete"],
            "cross_layer_diagnostic_aggregation_validated": visibility["cross_layer_diagnostic_aggregation_visible"],
            "cross_layer_explanation_aggregation_validated": visibility["cross_layer_explanation_aggregation_visible"],
            "unsupported_state_explanation_validated": visibility["unsupported_state_explanations_visible"],
            "blocked_state_explanation_validated": visibility["blocked_state_explanations_visible"],
            "prohibited_state_explanation_validated": visibility["prohibited_state_explanations_visible"],
            "limitation_explanation_validated": visibility["limitation_explanations_visible"],
            "diagnostics_provenance_continuity_validated": continuity["provenance_continuity_valid"],
            "diagnostics_lineage_continuity_validated": continuity["lineage_continuity_valid"],
            "diagnostics_replay_continuity_validated": continuity["replay_continuity_valid"],
            "diagnostics_rollback_continuity_validated": continuity["rollback_continuity_valid"],
            "non_remediation_enforcement_validated": non_execution["remediation_absent"],
            "non_correction_enforcement_validated": non_execution["automatic_correction_absent"],
            "non_recommendation_ranking_scoring_selection_enforcement_validated": (
                non_execution["recommendation_absent"]
                and non_execution["ranking_absent"]
                and non_execution["scoring_absent"]
                and non_execution["selection_absent"]
            ),
            "non_approval_authorization_enforcement_validated": (
                non_execution["approval_absent"] and non_execution["authorization_absent"]
            ),
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "explainability_validation_verified": visibility["valid"] and visibility["explanation_category_coverage_complete"],
            "cross_layer_diagnostic_validation_verified": visibility["diagnostic_layer_coverage_complete"],
        },
        "refresh_diagnostics_explainability": exported,
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_unified_refresh_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_diagnostics_explainability()
    diagnostics = build_unified_refresh_diagnostics(payload)
    non_execution = validate_diagnostics_explainability_non_execution(payload)
    status = _status(diagnostics["visibility_validation"]["diagnostic_layer_coverage_complete"] and diagnostics["enabled_capability_count"] == 0)
    report = {
        "schema_version": V4_1_UNIFIED_REFRESH_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID,
        "phase_name": "v4.1_phase_8_unified_refresh_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic unified refresh diagnostics without remediation correction recommendation or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "unified_diagnostics": diagnostics,
        "non_remediation_recommendation_approval_and_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "cross_layer_diagnostic_aggregation_validated": diagnostics["visibility_validation"][
                "cross_layer_diagnostic_aggregation_visible"
            ],
            "missing_diagnostic_coverage_visible": diagnostics["visibility_validation"]["missing_diagnostic_coverage_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "automatic_correction_absent": diagnostics["automatic_correction_absent"],
            "recommendation_absent": diagnostics["recommendation_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_unified_refresh_explainability_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_diagnostics_explainability()
    explainability = build_unified_refresh_explainability(payload)
    non_execution = validate_diagnostics_explainability_non_execution(payload)
    status = _status(
        explainability["visibility_validation"]["explanation_category_coverage_complete"]
        and explainability["enabled_capability_count"] == 0
    )
    report = {
        "schema_version": V4_1_UNIFIED_REFRESH_EXPLAINABILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID,
        "phase_name": "v4.1_phase_8_unified_refresh_explainability",
        "repo_root": str(root),
        "architectural_purpose": "deterministic unified refresh explainability without recommendation approval orchestration or execution",
        "explainability_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "unified_explainability": explainability,
        "non_remediation_recommendation_approval_and_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": explainability["enabled_capability_count"],
            "cross_layer_explanation_aggregation_validated": explainability["visibility_validation"][
                "cross_layer_explanation_aggregation_visible"
            ],
            "unsupported_state_explanation_validated": explainability["visibility_validation"][
                "unsupported_state_explanations_visible"
            ],
            "blocked_state_explanation_validated": explainability["visibility_validation"]["blocked_state_explanations_visible"],
            "prohibited_state_explanation_validated": explainability["visibility_validation"][
                "prohibited_state_explanations_visible"
            ],
            "limitation_explanation_validated": explainability["visibility_validation"]["limitation_explanations_visible"],
            "explanations_are_descriptive_only": explainability["explanations_are_descriptive_only"],
            "recommendation_absent": explainability["recommendation_absent"],
            "approval_absent": explainability["approval_absent"],
            "authorization_absent": explainability["authorization_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_diagnostics_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_diagnostics_explainability()
    continuity = certify_diagnostics_explainability_continuity(payload)
    status = _status(continuity["valid"])
    report = {
        "schema_version": V4_1_REFRESH_DIAGNOSTICS_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID,
        "phase_name": "v4.1_phase_8_refresh_diagnostics_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic diagnostics continuity certification without correction remediation or execution",
        "continuity_mode": "descriptive_certification_only",
        "foundation_status": status,
        "continuity_certification": continuity,
        "summary": {
            "foundation_status": status,
            "continuity_certification_verified": continuity["valid"],
            "diagnostics_continuity_verified": continuity["diagnostics_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
        },
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_diagnostics_integrity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    payload = default_refresh_diagnostics_explainability()
    integrity = validate_diagnostics_explainability_integrity(payload)
    status = _status(integrity["valid"])
    report = {
        "schema_version": V4_1_REFRESH_DIAGNOSTICS_INTEGRITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_PHASE_ID,
        "phase_name": "v4.1_phase_8_refresh_diagnostics_integrity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic diagnostics integrity auditing without remediation recommendation approval or execution",
        "integrity_mode": "descriptive_only_no_action",
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
            "remediation_disabled_validated": integrity["non_execution_validation"]["remediation_absent"],
            "automatic_correction_disabled_validated": integrity["non_execution_validation"]["automatic_correction_absent"],
            "recommendation_disabled_validated": integrity["non_execution_validation"]["recommendation_absent"],
            "approval_disabled_validated": integrity["non_execution_validation"]["approval_absent"],
            "authorization_disabled_validated": integrity["non_execution_validation"]["authorization_absent"],
            "production_consumption_disabled_validated": integrity["non_execution_validation"][
                "production_consumption_absent"
            ],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(payload.governance.explicit_limitations),
        "explicit_prohibitions": list(payload.governance.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Diagnostics explainability JSON report output path")
    parser.add_argument("--diagnostics-output", default=str(DIAGNOSTICS_REPORT_PATH))
    parser.add_argument("--explainability-output", default=str(EXPLAINABILITY_REPORT_PATH))
    parser.add_argument("--continuity-output", default=str(CONTINUITY_REPORT_PATH))
    parser.add_argument("--integrity-output", default=str(INTEGRITY_REPORT_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_refresh_diagnostics_explainability_report()
    diagnostics_report = build_v4_1_unified_refresh_diagnostics_report()
    explainability_report = build_v4_1_unified_refresh_explainability_report()
    continuity_report = build_v4_1_refresh_diagnostics_continuity_certification_report()
    integrity_report = build_v4_1_refresh_diagnostics_integrity_certification_report()
    write_report(report, Path(args.output))
    write_report(diagnostics_report, Path(args.diagnostics_output))
    write_report(explainability_report, Path(args.explainability_output))
    write_report(continuity_report, Path(args.continuity_output))
    write_report(integrity_report, Path(args.integrity_output))
    print(f"wrote {Path(args.output)}")
    print(f"wrote {Path(args.diagnostics_output)}")
    print(f"wrote {Path(args.explainability_output)}")
    print(f"wrote {Path(args.continuity_output)}")
    print(f"wrote {Path(args.integrity_output)}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"diagnostics_status={diagnostics_report['foundation_status']}")
    print(f"explainability_status={explainability_report['foundation_status']}")
    print(f"continuity_status={continuity_report['foundation_status']}")
    print(f"integrity_status={integrity_report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_diagnostics_report_hash={diagnostics_report['deterministic_report_hash']}")
    print(f"deterministic_explainability_report_hash={explainability_report['deterministic_report_hash']}")
    print(f"deterministic_continuity_report_hash={continuity_report['deterministic_report_hash']}")
    print(f"deterministic_integrity_report_hash={integrity_report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
