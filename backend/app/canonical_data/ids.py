"""Typed source identities (AUDIT-R2 P03).

Rules (docs/audits/2026-10-system-deep-audit/r2/R2_IDENTITY_POLICY.md):

* Source identity only. Every type wraps an id the game serializes, or a
  composite of such ids where the game itself identifies a thing by position.
* Names, slugs and display strings are never identity. There is no
  ``from_name`` constructor anywhere in this module, and constructors reject
  strings where the source id is numeric.
* Types do not mix: ``AffixId(3) != UniqueId(3)`` and neither equals ``3``.
* Masteries have no source id. They are identified by their position in
  ``CharacterClass.masteries`` (index 0 is the base class), so the type is
  the composite ``MasteryRef(class_id, mastery_index)``. There is no
  ``MasteryId(int)``.
* One formatter and one parser per type: ``ref.key()`` and ``parse_key()``.

Path ids are serialized-object ids valid inside one snapshot only; they are
not identities and have no type here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, ClassVar, dataclass_transform

from .errors import InvalidIdentity

_TREE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}$")


def _int(value: Any, field: str, type_name: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    # bool is an int subclass; a True/False id is always a bug.
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidIdentity(f"{type_name}.{field} must be an int source id, got {type(value).__name__} {value!r}")
    if value < minimum or (maximum is not None and value > maximum):
        raise InvalidIdentity(f"{type_name}.{field}={value} outside [{minimum}, {maximum}]")
    return value


def _instance(value: Any, cls: type, field: str, type_name: str) -> Any:
    if type(value) is not cls:
        raise InvalidIdentity(f"{type_name}.{field} must be {cls.__name__}, got {type(value).__name__}")
    return value


class SourceRef:
    """Base of every typed identity. Subclasses are frozen dataclasses."""

    __slots__ = ()
    PREFIX: ClassVar[str] = ""

    def key(self) -> str:  # pragma: no cover - implemented by subclasses
        raise NotImplementedError


_REGISTRY: dict[str, Callable[[list[str]], "SourceRef"]] = {}


def _register(prefix: str):
    def deco(cls):
        cls.PREFIX = prefix
        _REGISTRY[prefix] = cls._from_parts
        return cls
    return deco


def _parse_int(text: str, what: str) -> int:
    if not re.fullmatch(r"0|[1-9][0-9]*", text):
        raise InvalidIdentity(f"{what}: {text!r} is not a canonical non-negative integer")
    return int(text)


def parse_key(key: str) -> SourceRef:
    """Inverse of ``ref.key()`` for every registered type."""
    if not isinstance(key, str) or ":" not in key:
        raise InvalidIdentity(f"not an identity key: {key!r}")
    prefix, rest = key.split(":", 1)
    parser = _REGISTRY.get(prefix)
    if parser is None:
        raise InvalidIdentity(f"unknown identity prefix {prefix!r} in {key!r}")
    return parser(rest.split(":"))


def _arity(parts: list[str], n: int, prefix: str) -> list[str]:
    if len(parts) != n:
        raise InvalidIdentity(f"{prefix} key needs {n} part(s), got {len(parts)}: {parts!r}")
    return parts


# --- single integer source ids --------------------------------------------------

@dataclass_transform(order_default=True, frozen_default=True)
def _int_id(prefix: str, doc: str, maximum: int | None = None):
    def build(cls):
        cls.__doc__ = doc

        def __post_init__(self):
            _int(self.value, "value", cls.__name__, maximum=maximum)

        def key(self) -> str:
            return f"{prefix}:{self.value}"

        @classmethod
        def _from_parts(klass, parts):
            (v,) = _arity(parts, 1, prefix)
            return klass(_parse_int(v, prefix))

        cls.__post_init__ = __post_init__
        cls.key = key
        cls._from_parts = _from_parts
        return _register(prefix)(dataclass(frozen=True, slots=True, order=True)(cls))
    return build


@_int_id("class", "CharacterClass.classID (0-4 in 1.4.6).", maximum=255)
class ClassId(SourceRef):
    value: int


@_int_id("ability", "Ability.playerAbilityID (AbilityID enum value).")
class AbilityId(SourceRef):
    value: int


@_int_id("affix", "AffixList affix id (canonical affix_id).")
class AffixId(SourceRef):
    value: int


@_int_id("basetype", "Item base type id (baseTypeID).", maximum=255)
class BaseTypeId(SourceRef):
    value: int


@_int_id("unique", "Unique item id (UniqueList entry id).")
class UniqueId(SourceRef):
    value: int


@_int_id("set", "Set id (UniqueList setID / set bonus data).")
class SetId(SourceRef):
    value: int


@_int_id("ailment", "Ailment.id (AilmentID enum value).")
class AilmentId(SourceRef):
    value: int


# --- string source ids ------------------------------------------------------------

@_register("tree")
@dataclass(frozen=True, slots=True, order=True)
class SkillTreeId(SourceRef):
    """Tree.treeID as serialized (for example ``an0my``, ``ac-1``, ``weaver``).

    The tree code is a source id, not a name: it is never derived from a skill
    or class display name.
    """

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not _TREE_ID.fullmatch(self.value):
            raise InvalidIdentity(f"SkillTreeId must be a source tree code, got {self.value!r}")

    def key(self) -> str:
        return f"tree:{self.value}"

    @classmethod
    def _from_parts(cls, parts):
        (v,) = _arity(parts, 1, "tree")
        return cls(v)


# --- composites the game genuinely requires ---------------------------------------

@_register("mastery")
@dataclass(frozen=True, slots=True, order=True)
class MasteryRef(SourceRef):
    """``(class_id, mastery_index)``: position in ``CharacterClass.masteries``.

    The game has no mastery id. Index 0 is the base class; 1..n are masteries
    in source order. The index is the source list position carried by the
    canonical class view, never a position in a Forge-side array.
    """

    class_id: ClassId
    mastery_index: int

    def __post_init__(self):
        _instance(self.class_id, ClassId, "class_id", "MasteryRef")
        _int(self.mastery_index, "mastery_index", "MasteryRef", maximum=255)

    @property
    def is_base_class(self) -> bool:
        return self.mastery_index == 0

    def key(self) -> str:
        return f"mastery:{self.class_id.value}:{self.mastery_index}"

    @classmethod
    def _from_parts(cls, parts):
        c, i = _arity(parts, 2, "mastery")
        return cls(ClassId(_parse_int(c, "mastery.class")), _parse_int(i, "mastery.index"))


@_register("skill")
@dataclass(frozen=True, slots=True, order=True)
class SkillId(SourceRef):
    """A skill is a player-usable ability; its source identity is the ability id.

    Kept as a distinct type so a skill reference cannot be passed where any
    ability (including internal sub-abilities) is accepted. Variants with a
    different ability id are different skills.
    """

    ability: AbilityId

    def __post_init__(self):
        _instance(self.ability, AbilityId, "ability", "SkillId")

    def key(self) -> str:
        return f"skill:{self.ability.value}"

    @classmethod
    def _from_parts(cls, parts):
        (a,) = _arity(parts, 1, "skill")
        return cls(AbilityId(_parse_int(a, "skill.ability")))


@_register("node")
@dataclass(frozen=True, slots=True, order=True)
class TreeNodeId(SourceRef):
    """``(tree_id, node_id)``: ``SkillTreeNode.id`` is a u8 unique only within its tree."""

    tree: SkillTreeId
    node_id: int

    def __post_init__(self):
        _instance(self.tree, SkillTreeId, "tree", "TreeNodeId")
        _int(self.node_id, "node_id", "TreeNodeId", maximum=255)

    def key(self) -> str:
        return f"node:{self.tree.value}:{self.node_id}"

    @classmethod
    def _from_parts(cls, parts):
        t, n = _arity(parts, 2, "node")
        return cls(SkillTreeId(t), _parse_int(n, "node.node_id"))


@_register("passive")
@dataclass(frozen=True, slots=True, order=True)
class PassiveNodeId(SourceRef):
    """A passive node: ``(passive tree id, node_id)``.

    Distinct from ``TreeNodeId`` so passive and specialization nodes cannot be
    confused. The class of a passive tree comes from
    ``CharacterTree.characterClassID`` through the class view (R2-P04); the
    canonical passive export identifies trees by tree code, so that is the
    source identity used here rather than a class id the export does not carry.
    """

    tree: SkillTreeId
    node_id: int

    def __post_init__(self):
        _instance(self.tree, SkillTreeId, "tree", "PassiveNodeId")
        _int(self.node_id, "node_id", "PassiveNodeId", maximum=255)

    def key(self) -> str:
        return f"passive:{self.tree.value}:{self.node_id}"

    @classmethod
    def _from_parts(cls, parts):
        t, n = _arity(parts, 2, "passive")
        return cls(SkillTreeId(t), _parse_int(n, "passive.node_id"))


@_register("affixprop")
@dataclass(frozen=True, slots=True, order=True)
class AffixPropertyId(SourceRef):
    """``(affix_id, property_index)``: index 0 = top-level property, then extra rolls."""

    affix: AffixId
    property_index: int

    def __post_init__(self):
        _instance(self.affix, AffixId, "affix", "AffixPropertyId")
        _int(self.property_index, "property_index", "AffixPropertyId", maximum=63)

    def key(self) -> str:
        return f"affixprop:{self.affix.value}:{self.property_index}"

    @classmethod
    def _from_parts(cls, parts):
        a, i = _arity(parts, 2, "affixprop")
        return cls(AffixId(_parse_int(a, "affixprop.affix")), _parse_int(i, "affixprop.index"))


@_register("item")
@dataclass(frozen=True, slots=True, order=True)
class BaseItemId(SourceRef):
    """``(base_type_id, sub_type_id)``: ``subTypeID`` restarts at 0 in every base type."""

    base_type: BaseTypeId
    sub_type_id: int

    def __post_init__(self):
        _instance(self.base_type, BaseTypeId, "base_type", "BaseItemId")
        _int(self.sub_type_id, "sub_type_id", "BaseItemId", maximum=65535)

    def key(self) -> str:
        return f"item:{self.base_type.value}:{self.sub_type_id}"

    @classmethod
    def _from_parts(cls, parts):
        b, s = _arity(parts, 2, "item")
        return cls(BaseTypeId(_parse_int(b, "item.base_type")), _parse_int(s, "item.sub_type"))


@_register("blessing")
@dataclass(frozen=True, slots=True, order=True)
class BlessingId(SourceRef):
    """Blessings are item subtypes; identity is the item identity (confirm base type in the 1.5 dump)."""

    item: BaseItemId

    def __post_init__(self):
        _instance(self.item, BaseItemId, "item", "BlessingId")

    def key(self) -> str:
        return f"blessing:{self.item.base_type.value}:{self.item.sub_type_id}"

    @classmethod
    def _from_parts(cls, parts):
        b, s = _arity(parts, 2, "blessing")
        return cls(BaseItemId(BaseTypeId(_parse_int(b, "blessing.base_type")), _parse_int(s, "blessing.sub_type")))


class PropertyNamespace(str, Enum):
    """Property id spaces from the canonical property definitions."""

    SP = "SP"                                   # master stat properties (SP enum)
    PLAYER = "PLAYER"                           # player property ids
    ABILITY = "ABILITY"                         # (ability_id, property_index)
    TRACKER = "TRACKER"                         # TrackerPropertyID
    CONDITIONAL_DAMAGE = "CONDITIONAL_DAMAGE"   # ConditionalDamageProperty
    IDOL_ALTAR = "IDOL_ALTAR"                   # IdolAltarPropertyID
    AILMENT = "AILMENT"                         # tree stat bands keyed by AilmentID


@_register("prop")
@dataclass(frozen=True, slots=True, order=True)
class PropertyId(SourceRef):
    """A property in one namespace. ABILITY properties also carry their ability."""

    namespace: PropertyNamespace
    index: int
    ability: AbilityId | None = None

    def __post_init__(self):
        if not isinstance(self.namespace, PropertyNamespace):
            raise InvalidIdentity(f"PropertyId.namespace must be PropertyNamespace, got {self.namespace!r}")
        _int(self.index, "index", "PropertyId")
        if (self.namespace is PropertyNamespace.ABILITY) != (self.ability is not None):
            raise InvalidIdentity("PropertyId.ability is required for ABILITY properties and forbidden otherwise")
        if self.ability is not None:
            _instance(self.ability, AbilityId, "ability", "PropertyId")

    def key(self) -> str:
        if self.ability is not None:
            return f"prop:{self.namespace.value}:{self.ability.value}:{self.index}"
        return f"prop:{self.namespace.value}:{self.index}"

    @classmethod
    def _from_parts(cls, parts):
        if not parts:
            raise InvalidIdentity("prop key needs a namespace")
        try:
            ns = PropertyNamespace(parts[0])
        except ValueError as e:
            raise InvalidIdentity(f"unknown property namespace {parts[0]!r}") from e
        if ns is PropertyNamespace.ABILITY:
            _, a, i = _arity(parts, 3, "prop")
            return cls(ns, _parse_int(i, "prop.index"), AbilityId(_parse_int(a, "prop.ability")))
        _, i = _arity(parts, 2, "prop")
        return cls(ns, _parse_int(i, "prop.index"))


ALL_ID_TYPES: tuple[type, ...] = (
    ClassId, MasteryRef, SkillId, AbilityId, SkillTreeId, TreeNodeId, PassiveNodeId, AffixId,
    AffixPropertyId, BaseTypeId, BaseItemId, UniqueId, SetId, AilmentId, BlessingId, PropertyId,
)
