"""Developer command for read-only Forge data bundle compatibility checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_compat import (  # noqa: E402
    STATUS_INCOMPATIBLE,
    check_bundle_compatibility,
    resolve_bundle_dir,
)


def _print_list(title: str, values: list[str]) -> None:
    print(title)
    if values:
        for value in values:
            print(f"  - {value}")
    else:
        print("  none")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a last-epoch-data bundle control plane.")
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=None,
        help="Bundle directory. Defaults to FORGE_DATA_BUNDLE_DIR or D:\\Forge\\last-epoch-data\\data_bundle.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    args = parser.parse_args()

    bundle_dir = resolve_bundle_dir(args.bundle_dir)
    result = check_bundle_compatibility(bundle_dir)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"Bundle path: {bundle_dir}")
        print(f"Status: {result.status}")
        print(f"Bundle ID: {result.bundle_id}")
        print(f"Game version: {result.game_version}")
        print(f"Build number: {result.build_number}")
        print(f"Data patch: {result.data_patch}")
        print(f"Validation status: {result.validation_status}")
        print(f"Known gaps: {result.known_gap_count}")
        print("")
        _print_list("Errors", result.errors)
        print("")
        _print_list("Warnings", result.warnings)
        print("")
        print("Family action summary")
        for action, families in result.actions.items():
            print(f"  {action}: {len(families)}")
            for family in families:
                print(f"    - {family}")

    return 1 if result.status == STATUS_INCOMPATIBLE else 0


if __name__ == "__main__":
    raise SystemExit(main())
