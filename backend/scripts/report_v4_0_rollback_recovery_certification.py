"""Generate deterministic v4.0 rollback and recovery certification evidence."""

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

from operational_lifecycle.production_consumption_governance import (  # noqa: E402
    evaluate_controlled_production_consumption_governance,
)
from operational_lifecycle.recovery_certification_engine import certify_rollback_recovery  # noqa: E402
from operational_lifecycle.recovery_certification_hashing import (  # noqa: E402
    deterministic_recovery_certification_hash,
)
from operational_lifecycle.recovery_certification_models import (  # noqa: E402
    RECOVERY_CERTIFICATION_FINDING_TYPES,
    V4_0_RECOVERY_CERTIFICATION_GENERATED_AT,
    V4_0_RECOVERY_CERTIFICATION_PHASE_ID,
    V4_0_RECOVERY_CERTIFICATION_STATUS_BLOCKED,
    V4_0_RECOVERY_CERTIFICATION_STATUS_STABLE,
)
from operational_lifecycle.recovery_certification_serialization import (  # noqa: E402
    export_recovery_certification_report,
)
from operational_lifecycle.recovery_certification_visibility import (  # noqa: E402
    count_recovery_finding_types,
    count_recovery_severities,
    validate_recovery_certification_visibility,
)
from scripts.report_v4_0_controlled_production_consumption_governance import (  # noqa: E402
    build_representative_controlled_production_consumption_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_rollback_recovery_certification_report.json")


def build_representative_rollback_recovery_certification_inputs():
    lifecycle_foundation, drift_report, governance_report, validation_report = (
        build_representative_controlled_production_consumption_inputs()
    )
    production_consumption_report = evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    )
    return lifecycle_foundation, drift_report, governance_report, validation_report, production_consumption_report


