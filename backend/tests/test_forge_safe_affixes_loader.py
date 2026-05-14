import json

import pytest

from data.loaders.forge_safe_affixes_loader import (
    ForgeSafeAffixLoader,
    ForgeSafeAffixLoaderError,
)


def test_valid_forge_safe_export_loads(tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1), _record(2)]))

    result = ForgeSafeAffixLoader().load(path)

    assert result.count == 2
    assert result.source_path == path
    assert result.export_policy == "deterministic_affix_only"
    assert result.warnings == ()
    assert result.records[0]["safety"]["forge_safe"] is True


def test_missing_file_fails_cleanly(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        ForgeSafeAffixLoader().load(tmp_path / "missing.json")


def test_invalid_json_fails_cleanly(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ForgeSafeAffixLoaderError, match="Invalid JSON"):
        ForgeSafeAffixLoader().load(path)


def test_missing_top_level_fields_fail():
    with pytest.raises(ForgeSafeAffixLoaderError, match="top-level fields"):
        ForgeSafeAffixLoader().load_payload({"records": []})


def test_record_without_forge_safe_true_is_rejected():
    record = _record(1)
    record["safety"]["forge_safe"] = False

    with pytest.raises(ForgeSafeAffixLoaderError, match="forge_safe=true"):
        ForgeSafeAffixLoader().load_payload(_payload(records=[record]))


def test_record_with_production_safe_true_is_rejected():
    record = _record(1)
    record["safety"]["production_safe"] = True

    with pytest.raises(ForgeSafeAffixLoaderError, match="production_safe=true"):
        ForgeSafeAffixLoader().load_payload(_payload(records=[record]))


def test_top_level_production_safe_true_is_rejected():
    payload = _payload(records=[_record(1)])
    payload["production_safe"] = True

    with pytest.raises(ForgeSafeAffixLoaderError, match="top-level production_safe=true"):
        ForgeSafeAffixLoader().load_payload(payload)


def test_duplicate_affix_id_is_rejected():
    with pytest.raises(ForgeSafeAffixLoaderError, match="Duplicate affix_id"):
        ForgeSafeAffixLoader().load_payload(_payload(records=[_record(1), _record(1)]))


def test_missing_affix_id_is_rejected():
    record = _record(1)
    del record["affix_id"]

    with pytest.raises(ForgeSafeAffixLoaderError, match="affix_id"):
        ForgeSafeAffixLoader().load_payload(_payload(records=[record]))


def test_missing_source_type_is_rejected():
    record = _record(1)
    record["source_type"] = ""

    with pytest.raises(ForgeSafeAffixLoaderError, match="source_type"):
        ForgeSafeAffixLoader().load_payload(_payload(records=[record]))


def test_summary_count_mismatch_warns():
    payload = _payload(records=[_record(1)])
    payload["summary"]["exported_affix_records"] = 2

    result = ForgeSafeAffixLoader().load_payload(payload)

    assert result.count == 1
    assert result.warnings == (
        "summary.exported_affix_records=2 does not match loaded record count 1.",
    )


def _payload(records):
    return {
        "artifact": "forge_safe_canonical_affixes",
        "export_policy": "deterministic_affix_only",
        "production_safe": False,
        "records": records,
        "summary": {
            "export_status": "warning",
            "exported_affix_records": len(records),
            "forge_safe_records_only": True,
            "production_safe": False,
        },
    }


def _record(affix_id):
    return {
        "affix_id": affix_id,
        "affix_name": f"Affix {affix_id}",
        "source_type": "equipment",
        "tier_data": [
            {"tier": 1, "minRoll": 1.0, "maxRoll": 2.0},
        ],
        "modifier_references": [
            {"property": "Health", "modifierType": "ADDED"},
        ],
        "provenance": {
            "source_affix_identity": f"equipment:{affix_id}",
            "source_path": "exports_json/affixes.json",
        },
        "safety": {
            "diagnostic_domains_checked": ["affix_source_shape"],
            "diagnostic_only": False,
            "excluded_unsafe_behavior": False,
            "export_policy": "deterministic_affix_only",
            "forge_safe": True,
            "production_safe": False,
        },
    }


def _write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
