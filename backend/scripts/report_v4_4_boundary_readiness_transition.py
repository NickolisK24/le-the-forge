"""Generate deterministic v4.4 boundary readiness and v4.5 transition evidence."""

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

from orchestration_governance.v4_4_boundary_readiness_transition_audit import (  # noqa: E402
    build_v4_4_boundary_readiness_transition_report,
)


REPORT_PATH = Path("docs/generated/v4_4_boundary_readiness_transition_report.json")


def write_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.4 boundary readiness transition JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_4_boundary_readiness_transition_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"v4_4_readiness_certification_count={summary['v4_4_readiness_certification_count']}")
    print(f"v4_5_transition_certification_count={summary['v4_5_transition_certification_count']}")
    print(f"phase_evidence_reference_count={summary['phase_evidence_reference_count']}")
    print(f"phase_chain_completeness_count={summary['phase_chain_completeness_count']}")
    print(f"ready_for_closeout_count={summary['ready_for_closeout_count']}")
    print(f"ready_with_warnings_count={summary['ready_with_warnings_count']}")
    print(f"not_ready_count={summary['not_ready_count']}")
    print(f"transition_ready_count={summary['transition_ready_count']}")
    print(f"transition_warning_count={summary['transition_warning_count']}")
    print(f"transition_blocked_count={summary['transition_blocked_count']}")
    print(f"unresolved_diagnostic_count={summary['unresolved_diagnostic_count']}")
    print(f"limitation_count={summary['limitation_count']}")
    print(f"blocker_count={summary['blocker_count']}")
    print(f"warning_count={summary['warning_count']}")
    print(f"inherited_v4_5_constraint_count={summary['inherited_v4_5_constraint_count']}")
    print(f"inherited_v4_5_prohibition_count={summary['inherited_v4_5_prohibition_count']}")
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
        "enabled_orchestration_activation_count="
        f"{summary['enabled_orchestration_activation_count']}"
    )
    print(f"enabled_dispatch_execution_count={summary['enabled_dispatch_execution_count']}")
    print(f"enabled_routing_execution_count={summary['enabled_routing_execution_count']}")
    print(f"enabled_scheduling_execution_count={summary['enabled_scheduling_execution_count']}")
    print(f"enabled_recommendation_count={summary['enabled_recommendation_count']}")
    print(f"enabled_decision_count={summary['enabled_decision_count']}")
    print(f"enabled_readiness_authorization_count={summary['enabled_readiness_authorization_count']}")
    print(f"enabled_transition_approval_count={summary['enabled_transition_approval_count']}")
    print(f"enabled_v4_5_activation_count={summary['enabled_v4_5_activation_count']}")
    print(f"enabled_operational_mutation_count={summary['enabled_operational_mutation_count']}")
    print(f"planner_integration_enabled={summary['planner_integration_enabled']}")
    print(f"production_consumption_enabled={summary['production_consumption_enabled']}")
    print(f"runtime_mutation_enabled={summary['runtime_mutation_enabled']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
