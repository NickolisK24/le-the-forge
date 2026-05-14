from pathlib import Path

from app.planner_adapters.v2.golden_baselines import BASELINE_STATUSES, build_golden_baseline_plan
from scripts.report_v2_golden_baseline_plan import build_v2_golden_baseline_plan_report


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_v2_golden_baseline_plan_has_required_top_level_keys():
    report = build_v2_golden_baseline_plan_report()

    assert report["schema_version"] == "v2.golden_baseline_plan.1"
    for key in (
        "summary",
        "baseline_categories",
        "fixture_paths",
        "status_counts",
        "blocker_summary",
        "future_assertion_requirements",
        "required_preconditions_before_mechanical_remap",
        "safety_confirmations",
    ):
        assert key in report


def test_v2_golden_baseline_statuses_are_strict():
    plan = build_golden_baseline_plan()

    statuses = {category["current_status"] for category in plan["baseline_categories"]}
    assert statuses.issubset(BASELINE_STATUSES)
    assert plan["allowed_statuses"] == sorted(BASELINE_STATUSES)


def test_v2_golden_baseline_fixture_paths_are_unique_and_exist_for_safe_now():
    plan = build_golden_baseline_plan()
    fixture_paths = [category["fixture_path"] for category in plan["baseline_categories"]]

    assert len(plan["fixture_paths"]) == len(set(fixture_paths))
    for category in plan["baseline_categories"]:
        if category["safe_to_create_now"]:
            fixture_path = Path(category["fixture_path"])
            assert not fixture_path.is_absolute()
            assert (REPO_ROOT / fixture_path).exists()


def test_v2_golden_baseline_mechanical_categories_are_blocked():
    plan = build_golden_baseline_plan()

    for category in plan["baseline_categories"]:
        if category["mechanical_calculation_involved"]:
            assert category["current_status"] != "safe_non_mechanical_now"
            assert category["safe_to_create_now"] is False
            assert category["production_output_affected"] is False


def test_v2_golden_baseline_safe_now_fixtures_are_non_mechanical():
    plan = build_golden_baseline_plan()

    for category in plan["baseline_categories"]:
        if category["safe_to_create_now"]:
            assert category["mechanical_calculation_involved"] is False
            assert category["production_output_affected"] is False


def test_v2_golden_baseline_preserves_safety_state():
    report = build_v2_golden_baseline_plan_report()

    assert report["summary"]["production_consumed"] is False
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["summary"]["value_normalization_status"] == "audit_only"
    assert report["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert report["safety_confirmations"]["planner_output_changed"] is False
    assert report["safety_confirmations"]["value_normalization_promoted"] is False
    assert report["safety_confirmations"]["skill_identity_bridge_added"] is False


def test_v2_golden_baseline_dry_run_reference_keeps_blocked_state():
    report = build_v2_golden_baseline_plan_report()

    assert report["dry_run_reference"]["modifier_row_count"] == 19398
    assert report["dry_run_reference"]["blocked_modifier_count"] == 19398
    assert report["dry_run_reference"]["comparison_category_summary"]["blocked_by_value_normalization"] == 19398
