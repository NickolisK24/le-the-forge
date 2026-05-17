"""Generate deterministic v4.0 closeout and v4.1 readiness evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.v4_closeout_audit import audit_v4_closeout_and_v4_1_readiness  # noqa: E402
from operational_lifecycle.v4_closeout_hashing import deterministic_v4_closeout_hash  # noqa: E402
from operational_lifecycle.v4_closeout_models import (  # noqa: E402
    V4_CLOSEOUT_FINDING_TYPES,
    V4_0_CLOSEOUT_GENERATED_AT,
    V4_0_CLOSEOUT_PHASE_ID,
    V4_0_CLOSEOUT_STATUS_BLOCKED,
    V4_0_CLOSEOUT_STATUS_STABLE,
)
from operational_lifecycle.v4_closeout_serialization import export_v4_closeout_report  # noqa: E402
from operational_lifecycle.v4_closeout_visibility import (  # noqa: E402
    count_v4_closeout_finding_types,
    count_v4_closeout_severities,
    validate_v4_closeout_visibility,
)
from operational_lifecycle.continuity_certification_engine import (  # noqa: E402
    certify_operational_lifecycle_continuity,
)
from scripts.report_v4_0_operational_lifecycle_continuity_certification import (  # noqa: E402
    build_representative_operational_continuity_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_closeout_and_v4_1_readiness_report.json")


def build_representative_v4_closeout_inputs():
    inputs = build_representative_operational_continuity_inputs()
    continuity_report = certify_operational_lifecycle_continuity(*inputs)
    return (*inputs, continuity_report)


def build_v4_0_closeout_and_v4_1_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    inputs = build_representative_v4_closeout_inputs()
    closeout_report = audit_v4_closeout_and_v4_1_readiness(*inputs)
    exported = export_v4_closeout_report(closeout_report)
    visibility_validation = validate_v4_closeout_visibility(closeout_report)
    finding_type_counts = count_v4_closeout_finding_types(closeout_report.findings)
    severity_counts = count_v4_closeout_severities(closeout_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = V4_0_CLOSEOUT_STATUS_STABLE if validation_error_count == 0 else V4_0_CLOSEOUT_STATUS_BLOCKED
    rebuilt_hash = audit_v4_closeout_and_v4_1_readiness(*inputs).deterministic_report_hash
    preservation_booleans = {
        "replay_safe": closeout_report.replay_safe,
        "rollback_safe": closeout_report.rollback_safe,
        "provenance_safe": closeout_report.provenance_safe,
        "lineage_safe": closeout_report.lineage_safe,
        "serialization_stable": closeout_report.serialization_stable,
        "hashing_stable": closeout_report.hashing_stable,
        "visibility_preserved": closeout_report.visibility_preserved,
        "integrity_preserved": closeout_report.integrity_preserved,
        "continuity_preserved": closeout_report.continuity_preserved,
        "execution_authorized": closeout_report.execution_authorized,
        "remediation_authorized": closeout_report.remediation_authorized,
        "production_consumption_enabled": closeout_report.production_consumption_enabled,
        "orchestration_enabled": closeout_report.orchestration_enabled,
        "planner_integration_enabled": closeout_report.planner_integration_enabled,
    }
    report = {
        "schema_version": "v4_0.closeout_and_v4_1_readiness_report.1",
        "generated_at": V4_0_CLOSEOUT_GENERATED_AT,
        "phase_id": V4_0_CLOSEOUT_PHASE_ID,
        "phase_name": "v4.0_phase_10_closeout_and_v4_1_readiness",
        "repo_root": str(root),
        "architectural_purpose": "deterministic v4.0 closeout and v4.1 readiness certification without authorization",
        "closeout_mode": "descriptive_closeout_only",
        "foundation_status": status,
        "lifecycle_identity": closeout_report.lifecycle_identity,
        "drift_report_hash": closeout_report.drift_report_hash,
        "governance_report_hash": closeout_report.governance_report_hash,
        "validation_report_hash": closeout_report.validation_report_hash,
        "production_consumption_report_hash": closeout_report.production_consumption_report_hash,
        "recovery_report_hash": closeout_report.recovery_report_hash,
        "diagnostics_report_hash": closeout_report.diagnostics_report_hash,
        "integrity_report_hash": closeout_report.integrity_report_hash,
        "continuity_report_hash": closeout_report.continuity_report_hash,
        "closeout_status": closeout_report.closeout_status,
        "v4_1_readiness_status": closeout_report.v4_1_readiness_status,
        "finding_count": closeout_report.finding_count,
        "finding_type_counts": finding_type_counts,
        "severity_counts": severity_counts,
        "warning_count": closeout_report.warning_count,
        "blocked_count": closeout_report.blocked_count,
        "prohibited_count": closeout_report.prohibited_count,
        "unknown_count": closeout_report.unknown_count,
        "critical_count": closeout_report.critical_count,
        "replay_safety_status": closeout_report.replay_safe,
        "rollback_safety_status": closeout_report.rollback_safe,
        "provenance_safety_status": closeout_report.provenance_safe,
        "lineage_safety_status": closeout_report.lineage_safe,
        "serialization_stability_status": closeout_report.serialization_stable,
        "hashing_stability_status": closeout_report.hashing_stable,
        "visibility_preservation_status": closeout_report.visibility_preserved,
        "integrity_preservation_status": closeout_report.integrity_preserved,
        "continuity_preservation_status": closeout_report.continuity_preserved,
        "execution_authorization_status": closeout_report.execution_authorized,
        "remediation_authorization_status": closeout_report.remediation_authorized,
        "production_consumption_enabled_status": closeout_report.production_consumption_enabled,
        "orchestration_enabled_status": closeout_report.orchestration_enabled,
        "planner_integration_enabled_status": closeout_report.planner_integration_enabled,
        "deterministic_closeout_report_hash": closeout_report.deterministic_report_hash,
        "implemented_closeout_finding_types": list(V4_CLOSEOUT_FINDING_TYPES),
        "preservation_booleans": preservation_booleans,
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "all_report_hashes_preserved": all(
                bool(value)
                for value in (
                    closeout_report.drift_report_hash,
                    closeout_report.governance_report_hash,
                    closeout_report.validation_report_hash,
                    closeout_report.production_consumption_report_hash,
                    closeout_report.recovery_report_hash,
                    closeout_report.diagnostics_report_hash,
                    closeout_report.integrity_report_hash,
                    closeout_report.continuity_report_hash,
                )
            ),
            "closeout_hash_stable": closeout_report.deterministic_report_hash == rebuilt_hash,
            "serialization_stable": closeout_report.serialization_stable,
            "hashing_stable": closeout_report.hashing_stable,
            "visibility_preserved": closeout_report.visibility_preserved,
            "integrity_preserved": closeout_report.integrity_preserved,
            "continuity_preserved": closeout_report.continuity_preserved,
        },
        "fail_visible_guarantees": {
            finding_type: count > 0 for finding_type, count in finding_type_counts.items() if finding_type != "invalid"
        },
        "non_execution_guarantees": {
            "descriptive_only": closeout_report.descriptive_only,
            "approval_absent": not closeout_report.approval_enabled,
            "authorization_absent": not closeout_report.authorization_enabled,
            "execution_authorization_absent": not closeout_report.execution_authorized,
            "remediation_authorization_absent": not closeout_report.remediation_authorized,
            "production_consumption_disabled": not closeout_report.production_consumption_enabled,
            "orchestration_disabled": not closeout_report.orchestration_enabled,
            "planner_integration_disabled": not closeout_report.planner_integration_enabled,
            "execution_absent": not closeout_report.execution_enabled,
            "recommendation_absent": not closeout_report.recommendation_enabled,
            "ranking_absent": not closeout_report.ranking_enabled,
            "scoring_absent": not closeout_report.scoring_enabled,
            "selection_absent": not closeout_report.selection_enabled,
            "optimization_absent": not closeout_report.optimization_enabled,
            "runtime_mutation_absent": not closeout_report.runtime_mutation_enabled,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "finding_count": closeout_report.finding_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "closeout_status": closeout_report.closeout_status,
            "v4_1_readiness_status": closeout_report.v4_1_readiness_status,
            "warning_count": closeout_report.warning_count,
            "replay_safe": closeout_report.replay_safe,
            "rollback_safe": closeout_report.rollback_safe,
            "provenance_safe": closeout_report.provenance_safe,
            "lineage_safe": closeout_report.lineage_safe,
            "serialization_stable": closeout_report.serialization_stable,
            "hashing_stable": closeout_report.hashing_stable,
            "visibility_preserved": closeout_report.visibility_preserved,
            "integrity_preserved": closeout_report.integrity_preserved,
            "continuity_preserved": closeout_report.continuity_preserved,
        },
        "v4_closeout_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 10 performs deterministic closeout and v4.1 planning-readiness certification only.",
            "v4.0 Phase 10 does not authorize execution.",
            "v4.0 Phase 10 does not authorize remediation.",
            "v4.0 Phase 10 does not enable production consumption.",
            "v4.0 Phase 10 does not enable orchestration.",
            "v4.0 Phase 10 does not enable planner integration.",
            "v4.0 Phase 10 does not recommend, rank, score, select, optimize, approve, repair, execute, orchestrate, or mutate runtime state.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_v4_closeout_hash(payload)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_0_closeout_and_v4_1_readiness_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_closeout_report_hash={report['deterministic_closeout_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
