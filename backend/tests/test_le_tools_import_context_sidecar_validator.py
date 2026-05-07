from copy import deepcopy
from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.le_tools_import_context_sidecar import build_sidecar_from_fixture
from app.game_data.le_tools_import_context_sidecar_validator import validate_sidecar_artifact


def _sidecar():
    sidecar, _mapped = build_sidecar_from_fixture()
    return sidecar


def test_current_built_sidecar_validates_with_warning_not_failed():
    result = validate_sidecar_artifact(_sidecar())

    assert result["status"] == "warning"
    assert result["production_safe"] is False
    assert result["errors"] == []
    assert result["summary"] == {
        "total_items": 12,
        "resolved": 8,
        "needs_context": 2,
        "needs_review": 1,
        "deferred": 0,
        "unresolved": 1,
    }


def test_production_safe_true_fails():
    sidecar = _sidecar()
    sidecar["production_safe"] = True

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("production_safe" in error for error in result["errors"])


def test_item_resolver_production_safe_true_fails():
    sidecar = _sidecar()
    sidecar["items"][0]["resolver"]["production_safe"] = True

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("resolver.production_safe" in error for error in result["errors"])


def test_subtype_only_resolved_item_fails():
    sidecar = _sidecar()
    item = sidecar["items"][9]
    item["resolver"]["status"] = "resolved"
    item["resolver"]["bundle_item_type_id"] = "belt"
    sidecar["summary"]["needs_context"] -= 1
    sidecar["summary"]["resolved"] += 1

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("subtype_only record resolved" in error for error in result["errors"])


def test_name_only_resolved_item_fails():
    sidecar = _sidecar()
    item = sidecar["items"][11]
    item["resolver"]["status"] = "resolved"
    item["resolver"]["bundle_item_type_id"] = "helmet"
    sidecar["summary"]["unresolved"] -= 1
    sidecar["summary"]["resolved"] += 1

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("name-only record resolved" in error for error in result["errors"])


def test_spear_resolved_item_fails():
    sidecar = _sidecar()
    item = sidecar["items"][10]
    item["resolver"]["status"] = "resolved"
    item["resolver"]["bundle_item_type_id"] = "two_handed_spear"
    sidecar["summary"]["needs_review"] -= 1
    sidecar["summary"]["resolved"] += 1

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("spear resolved" in error for error in result["errors"])


def test_collapsed_slug_without_base_type_id_resolved_fails():
    sidecar = _sidecar()
    item = sidecar["items"][8]
    item["resolver"]["status"] = "resolved"
    item["resolver"]["bundle_item_type_id"] = "one_handed_axe"
    sidecar["summary"]["needs_context"] -= 1
    sidecar["summary"]["resolved"] += 1

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("collapsed slug missing base_type_id" in error for error in result["errors"])


def test_summary_mismatch_fails():
    sidecar = _sidecar()
    sidecar["summary"]["resolved"] = 999

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("summary resolved" in error for error in result["errors"])


def test_missing_required_sections_fail():
    sidecar = _sidecar()
    del sidecar["items"][0]["raw"]

    result = validate_sidecar_artifact(sidecar)

    assert result["status"] == "failed"
    assert any("missing raw section" in error for error in result["errors"])


def test_warnings_are_emitted_for_current_known_limitations():
    result = validate_sidecar_artifact(_sidecar())

    assert any("mapped.has_item_type is false" in warning for warning in result["warnings"])
    assert any("test-only pairing" in warning for warning in result["warnings"])
    assert any("subtype_id without base_type_id" in warning for warning in result["warnings"])
    assert any("unresolved" in warning for warning in result["warnings"])
    assert any("need base_type_id context" in warning for warning in result["warnings"])
    assert any("manual review" in warning for warning in result["warnings"])


def test_validation_does_not_mutate_input():
    sidecar = _sidecar()
    original = deepcopy(sidecar)

    validate_sidecar_artifact(sidecar)

    assert sidecar == original


def test_output_path_guard_refuses_production_data_directory():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "sidecar-validation.md")
