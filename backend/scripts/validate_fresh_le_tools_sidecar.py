"""Developer command to validate freshly built LE Tools sidecars."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.le_tools_fresh_sidecar_diagnostic import (  # noqa: E402
    DEFAULT_SAVED_SIDECAR,
    build_fresh_sidecar_diagnostic,
    fresh_sidecar_diagnostic_to_json,
    render_fresh_sidecar_diagnostic,
)
from app.game_data.le_tools_import_stage_context_report import DEFAULT_STAGE_FIXTURE  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a freshly built developer-only LE Tools import context sidecar."
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_STAGE_FIXTURE)
    parser.add_argument("--saved-sidecar", type=Path, default=DEFAULT_SAVED_SIDECAR)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional diagnostics output path.")
    args = parser.parse_args()

    try:
        report = build_fresh_sidecar_diagnostic(
            fixture_path=args.fixture,
            saved_sidecar_path=args.saved_sidecar,
        )
        content = fresh_sidecar_diagnostic_to_json(report) if args.json else render_fresh_sidecar_diagnostic(report)
        if args.output:
            validate_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote fresh LE Tools sidecar diagnostic report: {args.output}")
        else:
            print(content)
        return 1 if report["status"] == "failed" else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
