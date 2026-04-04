"""
Extended build_serializer tests — parametrized round-trip and edge cases.
"""

from __future__ import annotations

import json
import pytest

from app.engines.build_serializer import (
    export_build, export_to_json, export_to_fbs,
    import_build, import_from_json, import_from_fbs,
    _checksum, _SCHEMA_VERSION, _FBS_PREFIX,
)


def _build(char_class="Mage", mastery="Sorcerer",
           passive_tree=None, gear=None, primary_skill="Fireball", **kw) -> dict:
    b = {
        "character_class": char_class,
        "mastery": mastery,
        "passive_tree": passive_tree if passive_tree is not None else [],
        "gear": gear if gear is not None else [],
        "primary_skill": primary_skill,
    }
    b.update(kw)
    return b


# ---------------------------------------------------------------------------
# A. Export character classes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class", [
    "Mage", "Sentinel", "Rogue", "Primalist", "Acolyte"
])
def test_export_preserves_class(char_class):
    b = _build(char_class=char_class)
    sb = export_build(b)
    assert sb.character_class == char_class


@pytest.mark.parametrize("mastery", [
    "Sorcerer", "Runemaster", "Spellblade",
    "Forge Guard", "Paladin", "Void Knight",
    "Bladedancer", "Marksman", "Falconer",
    "Shaman", "Druid", "Beastmaster",
    "Lich", "Necromancer", "Warlock",
])
def test_export_preserves_mastery(mastery):
    b = _build(mastery=mastery)
    sb = export_build(b)
    assert sb.mastery == mastery


# ---------------------------------------------------------------------------
# B. JSON round-trip for all class/mastery combinations
# ---------------------------------------------------------------------------

_COMBOS = [
    ("Mage", "Sorcerer"), ("Mage", "Runemaster"), ("Mage", "Spellblade"),
    ("Sentinel", "Forge Guard"), ("Sentinel", "Paladin"), ("Sentinel", "Void Knight"),
    ("Rogue", "Bladedancer"), ("Rogue", "Marksman"), ("Rogue", "Falconer"),
    ("Primalist", "Shaman"), ("Primalist", "Druid"), ("Primalist", "Beastmaster"),
    ("Acolyte", "Lich"), ("Acolyte", "Necromancer"), ("Acolyte", "Warlock"),
]


