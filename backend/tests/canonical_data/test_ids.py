"""P03 typed source identities."""
from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from app.canonical_data import ids as I
from app.canonical_data.errors import InvalidIdentity

PKG = Path(I.__file__).resolve().parent

SAMPLES = [
    I.ClassId(3), I.MasteryRef(I.ClassId(1), 2), I.MasteryRef(I.ClassId(0), 0), I.SkillId(I.AbilityId(50)),
    I.AbilityId(0), I.SkillTreeId("an0my"), I.SkillTreeId("ac-1"), I.TreeNodeId(I.SkillTreeId("wo42"), 7),
    I.PassiveNodeId(I.SkillTreeId("ac-1"), 86), I.AffixId(0), I.AffixPropertyId(I.AffixId(14), 1),
    I.BaseTypeId(41), I.BaseItemId(I.BaseTypeId(0), 3), I.UniqueId(409), I.SetId(12), I.AilmentId(2),
    I.BlessingId(I.BaseItemId(I.BaseTypeId(34), 0)), I.PropertyId(I.PropertyNamespace.SP, 21),
    I.PropertyId(I.PropertyNamespace.ABILITY, 2, I.AbilityId(50)),
]


@pytest.mark.parametrize("ref", SAMPLES, ids=lambda r: r.key())
def test_key_round_trips(ref):
    assert I.parse_key(ref.key()) == ref
    assert hash(I.parse_key(ref.key())) == hash(ref)


def test_every_family_type_is_covered():
    assert {type(r) for r in SAMPLES} == set(I.ALL_ID_TYPES)


def test_types_never_compare_equal_across_families():
    assert I.AffixId(3) != I.UniqueId(3)
    assert I.AffixId(3) != 3
    assert I.TreeNodeId(I.SkillTreeId("x"), 1) != I.PassiveNodeId(I.SkillTreeId("x"), 1)
    assert I.SkillId(I.AbilityId(5)) != I.AbilityId(5)
    assert len({I.AffixId(3), I.UniqueId(3), I.SetId(3), I.AilmentId(3)}) == 4


@pytest.mark.parametrize("make", [
    lambda: I.AffixId("Void Penetration"),      # a display name is never an id
    lambda: I.AffixId("3"),                     # numeric source ids are ints, not strings
    lambda: I.AffixId(True),                    # bool is not an id
    lambda: I.AffixId(-1),
    lambda: I.AffixId(3.0),
    lambda: I.ClassId(256),
    lambda: I.TreeNodeId(I.SkillTreeId("x"), 256),      # SkillTreeNode.id is a u8
    lambda: I.SkillTreeId("Fire ball"),                 # tree codes have no spaces
    lambda: I.SkillTreeId(""),
    lambda: I.SkillTreeId(9),
    lambda: I.MasteryRef(1, 2),                         # class must be a ClassId
    lambda: I.MasteryRef(I.ClassId(1), -1),
    lambda: I.SkillId(5),
    lambda: I.TreeNodeId("an0my", 1),
    lambda: I.AffixPropertyId(I.UniqueId(1), 0),
    lambda: I.BaseItemId(0, 1),
    lambda: I.BlessingId(I.BaseTypeId(34)),
    lambda: I.PropertyId("SP", 1),
    lambda: I.PropertyId(I.PropertyNamespace.ABILITY, 1),                 # ability required
    lambda: I.PropertyId(I.PropertyNamespace.SP, 1, I.AbilityId(1)),      # ability forbidden
])
def test_invalid_identities_rejected(make):
    with pytest.raises(InvalidIdentity):
        make()


@pytest.mark.parametrize("key", ["affix:01", "affix:-1", "affix:x", "affix", "nope:1", "mastery:1",
                                 "mastery:1:2:3", "prop:NOPE:1", "prop:ABILITY:1", "node:bad id:1", 7, None])
def test_parse_key_rejects_malformed(key):
    with pytest.raises(InvalidIdentity):
        I.parse_key(key)


def test_identities_are_immutable():
    a = I.AffixId(1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        a.value = 2
    m = I.MasteryRef(I.ClassId(1), 1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.mastery_index = 3


def test_mastery_identity_is_composite_and_positional():
    """Masteries have no source id: identity is (class, position in CharacterClass.masteries)."""
    assert not hasattr(I, "MasteryId")
    assert I.MasteryRef(I.ClassId(1), 0).is_base_class
    assert not I.MasteryRef(I.ClassId(1), 2).is_base_class
    # Same index in different classes are different masteries.
    assert I.MasteryRef(I.ClassId(1), 2) != I.MasteryRef(I.ClassId(2), 2)
    assert set(I.MasteryRef.__dataclass_fields__) == {"class_id", "mastery_index"}


def test_no_name_based_constructors_in_package():
    """Names are presentation: nothing in the package builds an identity from a name."""
    bad = []
    for path in PKG.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n = node.name.lower()
                if "from_name" in n or "by_name" in n or "by_slug" in n or "from_slug" in n:
                    bad.append(f"{path.name}:{node.name}")
    assert bad == []


def test_wrong_metadata_tree_codes_are_plain_identities():
    """fi9/en6/me27/rf1azz carry wrong display names in the Forge metadata; identity ignores names."""
    for code in ("fi9", "en6", "me27", "rf1azz"):
        ref = I.SkillTreeId(code)
        assert ref.key() == f"tree:{code}"
        assert I.parse_key(ref.key()) == ref
