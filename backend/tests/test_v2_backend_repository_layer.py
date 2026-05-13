import json
from pathlib import Path

import pytest

from app.repositories.v2 import V2RepositoryRegistry
from scripts.report_v2_backend_repository_layer import build_v2_backend_repository_report


def test_v2_repository_registry_loads_all_generated_domains():
    registry = V2RepositoryRegistry()
    status = registry.validation_status()

    assert status["summary"]["repository_domain_count"] == 10
    assert status["summary"]["loaded_repository_count"] == 10
    assert status["summary"]["missing_artifact_count"] == 0
    assert status["summary"]["invalid_repository_count"] == 0
    assert all(repository["production_consumed"] is False for repository in status["repositories"])


@pytest.mark.parametrize(
    "domain, expected_summary_key",
    [
        ("affixes", "affix_count"),
        ("items", "item_base_count"),
        ("unique_sets", "unique_count"),
        ("idols", "idol_count"),
        ("classes_masteries", "class_count"),
        ("passives", "passive_tree_count"),
        ("skills", "skill_count"),
        ("stats", "stat_count"),
        ("modifiers", "modifier_count"),
    ],
)
def test_v2_repository_registry_exposes_debug_summaries(domain: str, expected_summary_key: str):
    registry = V2RepositoryRegistry()
    loaded = registry.validate_domain(domain)

    assert loaded["status"] == "ok"
    assert loaded["debug_summary"][expected_summary_key] > 0
    assert loaded["debug_summary"]["production_safe"] is False


def test_v2_repository_registry_reports_clear_missing_artifacts(tmp_path):
    registry = V2RepositoryRegistry(root=tmp_path)
    status = registry.validate_domain("affixes")

    assert status["status"] == "missing_artifacts"
    assert status["missing_artifact_count"] == 1
    assert "Missing v2 generated artifacts for affixes" in status["error"]


def test_v2_repository_registry_reports_invalid_bundle_errors(tmp_path):
    artifact = tmp_path / "docs" / "generated" / "v2_affix_bundle.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(json.dumps({"records": {"affixes": []}}), encoding="utf-8")

    registry = V2RepositoryRegistry(root=tmp_path)
    status = registry.validate_domain("affixes")

    assert status["status"] == "invalid"
    assert "records.affixes must not be empty" in status["error"]


def test_v2_backend_repository_report_covers_routes_and_methods():
    report = build_v2_backend_repository_report()

    assert report["summary"]["repository_domain_count"] == 10
    assert report["summary"]["missing_artifact_count"] == 0
    assert report["summary"]["invalid_repository_count"] == 0
    assert report["summary"]["missing_method_count"] == 0
    assert report["summary"]["experimental_route_count"] >= 30
    assert report["metadata"]["production_consumed"] is False
    assert report["metadata"]["unresolved_skill_identity_bridged"] is False


def test_v2_repository_registry_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "app" / "repositories" / "v2" / "registry.py",
        root / "backend" / "scripts" / "report_v2_backend_repository_layer.py",
        Path(__file__).resolve(),
    }
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "V2RepositoryRegistry" in text or "v2_backend_repository_report.json" in text:
            offenders.append(str(path.relative_to(root)))

    assert offenders == []