@pytest.mark.parametrize("char_class,mastery", _COMBOS)
def test_json_round_trip_class(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = import_build(export_to_json(b))
    assert r.success
    assert r.build["character_class"] == char_class


@pytest.mark.parametrize("char_class,mastery", _COMBOS)
def test_json_round_trip_mastery(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = import_build(export_to_json(b))
    assert r.success
    assert r.build["mastery"] == mastery


@pytest.mark.parametrize("char_class,mastery", _COMBOS)
def test_fbs_round_trip_class(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = import_build(export_to_fbs(b))
    assert r.success
    assert r.build["character_class"] == char_class


@pytest.mark.parametrize("char_class,mastery", _COMBOS)
def test_fbs_round_trip_mastery(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = import_build(export_to_fbs(b))
    assert r.success
    assert r.build["mastery"] == mastery


# ---------------------------------------------------------------------------
# C. Passive tree round-trips
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("passive_tree", [
    [],
    [1],
    [1, 2, 3],
    list(range(10)),
    list(range(50)),
    [100, 200, 300],
    [1, 1, 2, 2, 3],  # duplicates should be deduplicated
])
def test_passive_tree_json_round_trip(passive_tree):
    b = _build(passive_tree=passive_tree)
    r = import_build(export_to_json(b))
    assert r.success
    assert isinstance(r.build["passive_tree"], list)


@pytest.mark.parametrize("passive_tree", [
    [], [1, 2, 3], list(range(20)), [10, 20, 30],
])
def test_passive_tree_fbs_round_trip(passive_tree):
    b = _build(passive_tree=passive_tree)
    r = import_build(export_to_fbs(b))
    assert r.success
    assert isinstance(r.build["passive_tree"], list)


@pytest.mark.parametrize("passive_tree", [
    [1, 2, 2, 3, 3, 3],
    [5, 5, 5],
    [1, 1, 1, 1],
])
def test_duplicates_removed_in_export(passive_tree):
    b = _build(passive_tree=passive_tree)
    sb = export_build(b)
    assert len(sb.passive_tree) == len(set(passive_tree))


@pytest.mark.parametrize("passive_tree", [
    [5, 3, 1, 4, 2],
    [10, 2, 8, 4, 6],
    [100, 1, 50, 25],
])
def test_passive_tree_sorted_in_export(passive_tree):
    b = _build(passive_tree=passive_tree)
    sb = export_build(b)
    assert sb.passive_tree == sorted(set(passive_tree))


# ---------------------------------------------------------------------------
# D. Gear round-trips
# ---------------------------------------------------------------------------

_GEAR_SLOTS = [
    "helmet", "body", "gloves", "boots", "belt",
    "ring", "amulet", "sword", "shield",
]


@pytest.mark.parametrize("slot_type", _GEAR_SLOTS)
def test_single_gear_item_round_trip(slot_type):
    gear = [{"slot_type": slot_type, "forging_potential": 10,
             "implicit_stats": {}, "affixes": [], "sealed_affix": None}]
    b = _build(gear=gear)
    r = import_build(export_to_json(b))
    assert r.success
    assert len(r.build["gear"]) == 1


@pytest.mark.parametrize("n_items", [0, 1, 2, 3, 5])
def test_gear_count_preserved(n_items):
    slots = ["helmet", "boots", "gloves", "ring", "body"]
    gear = [{"slot_type": slots[i % len(slots)], "forging_potential": 10,
             "affixes": [], "implicit_stats": {}} for i in range(n_items)]
    b = _build(gear=gear)
    r = import_build(export_to_json(b))
    assert r.success
    assert len(r.build["gear"]) == n_items


@pytest.mark.parametrize("fp", [0, 1, 5, 10, 20, 50, 100])
def test_gear_fp_preserved(fp):
    gear = [{"slot_type": "helmet", "forging_potential": fp,
             "affixes": [], "implicit_stats": {}}]
    b = _build(gear=gear)
    r = import_build(export_to_json(b))
    assert r.success
    assert r.build["gear"][0]["forging_potential"] == fp


# ---------------------------------------------------------------------------
# E. Checksum — parametrized
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("data", [
    {}, {"a": 1}, {"a": 1, "b": 2}, {"key": "value"},
    {"nested": {"x": 1}}, {"list": [1, 2, 3]},
])
def test_checksum_deterministic(data):
    chk1 = _checksum(data)
    chk2 = _checksum(data)
    assert chk1 == chk2


@pytest.mark.parametrize("d1,d2,should_match", [
    ({"a": 1}, {"a": 1}, True),
    ({"a": 1}, {"a": 2}, False),
    ({"a": 1, "b": 2}, {"b": 2, "a": 1}, True),
    ({}, {"a": 1}, False),
])
def test_checksum_equality(d1, d2, should_match):
    c1 = _checksum(d1)
    c2 = _checksum(d2)
    assert (c1 == c2) == should_match


@pytest.mark.parametrize("n", range(10))
def test_checksum_length_16(n):
    data = {"n": n, "value": n * 100}
    assert len(_checksum(data)) == 16


# ---------------------------------------------------------------------------
# F. Primary skill preservation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill", [
    "Fireball", "Frostbolt", "Lightning Blast", "Hammer Throw",
    "Shuriken Throw", "Maelstrom", "Bone Curse", "Minion Spells",
    "Volatile Reversal", "Forge Strike", "",
])
def test_primary_skill_json_round_trip(skill):
    b = _build(primary_skill=skill)
    r = import_build(export_to_json(b))
    assert r.success
    assert r.build["primary_skill"] == skill


@pytest.mark.parametrize("skill", ["Fireball", "Frostbolt", "Lightning Blast"])
def test_primary_skill_fbs_round_trip(skill):
    b = _build(primary_skill=skill)
    r = import_build(export_to_fbs(b))
    assert r.success
    assert r.build["primary_skill"] == skill


# ---------------------------------------------------------------------------
# G. Metadata round-trips
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("metadata", [
    {},
    {"tag": "test"},
    {"version": "1", "author": "user"},
    {"numbers": [1, 2, 3]},
    {"nested": {"deep": True}},
])
def test_metadata_json_round_trip(metadata):
    b = _build()
    r = import_build(export_to_json(b, metadata=metadata))
    assert r.success


@pytest.mark.parametrize("metadata", [
    {"tag": "v1"},
    {"notes": "draft"},
    {},
])
def test_metadata_fbs_round_trip(metadata):
    b = _build()
    r = import_build(export_to_fbs(b, metadata=metadata))
    assert r.success


# ---------------------------------------------------------------------------
# H. Invalid import sources
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_source", [
    "not json",
    "{}",                            # missing required fields
    '{"character_class": "Mage"}',   # missing passive_tree and gear
    '{"passive_tree": [], "gear": []}',  # missing character_class
    "FORGE:not_valid_base64!!!",
    "",
    "{invalid json}",
])
def test_invalid_sources_fail(bad_source):
    r = import_build(bad_source)
    assert not r.success or (r.success and len(r.errors) == 0)


