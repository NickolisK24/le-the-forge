from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.bundle_item_type_context_report import (
    ContextInput,
    build_context_coverage_report,
    render_context_coverage_report,
)
from app.game_data.bundle_item_type_dry_run_resolver import BundleItemTypeDryRunResolver


def _report(inputs):
    return build_context_coverage_report(inputs, BundleItemTypeDryRunResolver())


def test_context_report_calculates_status_counts_from_inputs():
    report = _report(
        [
            ContextInput("belt", 2),
            ContextInput("helm", 0),
            ContextInput("axe"),
            ContextInput("spear"),
            ContextInput("unknown_type"),
        ]
    )

    assert report["production_safe"] is False
    assert report["total_inputs"] == 5
    assert report["with_base_type_id"] == 2
    assert report["missing_base_type_id"] == 1
    assert report["status_counts"]["resolved"] == 2
    assert report["status_counts"]["needs_context"] == 1
    assert report["status_counts"]["needs_review"] == 1
    assert report["status_counts"]["unresolved"] == 1


def test_inputs_with_base_type_id_resolve_when_mapping_exists():
    report = _report([ContextInput("belt", 2), ContextInput("helm", 0)])

    assert report["with_base_type_id"] == 2
    assert report["status_counts"]["resolved"] == 2
    assert {item["bundle_item_type_id"] for item in report["resolved_examples"]} == {"belt", "helmet"}


def test_collapsed_slug_without_base_type_id_counts_missing_context():
    report = _report([ContextInput("axe")])

    assert report["missing_base_type_id"] == 1
    assert report["status_counts"]["needs_context"] == 1
    assert report["collapsed_groups"][0]["forge_item_type"] == "axe"
    assert report["collapsed_groups"][0]["required_context"] == ["base_type_id"]


def test_idol_shape_without_base_type_id_counts_missing_context():
    report = _report([ContextInput("idol_1x1")])

    assert report["missing_base_type_id"] == 1
    assert report["status_counts"]["needs_context"] == 1
    assert report["collapsed_groups"][0]["forge_item_type"] == "idol_1x1"


def test_spear_is_needs_review_not_resolved():
    report = _report([ContextInput("spear", 14)])

    assert report["status_counts"]["needs_review"] == 1
    assert report["status_counts"]["resolved"] == 0
    assert report["needs_review_examples"][0]["forge_item_type"] == "spear"


def test_subtype_id_alone_is_not_sufficient_context():
    report = _report([ContextInput("belt", subtype_id=1)])

    assert report["with_base_type_id"] == 0
    assert report["missing_base_type_id"] == 1
    assert report["status_counts"]["needs_context"] == 1
    assert report["subtype_id_only_matching_attempted"] is False
    assert "subtype_id" in report["needs_context_examples"][0]["warnings"][0]


def test_report_shape_and_rendered_output_include_expected_keys():
    report = _report([ContextInput("belt", 2), ContextInput("axe")])
    rendered = render_context_coverage_report(report)

    for key in {
        "production_safe",
        "total_inputs",
        "with_base_type_id",
        "missing_base_type_id",
        "status_counts",
        "collapsed_groups",
        "needs_context_examples",
        "resolved_examples",
        "needs_review_examples",
        "recommendations",
    }:
        assert key in report
    assert "Bundle Item Type Context Coverage Report" in rendered
    assert "production_safe: false" in rendered


def test_output_path_guard_refuses_production_data_directory():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "context.md")
