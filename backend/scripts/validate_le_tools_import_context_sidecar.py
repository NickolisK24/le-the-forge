"""Developer command to validate LE Tools import context sidecars."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.le_tools_import_context_sidecar import build_sidecar_from_fixture  # noqa: E402
from app.game_data.le_tools_import_context_sidecar_validator import (  # noqa: E402
    load_sidecar,
    render_validation_result,
    validate_sidecar_artifact,
    validation_result_to_json,
)
from app.game_data.le_tools_import_stage_context_report import DEFAULT_STAGE_FIXTURE  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate developer-only LE Tools import context sidecar.")
    parser.add_argument("--sidecar", type=Path, default=None, help="Path to saved sidecar JSON.")
    parser.add_argument("--build-current", action="store_true", help="Build current offline sidecar in memory.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional diagnostics output path.")
    args = parser.parse_args()

    if not args.build_current and not args.sidecar:
        print("ERROR: provide --build-current or --sidecar path", file=sys.stderr)
        return 1
    try:
        if args.build_current:
            sidecar, _mapped = build_sidecar_from_fixture(DEFAULT_STAGE_FIXTURE)
        else:
            sidecar = load_sidecar(args.sidecar)
        result = validate_sidecar_artifact(sidecar)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    content = validation_result_to_json(result) if args.json else render_validation_result(result)
    if args.output:
        try:
            validate_output_path(args.output)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
        print(f"Wrote LE Tools import context sidecar validation report: {args.output}")
    else:
        print(content)
    return 1 if result["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
