import json

from data.repositories.forge_safe_affix_repository import ForgeSafeAffixRepository


def test_repository_get_all_and_summary(tmp_path):
    path = tmp_path / "forge_safe.json"
    path.write_text(json.dumps({"affixes": [
        {"id": "a", "name": "Alpha", "source_type": "prefix", "item_types": ["helm"], "safety": {"forge_safe": True}},
        {"id": "b", "name": "Beta", "source_type": "suffix", "item_types": ["helm", "ring"], "safety": {"forge_safe": True}},
    ]}), encoding="utf-8")
    repo = ForgeSafeAffixRepository(path)
    assert repo.get("a").name == "Alpha"
    assert len(repo.all()) == 2
    summary = repo.summary()
    assert summary["count"] == 2
    assert summary["source_types"] == {"prefix": 1, "suffix": 1}
    assert summary["production_consumer"] is False
