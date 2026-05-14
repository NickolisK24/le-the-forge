import json

import pytest

from data.loaders.forge_safe_affix_bundle_loader import ForgeSafeAffixBundleLoaderError
from data.repositories.forge_safe_affix_bundle_repository import (
    ForgeSafeAffixBundleRepository,
    ForgeSafeAffixBundleRepositoryNotLoadedError,
)


def test_repository_loads_and_counts_affixes_and_modifiers(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(
            tmp_path,
            [_affix(1), _affix(2)],
            [
                _modifier("equipment:1", "equipment:1"),
                _modifier("equipment:2-a", "equipment:2"),
                _modifier("equipment:2-b", "equipment:2"),
            ],
        )
    ).load()

    assert repository.is_loaded() is True
    assert repository.count_affixes() == 2
    assert repository.count_modifiers() == 3


def test_unloaded_repository_methods_fail():
    repository = ForgeSafeAffixBundleRepository()

    with pytest.raises(ForgeSafeAffixBundleRepositoryNotLoadedError):
        repository.list_affixes()

    with pytest.raises(ForgeSafeAffixBundleRepositoryNotLoadedError):
        repository.get_summary()


def test_affix_lookup_and_missing_lookup(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(tmp_path, [_affix(7, name="Void Penetration")], [_modifier("equipment:7", "equipment:7")])
    ).load()

    record = repository.get_affix(7)

    assert record is not None
    assert record["affix_id"] == 7
    assert record["affix_name"] == "Void Penetration"
    assert repository.get_affix(999) is None


def test_modifier_lookup_by_affix_identity(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(
            tmp_path,
            [_affix(1)],
            [_modifier("equipment:1-a", "equipment:1"), _modifier("equipment:1-b", "equipment:1")],
        )
    ).load()

    modifiers = repository.get_modifiers_for_affix("equipment:1")

    assert [modifier["modifier_id"] for modifier in modifiers] == ["equipment:1-a", "equipment:1-b"]


def test_get_affix_with_modifiers(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(tmp_path, [_affix(1)], [_modifier("equipment:1", "equipment:1")])
    ).load()

    result = repository.get_affix_with_modifiers(1)

    assert result is not None
    assert result["affix"]["affix_id"] == 1
    assert result["modifier_count"] == 1
    assert result["modifiers"][0]["modifier_id"] == "equipment:1"


def test_list_affixes_respects_limit_and_offset(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(
            tmp_path,
            [_affix(1), _affix(2), _affix(3)],
            [
                _modifier("equipment:1", "equipment:1"),
                _modifier("equipment:2", "equipment:2"),
                _modifier("equipment:3", "equipment:3"),
            ],
        )
    ).load()

    records = repository.list_affixes(limit=1, offset=1)

    assert [record["affix_id"] for record in records] == [2]


def test_search_and_filters_work(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(
            tmp_path,
            [
                _affix(1, name="Void Penetration", item_type="Equipment", eligible_item_types=["AMULET"]),
                _affix(2, name="Armor", source_type="idol", item_type="Idol", eligible_item_types=["IDOL_1X1"]),
                _affix(307, name="Cast Speed", display_name="Quick Casting"),
            ],
            [
                _modifier("equipment:1", "equipment:1"),
                _modifier("idol:2", "idol:2"),
                _modifier("equipment:307", "equipment:307"),
            ],
        )
    ).load()

    assert [record["affix_id"] for record in repository.search_affixes("void")] == [1]
    assert [record["affix_id"] for record in repository.search_affixes("quick")] == [307]
    assert [record["affix_id"] for record in repository.search_affixes("equipment:307")] == [307]
    assert [record["affix_id"] for record in repository.filter_by_source_type("IDOL")] == [2]
    assert [record["affix_id"] for record in repository.filter_by_item_type("IDOL_1X1")] == [2]


