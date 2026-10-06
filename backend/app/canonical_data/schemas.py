"""Accepted R1 canonical schemas: identity extraction and known fields.

This is schema-level knowledge only (no record counts, no values):

* which ``_meta.schema`` strings the Forge accepts;
* where records live and how each record's **source identity** is built
  (``ids`` types; never names);
* the field names the adapter knows at each record level. A record carrying a
  field outside this set puts the family into an explicit review state
  (``SCHEMA_REVIEW_REQUIRED``); the field is still carried, never dropped.

Typed domain views for classes, abilities, items, uniques, sets, ailments and
blessings (R2-P04) do not exist yet; they are added here when R1 produces
them from the 1.5 TypeTree dumps (B1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, Callable, Iterator

from .errors import InvalidIdentity, SchemaReviewRequired, UnsupportedCanonicalSchema
from .ids import (
    AbilityId, AffixId, AffixPropertyId, PassiveNodeId, PropertyId, PropertyNamespace, SkillTreeId,
    SourceRef, TreeNodeId,
)

# One indexed record: (identity, record dict, json path for diagnostics)
IndexedRecord = tuple[SourceRef, dict, str]


@dataclass(frozen=True)
class SchemaSpec:
    schema: str
    family_kind: str                       # affixes | tree | property_definitions | typetree_envelope
    known_fields: dict[str, frozenset[str]] = field(default_factory=dict)  # level -> field names
    index: Callable[[dict], Iterator[IndexedRecord]] | None = None
    records: Callable[[dict], Iterator[tuple[str, dict]]] | None = None   # (level, record) for field review
    build_identity: Callable[[dict], str | None] | None = None            # self-declared GameAssembly sha256


def _req(m: Any, key: str, where: str, kind: type | tuple = (list, tuple)) -> Any:
    """A required container. Absent or mistyped is a schema problem, never an empty family."""
    v = m.get(key) if isinstance(m, Mapping) else None
    if not isinstance(v, kind):
        raise SchemaReviewRequired(f"{where}.{key} is missing or has the wrong type")
    return v


def _meta(doc: Any) -> Mapping:
    return _req(doc, "_meta", "<document>", Mapping)


def _opt_map(m: Any, key: str) -> Mapping:
    """An optional provenance mapping; absence yields None from the caller's final lookup."""
    v = m.get(key) if isinstance(m, Mapping) else None
    return v if isinstance(v, Mapping) else MappingProxyType({})


def _fs(*names: str) -> frozenset[str]:
    return frozenset(names)


# --- r1_canonical_affix/1 ---------------------------------------------------------------
AFFIX_META = _fs("anomalies", "builder", "counts", "enums", "identity_contract", "roll_mapping_contract", "schema",
                 "source", "source_class", "value_scale_contract")
AFFIX_RECORD = _fs("affix_id", "affix_id_to_convert_to", "can_roll_on", "class_specificity",
                   "convert_on_incompatible_item_type", "display_category", "group", "level_requirement",
                   "maximum_affix_effect_modifier_for_t6", "morphology", "names", "properties", "rolls_on",
                   "shard_hue_shift", "shard_saturation_modifier", "source", "special_affix_type",
                   "specific_reroll_chances", "standard_affix_effect_modifier", "structure", "t6_compatibility",
                   "tiers", "title_type", "type", "unique_id", "value_scale", "weapon_effect", "weighting")


def _affix_records(doc):
    yield "_meta", _meta(doc)
    for r in _req(doc, "affixes", "<document>"):
        yield "affix", r


def _affix_index(doc):
    for i, r in enumerate(_req(doc, "affixes", "<document>")):
        aid = AffixId(r["affix_id"])
        yield aid, r, f"affixes[{i}]"
        for j, p in enumerate(_req(r, "properties", f"affixes[{i}]")):
            yield AffixPropertyId(aid, p["index"]), p, f"affixes[{i}].properties[{j}]"


def _affix_build(doc):
    return _opt_map(_meta(doc), "source").get("game_assembly_sha256")


# --- r1_canonical_tree/1 (passive, skill, weaver) -------------------------------------------
TREE_META = _fs("builder", "counts", "defective_trees", "enums", "identity_contract", "kind", "schema", "source",
                "stat_property_contract", "stat_property_raw_values", "stat_value_contract")
TREE_RECORD = _fs("ability_ref", "declared_node_count", "has_set_ability", "integrity_problems", "integrity_status",
                  "kind", "missing_nodes", "node_count", "nodes", "requirement_resolution", "specialised",
                  "tree_class", "tree_id", "tree_path_id")
TREE_NODE = _fs("ability_granted_by_node", "alt_text", "decode_suspect", "description", "field_shift_suspect",
                "lore_text", "mastery", "mastery_requirement", "max_points", "name", "no_scaling_point_threshold",
                "no_scaling_type", "node_description", "node_id", "path_id", "point_bonus_description",
                "requirements", "stats", "tree_path_id")
TREE_REQUIREMENT = _fs("node_id", "node_path_id", "points_required", "resolution")


def _tree_records(doc):
    yield "_meta", _meta(doc)
    for i, t in enumerate(_req(doc, "trees", "<document>")):
        yield "tree", t
        for j, n in enumerate(_req(t, "nodes", f"trees[{i}]")):
            yield "node", n
            for q in _req(n, "requirements", f"trees[{i}].nodes[{j}]"):
                yield "requirement", q


def node_identity(kind: str, tree: SkillTreeId, node_id: int) -> SourceRef:
    return PassiveNodeId(tree, node_id) if kind == "passive" else TreeNodeId(tree, node_id)


def _tree_index(doc):
    kind = _meta(doc).get("kind")
    if kind not in ("passive", "skill", "weaver"):
        raise UnsupportedCanonicalSchema(f"tree family kind {kind!r} is not passive/skill/weaver")
    for i, t in enumerate(_req(doc, "trees", "<document>")):
        tid = SkillTreeId(t["tree_id"])
        yield tid, t, f"trees[{i}]"
        for j, n in enumerate(_req(t, "nodes", f"trees[{i}]")):
            yield node_identity(kind, tid, n["node_id"]), n, f"trees[{i}].nodes[{j}]"


def _tree_build(doc):
    gb = _opt_map(_opt_map(_meta(doc), "source"), "raw_meta").get("game_build")
    return gb.get("gameAssemblySha256") if isinstance(gb, Mapping) else None


# --- r1_canonical_property_definitions/1 -----------------------------------------------------
PD_META = _fs("builder", "counts", "master_localization", "not_available", "schema", "semantics_contract", "source",
              "sources")
PD_FAMILIES = {
    "master_properties": _fs("alt_text", "alt_text_key", "alt_text_overrides", "display_flags", "display_name",
                             "enum_name", "identity_source", "localization_match", "property_id", "rounding",
                             "value_type"),
    "player_properties": _fs("alt_text", "alt_text_key", "identity_source", "name", "name_key",
                             "player_property_id", "value_type"),
    "ability_properties": _fs("ability_id", "ability_id_status", "ability_key", "alt_text", "alt_text_key",
                              "identity_source", "name", "name_key", "property_index", "value_type"),
    "tracker_properties": _fs("enum_name", "identity_source", "tracker_property_id", "value_type"),
    "conditional_damage_properties": _fs("conditional_damage_property_id", "enum_name", "identity_source",
                                         "value_type"),
    "idol_altar_properties": _fs("enum_name", "identity_source", "idol_altar_property_id", "value_type"),
    "tree_stat_name_table": _fs("note", "source_class", "status"),
}
_PD_ID = {
    "master_properties": (PropertyNamespace.SP, "property_id"),
    "player_properties": (PropertyNamespace.PLAYER, "player_property_id"),
    "tracker_properties": (PropertyNamespace.TRACKER, "tracker_property_id"),
    "conditional_damage_properties": (PropertyNamespace.CONDITIONAL_DAMAGE, "conditional_damage_property_id"),
    "idol_altar_properties": (PropertyNamespace.IDOL_ALTAR, "idol_altar_property_id"),
}


