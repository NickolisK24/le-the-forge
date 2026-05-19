"""Generate deterministic trusted gameplay data coverage audit reports."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.trusted_gameplay_data_coverage_audit import (  # noqa: E402
    REPORT_PATHS,
    build_all_trusted_gameplay_data_coverage_reports,
    write_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Repository root to inspect and write reports into.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root)
    reports = build_all_trusted_gameplay_data_coverage_reports(repo_root)
    write_reports(reports, repo_root)

    coverage = reports[REPORT_PATHS["coverage"]]
    summary = coverage["summary"]
    print(f"phase_id={coverage['phase_id']}")
    print(f"schema_version={coverage['schema_version']}")
    print(f"audited_system_count={summary['audited_system_count']}")
    print(f"coverage_certification={summary['coverage_certification']}")
    print(f"gameplay_maturity_state={summary['gameplay_maturity_state']}")
    print(f"partial_system_count={summary['partial_system_count']}")
    print(f"missing_system_count={summary['missing_system_count']}")
    print(f"unsupported_system_count={summary['unsupported_system_count']}")
    print(f"schema_mismatch_system_count={summary['schema_mismatch_system_count']}")
    print(f"planner_dependency_gap_system_count={summary['planner_dependency_gap_system_count']}")
    print(f"hardcoded_system_count={summary['hardcoded_system_count']}")
    print(f"non_operational_boundary_preserved={summary['non_operational_boundary_preserved']}")
    for report_path, report in sorted(reports.items()):
        print(f"wrote={report_path}")
        print(f"{report_path}.deterministic_report_hash={report['deterministic_report_hash']}")
        print(
            f"{report_path}.deterministic_hash_replay_verified="
            f"{report['deterministic_hash_replay_verified']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
