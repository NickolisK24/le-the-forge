"""Generate deterministic v4.0 operational lifecycle integrity enforcement evidence."""

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

from operational_lifecycle.diagnostics_engine import build_operational_diagnostics_report  # noqa: E402
from operational_lifecycle.integrity_enforcement_audit import audit_operational_lifecycle_integrity  # noqa: E402
from operational_lifecycle.integrity_enforcement_hashing import deterministic_operational_integrity_hash  # noqa: E402
from operational_lifecycle.integrity_enforcement_models import (  # noqa: E402
    OPERATIONAL_INTEGRITY_FINDING_TYPES,
    V4_0_INTEGRITY_ENFORCEMENT_GENERATED_AT,
    V4_0_INTEGRITY_ENFORCEMENT_PHASE_ID,
    V4_0_INTEGRITY_ENFORCEMENT_STATUS_BLOCKED,
    V4_0_INTEGRITY_ENFORCEMENT_STATUS_STABLE,
)
from operational_lifecycle.integrity_enforcement_serialization import export_operational_integrity_report  # noqa: E402
from operational_lifecycle.integrity_enforcement_visibility import (  # noqa: E402
    count_integrity_finding_types,
    count_integrity_severities,
    validate_operational_integrity_visibility,
)
from scripts.report_v4_0_operational_explainability_diagnostics import (  # noqa: E402
    build_representative_operational_diagnostics_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_operational_lifecycle_integrity_enforcement_report.json")


def build_representative_operational_integrity_inputs():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    ) = build_representative_operational_diagnostics_inputs()
    diagnostics_report = build_operational_diagnostics_report(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )
    return (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )


