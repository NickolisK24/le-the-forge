"""Generate deterministic v4.0 operational explainability diagnostics evidence."""

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
from operational_lifecycle.diagnostics_hashing import deterministic_operational_diagnostics_hash  # noqa: E402
from operational_lifecycle.diagnostics_models import (  # noqa: E402
    OPERATIONAL_DIAGNOSTIC_CATEGORIES,
    OPERATIONAL_DIAGNOSTIC_TYPES,
    V4_0_OPERATIONAL_DIAGNOSTICS_GENERATED_AT,
    V4_0_OPERATIONAL_DIAGNOSTICS_PHASE_ID,
    V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_BLOCKED,
    V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_STABLE,
)
from operational_lifecycle.diagnostics_serialization import export_operational_diagnostics_report  # noqa: E402
from operational_lifecycle.diagnostics_visibility import (  # noqa: E402
    count_diagnostic_categories,
    count_diagnostic_severities,
    count_diagnostic_types,
    validate_operational_diagnostics_visibility,
)
from operational_lifecycle.lifecycle_identity import lifecycle_identity_key  # noqa: E402
from operational_lifecycle.recovery_certification_engine import certify_rollback_recovery  # noqa: E402
from scripts.report_v4_0_rollback_recovery_certification import (  # noqa: E402
    build_representative_rollback_recovery_certification_inputs,
)


REPORT_PATH = Path("docs/generated/v4_0_operational_explainability_diagnostics_report.json")


def build_representative_operational_diagnostics_inputs():
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
    return (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )


