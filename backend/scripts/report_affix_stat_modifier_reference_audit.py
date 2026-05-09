"""Developer command to audit affix stat/modifier reference diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR  # noqa: E402
from app.game_data.affix_stat_modifier_reference_audit import (  # noqa: E402
    DEFAULT_PER_AFFIX_ARTIFACT,
    affix_stat_modifier_reference_audit_to_json,
    audit_affix_stat_modifier_references,
    render_affix_stat_modifier_reference_audit,
    validate_affix_stat_modifier_reference_audit_output_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit affix stat/modifier reference evidence from generated diagnostics."
    )
    parser.add_argument(
        "--diagnostics-dir",
        type=Path,
        default=DEFAULT_DIAGNOSTICS_DIR,
        help="Directory containing generated Phase 1-5 affix diagnostic JSON reports.",
    )
    parser.add_argument(
        "--per-affix-artifact",
        type=Path,
        default=DEFAULT_PER_AFFIX_ARTIFACT,
        help="Generated controlled per-affix diagnostic JSON artifact.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional diagnostics output path.")
    args = parser.parse_args()

    try:
        report = audit_affix_stat_modifier_references(
            args.diagnostics_dir,
            args.per_affix_artifact,
        )
        content = (
            affix_stat_modifier_reference_audit_to_json(report)
            if args.json
            else render_affix_stat_modifier_reference_audit(report)
        )
        if args.output:
            validate_affix_stat_modifier_reference_audit_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote affix stat/modifier reference audit: {args.output}")
        else:
            print(content)
        return 1 if report["errors"] else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
