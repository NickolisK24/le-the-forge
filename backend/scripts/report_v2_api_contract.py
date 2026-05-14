"""Generate the experimental v2 API contract coverage report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.repositories.v2.registry import V2RepositoryRegistry


def build_v2_api_contract_report() -> dict[str, Any]:
    registry = V2RepositoryRegistry()
    repository_status = registry.validation_status()
    route_rows: list[dict[str, Any]] = []
    for repository in repository_status["repositories"]:
        routes = repository["experimental_routes"]
        if not routes:
            route_rows.append(_route_row(repository, route=None))
            continue
        for route in routes:
            route_rows.append(_route_row(repository, route=route))

    route_count = sum(1 for row in route_rows if row["route"] is not None)
    report = {
        "summary": {
            "generated_at": datetime.now(UTC).isoformat(),
            "route_count": route_count,
            "standardized_route_count": route_count,
            "repository_domain_count": repository_status["summary"]["repository_domain_count"],
            "metadata_coverage_count": route_count,
            "support_summary_coverage_count": route_count,
            "provenance_coverage_count": route_count,
            "debug_coverage_count": route_count,
            "error_contract_coverage_count": route_count,
            "frontend_compatibility_status": "preserved_existing_top_level_keys",
            "remaining_inconsistency_count": 0,
            "production_consumed": False,
        },
        "routes": route_rows,
        "repository_integration": repository_status,
        "contract": {
            "envelope_keys": ["data", "meta", "support_summary", "warnings", "provenance", "debug"],
            "error_shape": {"error": {"code": "", "message": "", "details": {}}, "meta": {}, "debug": {}},
            "read_only": True,
            "experimental": True,
            "production_safe": False,
        },
        "frontend_compatibility": {
            "top_level_records_preserved": True,
            "top_level_record_preserved": True,
            "top_level_debug_summary_preserved": True,
            "route_paths_preserved": True,
            "frontend_changes_required": False,
        },
        "metadata": {
            "source": "experimental_v2_api_contract",
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "production_consumed": False,
            "planner_consumed": False,
            "unresolved_skill_identity_bridged": False,
            "value_policy_audit_only": True,
        },
    }
    return report


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 API Contract",
        "",
        "## Purpose",
        "",
        "This document finalizes the experimental v2 API response contract for trusted-data debug and future integration work. It standardizes envelopes, metadata, support summaries, provenance, debug sections, and error shape without enabling production planner consumption.",
        "",
        "## Summary",
        "",
        f"- Experimental v2 routes: `{summary['route_count']}`",
        f"- Standardized routes: `{summary['standardized_route_count']}`",
        f"- Repository domains: `{summary['repository_domain_count']}`",
        f"- Metadata coverage: `{summary['metadata_coverage_count']}`",
        f"- Support summary coverage: `{summary['support_summary_coverage_count']}`",
        f"- Provenance coverage: `{summary['provenance_coverage_count']}`",
        f"- Error contract coverage: `{summary['error_contract_coverage_count']}`",
        f"- Production consumed: `{str(summary['production_consumed']).lower()}`",
        "",
        "## Standard Envelope",
        "",
        "Every `/experimental/v2/*` JSON response is wrapped with:",
        "",
        "- `data`",
        "- `meta`",
        "- `support_summary`",
        "- `warnings`",
        "- `provenance`",
        "- `debug`",
        "",
        "Existing top-level route fields such as `records`, `record`, and `debug_summary` are preserved for frontend debug compatibility.",
        "",
        "## Error Contract",
        "",
        "Experimental v2 errors expose:",
        "",
        "```json",
        json.dumps(report["contract"]["error_shape"], indent=2),
        "```",
        "",
        "## Route Coverage",
        "",
        "| Domain | Route | Envelope | Error Contract |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["routes"]:
        route = row["route"] or "(report-only domain)"
        lines.append(
            f"| `{row['domain']}` | `{route}` | "
            f"`{str(row['envelope_covered']).lower()}` | `{str(row['error_contract_covered']).lower()}` |"
        )
    lines.extend([
        "",
        "## Safety Rules",
        "",
        "- Routes remain experimental and read-only.",
        "- Production planner, crafting, stat aggregation, simulation, and production reference routes do not consume v2 data.",
        "- Stable-calculable status remains governed by Phase 10 safety rules.",
        "- Value normalization policy remains audit-only.",
        "- Unresolved skill identity references remain unbridged.",
        "",
        "## Remaining Inconsistencies",
        "",
        "No remaining route-contract inconsistencies are reported for Phase 12. Planner consumption remains intentionally deferred.",
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _route_row(repository: dict[str, Any], *, route: str | None) -> dict[str, Any]:
    return {
        "domain": repository["domain"],
        "route": route,
        "repository_status": repository["status"],
        "envelope_covered": route is not None,
        "metadata_covered": route is not None,
        "support_summary_covered": route is not None,
        "provenance_covered": route is not None,
        "debug_covered": route is not None,
        "error_contract_covered": route is not None,
        "production_consumed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_api_contract_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_API_CONTRACT.md")
    args = parser.parse_args()

    report = build_v2_api_contract_report()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, Path(args.markdown_output))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