def test_summary_returns_bundle_metadata(tmp_path):
    path = _write_bundle(tmp_path, [_affix(1)], [_modifier("equipment:1", "equipment:1")])
    repository = ForgeSafeAffixBundleRepository(path).load()

    summary = repository.get_summary()

    assert summary["source_path"] == str(path)
    assert summary["loaded_affix_count"] == 1
    assert summary["loaded_modifier_count"] == 1
    assert summary["warning_count"] == 0
    assert summary["export_policy"] == "deterministic_affix_bundle"
    assert summary["export_status"] == "pass"
    assert summary["total_affix_records_seen"] == 1
    assert summary["excluded_affix_records"] == 0
    assert summary["cross_reference_validation"]["status"] == "pass"


def test_invalid_bundle_fails_through_loader(tmp_path):
    path = _write_bundle(tmp_path, [_affix(1, forge_safe=False)], [_modifier("equipment:1", "equipment:1")])

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="safety.forge_safe=true"):
        ForgeSafeAffixBundleRepository(path).load()


def test_repository_returns_defensive_copies(tmp_path):
    repository = ForgeSafeAffixBundleRepository(
        _write_bundle(tmp_path, [_affix(1)], [_modifier("equipment:1", "equipment:1")])
    ).load()

    listed = repository.list_affixes()
    listed[0]["affix_name"] = "Mutated"
    modifiers = repository.get_modifiers_for_affix("equipment:1")
    modifiers[0]["modifier_name"] = "Mutated"

    assert repository.get_affix(1)["affix_name"] == "Affix 1"
    assert repository.get_modifiers_for_affix("equipment:1")[0]["modifier_name"] == "Modifier equipment:1"


def _write_bundle(tmp_path, affixes, modifiers):
    path = tmp_path / "forge_safe_affix_bundle.json"
    path.write_text(json.dumps(_payload(affixes, modifiers)), encoding="utf-8")
    return path


def _payload(affixes, modifiers):
    return {
        "schema_version": "1.0",
        "artifact": "forge_safe_affix_bundle",
        "artifact_type": "forge_safe_affix_bundle",
        "diagnostic_only": False,
        "export_policy": "deterministic_affix_bundle",
        "production_safe": False,
        "records": {
            "affixes": affixes,
            "modifiers": modifiers,
        },
        "summary": {
            "affix_count": len(affixes),
            "modifier_count": len(modifiers),
            "export_status": "pass",
            "forge_safe_records_only": True,
            "production_safe": False,
            "total_affix_records_seen": len(affixes),
            "total_modifier_records_seen": len(modifiers),
            "excluded_record_count": 0,
        },
        "cross_reference_validation": {
            "status": "pass",
            "unmatched_affix_count": 0,
            "unmatched_modifier_count": 0,
            "duplicate_affix_id_count": 0,
            "duplicate_modifier_id_count": 0,
        },
    }


def _affix(
    affix_id,
    *,
    name=None,
    display_name=None,
    source_type="equipment",
    item_type="Equipment",
    eligible_item_types=None,
    forge_safe=True,
):
    affix_name = name or f"Affix {affix_id}"
    source_identity = f"{source_type}:{affix_id}"
    return {
        "affix_id": affix_id,
        "affix_name": affix_name,
        "display_name": display_name or affix_name,
        "source_type": source_type,
        "item_type": item_type,
        "eligible_item_types": eligible_item_types if eligible_item_types is not None else ["AMULET"],
        "provenance": {
            "source_affix_identity": source_identity,
            "source_path": "exports_json/affixes.json",
        },
        "safety": {
            "export_policy": "deterministic_affix_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }


def _modifier(modifier_id, affix_identity):
    return {
        "modifier_id": modifier_id,
        "modifier_name": f"Modifier {modifier_id}",
        "source": {
            "source_affix_identity": affix_identity,
            "source_type": affix_identity.split(":", 1)[0],
        },
        "provenance": {
            "source_affix_identity": affix_identity,
            "source_path": "exports_json/affixes.json",
        },
        "safety": {
            "export_policy": "deterministic_modifier_only",
            "forge_safe": True,
            "production_safe": False,
        },
    }
