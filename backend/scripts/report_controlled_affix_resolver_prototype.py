"""Developer command for the controlled affix resolver prototype."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR  # noqa: E402
from app.game_data.controlled_affix_resolver_prototype import (  # noqa: E402
    ControlledAffixResolverError,
    controlled_affix_resolver_report_to_json,
    render_controlled_affix_resolver_report,
    resolve_affix_diagnostics,
    validate_controlled_affix_resolver_output_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a controlled read-only affix resolver prototype report from generated diagnostics."
    )
    parser.add_argument(
        "--diagnostics-dir",
        type=Path,
        default=DEFAULT_DIAGNOSTICS_DIR,
        help="Directory containing generated Phase 1-5 affix diagnostic JSON reports.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional diagnostics output path.")
    args = parser.parse_args()

    try:
        report = resolve_affix_diagnostics(args.diagnostics_dir)
        content = (
            controlled_affix_resolver_report_to_json(report)
            if args.json
            else render_controlled_affix_resolver_report(report)
        )
        if args.output:
            validate_controlled_affix_resolver_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote controlled affix resolver prototype report: {args.output}")
        else:
            print(content)
        return 0
    except (ControlledAffixResolverError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
