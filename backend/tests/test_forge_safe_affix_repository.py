import json

import pytest

from data.loaders.forge_safe_affixes_loader import ForgeSafeAffixLoaderError
from data.repositories.forge_safe_affix_repository import (
    ForgeSafeAffixRepository,
    ForgeSafeAffixRepositoryNotLoadedError,
)


def test_repository_loads_valid_export(tmp_path):
    path = _write_export(tmp_path, [_record(1), _record(2)])

    repository = ForgeSafeAffixRepository(path).load()

    assert repository.is_loaded() is True
    assert repository.count() == 2


def test_unloaded_repository_methods_fail():
    repository = ForgeSafeAffixRepository()

    with pytest.raises(ForgeSafeAffixRepositoryNotLoadedError):
        repository.list_affixes()

    with pytest.raises(ForgeSafeAffixRepositoryNotLoadedError):
        repository.get_summary()


def test_count_returns_loaded_record_count(tmp_path):
    repository = ForgeSafeAffixRepository(_write_export(tmp_path, [_record(1), _record(2), _record(3)])).load()

    assert repository.count() == 3


def test_get_by_affix_id_returns_expected_record(tmp_path):
    repository = ForgeSafeAffixRepository(_write_export(tmp_path, [_record(1), _record(7, name="Void Penetration")])).load()

    record = repository.get_by_affix_id(7)

    assert record is not None
    assert record["affix_id"] == 7
    assert record["affix_name"] == "Void Penetration"


def test_get_by_affix_id_returns_none_for_missing_id(tmp_path):
    repository = ForgeSafeAffixRepository(_write_export(tmp_path, [_record(1)])).load()

    assert repository.get_by_affix_id(999) is None


def test_list_affixes_respects_limit_and_offset(tmp_path):
    repository = ForgeSafeAffixRepository(_write_export(tmp_path, [_record(1), _record(2), _record(3)])).load()

    records = repository.list_affixes(limit=1, offset=1)

    assert [record["affix_id"] for record in records] == [2]


def test_search_matches_affix_id_name_and_display_name(tmp_path):
    repository = ForgeSafeAffixRepository(
        _write_export(
            tmp_path,
            [
                _record(1, name="Void Penetration"),
                _record(22, name="Armor", display_name="Stout Defense"),
                _record(307, name="Cast Speed"),
            ],
        )
    ).load()

    assert [record["affix_id"] for record in repository.search("void")] == [1]
    assert [record["affix_id"] for record in repository.search("stout")] == [22]
    assert [record["affix_id"] for record in repository.search("307")] == [307]


def test_search_respects_limit(tmp_path):
    repository = ForgeSafeAffixRepository(_write_export(tmp_path, [_record(1, name="Speed"), _record(2, name="Speed")])).load()

    assert [record["affix_id"] for record in repository.search("speed", limit=1)] == [1]


def test_filter_by_source_type_works(tmp_path):
    repository = ForgeSafeAffixRepository(
        _write_export(
            tmp_path,
            [_record(1, source_type="equipment"), _record(2, source_type="idol")],
        )
    ).load()

    assert [record["affix_id"] for record in repository.filter_by_source_type("IDOL")] == [2]


def test_filter_by_item_type_matches_item_type_and_eligible_item_types(tmp_path):
    repository = ForgeSafeAffixRepository(
        _write_export(
            tmp_path,
            [
                _record(1, item_type="Equipment", eligible_item_types=["AMULET"]),
                _record(2, item_type="Idol", eligible_item_types=["IDOL_1X1"]),
            ],
        )
    ).load()

    assert [record["affix_id"] for record in repository.filter_by_item_type("equipment")] == [1]
    assert [record["affix_id"] for record in repository.filter_by_item_type("IDOL_1X1")] == [2]


def test_get_summary_returns_export_metadata(tmp_path):
    path = _write_export(tmp_path, [_record(1), _record(2)])
    repository = ForgeSafeAffixRepository(path).load()

    summary = repository.get_summary()

    assert summary["source_path"] == str(path)
    assert summary["loaded_record_count"] == 2
    assert summary["warning_count"] == 0
    assert summary["warnings"] == []
    assert summary["export_policy"] == "deterministic_affix_only"
    assert summary["export_status"] == "warning"
    assert summary["total_affix_records_seen"] == 2
    assert summary["excluded_affix_records"] == 0


def test_invalid_export_fails_through_loader(tmp_path):
    path = _write_export(tmp_path, [_record(1, forge_safe=False)])

    with pytest.raises(ForgeSafeAffixLoaderError, match="forge_safe=true"):
        ForgeSafeAffixRepository(path).load()


def test_repository_does_not_mutate_records_unexpectedly(tmp_path):
    repository = ForgeSafeAffixRepository(_write_export(tmp_path, [_record(1)])).load()

    listed = repository.list_affixes()
    listed[0]["affix_name"] = "Mutated"
    fetched = repository.get_by_affix_id(1)

    assert fetched is not None
    assert fetched["affix_name"] == "Affix 1"


def _write_export(tmp_path, records):
    path = tmp_path / "forge_safe_affixes.json"
    path.write_text(json.dumps(_payload(records)), encoding="utf-8")
    return path


def _payload(records):
    return {
        "artifact": "forge_safe_canonical_affixes",
        "export_policy": "deterministic_affix_only",
        "production_safe": False,
        "records": records,
        "summary": {
            "export_status": "warning",
            "exported_affix_records": len(records),
            "excluded_affix_records": 0,
            "forge_safe_records_only": True,
            "production_safe": False,
            "total_affix_records_seen": len(records),
        },
    }


def _record(
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
    return {
        "affix_id": affix_id,
        "affix_name": affix_name,
        "display_name": display_name or affix_name,
        "source_type": source_type,
        "item_type": item_type,
        "eligible_item_types": eligible_item_types if eligible_item_types is not None else ["AMULET"],
        "safety": {
            "export_policy": "deterministic_affix_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }
