"""
E7 — Tests for Build Serialization (JSON and URL formats).
"""

import pytest
from builds.build_definition import BuildDefinition
from builds.gear_system      import GearItem, GearAffix
from builds.buff_system      import Buff
from builds.serializers      import export_json, import_json, export_url, import_url


def _make_build() -> BuildDefinition:
    b = BuildDefinition(character_class="Acolyte", mastery="Lich", skill_id="Rip Blood")
    b.add_gear(GearItem("weapon", [GearAffix("Spell Damage", 3)]))
    b.add_passive(5)
    b.add_passive(10)
    b.add_buff(Buff("power", {"base_damage": 50.0}, duration=None))
    return b


class TestJsonSerialization:
    def test_export_produces_string(self):
        raw = export_json(_make_build())
        assert isinstance(raw, str)
        assert "Acolyte" in raw

    def test_import_roundtrip(self):
        b = _make_build()
        raw = export_json(b)
        b2 = import_json(raw)
        assert b2.character_class == b.character_class
        assert b2.mastery         == b.mastery
        assert b2.skill_id        == b.skill_id
        assert b2.passive_ids     == b.passive_ids
        assert len(b2.gear)  == len(b.gear)
        assert len(b2.buffs) == len(b.buffs)

    def test_gear_affixes_preserved(self):
        b = _make_build()
        b2 = import_json(export_json(b))
        assert b2.gear[0].affixes[0].name == "Spell Damage"
        assert b2.gear[0].affixes[0].tier == 3

    def test_import_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            import_json("not-json-at-all{{{{")

    def test_import_missing_required_fields_raises(self):
        with pytest.raises(ValueError, match="missing required fields"):
            import_json('{"skill_id": "Rip Blood"}')


class TestUrlSerialization:
    def test_export_produces_url_safe_string(self):
        token = export_url(_make_build())
        assert isinstance(token, str)
        # URL-safe characters only
        for ch in token:
            assert ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    def test_import_roundtrip(self):
        b = _make_build()
        token = export_url(b)
        b2 = import_url(token)
        assert b2.character_class == b.character_class
        assert b2.mastery         == b.mastery
        assert b2.passive_ids     == b.passive_ids
        assert len(b2.gear) == len(b.gear)

    def test_token_is_compact(self):
        token = export_url(_make_build())
        json_raw = export_json(_make_build())
        # Compressed token should be significantly shorter
        assert len(token) < len(json_raw)

    def test_corrupted_token_raises(self):
        with pytest.raises(ValueError, match="Corrupted build token"):
            import_url("this_is_not_a_valid_token_at_all_XXXX")
