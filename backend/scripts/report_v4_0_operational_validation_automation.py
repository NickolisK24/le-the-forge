"""Generate deterministic v4.0 operational validation automation evidence."""

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

from operational_lifecycle.bundle_governance_audit import (  # noqa: E402
    audit_trusted_bundle_lifecycle_governance,
)
from operational_lifecycle.validation_automation_engine import (  # noqa: E402
    build_operational_validation_report,
)
from operational_lifecycle.validation_automation_hashing import (  # noqa: E402
    deterministic_operational_validation_hash,
)
from operational_lifecycle.validation_automation_models import (  # noqa: E402
    OPERATIONAL_VALIDATION_FINDING_TYPES,
    V4_0_OPERATIONAL_VALIDATION_AUTOMATION_GENERATED_AT,
    V4_0_OPERATIONAL_VALIDATION_AUTOMATION_PHASE_ID,
    V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_BLOCKED,
    V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_STABLE,
)
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    export_operational_validation_report,
)
from operational_lifecycle.validation_automation_visibility import (  # noqa: E402
    count_validation_finding_types,
    count_validation_severities,
    validate_operational_validation_visibility,
)
from scripts.report_v4_0_trusted_bundle_lifecycle_governance import (  # noqa: E402
    build_representative_trusted_bundle_governance_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_operational_validation_automation_report.json")


def build_representative_operational_validation_inputs():
    (
        bundle_identity,
        trust_status,
        validation_status,
        support_status,
        blocked_domains,
        lifecycle_foundation,
        drift_report,
    ) = build_representative_trusted_bundle_governance_inputs()
    governance_report = audit_trusted_bundle_lifecycle_governance(
        bundle_identity=bundle_identity,
        trust_status=trust_status,
        validation_status=validation_status,
        support_status=support_status,
        blocked_domains=blocked_domains,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
    )
    return lifecycle_foundation, drift_report, governance_report


def build_v4_0_operational_validation_automation_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    lifecycle_foundation, drift_report, governance_report = build_representative_operational_validation_inputs()
    validation_report = build_operational_validation_report(lifecycle_foundation, drift_report, governance_report)
    exported = export_operational_validation_report(validation_report)
    visibility_validation = validate_operational_validation_visibility(validation_report)
    finding_type_counts = count_validation_finding_types(validation_report.findings)
    severity_counts = count_validation_severities(validation_report.findings)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_BLOCKED
    )
    report = {
        "schema_version": "v4_0.operational_validation_automation_report.1",
        "generated_at": V4_0_OPERATIONAL_VALIDATION_AUTOMATION_GENERATED_AT,
        "phase_id": V4_0_OPERATIONAL_VALIDATION_AUTOMATION_PHASE_ID,
        "phase_name": "v4.0_phase_4_operational_validation_automation",
        "repo_root": str(root),
        "architectural_purpose": "deterministic operational validation evidence generation without execution",
        "validation_mode": "descriptive_only",
        "foundation_status": status,
        "lifecycle_identity": validation_report.lifecycle_identity,
        "drift_report_hash": validation_report.drift_report_hash,
        "governance_report_hash": validation_report.governance_report_hash,
        "validation_state": validation_report.validation_state,
        "total_findings": validation_report.finding_count,
        "finding_type_counts": finding_type_counts,
        "severity_counts": severity_counts,
        "unsupported_count": validation_report.unsupported_count,
        "prohibited_count": validation_report.prohibited_count,
        "blocked_count": validation_report.blocked_count,
        "unknown_count": validation_report.unknown_count,
        "warning_count": validation_report.warning_count,
        "critical_count": validation_report.critical_count,
        "replay_safety_status": validation_report.replay_safe,
        "rollback_safety_status": validation_report.rollback_safe,
        "provenance_safety_status": validation_report.provenance_safe,
        "lineage_safety_status": validation_report.lineage_safe,
        "operational_execution_authorization_status": validation_report.operational_execution_authorized,
        "operational_certification_readiness_visibility": (
            finding_type_counts["operational_certification_readiness"] > 0
        ),
        "deterministic_validation_report_hash": validation_report.deterministic_report_hash,
        "implemented_validation_finding_types": list(OPERATIONAL_VALIDATION_FINDING_TYPES),
        "deterministic_guarantees": {
            "stable_finding_order": [finding["deterministic_key"] for finding in exported["findings"]]
            == sorted(finding["deterministic_key"] for finding in exported["findings"]),
            "lifecycle_identity_preserved": bool(validation_report.lifecycle_identity),
            "drift_report_hash_preserved": validation_report.drift_report_hash
            == drift_report.deterministic_report_hash,
            "governance_report_hash_preserved": validation_report.governance_report_hash
            == governance_report.deterministic_report_hash,
            "operational_execution_authorized_false": (
                validation_report.operational_execution_authorized is False
            ),
            "validation_hash_stable": validation_report.deterministic_report_hash
            == build_operational_validation_report(lifecycle_foundation, drift_report, governance_report).deterministic_report_hash,
        },
        "fail_visible_guarantees": {
            "unsupported_validation_visible": validation_report.unsupported_count > 0,
            "prohibited_validation_visible": validation_report.prohibited_count > 0,
            "blocked_validation_visible": validation_report.blocked_count > 0,
            "unknown_validation_visible": validation_report.unknown_count > 0,
            "warning_validation_visible": validation_report.warning_count > 0,
            "critical_validation_visible": validation_report.critical_count > 0,
            "lifecycle_validation_visible": finding_type_counts["lifecycle_validation_visibility"] > 0,
            "drift_validation_visible": finding_type_counts["drift_validation_visibility"] > 0,
            "governance_validation_visible": finding_type_counts["governance_validation_visibility"] > 0,
            "provenance_validation_visible": finding_type_counts["provenance_validation_visibility"] > 0,
            "lineage_validation_visible": finding_type_counts["lineage_validation_visibility"] > 0,
            "replay_validation_visible": finding_type_counts["replay_validation_visibility"] > 0,
            "rollback_validation_visible": finding_type_counts["rollback_validation_visibility"] > 0,
            "operational_execution_prohibition_visible": (
                finding_type_counts["operational_execution_prohibited"] > 0
            ),
            "operational_certification_readiness_visible": (
                finding_type_counts["operational_certification_readiness"] > 0
            ),
        },
        "non_execution_guarantees": {
            "descriptive_only": validation_report.descriptive_only,
            "approval_absent": not validation_report.approval_enabled,
            "authorization_absent": not validation_report.authorization_enabled,
            "deployment_absent": not validation_report.deployment_enabled,
            "remediation_absent": not validation_report.remediation_enabled,
            "execution_absent": not validation_report.execution_enabled,
            "routing_absent": not validation_report.routing_enabled,
            "scheduling_absent": not validation_report.scheduling_enabled,
            "dispatch_absent": not validation_report.dispatch_enabled,
            "orchestration_execution_absent": not validation_report.orchestration_execution_enabled,
            "runtime_mutation_absent": not validation_report.runtime_mutation_enabled,
            "production_consumption_authorized": validation_report.production_consumption_authorized,
            "operational_execution_authorized": validation_report.operational_execution_authorized,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "total_findings": validation_report.finding_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "validation_state": validation_report.validation_state,
            "replay_safe": validation_report.replay_safe,
            "rollback_safe": validation_report.rollback_safe,
            "provenance_safe": validation_report.provenance_safe,
            "lineage_safe": validation_report.lineage_safe,
            "operational_execution_authorized": validation_report.operational_execution_authorized,
        },
        "validation_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 4 automates deterministic validation evidence generation only.",
            "v4.0 Phase 4 does not authorize operational execution.",
            "v4.0 Phase 4 does not authorize deployment or production consumption.",
            "v4.0 Phase 4 does not remediate, route, schedule, dispatch, orchestrate, optimize, recommend, rank, score, select, or mutate lifecycle evidence.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_operational_validation_hash(payload)


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
    report = build_v4_0_operational_validation_automation_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_validation_report_hash={report['deterministic_validation_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
