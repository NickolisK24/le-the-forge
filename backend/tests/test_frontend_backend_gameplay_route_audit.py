from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "backend" / "scripts" / "report_frontend_backend_gameplay_route_audit.py"


def _load_report_module():
    spec = importlib.util.spec_from_file_location("gameplay_route_audit", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_gameplay_route_audit_report_is_deterministic():
    module = _load_report_module()

    first = module.build_report()
    second = module.build_report()

    assert first == second
    assert first["report_hash"] == second["report_hash"]
    assert first["root_cause_classification"] == ["api_base_url_mismatch"]
    assert first["audit_status"] == "diagnostics_stabilized_with_scoped_api_base_fix"


def test_gameplay_route_audit_inventories_frontend_and_backend_routes():
    module = _load_report_module()
    report = module.build_report()

    frontend_routes = {entry["route_path"] for entry in report["frontend_route_inventory"]}
    backend_routes = {entry["route_path"] for entry in report["backend_route_inventory"]}

    assert {
        "/classes",
        "/passives",
        "/builds",
        "/build",
        "/craft",
        "/bis-search",
        "/simulation",
        "/meta",
        "/trusted-data",
        "/trusted-data/frontend-trust",
    }.issubset(frontend_routes)
    assert {
        "/api/health",
        "/api/trust/visibility",
        "/api/ref/classes",
        "/api/passives/Acolyte",
    }.issubset(backend_routes)


def test_gameplay_route_audit_documents_proxy_fix_and_no_fake_data():
    module = _load_report_module()
    report = module.build_report()

    assert report["api_client_audit"]["browser_facing_api_base_after_fix"] == "/api"
    assert report["docker_networking_audit"]["correct_container_proxy_target"] == "http://backend:5000"
    assert report["gameplay_data_source_audit"]["classes_source"]["fake_data_introduced"] is False
    assert report["gameplay_data_source_audit"]["passives_source"]["fake_data_introduced"] is False
    assert report["gameplay_data_source_audit"]["missing_data_classification"] == (
        "no_missing_classes_or_passives_data_detected"
    )


def test_core_gameplay_routes_return_expected_envelopes(client):
    route_expectations = {
        "/api/health": None,
        "/api/trust/visibility": "schema_version",
        "/api/ref/classes": "data",
        "/api/passives/Acolyte": "data",
    }

    for route, expected_key in route_expectations.items():
        response = client.get(route)
        assert response.status_code == 200, route
        payload = response.get_json()
        assert isinstance(payload, dict), route
        if expected_key is not None:
            assert expected_key in payload, route


def test_gameplay_route_audit_preserves_stabilization_boundaries():
    module = _load_report_module()
    report = module.build_report()

    preserved = set(report["prohibitions_preserved"])
    assert {
        "planner_execution",
        "build_recommendations",
        "ranking",
        "scoring",
        "production_enablement",
        "runtime_mutation",
        "mutable_trust_state",
        "fake_gameplay_data",
    }.issubset(preserved)
