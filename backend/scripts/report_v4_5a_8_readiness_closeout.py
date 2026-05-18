"""Generate deterministic v4.5A.8 readiness closeout visibility."""

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

from orchestration_governance.v4_5a_8_readiness_closeout_audit import (  # noqa: E402
    build_v4_5a_8_readiness_closeout_report,
)


REPORT_PATH = Path("docs/generated/v4_5a_8_readiness_closeout_report.json")


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
        help="v4.5A.8 readiness closeout JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5a_8_readiness_closeout_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"closeout_record_count={summary['closeout_record_count']}")
    print(f"readiness_certification_count={summary['readiness_certification_count']}")
    print(f"phase_coverage_count={summary['phase_coverage_count']}")
    print(f"report_coverage_count={summary['report_coverage_count']}")
    print(f"migration_document_count={summary['migration_document_count']}")
    print(f"continuity_certification_count={summary['continuity_certification_count']}")
    print(
        "unsupported_state_certification_count="
        f"{summary['unsupported_state_certification_count']}"
    )
    print(
        "inherited_prohibition_certification_count="
        f"{summary['inherited_prohibition_certification_count']}"
    )
    print(f"readiness_visibility_count={summary['readiness_visibility_count']}")
    print(f"closeout_diagnostic_count={summary['closeout_diagnostic_count']}")
    print(
        "unsupported_readiness_state_count="
        f"{summary['unsupported_readiness_state_count']}"
    )
    print(
        "deterministic_serialization_verified="
        f"{summary['deterministic_serialization_verified']}"
    )
    print(f"deterministic_hashing_verified={summary['deterministic_hashing_verified']}")
    print(f"phase_coverage_stable={summary['phase_coverage_stable']}")
    print(f"report_coverage_stable={summary['report_coverage_stable']}")
    print(f"migration_documentation_stable={summary['migration_documentation_stable']}")
    print(f"continuity_certification_stable={summary['continuity_certification_stable']}")
    print(
        "unsupported_state_preservation_stable="
        f"{summary['unsupported_state_preservation_stable']}"
    )
    print(
        "inherited_prohibition_preservation_stable="
        f"{summary['inherited_prohibition_preservation_stable']}"
    )
    print(f"readiness_visibility_stable={summary['readiness_visibility_stable']}")
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(f"evidence_continuity_preserved={summary['evidence_continuity_preserved']}")
    print(
        "fail_visible_closeout_diagnostics_verified="
        f"{summary['fail_visible_closeout_diagnostics_verified']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"inherited_prohibition_count={summary['inherited_prohibition_count']}")
    print(f"inherited_constraint_count={summary['inherited_constraint_count']}")
    print(f"inherited_limitation_count={summary['inherited_limitation_count']}")
    print(f"inherited_blocker_count={summary['inherited_blocker_count']}")
    print(f"inherited_warning_count={summary['inherited_warning_count']}")
    print(f"validation_error_count={summary['validation_error_count']}")
    for key in sorted(k for k in summary if k.startswith("enabled_")):
        print(f"{key}={summary[key]}")
    print(f"repository_remains={','.join(summary['repository_remains'])}")
    for target, classification in sorted(summary["readiness_classifications"].items()):
        print(f"readiness_classification[{target}]={classification}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
