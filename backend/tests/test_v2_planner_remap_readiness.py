from scripts.report_v2_planner_remap_readiness import (
    ALLOWED_CLASSIFICATIONS,
    build_v2_planner_remap_readiness_report,
)


def test_v2_planner_remap_readiness_report_has_required_sections():
    report = build_v2_planner_remap_readiness_report()

    assert report["summary"]["status"] == "ready_for_review"
    assert "production_inventory" in report
    assert "dependency_classifications" in report
    assert "future_remap_sequence" in report
    assert "safety_confirmations" in report


def test_v2_planner_remap_readiness_classifications_are_allowed():
    report = build_v2_planner_remap_readiness_report()

    classifications = {
        item["classification"]
        for item in report["dependency_classifications"]
    }

    assert classifications
    assert classifications <= ALLOWED_CLASSIFICATIONS
    assert "blocked_by_value_normalization" in classifications
    assert "blocked_by_unsupported_mechanics" in classifications
    assert "blocked_by_identity_resolution" in classifications


def test_v2_planner_remap_readiness_preserves_safety_state():
    report = build_v2_planner_remap_readiness_report()
    safety = report["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["planner_output_changed"] is False
    assert safety["crafting_behavior_changed"] is False
    assert safety["simulation_behavior_changed"] is False
    assert safety["stat_aggregation_behavior_changed"] is False
    assert safety["value_normalization_promoted"] is False
    assert safety["skill_identity_bridge_added"] is False
    assert safety["stable_calculable_count"] == 0
    assert safety["eligible_planner_calculable_count"] == 0
    assert safety["skill_identity_bridge_status"] == "unbridged"


def test_v2_planner_remap_readiness_sequence_is_ordered_and_non_empty():
    report = build_v2_planner_remap_readiness_report()
    sequence = report["future_remap_sequence"]

    assert len(sequence) >= 5
    assert [phase["order"] for phase in sequence] == list(range(1, len(sequence) + 1))
    assert all(phase["required_tests"] for phase in sequence)
    assert sequence[0]["name"].lower().startswith("read-only")


def test_v2_planner_remap_readiness_finds_legacy_entrypoints():
    report = build_v2_planner_remap_readiness_report()
    backend_paths = {
        item["path"]
        for item in report["production_inventory"]["backend_entrypoints"]
    }
    legacy_paths = {
        item["path"]
        for item in report["hardcoded_and_legacy_data_sources"]
    }

    assert "backend/app/routes/ref.py" in backend_paths
    assert "backend/app/routes/craft.py" in backend_paths
    assert "backend/app/routes/simulate.py" in backend_paths
    assert "backend/app/engines/stat_engine.py" in legacy_paths
    assert "backend/app/game_data/game_data_loader.py" in legacy_paths
