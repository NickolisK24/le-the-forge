"""Generate deterministic v4.5B.8 trusted UX closeout report."""

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

from public_trust_visibility.v4_5b_8_trusted_ux_closeout_audit import (  # noqa: E402
    build_v4_5b_8_trusted_ux_closeout_report,
)


REPORT_PATH = Path("docs/generated/v4_5b_8_trusted_ux_closeout_report.json")


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
        help="v4.5B.8 trusted UX closeout JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5b_8_trusted_ux_closeout_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"closeout_record_count={summary['closeout_record_count']}")
    print(f"readiness_record_count={summary['readiness_record_count']}")
    print(f"phase_coverage_record_count={summary['phase_coverage_record_count']}")
    print(f"report_coverage_record_count={summary['report_coverage_record_count']}")
    print(
        "migration_document_coverage_record_count="
        f"{summary['migration_document_coverage_record_count']}"
    )
    print(
        "public_trust_continuity_record_count="
        f"{summary['public_trust_continuity_record_count']}"
    )
    print(f"unsupported_state_record_count={summary['unsupported_state_record_count']}")
    print(
        "inherited_prohibition_record_count="
        f"{summary['inherited_prohibition_record_count']}"
    )
    print(f"frontend_readiness_record_count={summary['frontend_readiness_record_count']}")
    print(
        "closeout_diagnostic_record_count="
        f"{summary['closeout_diagnostic_record_count']}"
    )
    print(
        "unsupported_operational_state_count="
        f"{summary['unsupported_operational_state_count']}"
    )
    print(
        "deterministic_closeout_serialization_verified="
        f"{summary['deterministic_closeout_serialization_verified']}"
    )
    print(
        "deterministic_closeout_hashing_verified="
        f"{summary['deterministic_closeout_hashing_verified']}"
    )
    print(f"phase_coverage_stable={summary['phase_coverage_stable']}")
    print(f"report_coverage_stable={summary['report_coverage_stable']}")
    print(
        "migration_document_coverage_stable="
        f"{summary['migration_document_coverage_stable']}"
    )
    print(
        "public_trust_continuity_preserved="
        f"{summary['public_trust_continuity_preserved']}"
    )
    print(
        "unsupported_state_preservation_stable="
        f"{summary['unsupported_state_preservation_stable']}"
    )
    print(
        "inherited_prohibition_preservation_stable="
        f"{summary['inherited_prohibition_preservation_stable']}"
    )
    print(
        "frontend_readiness_visibility_stable="
        f"{summary['frontend_readiness_visibility_stable']}"
    )
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(
        "continuity_reference_preserved="
        f"{summary['continuity_reference_preserved']}"
    )
    print(
        "fail_visible_closeout_diagnostics_preserved="
        f"{summary['fail_visible_closeout_diagnostics_preserved']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"publicly_transparent={summary['publicly_transparent']}")
    print(
        "trusted_ux_readiness_statement="
        f"{summary['trusted_ux_readiness_statement']}"
    )
    print(
        "trusted_ux_readiness_non_authority_statement="
        f"{summary['trusted_ux_readiness_non_authority_statement']}"
    )
    for key, value in sorted(summary["readiness_classifications"].items()):
        print(f"readiness_classification[{key}]={value}")
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
