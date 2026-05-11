import json

import pytest

from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoadError, ForgeSafeAffixLoader


def write_export(tmp_path, records):
    path = tmp_path / "forge_safe.json"
    path.write_text(json.dumps({"affixes": records}), encoding="utf-8")
    return path


def test_loader_accepts_only_forge_safe_records(tmp_path):
    path = write_export(tmp_path, [
        {"id": "a", "name": "Alpha", "source_type": "prefix", "item_types": ["helm"], "safety": {"forge_safe": True}},
        {"id": "b", "name": "Beta", "safety": {"forge_safe": False}},
    ])
    records = ForgeSafeAffixLoader(path).load()
    assert [r.id for r in records] == ["a"]
    assert records[0].to_catalog_dict()["production_consumer"] is False


def test_loader_rejects_production_safe_true(tmp_path):
    path = write_export(tmp_path, [
        {"id": "a", "name": "Alpha", "production_safe": True, "safety": {"forge_safe": True}},
    ])
    with pytest.raises(ForgeSafeAffixLoadError):
        ForgeSafeAffixLoader(path).load()


def test_loader_invalid_export_fails_cleanly(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ForgeSafeAffixLoadError):
        ForgeSafeAffixLoader(path).load()
