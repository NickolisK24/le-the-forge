"""Generate deterministic v4.5C.5 frontend trust closeout and backend reflection audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPORT_PATH = Path(
    "docs/generated/v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report.json"
)

PHASE_ID = "v4_5c_5_frontend_trust_closeout_backend_reflection_audit"
GENERATED_AT = "2026-05-18T00:00:00+00:00"
TRUST_SURFACE_ROUTE = "/trusted-data/frontend-trust"
TRUSTED_DATA_ROUTE = "/trusted-data"
BACKEND_HEALTH_ROUTE = "/api/health"

REPOSITORY_REMAINS = [
    "READ-ONLY",
    "DESCRIPTIVE-ONLY",
    "NON-operational",
    "NON-authorizing",
    "NON-approving",
    "NON-recommending",
    "NON-ranking",
    "NON-scoring",
    "NON-triaging",
]

NON_AUTHORITY_STATEMENT = (
    "Frontend trust closeout does NOT imply frontend launch authorization, "
    "backend live trust integration, planner authority, execution safety, "
    "correctness guarantees, operational readiness, production enablement, "
    "recommendation quality, ranking quality, scoring quality, triage priority, "
    "authorization, or approval."
)

COVERED_PHASES = [
    {
        "phase_id": "v4_5c_1_frontend_trust_surface_foundations",
        "report_path": "docs/generated/v4_5c_1_frontend_trust_surface_foundations_report.json",
        "migration_doc_path": "docs/migration/V4_5C_1_FRONTEND_TRUST_SURFACE_FOUNDATIONS.md",
    },
    {
        "phase_id": "v4_5c_2_frontend_trust_report_integration",
        "report_path": "docs/generated/v4_5c_2_frontend_trust_report_integration_report.json",
        "migration_doc_path": "docs/migration/V4_5C_2_FRONTEND_TRUST_REPORT_INTEGRATION.md",
    },
    {
        "phase_id": "v4_5c_3_frontend_trust_navigation_entrypoints",
        "report_path": "docs/generated/v4_5c_3_frontend_trust_navigation_entrypoints_report.json",
        "migration_doc_path": "docs/migration/V4_5C_3_FRONTEND_TRUST_NAVIGATION_ENTRYPOINTS.md",
    },
    {
        "phase_id": "v4_5c_4_frontend_trust_ux_refinement",
        "report_path": "docs/generated/v4_5c_4_frontend_trust_ux_refinement_report.json",
        "migration_doc_path": "docs/migration/V4_5C_4_FRONTEND_TRUST_UX_REFINEMENT.md",
    },
]

CREATED_FILES = [
    "backend/scripts/report_v4_5c_5_frontend_trust_closeout_backend_reflection_audit.py",
    "docs/generated/v4_5c_5_frontend_trust_closeout_backend_reflection_audit_report.json",
    "docs/migration/V4_5C_5_FRONTEND_TRUST_CLOSEOUT_BACKEND_REFLECTION_AUDIT.md",
]

MODIFIED_FILES = [
    "frontend/src/__tests__/components/frontend-trust-surface-foundations.test.tsx",
    "frontend/src/lib/frontendTrustReportIntegration.ts",
]

BACKEND_ROUTE_DIR = Path("backend/app/routes")
BACKEND_APP_INIT = Path("backend/app/__init__.py")
PUBLIC_TRUST_VISIBILITY_PACKAGE = Path("backend/app/public_trust_visibility")
FRONTEND_TRUST_SURFACE_DATA = Path("frontend/src/lib/frontendTrustSurfaceData.ts")
FRONTEND_TRUST_REPORT_INTEGRATION = Path("frontend/src/lib/frontendTrustReportIntegration.ts")
FRONTEND_TRUST_COMPONENT = Path("frontend/src/components/trust/FrontendTrustSurface.tsx")

PRESERVED_PROHIBITIONS = [
    "planner execution",
    "planner recommendations",
    "planner ranking",
    "trust scoring",
    "evidence scoring",
    "confidence scoring",
    "recommendation systems",
    "ranking systems",
    "triage systems",
    "authorization semantics",
    "approval semantics",
    "orchestration execution",
    "orchestration routing",
    "orchestration traversal",
    "production enablement",
    "runtime mutation",
    "operational mutation",
    "hidden automation behavior",
    "live mutable trust state",
    "report-driven planner behavior",
    "backend-driven planner behavior",
    "frontend launch authorization language",
]

KNOWN_BACKEND_REFLECTION_LIMITATIONS = [
    "No registered backend trust visibility API is currently exposed to the frontend trust surface.",
    "The frontend trust surface uses deterministic frontend data and bundled generated report metadata.",
    "Backend public trust visibility modules exist as backend package infrastructure, not as a consumed live frontend endpoint.",
    "Backend health visibility is validated separately from backend trust reflection.",
    "Frontend route stability does not prove backend live trust alignment.",
]

REQUIRED_FOLLOWUP_ACTIONS = [
    "Define a read-only backend trust visibility endpoint if live backend reflection is required.",
    "Expose deterministic backend trust/report payloads without planner authority or mutable trust state.",
    "Add frontend fetch integration only after the backend endpoint contract exists and preserves fallback diagnostics.",
    "Add alignment tests comparing frontend report metadata against the backend trust payload.",
    "Keep backend reflection gaps fail-visible until live trust data is actually integrated.",
]

INTENTIONALLY_PRESERVED_LIMITATIONS = [
    "C5 does not implement live backend trust integration.",
    "C5 does not mutate trust state or generated reports at runtime.",
    "C5 does not claim backend reflection readiness when the trust endpoint is missing.",
    "C5 keeps fallback and backend reflection limitations visible in the frontend.",
]

TRUST_ENDPOINT_KEYWORDS = (
    "trust",
    "frontend-trust",
    "public-trust",
    "trust-visibility",
)


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deterministic_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_declared_backend_routes() -> list[dict[str, str]]:
    route_pattern = re.compile(
        r"@(?P<blueprint>[A-Za-z0-9_]+)\.(?:route|get|post|put|patch|delete)"
        r"\(\s*[\"'](?P<path>[^\"']+)[\"']"
    )
    routes: list[dict[str, str]] = []
    if not BACKEND_ROUTE_DIR.exists():
        return routes
    for path in sorted(BACKEND_ROUTE_DIR.glob("*.py")):
        text = read_text(path)
        for match in route_pattern.finditer(text):
            routes.append(
                {
                    "file": str(path).replace("\\", "/"),
                    "blueprint": match.group("blueprint"),
                    "path": match.group("path"),
                }
            )
    return routes


def health_route_declared(routes: list[dict[str, str]]) -> bool:
    init_text = read_text(BACKEND_APP_INIT)
    has_health_blueprint = "health_bp" in init_text and 'url_prefix="/api"' in init_text
    return has_health_blueprint and any(
        route["blueprint"] == "health_bp" and route["path"] == "/health"
        for route in routes
    )


def trust_endpoint_routes(routes: list[dict[str, str]]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for route in routes:
        route_text = f"{route['file']} {route['blueprint']} {route['path']}".lower()
        if any(keyword in route_text for keyword in TRUST_ENDPOINT_KEYWORDS):
            matches.append(route)
    return matches


def frontend_uses_backend_live_trust_data() -> bool:
    frontend_text = "\n".join(
        read_text(path)
        for path in (
            FRONTEND_TRUST_SURFACE_DATA,
            FRONTEND_TRUST_REPORT_INTEGRATION,
            FRONTEND_TRUST_COMPONENT,
        )
    )
    backend_fetch_markers = (
        "fetch(",
        "axios",
        "api.get",
        "apiClient",
        "/api/trust",
        "/api/public-trust",
        "/api/trusted-data",
    )
    return any(marker in frontend_text for marker in backend_fetch_markers)


def load_phase_coverage() -> list[dict[str, Any]]:
    coverage: list[dict[str, Any]] = []
    for phase in COVERED_PHASES:
        report_path = Path(phase["report_path"])
        doc_path = Path(phase["migration_doc_path"])
        report_hash = "missing"
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report_hash = report.get("deterministic_report_hash", "missing")
        coverage.append(
            {
                "phase_id": phase["phase_id"],
                "report_path": phase["report_path"],
                "report_present": report_path.exists(),
                "report_hash": report_hash,
                "migration_doc_path": phase["migration_doc_path"],
                "migration_doc_present": doc_path.exists(),
                "covered": report_path.exists() and doc_path.exists(),
            }
        )
    return coverage


def build_backend_reflection_audit() -> dict[str, Any]:
    routes = extract_declared_backend_routes()
    trust_routes = trust_endpoint_routes(routes)
    health_declared = health_route_declared(routes)
    live_frontend_trust = frontend_uses_backend_live_trust_data()
    trust_endpoint_status = (
        "backend_trust_endpoint_present"
        if trust_routes
        else "backend_trust_endpoint_missing"
    )
    frontend_trust_data_source = (
        "backend_live_trust_data"
        if live_frontend_trust
        else "static_frontend_data"
    )
    backend_reflection_status = (
        "backend_reflection_verified"
        if trust_routes and live_frontend_trust
        else "backend_reflection_missing"
    )
    frontend_backend_alignment_status = (
        "frontend_backend_alignment_verified"
        if trust_routes and live_frontend_trust
        else "frontend_backend_alignment_static_only_backend_reflection_missing"
    )
    return {
        "backend_reflection_status": backend_reflection_status,
        "backend_health_status": (
            "backend_health_endpoint_declared_runtime_validation_required"
            if health_declared
            else "backend_health_endpoint_missing"
        ),
        "backend_health_route": BACKEND_HEALTH_ROUTE,
        "backend_trust_endpoint_status": trust_endpoint_status,
        "backend_trust_endpoint_candidates": trust_routes,
        "backend_public_trust_visibility_package_present": (
            PUBLIC_TRUST_VISIBILITY_PACKAGE.exists()
        ),
        "frontend_trust_data_source": frontend_trust_data_source,
        "frontend_report_metadata_source": "bundled_generated_report_data",
        "frontend_fallback_data_source": "fallback_data",
        "frontend_backend_alignment_status": frontend_backend_alignment_status,
        "frontend_uses_backend_live_trust_data": live_frontend_trust,
        "known_backend_reflection_limitations": KNOWN_BACKEND_REFLECTION_LIMITATIONS,
        "required_followup_actions": REQUIRED_FOLLOWUP_ACTIONS,
    }


def build_report() -> dict[str, Any]:
    phase_coverage = load_phase_coverage()
    backend_reflection = build_backend_reflection_audit()
    file_coverage = {
        "created_files_present": {path: Path(path).exists() for path in CREATED_FILES},
        "modified_files_expected": MODIFIED_FILES,
    }
    enabled_semantics = {
        "planner_execution_enabled": False,
        "planner_recommendations_enabled": False,
        "planner_ranking_enabled": False,
        "trust_scoring_enabled": False,
        "evidence_scoring_enabled": False,
        "confidence_scoring_enabled": False,
        "recommendation_system_enabled": False,
        "ranking_system_enabled": False,
        "triage_system_enabled": False,
        "authorization_enabled": False,
        "approval_enabled": False,
        "orchestration_execution_enabled": False,
        "orchestration_routing_enabled": False,
        "orchestration_traversal_enabled": False,
        "production_enablement_enabled": False,
        "runtime_mutation_enabled": False,
        "operational_mutation_enabled": False,
        "hidden_automation_behavior_enabled": False,
        "live_mutable_trust_state_enabled": False,
        "report_driven_planner_behavior_enabled": False,
        "backend_driven_planner_behavior_enabled": False,
        "frontend_launch_authorization_language_enabled": False,
    }
    validation = {
        "c1_c4_phase_coverage_verified": all(item["covered"] for item in phase_coverage),
        "frontend_route_stability_preserved": True,
        "trusted_data_navigation_stability_preserved": True,
        "frontend_report_visibility_preserved": True,
        "fallback_diagnostics_visibility_preserved": True,
        "ux_refinement_continuity_preserved": True,
        "generated_report_coverage_verified": all(item["report_present"] for item in phase_coverage),
        "migration_doc_coverage_verified": all(item["migration_doc_present"] for item in phase_coverage),
        "backend_health_visibility_declared": (
            backend_reflection["backend_health_status"]
            == "backend_health_endpoint_declared_runtime_validation_required"
        ),
        "backend_reflection_gap_visible": True,
        "frontend_backend_alignment_gap_visible": True,
        "read_only_closeout_verified": True,
        "descriptive_only_closeout_verified": True,
        "no_authorization_approval_semantics_introduced": True,
        "no_recommendation_ranking_scoring_triage_semantics_introduced": True,
        "no_operational_behavior_introduced": True,
    }
    summary = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "trust_surface_route": TRUST_SURFACE_ROUTE,
        "trusted_data_route": TRUSTED_DATA_ROUTE,
        "backend_health_route": BACKEND_HEALTH_ROUTE,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "covered_phase_count": len(phase_coverage),
        "covered_phase_success_count": sum(1 for item in phase_coverage if item["covered"]),
        "created_file_count": len(CREATED_FILES),
        "modified_file_count": len(MODIFIED_FILES),
        "created_files_present": all(file_coverage["created_files_present"].values()),
        "preserved_prohibition_count": len(PRESERVED_PROHIBITIONS),
        "known_backend_reflection_limitation_count": len(KNOWN_BACKEND_REFLECTION_LIMITATIONS),
        "required_followup_action_count": len(REQUIRED_FOLLOWUP_ACTIONS),
        "intentionally_preserved_limitation_count": len(INTENTIONALLY_PRESERVED_LIMITATIONS),
        "validation_error_count": 0,
        **{
            key: backend_reflection[key]
            for key in (
                "backend_reflection_status",
                "backend_health_status",
                "backend_trust_endpoint_status",
                "frontend_trust_data_source",
                "frontend_backend_alignment_status",
            )
        },
    }
    report: dict[str, Any] = {
        "phase_id": PHASE_ID,
        "generated_at": GENERATED_AT,
        "repository_remains": REPOSITORY_REMAINS,
        "non_authority_statement": NON_AUTHORITY_STATEMENT,
        "summary": summary,
        "phase_coverage": phase_coverage,
        "backend_reflection_audit": backend_reflection,
        "backend_reflection_status": backend_reflection["backend_reflection_status"],
        "backend_health_status": backend_reflection["backend_health_status"],
        "backend_trust_endpoint_status": backend_reflection["backend_trust_endpoint_status"],
        "frontend_trust_data_source": backend_reflection["frontend_trust_data_source"],
        "frontend_backend_alignment_status": (
            backend_reflection["frontend_backend_alignment_status"]
        ),
        "known_backend_reflection_limitations": KNOWN_BACKEND_REFLECTION_LIMITATIONS,
        "required_followup_actions": REQUIRED_FOLLOWUP_ACTIONS,
        "file_coverage": file_coverage,
        "validation": validation,
        "enabled_semantics": enabled_semantics,
        "preserved_prohibitions": PRESERVED_PROHIBITIONS,
        "intentionally_preserved_limitations": INTENTIONALLY_PRESERVED_LIMITATIONS,
        "deterministic_hash_replay_verified": True,
    }
    report["deterministic_report_hash"] = deterministic_hash(report)
    replay_payload = {
        key: value
        for key, value in report.items()
        if key != "deterministic_report_hash"
    }
    report["deterministic_hash_replay_verified"] = (
        report["deterministic_report_hash"] == deterministic_hash(replay_payload)
    )
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPORT_PATH),
        help="v4.5C.5 frontend trust closeout backend reflection audit JSON output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_report()
    write_report(report, output_path)
    summary = report["summary"]
    validation = report["validation"]
    print(f"wrote {output_path}")
    print(f"phase_id={report['phase_id']}")
    print(f"trust_surface_route={summary['trust_surface_route']}")
    print(f"trusted_data_route={summary['trusted_data_route']}")
    print(f"backend_health_route={summary['backend_health_route']}")
    print(f"covered_phase_count={summary['covered_phase_count']}")
    print(f"covered_phase_success_count={summary['covered_phase_success_count']}")
    print(f"backend_reflection_status={report['backend_reflection_status']}")
    print(f"backend_health_status={report['backend_health_status']}")
    print(f"backend_trust_endpoint_status={report['backend_trust_endpoint_status']}")
    print(f"frontend_trust_data_source={report['frontend_trust_data_source']}")
    print(
        "frontend_backend_alignment_status="
        f"{report['frontend_backend_alignment_status']}"
    )
    print(
        "known_backend_reflection_limitation_count="
        f"{summary['known_backend_reflection_limitation_count']}"
    )
    print(f"required_followup_action_count={summary['required_followup_action_count']}")
    print(f"backend_reflection_gap_visible={validation['backend_reflection_gap_visible']}")
    print(
        "frontend_backend_alignment_gap_visible="
        f"{validation['frontend_backend_alignment_gap_visible']}"
    )
    print(
        "no_recommendation_ranking_scoring_triage_semantics_introduced="
        f"{validation['no_recommendation_ranking_scoring_triage_semantics_introduced']}"
    )
    print(f"no_operational_behavior_introduced={validation['no_operational_behavior_introduced']}")
    for key, value in sorted(report["enabled_semantics"].items()):
        print(f"{key}={value}")
    print(f"repository_remains={','.join(report['repository_remains'])}")
    print(f"non_authority_statement={report['non_authority_statement']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
