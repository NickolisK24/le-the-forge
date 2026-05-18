"""Generate deterministic v4.5B.1 public trust visibility foundation report."""

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

from public_trust_visibility.v4_5b_1_trust_visibility_foundation_audit import (  # noqa: E402
    build_v4_5b_1_trust_visibility_foundation_report,
)


REPORT_PATH = Path("docs/generated/v4_5b_1_trust_visibility_foundations_report.json")


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
        help="v4.5B.1 public trust visibility JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_5b_1_trust_visibility_foundation_report()
    write_report(report, output_path)
    summary = report["summary"]
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"trust_visibility_record_count={summary['trust_visibility_record_count']}")
    print(f"evidence_visibility_count={summary['evidence_visibility_count']}")
    print(
        "unsupported_state_visibility_count="
        f"{summary['unsupported_state_visibility_count']}"
    )
    print(
        "governance_transparency_visibility_count="
        f"{summary['governance_transparency_visibility_count']}"
    )
    print(f"trust_summary_count={summary['trust_summary_count']}")
    print(f"explainability_visibility_count={summary['explainability_visibility_count']}")
    print(f"integrity_visibility_count={summary['integrity_visibility_count']}")
    print(f"public_trust_diagnostic_count={summary['public_trust_diagnostic_count']}")
    print(
        "unsupported_public_trust_state_count="
        f"{summary['unsupported_public_trust_state_count']}"
    )
    print(
        "deterministic_serialization_verified="
        f"{summary['deterministic_serialization_verified']}"
    )
    print(f"deterministic_hashing_verified={summary['deterministic_hashing_verified']}")
    print(f"evidence_visibility_stable={summary['evidence_visibility_stable']}")
    print(
        "unsupported_state_visibility_preserved="
        f"{summary['unsupported_state_visibility_preserved']}"
    )
    print(
        "governance_transparency_visibility_preserved="
        f"{summary['governance_transparency_visibility_preserved']}"
    )
    print(f"trust_summary_stable={summary['trust_summary_stable']}")
    print(f"explainability_visibility_stable={summary['explainability_visibility_stable']}")
    print(f"integrity_visibility_stable={summary['integrity_visibility_stable']}")
    print(f"lineage_continuity_preserved={summary['lineage_continuity_preserved']}")
    print(
        "provenance_continuity_preserved="
        f"{summary['provenance_continuity_preserved']}"
    )
    print(f"evidence_continuity_preserved={summary['evidence_continuity_preserved']}")
    print(
        "fail_visible_public_trust_diagnostics_verified="
        f"{summary['fail_visible_public_trust_diagnostics_verified']}"
    )
    print(
        "descriptive_only_guarantees_verified="
        f"{summary['descriptive_only_guarantees_verified']}"
    )
    print(f"publicly_transparent={summary['publicly_transparent']}")
    print(
        "public_trust_visibility_statement="
        f"{summary['public_trust_visibility_statement']}"
    )
    print(
        "trust_visibility_non_authority_statement="
        f"{summary['trust_visibility_non_authority_statement']}"
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
