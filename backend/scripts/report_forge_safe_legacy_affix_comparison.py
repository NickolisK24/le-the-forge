"""Generate the read-only Forge-safe legacy affix comparison report.

This script invokes the experimental Flask endpoint through the local test
client so the saved output matches the API response shape. It only raises the
in-process diagnostic list cap for this run so the full detail payload can be
preserved without changing application code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE_PATH = Path(
    r"D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json"
)
DEFAULT_OUTPUT_PATH = (
    ROOT / "docs" / "generated" / "forge_safe_legacy_affix_comparison.json"
)
DEFAULT_LIMIT = 2000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Save the experimental legacy-vs-Forge-safe affix comparison JSON."
    )
    parser.add_argument("--bundle-path", type=Path, default=DEFAULT_BUNDLE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--env", default="testing")
    return parser.parse_args()


def generate_report(bundle_path: Path, *, limit: int, env: str) -> dict[str, Any]:
    if not bundle_path.exists():
        raise FileNotFoundError(f"Forge-safe affix bundle is missing: {bundle_path}")

    os.environ["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = "true"
    os.environ["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = "true"
    os.environ["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = str(bundle_path)

    sys.path.insert(0, str(ROOT / "backend"))

    from app import create_app
    import app.routes.experimental as experimental_routes
    import app.services.forge_safe_affix_comparison_service as comparison_service

    app = create_app(env)
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = str(bundle_path)

    detail_limit = max(limit, 0)
    experimental_routes.MAX_LIMIT = detail_limit
    comparison_service.MAX_LIMIT = detail_limit

    response = app.test_client().get(
        f"/experimental/forge-safe-affixes/compare-legacy"
        f"?include_details=true&limit={detail_limit}"
    )
    body = response.get_json()
    if response.status_code != 200:
        raise RuntimeError(
            f"comparison endpoint failed with HTTP {response.status_code}: {body}"
        )
    return body


def main() -> int:
    args = parse_args()
    report = generate_report(args.bundle_path, limit=args.limit, env=args.env)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["comparison"]["summary"]
    print(
        json.dumps(
            {
                "output": str(args.output),
                "summary": summary,
                "truncated": report["comparison"]["metadata"]["truncated"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