def build_v4_0_operational_explainability_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
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
    exported = export_operational_diagnostics_report(diagnostics_report)
    visibility_validation = validate_operational_diagnostics_visibility(diagnostics_report)
    category_counts = count_diagnostic_categories(diagnostics_report.entries)
    diagnostic_type_counts = count_diagnostic_types(diagnostics_report.entries)
    severity_counts = count_diagnostic_severities(diagnostics_report.entries)
    validation_error_count = 0 if visibility_validation["valid"] else 1
    status = (
        V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_STABLE
        if validation_error_count == 0
        else V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_BLOCKED
    )
    rebuilt_hash = build_operational_diagnostics_report(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    ).deterministic_report_hash
    report = {
        "schema_version": "v4_0.operational_explainability_diagnostics_report.1",
        "generated_at": V4_0_OPERATIONAL_DIAGNOSTICS_GENERATED_AT,
        "phase_id": V4_0_OPERATIONAL_DIAGNOSTICS_PHASE_ID,
        "phase_name": "v4.0_phase_7_operational_explainability_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic human-readable operational diagnostics without recommendations or execution",
        "diagnostics_mode": "descriptive_only",
        "foundation_status": status,
        "lifecycle_identity": diagnostics_report.lifecycle_identity,
        "drift_report_hash": diagnostics_report.drift_report_hash,
        "governance_report_hash": diagnostics_report.governance_report_hash,
        "validation_report_hash": diagnostics_report.validation_report_hash,
        "production_consumption_report_hash": diagnostics_report.production_consumption_report_hash,
        "recovery_report_hash": diagnostics_report.recovery_report_hash,
        "diagnostic_entry_count": diagnostics_report.entry_count,
        "category_counts": category_counts,
        "diagnostic_type_counts": diagnostic_type_counts,
        "severity_counts": severity_counts,
        "unsupported_count": diagnostics_report.unsupported_count,
        "prohibited_count": diagnostics_report.prohibited_count,
        "blocked_count": diagnostics_report.blocked_count,
        "unknown_count": diagnostics_report.unknown_count,
        "warning_count": diagnostics_report.warning_count,
        "critical_count": diagnostics_report.critical_count,
        "replay_safety_status": diagnostics_report.replay_safe,
        "rollback_safety_status": diagnostics_report.rollback_safe,
        "provenance_safety_status": diagnostics_report.provenance_safe,
        "lineage_safety_status": diagnostics_report.lineage_safe,
        "recommendations_present_status": diagnostics_report.recommendations_present,
        "execution_authorized_status": diagnostics_report.execution_authorized,
        "deterministic_diagnostics_report_hash": diagnostics_report.deterministic_report_hash,
        "implemented_diagnostic_categories": list(OPERATIONAL_DIAGNOSTIC_CATEGORIES),
        "implemented_diagnostic_types": list(OPERATIONAL_DIAGNOSTIC_TYPES),
        "deterministic_guarantees": {
            "stable_entry_order": [entry["deterministic_key"] for entry in exported["entries"]]
            == sorted(entry["deterministic_key"] for entry in exported["entries"]),
            "lifecycle_identity_preserved": diagnostics_report.lifecycle_identity
            == lifecycle_identity_key(lifecycle_foundation.patch_identity),
            "drift_report_hash_preserved": diagnostics_report.drift_report_hash
            == drift_report.deterministic_report_hash,
            "governance_report_hash_preserved": diagnostics_report.governance_report_hash
            == governance_report.deterministic_report_hash,
            "validation_report_hash_preserved": diagnostics_report.validation_report_hash
            == validation_report.deterministic_report_hash,
            "production_consumption_report_hash_preserved": (
                diagnostics_report.production_consumption_report_hash
                == production_consumption_report.deterministic_report_hash
            ),
            "recovery_report_hash_preserved": diagnostics_report.recovery_report_hash
            == recovery_report.deterministic_report_hash,
            "diagnostics_hash_stable": diagnostics_report.deterministic_report_hash == rebuilt_hash,
            "recommendations_present_false": diagnostics_report.recommendations_present is False,
            "execution_authorized_false": diagnostics_report.execution_authorized is False,
        },
        "fail_visible_guarantees": {
            "lifecycle_diagnostic_visible": category_counts["lifecycle"] > 0,
            "drift_diagnostic_visible": category_counts["drift"] > 0,
            "bundle_governance_diagnostic_visible": category_counts["bundle_governance"] > 0,
            "validation_diagnostic_visible": category_counts["validation"] > 0,
            "production_consumption_diagnostic_visible": category_counts["production_consumption"] > 0,
            "recovery_diagnostic_visible": category_counts["recovery"] > 0,
            "provenance_diagnostic_visible": category_counts["provenance"] > 0,
            "lineage_diagnostic_visible": category_counts["lineage"] > 0,
            "replay_diagnostic_visible": category_counts["replay"] > 0,
            "rollback_diagnostic_visible": category_counts["rollback"] > 0,
            "unsupported_diagnostic_visible": diagnostics_report.unsupported_count > 0,
            "prohibited_diagnostic_visible": diagnostics_report.prohibited_count > 0,
            "blocked_diagnostic_visible": diagnostics_report.blocked_count > 0,
            "unknown_diagnostic_visible": diagnostics_report.unknown_count > 0,
            "warning_diagnostic_visible": diagnostics_report.warning_count > 0,
            "critical_diagnostic_visible": diagnostics_report.critical_count > 0,
            "execution_boundary_diagnostic_visible": category_counts["execution_boundary"] > 0,
        },
        "non_execution_guarantees": {
            "descriptive_only": diagnostics_report.descriptive_only,
            "recommendations_present": diagnostics_report.recommendations_present,
            "ranking_absent": not diagnostics_report.ranking_enabled,
            "scoring_absent": not diagnostics_report.scoring_enabled,
            "selection_absent": not diagnostics_report.selection_enabled,
            "optimization_absent": not diagnostics_report.optimization_enabled,
            "approval_absent": not diagnostics_report.approval_enabled,
            "authorization_absent": not diagnostics_report.authorization_enabled,
            "remediation_absent": not diagnostics_report.remediation_enabled,
            "execution_authorized": diagnostics_report.execution_authorized,
            "execution_absent": not diagnostics_report.execution_enabled,
            "orchestration_execution_absent": not diagnostics_report.orchestration_execution_enabled,
            "runtime_mutation_absent": not diagnostics_report.runtime_mutation_enabled,
        },
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "entry_count": diagnostics_report.entry_count,
            "visibility_validation_passed": visibility_validation["valid"],
            "capability_enabled_count": visibility_validation["capability_enabled_count"],
            "replay_safe": diagnostics_report.replay_safe,
            "rollback_safe": diagnostics_report.rollback_safe,
            "provenance_safe": diagnostics_report.provenance_safe,
            "lineage_safe": diagnostics_report.lineage_safe,
            "recommendations_present": diagnostics_report.recommendations_present,
            "execution_authorized": diagnostics_report.execution_authorized,
        },
        "operational_diagnostics_report": exported,
        "explicit_limitations": [
            "v4.0 Phase 7 explains operational evidence only.",
            "v4.0 Phase 7 does not generate recommendations.",
            "v4.0 Phase 7 does not authorize execution.",
            "v4.0 Phase 7 does not remediate, approve, route, schedule, dispatch, orchestrate, optimize, rank, score, select, execute, or mutate runtime state.",
        ],
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_operational_diagnostics_hash(payload)


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
    report = build_v4_0_operational_explainability_diagnostics_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_diagnostics_report_hash={report['deterministic_diagnostics_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
