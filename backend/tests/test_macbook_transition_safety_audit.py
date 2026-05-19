from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "backend" / "scripts" / "report_macbook_transition_safety_audit.py"


def _load_report_module():
    spec = importlib.util.spec_from_file_location("macbook_transition_safety_audit", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_macbook_transition_audit_report_is_deterministic():
    module = _load_report_module()

    first = module.build_report()
    second = module.build_report()

    assert first == second
    assert first["report_hash"] == second["report_hash"]
    assert first["schema_version"] == "macbook_transition_safety_audit.v1"
    assert first["audit_status"] == "read_only_descriptive_transition_audit"


def test_macbook_transition_audit_classifies_setup_required_without_blockers():
    module = _load_report_module()
    report = module.build_report()

    assert report["transition_classification"] == "macbook_transition_safe_with_setup_required"
    assert report["blockers"] == []
    assert len(report["warnings"]) >= 1
    assert report["windows_pc_still_required"]["required"] is False


def test_macbook_transition_audit_inventories_cross_platform_risks():
    module = _load_report_module()
    report = module.build_report()

    path_scan = report["path_assumption_scan"]
    active_paths = {
        entry["path"] for entry in path_scan["active_workflow_files_with_path_assumptions"]
    }

    assert "docs/LOCAL_DEVELOPMENT.md" in active_paths
    assert "docs/WORKSPACE_HEALTHCHECK.md" in active_paths
    assert "package.json" in active_paths
    assert path_scan["generated_report_windows_source_path_hits"] >= 1


def test_macbook_transition_audit_confirms_proxy_and_docker_visibility():
    module = _load_report_module()
    report = module.build_report()

    docker_proxy = report["docker_and_proxy_compatibility"]

    assert docker_proxy["browser_api_base_is_relative_in_docker"] is True
    assert docker_proxy["vite_proxy_target_is_container_internal_in_docker"] is True
    assert docker_proxy["vite_proxy_target_env_supported"] is True
    assert docker_proxy["has_apple_silicon_blocking_platform_pin"] is False


def test_macbook_transition_audit_preserves_prohibitions():
    module = _load_report_module()
    report = module.build_report()

    preserved = report["prohibitions_preserved"]
    assert preserved == {
        "planner_execution_enabled": False,
        "planner_recommendations_enabled": False,
        "ranking_enabled": False,
        "scoring_enabled": False,
        "production_consumption_enabled": False,
        "runtime_mutation_enabled": False,
        "orchestration_execution_enabled": False,
    }
