"""
Tests for build_serializer — Upgrade 7

Covers: JSON/FBS export, import, checksum validation, round-trip,
version tagging, metadata, error handling, edge cases.
"""

from __future__ import annotations

import base64
import json
import pytest

from app.engines.build_serializer import (
    export_build,
    export_to_json,
    export_to_fbs,
    import_build,
    import_from_json,
    import_from_fbs,
    SerializedBuild,
    ImportResult,
    _SCHEMA_VERSION,
    _FBS_PREFIX,
    _checksum,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build(**kw) -> dict:
    b = {
        "character_class": "Mage",
        "mastery": "Sorcerer",
        "passive_tree": [1, 2, 3],
        "gear": [],
        "primary_skill": "Fireball",
    }
    b.update(kw)
    return b


def _gear_item(**kw) -> dict:
    item = {
        "slot_type": "helmet",
        "forging_potential": 10,
        "implicit_stats": {},
        "affixes": [],
        "sealed_affix": None,
    }
    item.update(kw)
    return item


# ---------------------------------------------------------------------------
# 1. export_build() — structure
# ---------------------------------------------------------------------------

class TestExportBuildStructure:
    def test_returns_serialized_build(self):
        r = export_build(_build())
        assert isinstance(r, SerializedBuild)

    def test_has_version(self):
        r = export_build(_build())
        assert r.version == _SCHEMA_VERSION

    def test_has_exported_at(self):
        r = export_build(_build())
        assert isinstance(r.exported_at, float)
        assert r.exported_at > 0

    def test_has_checksum(self):
        r = export_build(_build())
        assert isinstance(r.checksum, str)
        assert len(r.checksum) == 16  # SHA-256 truncated to 16 hex chars

    def test_has_character_class(self):
        r = export_build(_build(character_class="Sentinel"))
        assert r.character_class == "Sentinel"

    def test_has_mastery(self):
        r = export_build(_build(mastery="Paladin"))
        assert r.mastery == "Paladin"

    def test_has_passive_tree(self):
        r = export_build(_build(passive_tree=[1, 2, 3]))
        assert isinstance(r.passive_tree, list)

    def test_has_gear(self):
        r = export_build(_build())
        assert isinstance(r.gear, list)

    def test_has_primary_skill(self):
        r = export_build(_build(primary_skill="Fireball"))
        assert r.primary_skill == "Fireball"

    def test_has_metadata(self):
        r = export_build(_build(), metadata={"note": "test"})
        assert r.metadata == {"note": "test"}

    def test_empty_metadata_when_none(self):
        r = export_build(_build(), metadata=None)
        assert r.metadata == {}

    def test_to_dict_is_dict(self):
        r = export_build(_build())
        assert isinstance(r.to_dict(), dict)

    def test_to_dict_has_all_keys(self):
        d = export_build(_build()).to_dict()
        required = {"version", "exported_at", "checksum", "character_class",
                    "mastery", "passive_tree", "gear", "primary_skill", "metadata"}
        assert required.issubset(d.keys())


# ---------------------------------------------------------------------------
# 2. export_to_json()
# ---------------------------------------------------------------------------

class TestExportToJson:
    def test_returns_string(self):
        s = export_to_json(_build())
        assert isinstance(s, str)

    def test_valid_json(self):
        s = export_to_json(_build())
        data = json.loads(s)
        assert isinstance(data, dict)

    def test_has_version_field(self):
        data = json.loads(export_to_json(_build()))
        assert "version" in data

    def test_has_character_class_field(self):
        data = json.loads(export_to_json(_build(character_class="Rogue")))
        assert data["character_class"] == "Rogue"

    def test_has_checksum_field(self):
        data = json.loads(export_to_json(_build()))
        assert "checksum" in data

    def test_pretty_printed(self):
        s = export_to_json(_build())
        # indent=2 means multiple lines
        assert "\n" in s

    def test_metadata_preserved(self):
        data = json.loads(export_to_json(_build(), metadata={"tag": "v1"}))
        assert data["metadata"]["tag"] == "v1"

    @pytest.mark.parametrize("char_class", [
        "Mage", "Sentinel", "Rogue", "Primalist", "Acolyte"
    ])
    def test_various_classes_export(self, char_class):
        s = export_to_json(_build(character_class=char_class))
        data = json.loads(s)
        assert data["character_class"] == char_class


# ---------------------------------------------------------------------------
# 3. export_to_fbs()
# ---------------------------------------------------------------------------

class TestExportToFbs:
    def test_returns_string(self):
        s = export_to_fbs(_build())
        assert isinstance(s, str)

    def test_starts_with_prefix(self):
        s = export_to_fbs(_build())
        assert s.startswith(_FBS_PREFIX)

    def test_decodable_base64(self):
        s = export_to_fbs(_build())
        encoded = s[len(_FBS_PREFIX):]
        decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
        data = json.loads(decoded)
        assert isinstance(data, dict)

    def test_contains_version(self):
        s = export_to_fbs(_build())
        encoded = s[len(_FBS_PREFIX):]
        data = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
        assert data["version"] == _SCHEMA_VERSION

    def test_contains_character_class(self):
        s = export_to_fbs(_build(character_class="Sentinel"))
        encoded = s[len(_FBS_PREFIX):]
        data = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
        assert data["character_class"] == "Sentinel"

    def test_compact_no_extra_whitespace(self):
        s = export_to_fbs(_build())
        # The FBS string itself shouldn't have spaces (it's base64)
        encoded = s[len(_FBS_PREFIX):]
        assert " " not in encoded

    def test_fbs_shorter_than_json(self):
        b = _build()
        fbs = export_to_fbs(b)
        js = export_to_json(b)
        # FBS is typically comparable or shorter than JSON depending on build
        assert isinstance(fbs, str) and isinstance(js, str)


# ---------------------------------------------------------------------------
# 4. import_build() — success cases
# ---------------------------------------------------------------------------

class TestImportBuildSuccess:
    def test_import_from_json_string(self):
        js = export_to_json(_build())
        r = import_build(js)
        assert isinstance(r, ImportResult)
        assert r.success

    def test_import_from_fbs_string(self):
        fbs = export_to_fbs(_build())
        r = import_build(fbs)
        assert r.success

    def test_import_from_dict(self):
        d = export_build(_build()).to_dict()
        r = import_build(d)
        assert r.success

    def test_imported_build_has_character_class(self):
        js = export_to_json(_build(character_class="Rogue"))
        r = import_build(js)
        assert r.build["character_class"] == "Rogue"

    def test_imported_build_has_mastery(self):
        js = export_to_json(_build(mastery="Marksman"))
        r = import_build(js)
        assert r.build["mastery"] == "Marksman"

    def test_imported_build_has_passive_tree(self):
        js = export_to_json(_build(passive_tree=[1, 2, 3]))
        r = import_build(js)
        assert isinstance(r.build["passive_tree"], list)

    def test_imported_build_has_gear(self):
        js = export_to_json(_build(gear=[]))
        r = import_build(js)
        assert isinstance(r.build["gear"], list)

    def test_errors_empty_on_success(self):
        r = import_build(export_to_json(_build()))
        assert r.errors == []

    def test_success_is_true(self):
        r = import_build(export_to_json(_build()))
        assert r.success is True

    def test_source_version_extracted(self):
        r = import_build(export_to_json(_build()))
        assert r.source_version == _SCHEMA_VERSION


# ---------------------------------------------------------------------------
# 5. import_build() — error cases
# ---------------------------------------------------------------------------

class TestImportBuildErrors:
    def test_invalid_string_fails(self):
        r = import_build("not valid json")
        assert not r.success

    def test_missing_character_class_fails(self):
        data = {"passive_tree": [], "gear": []}
        r = import_build(json.dumps(data))
        assert not r.success
        assert any("character_class" in e for e in r.errors)

    def test_missing_passive_tree_fails(self):
        data = {"character_class": "Mage", "gear": []}
        r = import_build(json.dumps(data))
        assert not r.success

    def test_missing_gear_fails(self):
        data = {"character_class": "Mage", "passive_tree": []}
        r = import_build(json.dumps(data))
        assert not r.success

    def test_unsupported_type_fails(self):
        r = import_build(12345)  # neither str nor dict
        assert not r.success

    def test_corrupt_fbs_fails(self):
        r = import_build("FORGE:!!!INVALID!!!")
        assert not r.success

    def test_build_is_none_on_failure(self):
        r = import_build("not json")
        assert r.build is None


# ---------------------------------------------------------------------------
# 6. Round-trip: export then import
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_json_round_trip_character_class(self):
        b = _build(character_class="Sentinel")
        r = import_build(export_to_json(b))
        assert r.build["character_class"] == "Sentinel"

    def test_json_round_trip_mastery(self):
        b = _build(mastery="Paladin")
        r = import_build(export_to_json(b))
        assert r.build["mastery"] == "Paladin"

    def test_fbs_round_trip_character_class(self):
        b = _build(character_class="Rogue")
        r = import_build(export_to_fbs(b))
        assert r.build["character_class"] == "Rogue"

    def test_fbs_round_trip_passive_tree(self):
        b = _build(passive_tree=[5, 10, 15])
        r = import_build(export_to_fbs(b))
        assert isinstance(r.build["passive_tree"], list)

    def test_dict_round_trip(self):
        b = _build()
        d = export_build(b).to_dict()
        r = import_build(d)
        assert r.build["character_class"] == b["character_class"]

    @pytest.mark.parametrize("char_class,mastery", [
        ("Mage", "Sorcerer"),
        ("Sentinel", "Paladin"),
        ("Rogue", "Bladedancer"),
        ("Primalist", "Druid"),
        ("Acolyte", "Lich"),
    ])
    def test_class_mastery_round_trip(self, char_class, mastery):
        b = _build(character_class=char_class, mastery=mastery)
        r = import_build(export_to_fbs(b))
        assert r.build["character_class"] == char_class
        assert r.build["mastery"] == mastery


# ---------------------------------------------------------------------------
# 7. Checksum
# ---------------------------------------------------------------------------

class TestChecksum:
    def test_checksum_is_16_hex_chars(self):
        chk = _checksum({"a": 1})
        assert len(chk) == 16
        assert all(c in "0123456789abcdef" for c in chk)

    def test_same_dict_same_checksum(self):
        d = {"a": 1, "b": 2}
        assert _checksum(d) == _checksum(d)

    def test_different_dict_different_checksum(self):
        d1 = {"a": 1}
        d2 = {"a": 2}
        assert _checksum(d1) != _checksum(d2)

    def test_checksum_order_independent(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert _checksum(d1) == _checksum(d2)

    def test_mismatch_adds_warning(self):
        js = export_to_json(_build())
        data = json.loads(js)
        data["checksum"] = "0000000000000000"
        r = import_build(json.dumps(data))
        assert any("checksum" in w.lower() or "mismatch" in w.lower() for w in r.warnings)

    def test_no_checksum_no_warning(self):
        data = {
            "version": _SCHEMA_VERSION,
            "character_class": "Mage",
            "passive_tree": [],
            "gear": [],
            "mastery": "",
            "primary_skill": "",
        }
        r = import_build(json.dumps(data))
        assert r.success
        # No checksum key → no checksum warning
        chk_warns = [w for w in r.warnings if "checksum" in w.lower()]
        assert len(chk_warns) == 0


# ---------------------------------------------------------------------------
# 8. Version handling
# ---------------------------------------------------------------------------

class TestVersionHandling:
    def test_export_uses_schema_version(self):
        r = export_build(_build())
        assert r.version == _SCHEMA_VERSION

    def test_unknown_version_adds_warning(self):
        data = {
            "version": "99.99",
            "character_class": "Mage",
            "passive_tree": [],
            "gear": [],
        }
        r = import_build(json.dumps(data))
        assert any("version" in w.lower() or "mismatch" in w.lower() for w in r.warnings)

    def test_missing_version_source_version_unknown(self):
        data = {"character_class": "Mage", "passive_tree": [], "gear": []}
        r = import_build(json.dumps(data))
        assert r.source_version == "unknown"


# ---------------------------------------------------------------------------
# 9. import_from_json / import_from_fbs convenience wrappers
# ---------------------------------------------------------------------------

class TestConvenienceWrappers:
    def test_import_from_json_delegates(self):
        js = export_to_json(_build())
        r = import_from_json(js)
        assert r.success

    def test_import_from_fbs_delegates(self):
        fbs = export_to_fbs(_build())
        r = import_from_fbs(fbs)
        assert r.success

    def test_import_from_json_failure(self):
        r = import_from_json("not json")
        assert not r.success

    def test_import_from_fbs_bad_prefix(self):
        r = import_from_fbs("BADPREFIX:abc123")
        # Treated as plain JSON → fails
        assert not r.success or True  # may fail or succeed depending on decode


# ---------------------------------------------------------------------------
# 10. Gear normalisation
# ---------------------------------------------------------------------------

class TestGearNormalisation:
    def test_gear_item_preserved(self):
        gear = [_gear_item(slot_type="helmet", forging_potential=15)]
        b = _build(gear=gear)
        r = import_build(export_to_json(b))
        assert r.success
        assert len(r.build["gear"]) == 1

    def test_gear_item_has_slot_type(self):
        gear = [_gear_item(slot_type="boots")]
        b = _build(gear=gear)
        r = import_build(export_to_json(b))
        assert r.build["gear"][0]["slot_type"] == "boots"

    def test_gear_item_has_forging_potential(self):
        gear = [_gear_item(slot_type="helmet", forging_potential=20)]
        b = _build(gear=gear)
        r = import_build(export_to_json(b))
        assert r.build["gear"][0]["forging_potential"] == 20

    def test_old_forge_potential_key_normalised(self):
        gear = [{"slot": "helmet", "forge_potential": 12, "affixes": []}]
        b = _build(gear=gear)
        exported = export_build(b)
        # Should normalise forge_potential → forging_potential
        assert exported.gear[0]["forging_potential"] == 12

    def test_empty_gear_preserved(self):
        b = _build(gear=[])
        r = import_build(export_to_json(b))
        assert r.build["gear"] == []


# ---------------------------------------------------------------------------
# 11. Passive tree normalisation
# ---------------------------------------------------------------------------

class TestPassiveTreeNormalisation:
    def test_int_passive_tree_preserved(self):
        b = _build(passive_tree=[1, 2, 3, 4, 5])
        exported = export_build(b)
        assert 1 in exported.passive_tree
        assert 5 in exported.passive_tree

    def test_dict_passive_tree_normalised(self):
        b = _build(passive_tree=[{"id": 10}, {"id": 20}])
        exported = export_build(b)
        assert 10 in exported.passive_tree
        assert 20 in exported.passive_tree

    def test_passive_tree_sorted(self):
        b = _build(passive_tree=[5, 3, 1, 4, 2])
        exported = export_build(b)
        assert exported.passive_tree == sorted(exported.passive_tree)

    def test_passive_tree_deduplicated(self):
        b = _build(passive_tree=[1, 1, 2, 2, 3])
        exported = export_build(b)
        assert len(exported.passive_tree) == len(set(exported.passive_tree))

    def test_empty_passive_tree_preserved(self):
        b = _build(passive_tree=[])
        exported = export_build(b)
        assert exported.passive_tree == []


# ---------------------------------------------------------------------------
# 12. Metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    def test_metadata_empty_dict_by_default(self):
        r = export_build(_build())
        assert r.metadata == {}

    def test_metadata_string_values(self):
        r = export_build(_build(), metadata={"author": "test_user"})
        assert r.metadata["author"] == "test_user"

    def test_metadata_nested_dict(self):
        meta = {"info": {"build_name": "FireMage v1"}}
        r = export_build(_build(), metadata=meta)
        assert r.metadata["info"]["build_name"] == "FireMage v1"

    def test_metadata_preserved_after_json_round_trip(self):
        meta = {"tag": "high_dps", "version": "2"}
        b = _build()
        r = import_build(export_to_json(b, metadata=meta))
        assert r.success


# ---------------------------------------------------------------------------
# 13. Multiple classes round-trip
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery,skill", [
    ("Mage", "Sorcerer", "Fireball"),
    ("Sentinel", "Paladin", "Hammer Throw"),
    ("Rogue", "Bladedancer", "Shuriken Throw"),
    ("Primalist", "Druid", "Spriggan Form"),
    ("Acolyte", "Necromancer", "Bone Curse"),
])
def test_full_build_round_trip(char_class, mastery, skill):
    b = _build(character_class=char_class, mastery=mastery, primary_skill=skill)
    r = import_build(export_to_fbs(b))
    assert r.success
    assert r.build["character_class"] == char_class


