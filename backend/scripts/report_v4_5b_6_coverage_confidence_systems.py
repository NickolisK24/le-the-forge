"""Generate deterministic v4.5B.6 coverage and confidence report."""

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

from public_trust_visibility.v4_5b_6_coverage_confidence_audit import (  # noqa: E402
    build_v4_5b_6_coverage_confidence_report,
)


REPORT_PATH = Path("docs/generated/v4_5b_6_coverage_confidence_systems_report.json")


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
        help="v4.5B.6 coverage and confidence JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5b_6_coverage_confidence_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(
        "coverage_visibility_record_count="
        f"{summary['coverage_visibility_record_count']}"
    )
    print(f"support_coverage_record_count={summary['support_coverage_record_count']}")
    print(f"evidence_coverage_record_count={summary['evidence_coverage_record_count']}")
    print(
        "explainability_coverage_record_count="
        f"{summary['explainability_coverage_record_count']}"
    )
    print(
        "provenance_lineage_coverage_record_count="
        f"{summary['provenance_lineage_coverage_record_count']}"
    )
    print(
        "confidence_visibility_record_count="
        f"{summary['confidence_visibility_record_count']}"
    )
    print(
        "incomplete_unknown_coverage_record_count="
        f"{summary['incomplete_unknown_coverage_record_count']}"
    )
    print(f"summary_record_count={summary['summary_record_count']}")
    print(f"diagnostic_record_count={summary['diagnostic_record_count']}")
    print(
        "unsupported_operational_state_count="
        f"{summary['unsupported_operational_state_count']}"
    )
    print(
        "deterministic_coverage_serialization_verified="
        f"{summary['deterministic_coverage_serialization_verified']}"
    )
    print(
        "deterministic_confidence_serialization_verified="
        f"{summary['deterministic_confidence_serialization_verified']}"
    )
    print(
        "deterministic_coverage_hashing_verified="
        f"{summary['deterministic_coverage_hashing_verified']}"
    )
    print(
        "deterministic_confidence_hashing_verified="
        f"{summary['deterministic_confidence_hashing_verified']}"
    )
    print(f"coverage_visibility_stable={summary['coverage_visibility_stable']}")
    print(f"support_coverage_stable={summary['support_coverage_stable']}")
    print(f"evidence_coverage_stable={summary['evidence_coverage_stable']}")
    print(
        "explainability_coverage_stable="
        f"{summary['explainability_coverage_stable']}"
    )
    print(
        "provenance_lineage_coverage_stable="
        f"{summary['provenance_lineage_coverage_stable']}"
    )
    print(f"confidence_visibility_stable={summary['confidence_visibility_stable']}")
    print(
        "incomplete_unknown_coverage_visibility_preserved="
        f"{summary['incomplete_unknown_coverage_visibility_preserved']}"
    )
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(
        "evidence_panel_continuity_preserved="
        f"{summary['evidence_panel_continuity_preserved']}"
    )
    print(
        "fail_visible_coverage_diagnostics_verified="
        f"{summary['fail_visible_coverage_diagnostics_verified']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"publicly_transparent={summary['publicly_transparent']}")
    print(
        "coverage_confidence_statement="
        f"{summary['coverage_confidence_statement']}"
    )
    print(
        "coverage_confidence_non_authority_statement="
        f"{summary['coverage_confidence_non_authority_statement']}"
    )
    print(f"inherited_prohibition_count={summary['inherited_prohibition_count']}")
    print(f"inherited_constraint_count={summary['inherited_constraint_count']}")
    print(f"explicit_limitation_count={summary['explicit_limitation_count']}")
    print(f"validation_error_count={summary['validation_error_count']}")
    for key in sorted(k for k in summary if k.startswith("enabled_")):
        print(f"{key}={summary[key]}")
    print(f"repository_remains={','.join(summary['repository_remains'])}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
