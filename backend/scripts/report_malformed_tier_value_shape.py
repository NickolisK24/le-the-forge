"""Developer command for malformed tier/value shape policy validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR  # noqa: E402
from app.game_data.malformed_tier_value_shape_validator import (  # noqa: E402
    MalformedTierValueShapeValidatorError,
    malformed_tier_value_shape_report_to_json,
    render_malformed_tier_value_shape_report,
    validate_malformed_tier_value_shape_output_path,
    validate_malformed_tier_value_shapes,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate malformed tier/value shape diagnostic evidence.")
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
        report = validate_malformed_tier_value_shapes(args.diagnostics_dir)
        content = (
            malformed_tier_value_shape_report_to_json(report)
            if args.json
            else render_malformed_tier_value_shape_report(report)
        )
        if args.output:
            validate_malformed_tier_value_shape_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote malformed tier/value shape report: {args.output}")
        else:
            print(content)
        return 0
    except (MalformedTierValueShapeValidatorError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
