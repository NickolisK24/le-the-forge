"""Developer command to compare saved and fresh LE Tools sidecar diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.le_tools_fresh_sidecar_diagnostic import DEFAULT_SAVED_SIDECAR  # noqa: E402
from app.game_data.le_tools_import_stage_context_report import DEFAULT_STAGE_FIXTURE  # noqa: E402
from app.game_data.le_tools_sidecar_diagnostic_comparison import (  # noqa: E402
    build_sidecar_diagnostic_comparison,
    render_sidecar_diagnostic_comparison,
    sidecar_diagnostic_comparison_to_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare saved and fresh developer-only LE Tools sidecar diagnostics."
    )
    parser.add_argument("--sidecar", type=Path, default=DEFAULT_SAVED_SIDECAR)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_STAGE_FIXTURE)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional diagnostics output path.")
    args = parser.parse_args()

    try:
        report = build_sidecar_diagnostic_comparison(
            sidecar_path=args.sidecar,
            fixture_path=args.fixture,
        )
        content = (
            sidecar_diagnostic_comparison_to_json(report)
            if args.json
            else render_sidecar_diagnostic_comparison(report)
        )
        if args.output:
            validate_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote LE Tools sidecar diagnostic comparison report: {args.output}")
        else:
            print(content)
        return 1 if report["migration_gate_status"] == "blocked" else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
