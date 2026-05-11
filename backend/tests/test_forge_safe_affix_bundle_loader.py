import json
from pathlib import Path

import pytest

from data.loaders.forge_safe_affix_bundle_loader import (
    ForgeSafeAffixBundleLoader,
    ForgeSafeAffixBundleLoaderError,
)


REAL_BUNDLE_PATH = Path(r"D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json")


def test_valid_small_bundle_loads(tmp_path):
    path = _write_bundle(tmp_path, [_affix(1)], [_modifier("equipment:1", "equipment:1")])

    loaded = ForgeSafeAffixBundleLoader().load(path)

    assert len(loaded.affixes) == 1
    assert len(loaded.modifiers) == 1
    assert loaded.modifiers_by_affix_identity["equipment:1"][0]["modifier_id"] == "equipment:1"
    assert loaded.warnings == ()


def test_real_bundle_smoke_loads_when_available():
    if not REAL_BUNDLE_PATH.exists():
        pytest.skip(f"real bundle not available: {REAL_BUNDLE_PATH}")

    loaded = ForgeSafeAffixBundleLoader().load(REAL_BUNDLE_PATH)

    assert len(loaded.affixes) == 1098
    assert len(loaded.modifiers) == 1624
    assert loaded.export_policy == "deterministic_affix_bundle"
    assert loaded.cross_reference_validation["status"] == "pass"


def test_missing_file_fails_cleanly(tmp_path):
    with pytest.raises(FileNotFoundError):
        ForgeSafeAffixBundleLoader().load(tmp_path / "missing.json")


def test_invalid_json_fails_cleanly(tmp_path):
    path = tmp_path / "bundle.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="Invalid JSON"):
        ForgeSafeAffixBundleLoader().load(path)


def test_production_safe_true_is_rejected(tmp_path):
    payload = _payload([_affix(1)], [_modifier("equipment:1", "equipment:1")])
    payload["records"]["affixes"][0]["safety"]["production_safe"] = True

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="production_safe=true"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_forge_safe_false_affix_is_rejected(tmp_path):
    payload = _payload([_affix(1, forge_safe=False)], [_modifier("equipment:1", "equipment:1")])

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="safety.forge_safe=true"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_forge_safe_false_modifier_is_rejected(tmp_path):
    payload = _payload([_affix(1)], [_modifier("equipment:1", "equipment:1", forge_safe=False)])

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="safety.forge_safe=true"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_cross_reference_status_not_pass_is_rejected(tmp_path):
    payload = _payload([_affix(1)], [_modifier("equipment:1", "equipment:1")])
    payload["cross_reference_validation"]["status"] = "warning"

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="status must be 'pass'"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_unmatched_modifier_is_rejected(tmp_path):
    payload = _payload([_affix(1)], [_modifier("equipment:1", "equipment:999")])

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="references unknown"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_affix_without_modifier_is_rejected(tmp_path):
    payload = _payload(
        [_affix(1), _affix(2)],
        [_modifier("equipment:1", "equipment:1")],
    )

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="must have at least one modifier"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_duplicate_affix_id_is_rejected(tmp_path):
    payload = _payload(
        [_affix(1, identity="equipment:1"), _affix(1, identity="equipment:2")],
        [
            _modifier("equipment:1", "equipment:1"),
            _modifier("equipment:2", "equipment:2"),
        ],
    )

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="Duplicate affix_id"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


def test_duplicate_modifier_id_is_rejected(tmp_path):
    payload = _payload(
        [_affix(1), _affix(2, identity="equipment:2")],
        [
            _modifier("duplicate", "equipment:1"),
            _modifier("duplicate", "equipment:2"),
        ],
    )

    with pytest.raises(ForgeSafeAffixBundleLoaderError, match="Duplicate modifier_id"):
        ForgeSafeAffixBundleLoader().load_payload(payload)


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


def _affix(affix_id, *, identity=None, forge_safe=True):
    source_identity = identity or f"equipment:{affix_id}"
    return {
        "affix_id": affix_id,
        "affix_name": f"Affix {affix_id}",
        "display_name": f"Affix {affix_id}",
        "source_type": "equipment",
        "item_type": "Equipment",
        "eligible_item_types": ["AMULET"],
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


def _modifier(modifier_id, affix_identity, *, forge_safe=True):
    return {
        "modifier_id": modifier_id,
        "modifier_name": f"Modifier {modifier_id}",
        "source": {
            "source_affix_identity": affix_identity,
            "source_type": "equipment",
        },
        "provenance": {
            "source_affix_identity": affix_identity,
            "source_path": "exports_json/affixes.json",
        },
        "safety": {
            "export_policy": "deterministic_modifier_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }
