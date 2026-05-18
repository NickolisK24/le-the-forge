"""Generate deterministic v4.4 boundary continuity and integrity evidence."""

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

from orchestration_governance.v4_4_boundary_continuity_integrity_audit import (  # noqa: E402
    build_v4_4_boundary_continuity_integrity_report,
)


REPORT_PATH = Path("docs/generated/v4_4_boundary_continuity_integrity_report.json")


def write_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.4 boundary continuity and integrity JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_4_boundary_continuity_integrity_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"phase_evidence_reference_count={summary['phase_evidence_reference_count']}")
    print(
        "continuity_certification_record_count="
        f"{summary['continuity_certification_record_count']}"
    )
    print(
        "integrity_certification_record_count="
        f"{summary['integrity_certification_record_count']}"
    )
    print(f"certified_count={summary['certified_count']}")
    print(f"partially_certified_count={summary['partially_certified_count']}")
    print(f"uncertified_count={summary['uncertified_count']}")
    print(f"continuous_count={summary['continuous_count']}")
    print(f"discontinuous_count={summary['discontinuous_count']}")
    print(f"integrity_safe_count={summary['integrity_safe_count']}")
    print(f"integrity_warning_count={summary['integrity_warning_count']}")
    print(f"integrity_blocked_count={summary['integrity_blocked_count']}")
    print(f"replay_safe_count={summary['replay_safe_count']}")
    print(f"rollback_safe_count={summary['rollback_safe_count']}")
    print(f"provenance_safe_count={summary['provenance_safe_count']}")
    print(f"lineage_safe_count={summary['lineage_safe_count']}")
    print(f"limitation_count={summary['limitation_count']}")
    print(f"fail_visible_diagnostic_count={summary['fail_visible_diagnostic_count']}")
    print(f"enabled_runtime_execution_count={summary['enabled_runtime_execution_count']}")
    print(
        "enabled_orchestration_authorization_count="
        f"{summary['enabled_orchestration_authorization_count']}"
    )
    print(
        "enabled_orchestration_approval_count="
        f"{summary['enabled_orchestration_approval_count']}"
    )
    print(f"enabled_dispatch_execution_count={summary['enabled_dispatch_execution_count']}")
    print(f"enabled_routing_execution_count={summary['enabled_routing_execution_count']}")
    print(f"enabled_scheduling_execution_count={summary['enabled_scheduling_execution_count']}")
    print(f"enabled_recommendation_count={summary['enabled_recommendation_count']}")
    print(f"enabled_decision_count={summary['enabled_decision_count']}")
    print(
        "enabled_certification_authorization_count="
        f"{summary['enabled_certification_authorization_count']}"
    )
    print(f"enabled_integrity_approval_count={summary['enabled_integrity_approval_count']}")
    print(f"enabled_operational_mutation_count={summary['enabled_operational_mutation_count']}")
    print(f"planner_integration_enabled={summary['planner_integration_enabled']}")
    print(f"production_consumption_enabled={summary['production_consumption_enabled']}")
    print(f"runtime_mutation_enabled={summary['runtime_mutation_enabled']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
