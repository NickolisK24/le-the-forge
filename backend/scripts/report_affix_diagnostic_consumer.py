"""Developer command for the Phase 6 affix diagnostic consumer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.affix_diagnostic_consumer import (  # noqa: E402
    DEFAULT_DIAGNOSTICS_DIR,
    AffixDiagnosticConsumerError,
    affix_diagnostic_report_to_json,
    consume_affix_diagnostics,
    render_affix_diagnostic_report,
    validate_affix_diagnostic_output_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consume generated affix diagnostics in a read-only non-production report."
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
        report = consume_affix_diagnostics(args.diagnostics_dir)
        content = affix_diagnostic_report_to_json(report) if args.json else render_affix_diagnostic_report(report)
        if args.output:
            validate_affix_diagnostic_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote affix diagnostic consumer report: {args.output}")
        else:
            print(content)
        return 0
    except (AffixDiagnosticConsumerError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
