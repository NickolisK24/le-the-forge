"""Generate deterministic v4.0 controlled production consumption governance evidence."""

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
from operational_lifecycle.production_consumption_hashing import (  # noqa: E402
    deterministic_production_consumption_hash,
)
from operational_lifecycle.production_consumption_models import (  # noqa: E402
    PRODUCTION_CONSUMPTION_GATE_TYPES,
    V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_GENERATED_AT,
    V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_PHASE_ID,
    V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_BLOCKED,
    V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_STABLE,
)
from operational_lifecycle.production_consumption_serialization import (  # noqa: E402
    export_production_consumption_governance_report,
)
from operational_lifecycle.production_consumption_visibility import (  # noqa: E402
    count_production_consumption_gate_states,
    count_production_consumption_gate_types,
    count_production_consumption_severities,
    validate_production_consumption_visibility,
)
from operational_lifecycle.validation_automation_engine import build_operational_validation_report  # noqa: E402
from scripts.report_v4_0_operational_validation_automation import (  # noqa: E402
    build_representative_operational_validation_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_controlled_production_consumption_governance_report.json")


def build_representative_controlled_production_consumption_inputs():
    lifecycle_foundation, drift_report, governance_report = build_representative_operational_validation_inputs()
    validation_report = build_operational_validation_report(lifecycle_foundation, drift_report, governance_report)
    return lifecycle_foundation, drift_report, governance_report, validation_report


def build_v4_0_controlled_production_consumption_governance_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    lifecycle_foundation, drift_report, governance_report, validation_report = (
        build_representative_controlled_production_consumption_inputs()
    )
    production_report = evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    )
    exported = export_production_consumption_governance_report(production_report)
    visibility_validation = validate_production_consumption_visibility(production_report)
    gate_type_counts = count_production_consumption_gate_types(production_report.gates)
    gate_state_counts = count_production_consumption_gate_states(production_report.gates)
    severity_counts = count_production_consumption_severities(production_report.gates)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_STATUS_BLOCKED
    )
    rebuilt_hash = evaluate_controlled_production_consumption_governance(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
    ).deterministic_report_hash
    report = {
        "schema_version": "v4_0.controlled_production_consumption_governance_report.1",
        "generated_at": V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_GENERATED_AT,
        "phase_id": V4_0_PRODUCTION_CONSUMPTION_GOVERNANCE_PHASE_ID,
        "phase_name": "v4.0_phase_5_controlled_production_consumption_governance",
        "repo_root": str(root),
        "architectural_purpose": "deterministic production consumption evidence gates without activation",
        "governance_mode": "descriptive_only",
        "foundation_status": status,
        "lifecycle_identity": production_report.lifecycle_identity,
        "drift_report_hash": production_report.drift_report_hash,
        "governance_report_hash": production_report.governance_report_hash,
        "validation_report_hash": production_report.validation_report_hash,
        "gate_count": production_report.gate_count,
        "gate_type_counts": gate_type_counts,
        "gate_state_counts": gate_state_counts,
        "severity_counts": severity_counts,
        "satisfied_gate_count": production_report.satisfied_gate_count,
        "blocked_gate_count": production_report.blocked_gate_count,
        "unsupported_gate_count": production_report.unsupported_gate_count,
        "prohibited_gate_count": production_report.prohibited_gate_count,
        "unknown_gate_count": production_report.unknown_gate_count,
        "warning_count": production_report.warning_count,
        "critical_count": production_report.critical_count,
        "replay_safety_status": production_report.replay_safe,
        "rollback_safety_status": production_report.rollback_safe,
        "provenance_safety_status": production_report.provenance_safe,
        "lineage_safety_status": production_report.lineage_safe,
        "production_consumption_authorization_status": production_report.production_consumption_authorized,
        "production_consumption_enabled_status": production_report.production_consumption_enabled,
        "planner_behavior_changed": production_report.planner_behavior_changed,
        "deterministic_production_consumption_report_hash": production_report.deterministic_report_hash,
        "implemented_production_consumption_gate_types": list(PRODUCTION_CONSUMPTION_GATE_TYPES),
        "deterministic_guarantees": {
            "stable_gate_order": [gate["deterministic_key"] for gate in exported["gates"]]
            == sorted(gate["deterministic_key"] for gate in exported["gates"]),
            "lifecycle_identity_preserved": bool(production_report.lifecycle_identity),
            "drift_report_hash_preserved": production_report.drift_report_hash
            == drift_report.deterministic_report_hash,
            "governance_report_hash_preserved": production_report.governance_report_hash
            == governance_report.deterministic_report_hash,
            "validation_report_hash_preserved": production_report.validation_report_hash
            == validation_report.deterministic_report_hash,
            "production_consumption_authorized_false": (
                production_report.production_consumption_authorized is False
            ),
            "production_consumption_enabled_false": production_report.production_consumption_enabled is False,
            "planner_behavior_unchanged": production_report.planner_behavior_changed is False,
            "production_consumption_hash_stable": production_report.deterministic_report_hash == rebuilt_hash,
        },
        "fail_visible_guarantees": {
            "lifecycle_gate_visible": gate_type_counts["lifecycle_evidence_gate"] > 0,
            "drift_gate_visible": gate_type_counts["drift_evidence_gate"] > 0,
            "governance_gate_visible": gate_type_counts["bundle_governance_gate"] > 0,
            "validation_gate_visible": gate_type_counts["operational_validation_gate"] > 0,
            "unsupported_gate_visible": production_report.unsupported_gate_count > 0,
            "prohibited_gate_visible": production_report.prohibited_gate_count > 0,
            "blocked_gate_visible": production_report.blocked_gate_count > 0,
            "unknown_gate_visible": production_report.unknown_gate_count > 0,
            "warning_gate_visible": production_report.warning_count > 0,
            "critical_gate_visible": production_report.critical_count > 0,
            "provenance_gate_visible": gate_type_counts["provenance_continuity_gate"] > 0,
            "lineage_gate_visible": gate_type_counts["lineage_continuity_gate"] > 0,
            "replay_gate_visible": gate_type_counts["replay_continuity_gate"] > 0,
            "rollback_gate_visible": gate_type_counts["rollback_continuity_gate"] > 0,
            "production_consumption_prohibition_visible": (
                gate_type_counts["production_consumption_prohibition_gate"] > 0
            ),
            "production_consumption_readiness_limitations_visible": (
                gate_type_counts["production_consumption_readiness_gate"] > 0
            ),
        },
        "non_execution_guarantees": {
            "descriptive_only": production_report.descriptive_only,
            "approval_absent": not production_report.approval_enabled,
            "authorization_absent": not production_report.authorization_enabled,
            "deployment_absent": not production_report.deployment_enabled,
            "remediation_absent": not production_report.remediation_enabled,
            "execution_absent": not production_report.execution_enabled,
            "routing_absent": not production_report.routing_enabled,
            "scheduling_absent": not production_report.scheduling_enabled,
            "dispatch_absent": not production_report.dispatch_enabled,
            "orchestration_execution_absent": not production_report.orchestration_execution_enabled,
            "runtime_mutation_absent": not production_report.runtime_mutation_enabled,
            "production_bundle_consumption_absent": not production_report.production_bundle_consumption_enabled,
            "planner_integration_absent": not production_report.planner_integration_enabled,
            "planner_behavior_unchanged": not production_report.planner_behavior_changed,
            "production_consumption_authorized": production_report.production_consumption_authorized,
            "production_consumption_enabled": production_report.production_consumption_enabled,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "gate_count": production_report.gate_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "replay_safe": production_report.replay_safe,
            "rollback_safe": production_report.rollback_safe,
            "provenance_safe": production_report.provenance_safe,
            "lineage_safe": production_report.lineage_safe,
            "production_consumption_authorized": production_report.production_consumption_authorized,
            "production_consumption_enabled": production_report.production_consumption_enabled,
            "planner_behavior_changed": production_report.planner_behavior_changed,
        },
        "production_consumption_governance_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 5 models production consumption gates and blockers only.",
            "v4.0 Phase 5 does not authorize production consumption.",
            "v4.0 Phase 5 does not enable production consumption.",
            "v4.0 Phase 5 does not load trusted bundles into production planners.",
            "v4.0 Phase 5 does not change planner behavior.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_production_consumption_hash(payload)


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
    report = build_v4_0_controlled_production_consumption_governance_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(
        "deterministic_production_consumption_report_hash="
        f"{report['deterministic_production_consumption_report_hash']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
