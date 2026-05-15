"""Generate the v3.1 trusted production shadow consumption report."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.planner_adapters.v3_1.trusted_shadow_consumption import (  # noqa: E402
    V31TrustedProductionShadowConsumption,
    build_default_trusted_repository_probes,
)

DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_trusted_shadow_consumption_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    adapter = V31TrustedProductionShadowConsumption()
    probes = build_default_trusted_repository_probes(repo_root)
    disabled = adapter.inspect(
        enabled=False,
        trusted_repository_probes=probes,
        legacy_output={"route": "legacy", "sample_total": 3},
    )
    enabled = adapter.inspect(
        enabled=True,
        trusted_repository_probes=probes,
        legacy_output={"route": "legacy", "sample_total": 3},
    )
    repeated = adapter.inspect(
        enabled=True,
        trusted_repository_probes=probes,
        legacy_output={"route": "legacy", "sample_total": 3},
    )

    deterministic = enabled["deterministic_hash"] == repeated["deterministic_hash"]
    report = {
        "schema_version": "v3_1.trusted_shadow_consumption_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_1_trusted_production_shadow_consumption_gate",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            "gate_default_enabled": disabled["gate"]["default_enabled"],
            "disabled_production_output_affected": disabled["summary"]["production_output_affected"],
            "enabled_production_output_affected": enabled["summary"]["production_output_affected"],
            "trusted_repository_available_count": enabled["summary"]["trusted_repository_available_count"],
            "trusted_repository_unavailable_count": enabled["summary"]["trusted_repository_unavailable_count"],
            "trusted_entity_count": enabled["summary"]["trusted_entity_count"],
            "unsupported_domain_count": enabled["summary"]["unsupported_domain_count"],
            "legacy_path_still_active": enabled["summary"]["legacy_path_still_active"],
            "trusted_path_shadowed_only": enabled["summary"]["trusted_path_shadowed_only"],
            "deterministic": deterministic,
        },
        "disabled_gate_sample": disabled,
        "enabled_shadow_sample": enabled,
        "deterministic_guarantees": {
            "passed": deterministic,
            "sample_hash": enabled["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_1_boundaries": [
            "trusted repositories may be inspected only in shadow mode",
            "legacy production routing remains the truth source",
            "trusted repository availability failures are reported explicitly",
            "unsupported trusted domains remain blocked",
            "production default routing is not authorized",
        ],
        "metadata": {
            "source": "v3_1_trusted_shadow_consumption_report",
            "observational_only": True,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "planner_remap_performed": False,
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            normalized[key] = DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item)
        return normalized
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V3.1 Trusted Shadow Consumption",
        "",
        "Phase 1 introduces a disabled-by-default trusted production shadow-consumption gate.",
        "It is observational only and does not authorize trusted repositories as production default routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Gate default enabled: `{str(summary['gate_default_enabled']).lower()}`",
        f"- Disabled production output affected: `{str(summary['disabled_production_output_affected']).lower()}`",
        f"- Enabled production output affected: `{str(summary['enabled_production_output_affected']).lower()}`",
        f"- Trusted repositories available: `{summary['trusted_repository_available_count']}`",
        f"- Trusted repositories unavailable: `{summary['trusted_repository_unavailable_count']}`",
        f"- Trusted entity count: `{summary['trusted_entity_count']}`",
        f"- Unsupported domains: `{summary['unsupported_domain_count']}`",
        f"- Legacy path still active: `{str(summary['legacy_path_still_active']).lower()}`",
        f"- Trusted path shadowed only: `{str(summary['trusted_path_shadowed_only']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Shadow Rows",
        "",
        "| Domain | Repository | Status | Entities | Production Output Affected |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in report["enabled_shadow_sample"]["trusted_repository_rows"]:
        lines.append(
            f"| `{row['domain']}` | `{row['repository_name']}` | `{row['routing_status']}` | `{row['trusted_entity_count']}` | `{str(row['production_output_affected']).lower()}` |"
        )
    lines.extend(["", "## Phase 1 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_1_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Trusted repository consumption remains shadow-only. Production planner/runtime outputs continue to come from legacy paths.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_trusted_shadow_consumption_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_TRUSTED_SHADOW_CONSUMPTION.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_trusted_shadow_consumption_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
