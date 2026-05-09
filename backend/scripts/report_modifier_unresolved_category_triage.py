"""Developer command for unresolved modifier category triage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR  # noqa: E402
from app.game_data.modifier_unresolved_category_triage import (  # noqa: E402
    ModifierUnresolvedTriageError,
    build_modifier_unresolved_triage,
    modifier_unresolved_triage_to_json,
    render_modifier_unresolved_triage_report,
    validate_modifier_unresolved_triage_output_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify unresolved, malformed, and unsupported modifier diagnostic evidence."
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
        report = build_modifier_unresolved_triage(args.diagnostics_dir)
        content = (
            modifier_unresolved_triage_to_json(report)
            if args.json
            else render_modifier_unresolved_triage_report(report)
        )
        if args.output:
            validate_modifier_unresolved_triage_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote modifier unresolved category triage report: {args.output}")
        else:
            print(content)
        return 0
    except (ModifierUnresolvedTriageError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
