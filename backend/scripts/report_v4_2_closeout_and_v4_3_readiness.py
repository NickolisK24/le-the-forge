"""Generate deterministic v4.2 closeout and v4.3 planning readiness evidence."""

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

from refresh_coordination.v4_2_closeout_readiness_audit import (  # noqa: E402
    build_v4_2_closeout_and_v4_3_readiness_report,
)


REPORT_PATH = Path("docs/generated/v4_2_closeout_and_v4_3_readiness_report.json")


def write_report(repo_root: Path) -> Path:
    report = build_v4_2_closeout_and_v4_3_readiness_report(repo_root)
    target = repo_root / REPORT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    target = write_report(args.repo_root)
    print(f"v4_2_closeout_and_v4_3_readiness: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