def _pd_records(doc):
    yield "_meta", _meta(doc)
    for name, recs in _req(doc, "families", "<document>", Mapping).items():
        if isinstance(recs, (list, tuple)):
            for r in recs:
                yield f"families.{name}", r
        else:
            yield f"families.{name}", recs


def _pd_index(doc):
    fams = _req(doc, "families", "<document>", Mapping)
    for name, (ns, key) in _PD_ID.items():
        for i, r in enumerate(_req(fams, name, "families")):
            yield PropertyId(ns, r[key]), r, f"families.{name}[{i}]"
    for i, r in enumerate(_req(fams, "ability_properties", "families")):
        if not isinstance(r.get("ability_id"), int):
            # An ability property without a resolved ability id has no source identity yet.
            raise InvalidIdentity(f"families.ability_properties[{i}] has no integer ability_id")
        yield (PropertyId(PropertyNamespace.ABILITY, r["property_index"], AbilityId(r["ability_id"])), r,
               f"families.ability_properties[{i}]")


# --- r1_canonical_typetree_envelope/1 (lossless raw envelopes; no identity index) -------------
ENVELOPE_META = _fs("class", "complete", "contract", "counts", "denominator", "schema", "source", "builder")


def _envelope_records(doc):
    yield "_meta", _meta(doc)


def _envelope_build(doc):
    gb = _opt_map(_meta(doc), "source").get("game_build")
    return gb.get("gameAssemblySha256") if isinstance(gb, Mapping) else None


SCHEMAS: dict[str, SchemaSpec] = {
    "r1_canonical_affix/1": SchemaSpec(
        "r1_canonical_affix/1", "affixes", {"_meta": AFFIX_META, "affix": AFFIX_RECORD},
        _affix_index, _affix_records, _affix_build),
    "r1_canonical_tree/1": SchemaSpec(
        "r1_canonical_tree/1", "tree",
        {"_meta": TREE_META, "tree": TREE_RECORD, "node": TREE_NODE, "requirement": TREE_REQUIREMENT},
        _tree_index, _tree_records, _tree_build),
    "r1_canonical_property_definitions/1": SchemaSpec(
        "r1_canonical_property_definitions/1", "property_definitions",
        {"_meta": PD_META, **{f"families.{k}": v for k, v in PD_FAMILIES.items()}},
        _pd_index, _pd_records, None),
    "r1_canonical_typetree_envelope/1": SchemaSpec(
        "r1_canonical_typetree_envelope/1", "typetree_envelope", {"_meta": ENVELOPE_META},
        None, _envelope_records, _envelope_build),
}

# Families a bundle must contain today (the canonical families R1 produces).
# R2-P04 adds the typed views (classes, abilities, items, uniques, sets,
# ailments, blessings) once they exist; until then they cannot be required.
REQUIRED_FAMILIES: frozenset[str] = frozenset(
    {"affixes", "passive_trees", "skill_trees", "weaver_tree", "property_definitions"})


def spec_for(schema: Any, family_id: str) -> SchemaSpec:
    spec = SCHEMAS.get(schema) if isinstance(schema, str) else None
    if spec is None:
        raise UnsupportedCanonicalSchema(f"family {family_id!r}: schema {schema!r} is not accepted; accepted: "
                                         f"{sorted(SCHEMAS)}", family=family_id, schema=schema)
    return spec


def unknown_fields(spec: SchemaSpec, doc: dict) -> dict[str, list[str]]:
    """Field names present in records but unknown to the adapter, per level."""
    out: dict[str, set[str]] = {}
    if spec.records is None:
        return {}
    for level, rec in spec.records(doc):
        known = spec.known_fields.get(level)
        if known is None or not isinstance(rec, Mapping):
            continue
        extra = set(rec) - known
        if extra:
            out.setdefault(level, set()).update(extra)
    return {k: sorted(v) for k, v in sorted(out.items())}