def build_v4_0_operational_lifecycle_integrity_enforcement_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    inputs = build_representative_operational_integrity_inputs()
    integrity_report = audit_operational_lifecycle_integrity(*inputs)
    exported = export_operational_integrity_report(integrity_report)
    visibility_validation = validate_operational_integrity_visibility(integrity_report)
    finding_type_counts = count_integrity_finding_types(integrity_report.findings)
    severity_counts = count_integrity_severities(integrity_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_INTEGRITY_ENFORCEMENT_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_INTEGRITY_ENFORCEMENT_STATUS_BLOCKED
    )
    rebuilt_hash = audit_operational_lifecycle_integrity(*inputs).deterministic_report_hash
    leakage_booleans = {
        "execution_leakage_detected": integrity_report.execution_leakage_detected,
        "orchestration_leakage_detected": integrity_report.orchestration_leakage_detected,
        "remediation_leakage_detected": integrity_report.remediation_leakage_detected,
        "recommendation_leakage_detected": integrity_report.recommendation_leakage_detected,
        "ranking_leakage_detected": integrity_report.ranking_leakage_detected,
        "scoring_leakage_detected": integrity_report.scoring_leakage_detected,
        "selection_leakage_detected": integrity_report.selection_leakage_detected,
        "approval_leakage_detected": integrity_report.approval_leakage_detected,
        "authorization_leakage_detected": integrity_report.authorization_leakage_detected,
        "mutation_leakage_detected": integrity_report.mutation_leakage_detected,
        "production_consumption_leakage_detected": (
            integrity_report.production_consumption_leakage_detected
        ),
        "planner_integration_leakage_detected": integrity_report.planner_integration_leakage_detected,
    }
    report = {
        "schema_version": "v4_0.operational_lifecycle_integrity_enforcement_report.1",
        "generated_at": V4_0_INTEGRITY_ENFORCEMENT_GENERATED_AT,
        "phase_id": V4_0_INTEGRITY_ENFORCEMENT_PHASE_ID,
        "phase_name": "v4.0_phase_8_operational_lifecycle_integrity_enforcement",
        "repo_root": str(root),
        "architectural_purpose": "deterministic operational lifecycle integrity enforcement without remediation",
        "integrity_mode": "descriptive_audit_only",
        "foundation_status": status,
        "lifecycle_identity": integrity_report.lifecycle_identity,
        "drift_report_hash": integrity_report.drift_report_hash,
        "governance_report_hash": integrity_report.governance_report_hash,
        "validation_report_hash": integrity_report.validation_report_hash,
        "production_consumption_report_hash": integrity_report.production_consumption_report_hash,
        "recovery_report_hash": integrity_report.recovery_report_hash,
        "diagnostics_report_hash": integrity_report.diagnostics_report_hash,
        "integrity_status": integrity_report.integrity_status,
        "finding_count": integrity_report.finding_count,
        "finding_type_counts": finding_type_counts,
        "severity_counts": severity_counts,
        "violation_count": integrity_report.violation_count,
        "warning_count": integrity_report.warning_count,
        "blocked_count": integrity_report.blocked_count,
        "prohibited_count": integrity_report.prohibited_count,
        "unknown_count": integrity_report.unknown_count,
        "critical_count": integrity_report.critical_count,
        "leakage_booleans": leakage_booleans,
        "replay_safety_status": integrity_report.replay_safe,
        "rollback_safety_status": integrity_report.rollback_safe,
        "provenance_safety_status": integrity_report.provenance_safe,
        "lineage_safety_status": integrity_report.lineage_safe,
        "integrity_enforcement_performed_status": integrity_report.integrity_enforcement_performed,
        "deterministic_integrity_report_hash": integrity_report.deterministic_report_hash,
        "implemented_integrity_finding_types": list(OPERATIONAL_INTEGRITY_FINDING_TYPES),
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "all_report_hashes_preserved": all(
                bool(value)
                for value in (
                    integrity_report.drift_report_hash,
                    integrity_report.governance_report_hash,
                    integrity_report.validation_report_hash,
                    integrity_report.production_consumption_report_hash,
                    integrity_report.recovery_report_hash,
                    integrity_report.diagnostics_report_hash,
                )
            ),
            "integrity_hash_stable": integrity_report.deterministic_report_hash == rebuilt_hash,
            "integrity_enforcement_performed_true": integrity_report.integrity_enforcement_performed is True,
            "all_leakage_booleans_false": not any(leakage_booleans.values()),
        },
        "fail_visible_guarantees": {
            finding_type: count > 0 for finding_type, count in finding_type_counts.items() if finding_type != "invalid"
        },
        "non_execution_guarantees": {
            "descriptive_only": integrity_report.descriptive_only,
            "correction_absent": not integrity_report.correction_enabled,
            "remediation_absent": not integrity_report.remediation_enabled,
            "repair_absent": not integrity_report.repair_enabled,
            "approval_absent": not integrity_report.approval_enabled,
            "authorization_absent": not integrity_report.authorization_enabled,
            "execution_absent": not integrity_report.execution_enabled,
            "orchestration_execution_absent": not integrity_report.orchestration_execution_enabled,
            "recommendation_absent": not integrity_report.recommendation_enabled,
            "ranking_absent": not integrity_report.ranking_enabled,
            "scoring_absent": not integrity_report.scoring_enabled,
            "selection_absent": not integrity_report.selection_enabled,
            "optimization_absent": not integrity_report.optimization_enabled,
            "runtime_mutation_absent": not integrity_report.runtime_mutation_enabled,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "finding_count": integrity_report.finding_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "integrity_status": integrity_report.integrity_status,
            "violation_count": integrity_report.violation_count,
            "replay_safe": integrity_report.replay_safe,
            "rollback_safe": integrity_report.rollback_safe,
            "provenance_safe": integrity_report.provenance_safe,
            "lineage_safe": integrity_report.lineage_safe,
            "integrity_enforcement_performed": integrity_report.integrity_enforcement_performed,
        },
        "operational_integrity_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 8 performs deterministic integrity audit only.",
            "v4.0 Phase 8 does not remediate integrity findings.",
            "v4.0 Phase 8 does not authorize execution.",
            "v4.0 Phase 8 does not enable production consumption.",
            "v4.0 Phase 8 does not recommend, rank, score, select, optimize, approve, repair, execute, orchestrate, or mutate runtime state.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_operational_integrity_hash(payload)


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
    report = build_v4_0_operational_lifecycle_integrity_enforcement_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_integrity_report_hash={report['deterministic_integrity_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