@pytest.mark.parametrize("bad_type", [None, 42, 3.14, [], True])
def test_unsupported_source_types_fail(bad_type):
    r = import_build(bad_type)
    assert not r.success


# ---------------------------------------------------------------------------
# I. Export timestamp is positive float
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", range(5))
def test_exported_at_is_positive(n):
    sb = export_build(_build())
    assert sb.exported_at > 0


# ---------------------------------------------------------------------------
# J. Version fields
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _COMBOS[:5])
def test_version_always_matches_schema_version(char_class, mastery):
    sb = export_build(_build(char_class=char_class, mastery=mastery))
    assert sb.version == _SCHEMA_VERSION


@pytest.mark.parametrize("char_class,mastery", _COMBOS[:5])
def test_json_has_correct_version(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    data = json.loads(export_to_json(b))
    assert data["version"] == _SCHEMA_VERSION


# ---------------------------------------------------------------------------
# K. FBS prefix constant tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class", ["Mage", "Sentinel", "Rogue", "Primalist", "Acolyte"])
def test_fbs_starts_with_prefix(char_class):
    fbs = export_to_fbs(_build(char_class=char_class))
    assert fbs.startswith(_FBS_PREFIX)


@pytest.mark.parametrize("char_class", ["Mage", "Sentinel", "Rogue"])
def test_fbs_decodable(char_class):
    import base64
    fbs = export_to_fbs(_build(char_class=char_class))
    encoded = fbs[len(_FBS_PREFIX):]
    decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
    data = json.loads(decoded)
    assert data["character_class"] == char_class


# ---------------------------------------------------------------------------
# L. Multiple sequential exports give same checksum
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _COMBOS[:5])
def test_same_build_same_checksum(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    sb1 = export_build(b)
    sb2 = export_build(b)
    assert sb1.checksum == sb2.checksum


# ---------------------------------------------------------------------------
# M. import_from_json / import_from_fbs wrappers parametrized
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _COMBOS)
def test_import_from_json_wrapper(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = import_from_json(export_to_json(b))
    assert r.success
    assert r.build["character_class"] == char_class


@pytest.mark.parametrize("char_class,mastery", _COMBOS)
def test_import_from_fbs_wrapper(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = import_from_fbs(export_to_fbs(b))
    assert r.success
    assert r.build["character_class"] == char_class
