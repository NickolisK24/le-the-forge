"""Generate deterministic v4.4 boundary segmentation scope evidence."""

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

from orchestration_governance.v4_4_boundary_segmentation_scope_audit import (  # noqa: E402
    build_v4_4_boundary_segmentation_scope_report,
)


REPORT_PATH = Path("docs/generated/v4_4_boundary_segmentation_scope_report.json")


def write_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.4 boundary segmentation scope JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_4_boundary_segmentation_scope_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"segment_record_count={summary['segment_record_count']}")
    print(f"scope_record_count={summary['scope_record_count']}")
    print(f"scoped_count={summary['scoped_count']}")
    print(f"unscoped_count={summary['unscoped_count']}")
    print(f"segmented_count={summary['segmented_count']}")
    print(f"unsegmented_count={summary['unsegmented_count']}")
    print(f"isolated_count={summary['isolated_count']}")
    print(f"coupled_count={summary['coupled_count']}")
    print(f"overlap_count={summary['overlap_count']}")
    print(f"ambiguity_count={summary['ambiguity_count']}")
    print(f"conflict_count={summary['conflict_count']}")
    print(f"degraded_count={summary['degraded_count']}")
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
    print(f"enabled_operational_mutation_count={summary['enabled_operational_mutation_count']}")
    print(f"planner_integration_enabled={summary['planner_integration_enabled']}")
    print(f"production_consumption_enabled={summary['production_consumption_enabled']}")
    print(f"runtime_mutation_enabled={summary['runtime_mutation_enabled']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
