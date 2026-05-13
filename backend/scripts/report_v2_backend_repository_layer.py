"""Generate the v2 backend repository layer consolidation report."""

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


def build_v2_backend_repository_report(*, root: str | Path | None = None) -> dict[str, Any]:
    registry = V2RepositoryRegistry(root=root)
    validation = registry.validation_status()
    repositories = validation["repositories"]
    route_count = sum(len(repository["experimental_routes"]) for repository in repositories)
    method_count = sum(len(repository["method_coverage"]) for repository in repositories)
    missing_method_count = sum(len(repository["missing_methods"]) for repository in repositories)
    domains_with_debug = [
        repository["domain"]
        for repository in repositories
        if repository["status"] == "ok" and repository.get("debug_summary") is not None
    ]
    report = {
        "summary": {
            "generated_at": datetime.now(UTC).isoformat(),
            "repository_domain_count": validation["summary"]["repository_domain_count"],
            "loaded_repository_count": validation["summary"]["loaded_repository_count"],
            "missing_artifact_count": validation["summary"]["missing_artifact_count"],
            "invalid_repository_count": validation["summary"]["invalid_repository_count"],
            "method_coverage_count": method_count,
            "missing_method_count": missing_method_count,
            "experimental_route_count": route_count,
            "debug_summary_domain_count": len(domains_with_debug),
            "production_consumed": False,
        },
        "repositories": repositories,
        "method_coverage": {
            repository["domain"]: repository["method_coverage"]
            for repository in repositories
        },
        "experimental_route_coverage": {
            repository["domain"]: repository["experimental_routes"]
            for repository in repositories
        },
        "missing_artifacts": [
            {
                "domain": repository["domain"],
                "artifact_key": artifact["artifact_key"],
                "path": artifact["path"],
            }
            for repository in repositories
            for artifact in repository["artifacts"]
            if not artifact["exists"]
        ],
        "metadata": {
            "source": "generated_v2_backend_repositories",
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "production_consumed": False,
            "planner_consumed": False,
            "unresolved_skill_identity_bridged": False,
        },
    }
    return report


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 Backend Repository Layer",
        "",
        "## Purpose",
        "",
        "This report consolidates the read-only v2 backend repository layer after Phases 3 through 10.5. It documents generated artifact dependencies, loader validation, method coverage, experimental route coverage, and production-consumption safety.",
        "",
        "This phase does not remap planner behavior and does not make partial, unsupported, unknown, or source-unit records stable-calculable.",
        "",
        "## Summary",
        "",
        f"- Repository domains: `{summary['repository_domain_count']}`",
        f"- Loaded repositories/artifacts: `{summary['loaded_repository_count']}`",
        f"- Missing artifacts: `{summary['missing_artifact_count']}`",
        f"- Invalid repositories: `{summary['invalid_repository_count']}`",
        f"- Missing required methods: `{summary['missing_method_count']}`",
        f"- Experimental routes documented: `{summary['experimental_route_count']}`",
        f"- Production consumed: `{str(summary['production_consumed']).lower()}`",
        "",
        "## Repository Coverage",
        "",
        "| Domain | Status | Artifacts | Missing Methods | Experimental Routes |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for repository in report["repositories"]:
        lines.append(
            f"| `{repository['domain']}` | `{repository['status']}` | "
            f"`{len(repository['artifacts'])}` | `{len(repository['missing_methods'])}` | "
            f"`{len(repository['experimental_routes'])}` |"
        )

    lines.extend([
        "",
        "## Missing Artifacts",
        "",
    ])
    if report["missing_artifacts"]:
        for artifact in report["missing_artifacts"]:
            lines.append(f"- `{artifact['domain']}` missing `{artifact['artifact_key']}` at `{artifact['path']}`")
    else:
        lines.append("No missing generated artifacts were found.")

    lines.extend([
        "",
        "## Route Coverage",
        "",
    ])
    for domain, routes in report["experimental_route_coverage"].items():
        if not routes:
            lines.append(f"- `{domain}`: no experimental route; audit/report-only domain.")
            continue
        joined = ", ".join(f"`{route}`" for route in routes)
        lines.append(f"- `{domain}`: {joined}")

    lines.extend([
        "",
        "## Safety Notes",
        "",
        "- All v2 repositories remain read-only.",
        "- Production planner, crafting, stat aggregation, simulation, and production reference routes do not consume this registry.",
        "- The value normalization policy remains audit-only.",
        "- Remaining skill identity gaps remain unbridged and must not be treated as resolved.",
        "",
        "## Recommended Next Step",
        "",
        "Proceed to API contract finalization only after this repository layer is reviewed. Planner remapping should remain deferred until value-scale normalization and stable eligibility policy have stronger evidence.",
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_backend_repository_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_BACKEND_REPOSITORY_LAYER.md")
    args = parser.parse_args()

    report = build_v2_backend_repository_report()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, Path(args.markdown_output))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
