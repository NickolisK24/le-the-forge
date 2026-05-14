from pathlib import Path

from scripts.report_forge_safe_adapter_candidates import build_adapter_candidates


ROOT = Path(__file__).resolve().parents[2]


def test_candidate_generation_includes_only_one_to_one_mappings():
    report = build_adapter_candidates(_mapping_report([
        _mapping("legacy_health", "one_to_one", ["ADDED:Health:None"]),
        _mapping("legacy_combo", "one_to_many", ["ADDED:Health:None", "INCREASED:Damage:Fire"]),
        _mapping("legacy_conflict", "ambiguous", ["ADDED:Health:None", "INCREASED:Health:None"]),
        _mapping("legacy_missing", "missing", []),
    ]), source_path="mapping.json")

    assert report["summary"]["candidate_count"] == 1
    assert [candidate["legacy_stat_key"] for candidate in report["candidates"]] == [
        "legacy_health"
    ]
    candidate = report["candidates"][0]
    assert candidate["bundle_modifier_reference"]["property_path"] == "ADDED:Health:None"
    assert candidate["candidate_status"] == "reviewed_candidate"
    assert candidate["consumption_status"] == "not_consumed"


def test_one_to_many_mappings_are_excluded():
    report = build_adapter_candidates(_mapping_report([
        _mapping("legacy_combo", "one_to_many", ["ADDED:Health:None", "INCREASED:Damage:Fire"]),
    ]), source_path="mapping.json")

    assert report["summary"]["candidate_count"] == 0
    assert report["summary"]["excluded_one_to_many_count"] == 1
    assert report["excluded"]["one_to_many"][0]["legacy_stat_key"] == "legacy_combo"


def test_ambiguous_mappings_are_excluded():
    report = build_adapter_candidates(_mapping_report([
        _mapping("legacy_conflict", "ambiguous", ["ADDED:Health:None", "INCREASED:Health:None"]),
    ]), source_path="mapping.json")

    assert report["summary"]["candidate_count"] == 0
    assert report["summary"]["excluded_ambiguous_count"] == 1
    assert report["excluded"]["ambiguous"][0]["legacy_stat_key"] == "legacy_conflict"


def test_metadata_marks_artifact_read_only_candidate_only_and_not_production_safe():
    report = build_adapter_candidates(_mapping_report([
        _mapping("legacy_health", "one_to_one", ["ADDED:Health:None"]),
    ]), source_path="mapping.json")

    assert report["metadata"]["read_only"] is True
    assert report["metadata"]["candidate_only"] is True
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_safe"] is False
    assert report["metadata"]["consumption_status"] == "not_consumed"
    assert report["summary"]["production_consumed"] is False


def test_production_modules_do_not_reference_candidate_artifact_or_generator():
    forbidden = [
        "forge_safe_adapter_candidates.json",
        "report_forge_safe_adapter_candidates",
    ]
    searched_roots = [ROOT / "backend" / "app", ROOT / "backend" / "data"]
    offenders = []

    for root in searched_roots:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _mapping_report(mappings):
    return {
        "summary": {
            "legacy_stat_key_count": len(mappings),
            "one_to_one_mapping_count": sum(
                1 for mapping in mappings if mapping["mapping_shape"] == "one_to_one"
            ),
            "one_to_many_mapping_count": sum(
                1 for mapping in mappings if mapping["mapping_shape"] == "one_to_many"
            ),
            "ambiguous_mapping_count": sum(
                1 for mapping in mappings if mapping["mapping_shape"] == "ambiguous"
            ),
            "missing_mapping_count": sum(
                1 for mapping in mappings if mapping["mapping_shape"] == "missing"
            ),
        },
        "mappings": mappings,
        "metadata": {
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
        },
    }


def _mapping(legacy_stat_key, shape, property_paths):
    return {
        "legacy_stat_key": legacy_stat_key,
        "affix_count": 2,
        "bundle_modifier_references": [
            {
                "modifier_id": "equipment:1",
                "modifier_ids": ["equipment:1"],
                "modifier_type": path.split(":", 1)[0],
                "property": path.split(":")[1],
                "property_path": path,
                "affix_count": 2,
            }
            for path in property_paths
        ],
        "mapping_shape": shape,
        "migration_risk": "low" if shape == "one_to_one" else "high",
        "example_affix_ids": [1, 2],
    }
