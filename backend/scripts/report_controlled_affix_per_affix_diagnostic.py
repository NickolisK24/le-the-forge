"""Developer command to emit controlled per-affix diagnostic records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.affix_diagnostic_consumer import DEFAULT_DIAGNOSTICS_DIR  # noqa: E402
from app.game_data.controlled_affix_per_affix_diagnostic import (  # noqa: E402
    build_per_affix_diagnostic_artifact,
    per_affix_diagnostic_artifact_to_json,
    render_per_affix_diagnostic_artifact,
    validate_per_affix_diagnostic_output_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate controlled per-affix diagnostic records from resolver output."
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
        artifact = build_per_affix_diagnostic_artifact(args.diagnostics_dir)
        content = (
            per_affix_diagnostic_artifact_to_json(artifact)
            if args.json
            else render_per_affix_diagnostic_artifact(artifact)
        )
        if args.output:
            validate_per_affix_diagnostic_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote controlled per-affix diagnostic artifact: {args.output}")
        else:
            print(content)
        return 1 if artifact["errors"] else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
