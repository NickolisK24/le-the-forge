"""Developer command to consume a saved LE Tools sidecar diagnostic artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.le_tools_sidecar_diagnostic_consumer import (  # noqa: E402
    SidecarDiagnosticConsumerError,
    consume_sidecar_diagnostic,
    consumer_report_to_json,
    render_consumer_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consume a developer-only saved LE Tools import context sidecar."
    )
    parser.add_argument("--sidecar", type=Path, required=True, help="Path to saved sidecar JSON.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional diagnostics output path.")
    args = parser.parse_args()

    try:
        report = consume_sidecar_diagnostic(args.sidecar)
        content = consumer_report_to_json(report) if args.json else render_consumer_report(report)
        if args.output:
            validate_output_path(args.output)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content + "\n", encoding="utf-8")
            print(f"Wrote LE Tools sidecar diagnostic consumer report: {args.output}")
        else:
            print(content)
        return 0
    except (FileNotFoundError, ValueError, SidecarDiagnosticConsumerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