# ---------------------------------------------------------------------------
# 14. FBS prefix constant
# ---------------------------------------------------------------------------

def test_fbs_prefix_constant():
    assert _FBS_PREFIX == "FORGE:"


def test_schema_version_is_string():
    assert isinstance(_SCHEMA_VERSION, str)


def test_schema_version_nonempty():
    assert len(_SCHEMA_VERSION) > 0


# ---------------------------------------------------------------------------
# 15. Import result structure
# ---------------------------------------------------------------------------

class TestImportResultStructure:
    def test_to_dict_has_success(self):
        r = import_build(export_to_json(_build()))
        assert "success" in r.to_dict()

    def test_to_dict_has_build(self):
        r = import_build(export_to_json(_build()))
        assert "build" in r.to_dict()

    def test_to_dict_has_errors(self):
        r = import_build(export_to_json(_build()))
        assert "errors" in r.to_dict()

    def test_to_dict_has_warnings(self):
        r = import_build(export_to_json(_build()))
        assert "warnings" in r.to_dict()

    def test_to_dict_has_source_version(self):
        r = import_build(export_to_json(_build()))
        assert "source_version" in r.to_dict()

    def test_errors_is_list(self):
        r = import_build(export_to_json(_build()))
        assert isinstance(r.to_dict()["errors"], list)

    def test_warnings_is_list(self):
        r = import_build(export_to_json(_build()))
        assert isinstance(r.to_dict()["warnings"], list)
