"""Generate the frontend/backend gameplay route audit report.

The report is deterministic and descriptive-only. It documents the observed
browser-facing gameplay data loading failure, the scoped configuration fix, and
the remaining route/data limitations without changing gameplay behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    REPO_ROOT
    / "docs"
    / "generated"
    / "frontend_backend_gameplay_route_audit_report.json"
)

AUDITED_FRONTEND_ROUTES = [
    {
        "route_path": "/classes",
        "page_component": "frontend/src/pages/classes/ClassesPage.tsx",
        "backend_calls_made": ["GET /api/ref/classes"],
        "expected_response_shape": "{data: Record<className, classMeta>, meta, errors}",
        "current_browser_visible_status": (
            "pre_fix_reproduced_network_error_post_fix_expected_loaded_classes"
        ),
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/passives",
        "page_component": "frontend/src/pages/PassiveTreePage.tsx",
        "backend_calls_made": ["GET /api/passives/<class>"],
        "expected_response_shape": "{data: {class, mastery, count, nodes, grouped}, meta, errors}",
        "current_browser_visible_status": (
            "pre_fix_reproduced_loading_network_failure_post_fix_expected_loaded_tree"
        ),
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/builds",
        "page_component": "frontend/src/components/features/builds/BuildsPage.tsx",
        "backend_calls_made": ["GET /api/builds"],
        "expected_response_shape": "{data: BuildListItem[], meta: pagination, errors}",
        "current_browser_visible_status": "affected_by_same_browser_api_base_url_mismatch",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/build",
        "page_component": "frontend/src/components/features/build/BuildPlannerPage.tsx",
        "backend_calls_made": [
            "GET /api/version",
            "GET /api/builds/<slug>",
            "POST /api/builds/<slug>/simulate",
            "GET /api/builds/<slug>/optimize",
            "POST /api/builds/<slug>/view",
        ],
        "expected_response_shape": "route-dependent API envelopes",
        "current_browser_visible_status": "route_exists_build_planner_aliases_documented",
        "fallback_behavior_exists": "partial_client_side_defaults",
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/build-planner",
        "page_component": None,
        "backend_calls_made": [],
        "expected_response_shape": None,
        "current_browser_visible_status": "not_registered_real_route_is_/build",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/craft",
        "page_component": "frontend/src/components/features/craft/CraftSimulatorPage.tsx",
        "backend_calls_made": [
            "GET /api/ref/affixes",
            "GET /api/ref/base-items",
            "GET /api/ref/fp-ranges",
            "POST /api/craft",
            "GET /api/craft/<slug>",
            "POST /api/craft/<slug>/action",
            "GET /api/craft/<slug>/summary",
        ],
        "expected_response_shape": "route-dependent API envelopes",
        "current_browser_visible_status": "affected_by_same_browser_api_base_url_mismatch",
        "fallback_behavior_exists": "client_side_crafting_preview_only",
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/crafting-lab",
        "page_component": None,
        "backend_calls_made": [],
        "expected_response_shape": None,
        "current_browser_visible_status": "not_registered_real_routes_are_/craft_and_/crafting",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/crafting",
        "page_component": "frontend/src/pages/crafting/CraftingPage.tsx",
        "backend_calls_made": ["POST /api/craft/predict", "GET /api/ref/affixes"],
        "expected_response_shape": "{data: CraftPredictResponse, meta, errors}",
        "current_browser_visible_status": "route_exists_backend_fetch_user_triggered",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/bis-search",
        "page_component": "frontend/src/pages/bis/BisSearchPage.tsx",
        "backend_calls_made": ["GET /api/ref/affixes", "POST /api/bis/search"],
        "expected_response_shape": "{data: BisSearchResponse, meta, errors}",
        "current_browser_visible_status": "route_exists_backend_fetch_user_triggered",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/simulation",
        "page_component": "frontend/src/App.tsx",
        "backend_calls_made": [],
        "expected_response_shape": "redirects_to_/encounter",
        "current_browser_visible_status": "registered_alias_to_/encounter",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/encounter",
        "page_component": "frontend/src/pages/simulation/SimulationPage.tsx",
        "backend_calls_made": [
            "POST /api/simulate/encounter",
            "POST /api/simulate/encounter-build",
        ],
        "expected_response_shape": "{data: EncounterResult, meta, errors}",
        "current_browser_visible_status": "route_exists_backend_fetch_user_triggered",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/meta",
        "page_component": "frontend/src/components/features/builds/MetaSnapshotPage.tsx",
        "backend_calls_made": ["GET /api/meta/snapshot", "GET /api/meta/trending"],
        "expected_response_shape": "{data: meta payload, meta, errors}",
        "current_browser_visible_status": "affected_by_same_browser_api_base_url_mismatch",
        "fallback_behavior_exists": False,
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/trusted-data",
        "page_component": "frontend/src/pages/TrustedDataExplanationPage.tsx",
        "backend_calls_made": [],
        "expected_response_shape": None,
        "current_browser_visible_status": "static_route_http_200",
        "fallback_behavior_exists": "static_explanation",
        "failure_is_fail_visible": True,
    },
    {
        "route_path": "/trusted-data/frontend-trust",
        "page_component": "frontend/src/pages/FrontendTrustSurfaceFoundationsPage.tsx",
        "backend_calls_made": ["GET /api/trust/visibility"],
        "expected_response_shape": "backend trust visibility payload",
        "current_browser_visible_status": "route_exists_trust_endpoint_healthy",
        "fallback_behavior_exists": True,
        "failure_is_fail_visible": True,
    },
]


BACKEND_ROUTE_INVENTORY = [
    {
        "route_path": "/api/health",
        "router_module": "backend/app/routes/health.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "verified_http_200_after_backend_startup",
        "response_shape": "health status JSON",
    },
    {
        "route_path": "/api/trust/visibility",
        "router_module": "backend/app/routes/trust.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "verified_http_200_after_backend_startup",
        "response_shape": "expanded read-only trust visibility payload",
    },
    {
        "route_path": "/api/ref/classes",
        "router_module": "backend/app/routes/ref.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "verified_http_200_direct_and_vite_proxy",
        "response_shape": "{data: Record<className, classMeta>, meta, errors}",
    },
    {
        "route_path": "/api/passives",
        "router_module": "backend/app/routes/passives.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "verified_http_200_via_backend_contract_tests",
        "response_shape": "{data: {class, mastery, count, nodes, grouped}, meta, errors}",
    },
    {
        "route_path": "/api/passives/Acolyte",
        "router_module": "backend/app/routes/passives.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "verified_http_200_direct_and_vite_proxy",
        "response_shape": "{data: {class, mastery, count, nodes, grouped}, meta, errors}",
    },
    {
        "route_path": "/api/builds",
        "router_module": "backend/app/routes/builds.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "mounted_not_browser_retested_before_fix",
        "response_shape": "{data: BuildListItem[], meta, errors}",
    },
    {
        "route_path": "/api/craft/predict",
        "router_module": "backend/app/routes/craft.py",
        "http_method": "POST",
        "mounted": True,
        "docker_accessible_status": "mounted_user_action_endpoint_not_auto_invoked",
        "response_shape": "{data: CraftPredictResult, meta, errors}",
    },
    {
        "route_path": "/api/bis/search",
        "router_module": "backend/app/routes/bis.py",
        "http_method": "POST",
        "mounted": True,
        "docker_accessible_status": "mounted_user_action_endpoint_not_auto_invoked",
        "response_shape": "{data: BisSearchResponse, meta, errors}",
    },
    {
        "route_path": "/api/simulate/encounter",
        "router_module": "backend/app/routes/simulate.py",
        "http_method": "POST",
        "mounted": True,
        "docker_accessible_status": "mounted_user_action_endpoint_not_auto_invoked",
        "response_shape": "{data: EncounterResult, meta, errors}",
    },
    {
        "route_path": "/api/meta/snapshot",
        "router_module": "backend/app/routes/meta.py",
        "http_method": "GET",
        "mounted": True,
        "docker_accessible_status": "mounted_not_browser_retested_before_fix",
        "response_shape": "{data: FullMetaSnapshot, meta, errors}",
    },
]


PROHIBITIONS_PRESERVED = [
    "planner_execution",
    "build_recommendations",
    "ranking",
    "scoring",
    "automatic_optimization",
    "production_enablement",
    "runtime_mutation",
    "mutable_trust_state",
    "fake_gameplay_data",
    "broad_frontend_redesign",
    "broad_backend_rewrite",
]


def _file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_status(relative_path: str) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    return {
        "path": relative_path,
        "available": path.exists(),
        "sha256": _file_hash(path),
    }


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def build_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": "frontend_backend_gameplay_route_audit.v1",
        "audit_status": "diagnostics_stabilized_with_scoped_api_base_fix",
        "frontend_route_inventory": AUDITED_FRONTEND_ROUTES,
        "backend_route_inventory": BACKEND_ROUTE_INVENTORY,
        "api_client_audit": {
            "shared_client": "frontend/src/lib/api.ts",
            "base_url_resolution": [
                "VITE_API_BASE_URL",
                "VITE_API_URL",
                "/api",
            ],
            "browser_facing_api_base_after_fix": "/api",
            "pre_fix_browser_facing_api_base": "http://backend:5000/api",
            "pre_fix_failure": (
                "Browser-side fetches attempted the Docker service hostname "
                "backend, which is not resolvable from the host browser."
            ),
            "error_normalization": (
                "Fetch failures remain fail-visible as Network error - check your connection."
            ),
            "scoped_config_fix": (
                "VITE_API_BASE_URL remains browser-facing while "
                "VITE_API_PROXY_TARGET supplies the Vite container-to-backend target."
            ),
        },
        "docker_networking_audit": {
            "frontend_service": "frontend",
            "backend_service": "backend",
            "frontend_port": "5173:5173",
            "backend_port": "5050:5000",
            "correct_browser_facing_api_path": "/api",
            "correct_container_proxy_target": "http://backend:5000",
            "vite_proxy_paths": ["/api", "/experimental"],
            "nginx_proxy_path": "/api/",
            "pre_fix_mismatch": (
                "Docker Compose configured VITE_API_BASE_URL to "
                "http://backend:5000/api, bypassing the Vite proxy from the browser."
            ),
            "post_fix_status": (
                "Docker Compose now uses /api for browser requests and "
                "VITE_API_PROXY_TARGET for container-internal proxying."
            ),
        },
        "gameplay_data_source_audit": {
            "classes_source": {
                "module": "backend/app/routes/ref.py",
                "source_type": "static backend CLASS_META",
                "expected_count": 5,
                "fake_data_introduced": False,
            },
            "passives_source": {
                "module": "backend/app/routes/passives.py",
                "db_seed_command": "flask seed-passives",
                "fallback_file": _file_status("data/classes/passives.json"),
                "fake_data_introduced": False,
            },
            "affixes_source": {
                "fallback_file": _file_status("data/items/affixes.json"),
                "fake_data_introduced": False,
            },
            "base_items_source": {
                "module": "backend/app/engines/base_engine.py",
                "fake_data_introduced": False,
            },
            "missing_data_classification": "no_missing_classes_or_passives_data_detected",
        },
        "browser_reproduction_results": {
            "pre_fix_classes": {
                "route": "http://localhost:5173/classes",
                "document_status": 200,
                "visible_failure": "Error loading classes / Network error - check your connection",
                "root_observation": "client_fetch_failed_after_spa_loaded",
            },
            "pre_fix_passives": {
                "route": "http://localhost:5173/passives",
                "document_status": 200,
                "visible_failure": "Loading passive tree persisted until network failure state",
                "root_observation": "client_fetch_failed_after_spa_loaded",
            },
            "backend_direct_probe": {
                "GET http://localhost:5050/api/ref/classes": 200,
                "GET http://localhost:5050/api/passives/Acolyte": 200,
            },
            "vite_proxy_probe": {
                "GET http://localhost:5173/api/ref/classes": 200,
                "GET http://localhost:5173/api/passives/Acolyte": 200,
            },
            "post_fix_browser_verification": {
                "/classes": "classes_loaded_count_5_no_browser_error_logs",
                "/passives": "passive_tree_loaded_acolyte_base_nodes_no_browser_error_logs",
                "/builds": "community_builds_route_loaded_empty_state_no_browser_error_logs",
                "/meta": "meta_snapshot_route_loaded_empty_state_no_browser_error_logs",
                "/trusted-data/frontend-trust": "trust_surface_loaded_no_browser_error_logs",
            },
        },
        "root_cause_classification": ["api_base_url_mismatch"],
        "fixes_applied": [
            {
                "id": "docker_browser_api_base_path_corrected",
                "files": ["docker-compose.yml"],
                "description": "Changed frontend VITE_API_BASE_URL to /api for browser-facing requests.",
            },
            {
                "id": "vite_proxy_target_split",
                "files": ["frontend/vite.config.ts"],
                "description": (
                    "Added VITE_API_PROXY_TARGET support so the Vite dev server "
                    "can proxy /api to http://backend:5000 inside Docker."
                ),
            },
            {
                "id": "focused_proxy_test_added",
                "files": ["frontend/src/__tests__/config/vite-proxy-routing.test.ts"],
                "description": "Added coverage for the separated browser base path and proxy target.",
            },
        ],
        "remaining_limitations": [
            "POST-backed gameplay routes are mounted but require user action or payload-specific tests.",
            "/build-planner and /crafting-lab are not registered routes; current routes are /build and /craft or /crafting.",
            "No fake gameplay data was introduced to mask unavailable or empty backend data.",
        ],
        "required_followup_actions": [
            "If additional page-specific errors appear after connectivity is restored, audit response shapes for that page.",
            "Keep gameplay route diagnostics separate from v4.6 governance aggregation work.",
        ],
        "prohibitions_preserved": PROHIBITIONS_PRESERVED,
        "trust_visibility_regression_guard": {
            "health_endpoint": "/api/health",
            "trust_endpoint": "/api/trust/visibility",
            "frontend_trust_route": "/trusted-data/frontend-trust",
            "status": "preserved",
        },
    }
    report["report_hash"] = hashlib.sha256(_canonical_json(report).encode("utf-8")).hexdigest()
    return report


def write_report(path: Path = REPORT_PATH) -> dict[str, Any]:
    report = build_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json(report), encoding="utf-8")
    return report


def main() -> None:
    report = write_report()
    print(
        json.dumps(
            {
                "report_path": str(REPORT_PATH.relative_to(REPO_ROOT)),
                "report_hash": report["report_hash"],
                "root_cause_classification": report["root_cause_classification"],
                "audit_status": report["audit_status"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
