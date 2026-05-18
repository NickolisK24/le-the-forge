"""Generate deterministic v4.3 closeout and v4.4 readiness evidence."""

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

from orchestration_governance.v4_3_closeout_readiness_audit import (  # noqa: E402
    build_v4_3_closeout_and_v4_4_readiness_report,
)


REPORT_PATH = Path("docs/generated/v4_3_closeout_and_v4_4_readiness_report.json")


def write_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.3 closeout and v4.4 readiness JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_closeout_and_v4_4_readiness_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(
        "final_closeout_classification="
        f"{report['summary']['final_closeout_classification']}"
    )
    print(
        "v4_4_readiness_classification="
        f"{report['summary']['v4_4_readiness_classification']}"
    )
    print(f"enabled_coordination_execution_count={report['summary']['enabled_coordination_execution_count']}")
    print(f"enabled_transition_execution_count={report['summary']['enabled_transition_execution_count']}")
    print(f"enabled_policy_enforcement_count={report['summary']['enabled_policy_enforcement_count']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"enabled_orchestration_decision_count={report['summary']['enabled_orchestration_decision_count']}")
    print(
        "enabled_orchestration_recommendation_count="
        f"{report['summary']['enabled_orchestration_recommendation_count']}"
    )
    print(
        "enabled_orchestration_authorization_count="
        f"{report['summary']['enabled_orchestration_authorization_count']}"
    )
    print(
        "enabled_orchestration_approval_count="
        f"{report['summary']['enabled_orchestration_approval_count']}"
    )
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