def build_v4_0_rollback_recovery_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    lifecycle_foundation, drift_report, governance_report, validation_report, production_consumption_report = (
        build_representative_rollback_recovery_certification_inputs()
    )
    recovery_report = certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
    )
    exported = export_recovery_certification_report(recovery_report)
    visibility_validation = validate_recovery_certification_visibility(recovery_report)
    finding_type_counts = count_recovery_finding_types(recovery_report.findings)
    severity_counts = count_recovery_severities(recovery_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_RECOVERY_CERTIFICATION_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_RECOVERY_CERTIFICATION_STATUS_BLOCKED
    )
    rebuilt_hash = certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
    ).deterministic_report_hash
    report = {
        "schema_version": "v4_0.rollback_recovery_certification_report.1",
        "generated_at": V4_0_RECOVERY_CERTIFICATION_GENERATED_AT,
        "phase_id": V4_0_RECOVERY_CERTIFICATION_PHASE_ID,
        "phase_name": "v4.0_phase_6_rollback_recovery_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic rollback and recovery certification evidence without execution",
        "certification_mode": "descriptive_only",
        "foundation_status": status,
        "lifecycle_identity": recovery_report.lifecycle_identity,
        "drift_report_hash": recovery_report.drift_report_hash,
        "governance_report_hash": recovery_report.governance_report_hash,
        "validation_report_hash": recovery_report.validation_report_hash,
        "production_consumption_report_hash": recovery_report.production_consumption_report_hash,
        "certification_state": recovery_report.certification_state,
        "finding_count": recovery_report.finding_count,
        "finding_type_counts": finding_type_counts,
        "severity_counts": severity_counts,
        "certifiable_finding_count": recovery_report.certifiable_finding_count,
        "blocked_count": recovery_report.blocked_count,
        "unsupported_count": recovery_report.unsupported_count,
        "prohibited_count": recovery_report.prohibited_count,
        "unknown_count": recovery_report.unknown_count,
        "warning_count": recovery_report.warning_count,
        "critical_count": recovery_report.critical_count,
        "replay_safety_status": recovery_report.replay_safe,
        "rollback_safety_status": recovery_report.rollback_safe,
        "provenance_safety_status": recovery_report.provenance_safe,
        "lineage_safety_status": recovery_report.lineage_safe,
        "recovery_execution_authorization_status": recovery_report.recovery_execution_authorized,
        "rollback_execution_authorization_status": recovery_report.rollback_execution_authorized,
        "deterministic_recovery_certification_report_hash": recovery_report.deterministic_report_hash,
        "implemented_recovery_certification_finding_types": list(RECOVERY_CERTIFICATION_FINDING_TYPES),
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "lifecycle_identity_preserved": bool(recovery_report.lifecycle_identity),
            "drift_report_hash_preserved": recovery_report.drift_report_hash
            == drift_report.deterministic_report_hash,
            "governance_report_hash_preserved": recovery_report.governance_report_hash
            == governance_report.deterministic_report_hash,
            "validation_report_hash_preserved": recovery_report.validation_report_hash
            == validation_report.deterministic_report_hash,
            "production_consumption_report_hash_preserved": (
                recovery_report.production_consumption_report_hash
                == production_consumption_report.deterministic_report_hash
            ),
            "recovery_execution_authorized_false": recovery_report.recovery_execution_authorized is False,
            "rollback_execution_authorized_false": recovery_report.rollback_execution_authorized is False,
            "recovery_hash_stable": recovery_report.deterministic_report_hash == rebuilt_hash,
        },
        "fail_visible_guarantees": {
            "lifecycle_recovery_visible": finding_type_counts["lifecycle_recovery_visibility"] > 0,
            "drift_recovery_visible": finding_type_counts["drift_recovery_visibility"] > 0,
            "bundle_governance_recovery_visible": (
                finding_type_counts["bundle_governance_recovery_visibility"] > 0
            ),
            "operational_validation_recovery_visible": (
                finding_type_counts["operational_validation_recovery_visibility"] > 0
            ),
            "production_consumption_recovery_visible": (
                finding_type_counts["production_consumption_recovery_visibility"] > 0
            ),
            "unsupported_recovery_visible": recovery_report.unsupported_count > 0,
            "prohibited_recovery_visible": recovery_report.prohibited_count > 0,
            "blocked_recovery_visible": recovery_report.blocked_count > 0,
            "unknown_recovery_visible": recovery_report.unknown_count > 0,
            "warning_recovery_visible": recovery_report.warning_count > 0,
            "critical_recovery_visible": recovery_report.critical_count > 0,
            "provenance_recovery_visible": finding_type_counts["provenance_recovery_continuity"] > 0,
            "lineage_recovery_visible": finding_type_counts["lineage_recovery_continuity"] > 0,
            "replay_recovery_visible": finding_type_counts["replay_recovery_continuity"] > 0,
            "rollback_recovery_visible": finding_type_counts["rollback_recovery_continuity"] > 0,
            "recovery_certification_readiness_visible": (
                finding_type_counts["recovery_certification_readiness"] > 0
            ),
            "rollback_execution_prohibition_visible": finding_type_counts["rollback_execution_prohibited"] > 0,
            "recovery_execution_prohibition_visible": finding_type_counts["recovery_execution_prohibited"] > 0,
        },
        "non_execution_guarantees": {
            "descriptive_only": recovery_report.descriptive_only,
            "approval_absent": not recovery_report.approval_enabled,
            "authorization_absent": not recovery_report.authorization_enabled,
            "remediation_absent": not recovery_report.remediation_enabled,
            "recovery_execution_absent": not recovery_report.recovery_execution_enabled,
            "rollback_execution_absent": not recovery_report.rollback_execution_enabled,
            "execution_absent": not recovery_report.execution_enabled,
            "routing_absent": not recovery_report.routing_enabled,
            "scheduling_absent": not recovery_report.scheduling_enabled,
            "dispatch_absent": not recovery_report.dispatch_enabled,
            "orchestration_execution_absent": not recovery_report.orchestration_execution_enabled,
            "runtime_mutation_absent": not recovery_report.runtime_mutation_enabled,
            "production_consumption_authorized": recovery_report.production_consumption_authorized,
            "recovery_execution_authorized": recovery_report.recovery_execution_authorized,
            "rollback_execution_authorized": recovery_report.rollback_execution_authorized,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "finding_count": recovery_report.finding_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "certification_state": recovery_report.certification_state,
            "replay_safe": recovery_report.replay_safe,
            "rollback_safe": recovery_report.rollback_safe,
            "provenance_safe": recovery_report.provenance_safe,
            "lineage_safe": recovery_report.lineage_safe,
            "recovery_execution_authorized": recovery_report.recovery_execution_authorized,
            "rollback_execution_authorized": recovery_report.rollback_execution_authorized,
        },
        "recovery_certification_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 6 certifies rollback and recovery evidence visibility only.",
            "v4.0 Phase 6 does not execute recovery.",
            "v4.0 Phase 6 does not execute rollback.",
            "v4.0 Phase 6 does not remediate, repair, authorize, route, schedule, dispatch, orchestrate, optimize, recommend, rank, score, select, or mutate runtime state.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_recovery_certification_hash(payload)


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
    report = build_v4_0_rollback_recovery_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_recovery_certification_report_hash={report['deterministic_recovery_certification_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
