"""Generate deterministic v4.5B.5 public evidence panel report."""

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

from public_trust_visibility.v4_5b_5_evidence_panel_audit import (  # noqa: E402
    build_v4_5b_5_evidence_panels_report,
)


REPORT_PATH = Path("docs/generated/v4_5b_5_evidence_panels_report.json")


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
        help="v4.5B.5 public evidence panel JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5b_5_evidence_panels_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"evidence_panel_record_count={summary['evidence_panel_record_count']}")
    print(f"evidence_group_count={summary['evidence_group_count']}")
    print(f"evidence_item_count={summary['evidence_item_count']}")
    print(
        "evidence_source_visibility_count="
        f"{summary['evidence_source_visibility_count']}"
    )
    print(
        "evidence_freshness_visibility_count="
        f"{summary['evidence_freshness_visibility_count']}"
    )
    print(
        "support_status_evidence_panel_count="
        f"{summary['support_status_evidence_panel_count']}"
    )
    print(
        "explainability_evidence_panel_count="
        f"{summary['explainability_evidence_panel_count']}"
    )
    print(
        "provenance_lineage_evidence_panel_count="
        f"{summary['provenance_lineage_evidence_panel_count']}"
    )
    print(
        "unsupported_missing_evidence_count="
        f"{summary['unsupported_missing_evidence_count']}"
    )
    print(f"evidence_panel_summary_count={summary['evidence_panel_summary_count']}")
    print(
        "evidence_panel_diagnostic_count="
        f"{summary['evidence_panel_diagnostic_count']}"
    )
    print(
        "unsupported_operational_state_count="
        f"{summary['unsupported_operational_state_count']}"
    )
    print(
        "deterministic_evidence_panel_serialization_verified="
        f"{summary['deterministic_evidence_panel_serialization_verified']}"
    )
    print(
        "deterministic_evidence_panel_hashing_verified="
        f"{summary['deterministic_evidence_panel_hashing_verified']}"
    )
    print(f"evidence_grouping_stable={summary['evidence_grouping_stable']}")
    print(
        "evidence_source_visibility_stable="
        f"{summary['evidence_source_visibility_stable']}"
    )
    print(
        "evidence_freshness_visibility_preserved="
        f"{summary['evidence_freshness_visibility_preserved']}"
    )
    print(
        "support_status_evidence_panel_stable="
        f"{summary['support_status_evidence_panel_stable']}"
    )
    print(
        "explainability_evidence_panel_stable="
        f"{summary['explainability_evidence_panel_stable']}"
    )
    print(
        "provenance_lineage_evidence_panel_stable="
        f"{summary['provenance_lineage_evidence_panel_stable']}"
    )
    print(
        "unsupported_missing_evidence_visibility_preserved="
        f"{summary['unsupported_missing_evidence_visibility_preserved']}"
    )
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(f"evidence_continuity_preserved={summary['evidence_continuity_preserved']}")
    print(f"source_visibility_preserved={summary['source_visibility_preserved']}")
    print(
        "fail_visible_evidence_panel_diagnostics_verified="
        f"{summary['fail_visible_evidence_panel_diagnostics_verified']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"publicly_transparent={summary['publicly_transparent']}")
    print(f"evidence_panel_statement={summary['evidence_panel_statement']}")
    print(
        "evidence_visibility_non_authority_statement="
        f"{summary['evidence_visibility_non_authority_statement']}"
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
