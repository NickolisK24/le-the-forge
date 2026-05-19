from __future__ import annotations

from pathlib import Path

from app.game_data.trusted_gameplay_data_coverage_audit import (
    CLASSIFICATION_KEYS,
    ENABLED_SEMANTICS,
    REPORT_PATHS,
    build_all_trusted_gameplay_data_coverage_reports,
    deterministic_hash,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _reports():
    return build_all_trusted_gameplay_data_coverage_reports(REPO_ROOT)


def test_builds_all_required_deterministic_reports():
    reports = _reports()

    assert set(reports) == set(REPORT_PATHS.values())
    for report in reports.values():
        assert report["deterministic_hash_replay_verified"] is True
        replay = dict(report)
        report_hash = replay.pop("deterministic_report_hash")
        assert report_hash == deterministic_hash(replay)

    rebuilt = _reports()
    assert {
        path: report["deterministic_report_hash"]
        for path, report in reports.items()
    } == {
        path: report["deterministic_report_hash"]
        for path, report in rebuilt.items()
    }


def test_coverage_report_inventories_required_gameplay_domains():
    coverage = _reports()[REPORT_PATHS["coverage"]]
    systems = {record["system_id"]: record for record in coverage["audited_systems"]}

    for required in [
        "classes",
        "masteries",
        "passive_trees",
        "passives",
        "skills",
        "skill_trees",
        "skill_nodes",
        "items",
        "uniques",
        "set_items",
        "affixes",
        "idols",
        "blessings",
        "crafting_materials",
        "monolith_systems",
        "echo_systems",
        "bosses",
        "ailments",
        "damage_types",
        "mechanics",
        "tags",
        "gameplay_backend_payloads",
        "gameplay_frontend_payloads",
        "trusted_extraction_manifests",
        "trusted_generated_assets",
        "schema_mappings",
        "planner_facing_gameplay_contracts",
    ]:
        assert required in systems
        assert set(systems[required]["classification_flags"]) == set(CLASSIFICATION_KEYS)


def test_unsupported_missing_stale_hardcoded_and_planner_gap_states_are_visible():
    coverage = _reports()[REPORT_PATHS["coverage"]]
    totals = coverage["classification_totals"]
    systems = {record["system_id"]: record for record in coverage["audited_systems"]}

    assert totals["partial"] > 0
    assert totals["missing"] > 0
    assert totals["stale"] > 0
    assert totals["unsupported"] > 0
    assert totals["hardcoded"] > 0
    assert totals["schema_mismatch"] > 0
    assert totals["planner_dependency_gap"] > 0

    assert systems["skills"]["classification_flags"]["unsupported"] is True
    assert systems["skills"]["classification_flags"]["schema_mismatch"] is True
    assert systems["echo_systems"]["classification_flags"]["missing"] is True
    assert systems["crafting_materials"]["classification_flags"]["hardcoded"] is True
    assert systems["planner_facing_gameplay_contracts"]["classification_flags"]["planner_dependency_gap"] is True


def test_frontend_backend_visibility_and_route_expectations_are_reported():
    coverage = _reports()[REPORT_PATHS["coverage"]]
    routes = {record["route_id"]: record for record in coverage["stabilized_route_expectations"]}

    for route_id in [
        "backend_health",
        "backend_trust_visibility",
        "frontend_classes",
        "frontend_passives",
        "frontend_trusted_data",
        "frontend_trusted_data_frontend_trust",
    ]:
        assert routes[route_id]["visible"] is True

    systems = {record["system_id"]: record for record in coverage["audited_systems"]}
    assert systems["classes"]["classification_flags"]["frontend_visible"] is True
    assert systems["classes"]["classification_flags"]["backend_visible"] is True
    assert systems["gameplay_backend_payloads"]["classification_flags"]["backend_visible"] is True
    assert systems["gameplay_frontend_payloads"]["classification_flags"]["frontend_visible"] is True


def test_audit_preserves_non_operational_boundaries():
    coverage = _reports()[REPORT_PATHS["coverage"]]

    assert not any(ENABLED_SEMANTICS.values())
    assert coverage["summary"]["non_operational_boundary_preserved"] is True
    assert coverage["validation"]["non_operational_boundary_preserved"] is True
    assert "READ-ONLY" in coverage["repository_remains"]
    assert "DESCRIPTIVE-ONLY" in coverage["repository_remains"]
    assert "FAIL-VISIBLE" in coverage["repository_remains"]
