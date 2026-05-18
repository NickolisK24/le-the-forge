"""Generate deterministic v4.5A.6 drift diagnostics aggregation visibility."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from orchestration_governance.v4_5a_6_drift_diagnostics_aggregation_audit import (  # noqa: E402
    build_v4_5a_6_drift_diagnostics_aggregation_report,
)


REPORT_PATH = Path("docs/generated/v4_5a_6_drift_diagnostics_aggregation_report.json")


def write_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.5A.6 drift diagnostics aggregation JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5a_6_drift_diagnostics_aggregation_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(
        "diagnostic_aggregation_record_count="
        f"{summary['diagnostic_aggregation_record_count']}"
    )
    print(f"diagnostic_source_count={summary['diagnostic_source_count']}")
    print(f"unsupported_state_summary_count={summary['unsupported_state_summary_count']}")
    print(f"evidence_gap_summary_count={summary['evidence_gap_summary_count']}")
    print(f"continuity_gap_summary_count={summary['continuity_gap_summary_count']}")
    print(f"severity_summary_count={summary['severity_summary_count']}")
    print(f"blocker_warning_summary_count={summary['blocker_warning_summary_count']}")
    print(f"aggregated_diagnostic_count={summary['aggregated_diagnostic_count']}")
    print(
        "unsupported_aggregation_state_count="
        f"{summary['unsupported_aggregation_state_count']}"
    )
    print(
        "deterministic_serialization_verified="
        f"{summary['deterministic_serialization_verified']}"
    )
    print(f"deterministic_hashing_verified={summary['deterministic_hashing_verified']}")
    print(
        "diagnostic_source_aggregation_stable="
        f"{summary['diagnostic_source_aggregation_stable']}"
    )
    print(
        "unsupported_state_visibility_preserved="
        f"{summary['unsupported_state_visibility_preserved']}"
    )
    print(
        "evidence_gap_visibility_preserved="
        f"{summary['evidence_gap_visibility_preserved']}"
    )
    print(
        "continuity_gap_visibility_preserved="
        f"{summary['continuity_gap_visibility_preserved']}"
    )
    print(f"severity_summary_stable={summary['severity_summary_stable']}")
    print(f"blocker_warning_summary_stable={summary['blocker_warning_summary_stable']}")
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(f"continuity_reference_preserved={summary['continuity_reference_preserved']}")
    print(
        "fail_visible_aggregation_diagnostics_verified="
        f"{summary['fail_visible_aggregation_diagnostics_verified']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"inherited_prohibition_count={summary['inherited_prohibition_count']}")
    print(f"inherited_constraint_count={summary['inherited_constraint_count']}")
    print(f"explicit_limitation_count={summary['explicit_limitation_count']}")
    print(f"validation_error_count={summary['validation_error_count']}")
    print(f"enabled_runtime_execution_count={summary['enabled_runtime_execution_count']}")
    print(
        "enabled_orchestration_authorization_count="
        f"{summary['enabled_orchestration_authorization_count']}"
    )
    print(
        "enabled_orchestration_approval_count="
        f"{summary['enabled_orchestration_approval_count']}"
    )
    print(
        "enabled_orchestration_dispatch_count="
        f"{summary['enabled_orchestration_dispatch_count']}"
    )
    print(
        "enabled_orchestration_routing_count="
        f"{summary['enabled_orchestration_routing_count']}"
    )
    print(
        "enabled_orchestration_traversal_count="
        f"{summary['enabled_orchestration_traversal_count']}"
    )
    print(
        "enabled_orchestration_scheduling_count="
        f"{summary['enabled_orchestration_scheduling_count']}"
    )
    print(
        "enabled_orchestration_sequencing_count="
        f"{summary['enabled_orchestration_sequencing_count']}"
    )
    print(
        "enabled_orchestration_decision_count="
        f"{summary['enabled_orchestration_decision_count']}"
    )
    print(
        "enabled_orchestration_recommendation_count="
        f"{summary['enabled_orchestration_recommendation_count']}"
    )
    print(
        "enabled_automated_prioritization_count="
        f"{summary['enabled_automated_prioritization_count']}"
    )
    print(f"enabled_automated_triage_count={summary['enabled_automated_triage_count']}")
    print(f"enabled_ranking_count={summary['enabled_ranking_count']}")
    print(f"enabled_recommendation_count={summary['enabled_recommendation_count']}")
    print(
        "enabled_prioritization_action_count="
        f"{summary['enabled_prioritization_action_count']}"
    )
    print(f"enabled_remediation_count={summary['enabled_remediation_count']}")
    print(f"enabled_repair_count={summary['enabled_repair_count']}")
    print(f"enabled_mitigation_count={summary['enabled_mitigation_count']}")
    print(f"enabled_auto_correction_count={summary['enabled_auto_correction_count']}")
    print(
        "enabled_continuity_restoration_count="
        f"{summary['enabled_continuity_restoration_count']}"
    )
    print(f"enabled_runtime_mutation_count={summary['enabled_runtime_mutation_count']}")
    print(
        "enabled_operational_mutation_count="
        f"{summary['enabled_operational_mutation_count']}"
    )
    print(f"enabled_planner_integration_count={summary['enabled_planner_integration_count']}")
    print(
        "enabled_production_consumption_count="
        f"{summary['enabled_production_consumption_count']}"
    )
    print(f"repository_remains={','.join(summary['repository_remains'])}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
