"""Relationship and graph primitives (AUDIT-R2 P09).

An ``Edge`` links two typed source identities under a ``RelationshipType``
and always carries its resolution state. A missing target is never ``0``,
never "the first candidate" and never a silent ``None``: an edge whose target
is not resolved has ``target=None`` *and* a non-RESOLVED ``resolution``, and
APIs that return targets refuse to drop unresolved edges of a required
relationship.

Graphs stay graphs. A node may have zero, one or many prerequisite edges;
there is no ``parentId``. What "satisfied" means for several prerequisites
(all-of or any-of) is game logic, decided with source evidence by the
consumer packages (R2-P07/P08), not here.

Only schema-level adapters live here (built from R1 canonical schemas). No
1.5 relationships are populated; classes, abilities and items gain adapters
when their typed views exist (R2-P04).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping

from .errors import InvalidIdentity, RelationshipIntegrityFailure, SchemaReviewRequired
from .ids import AbilityId, AffixId, AffixPropertyId, PropertyId, PropertyNamespace, SkillTreeId, SourceRef
from .trust import TrustState


class Cardinality(str, Enum):
    ONE_TO_ONE = "ONE_TO_ONE"        # each source <= 1 edge, each target <= 1 incoming
    ONE_TO_MANY = "ONE_TO_MANY"      # each target <= 1 incoming (a parent owns its children)
    MANY_TO_ONE = "MANY_TO_ONE"      # each source <= 1 edge
    MANY_TO_MANY = "MANY_TO_MANY"    # graph edges (e.g. multi-prerequisite nodes)


class Resolution(str, Enum):
    RESOLVED = "RESOLVED"
    NULL_REFERENCE = "NULL_REFERENCE"                    # source holds an explicit empty reference
    IMPLAUSIBLE_REFERENCE = "IMPLAUSIBLE_REFERENCE"      # bytes misread as a reference (decoder fault)
    TARGET_FAILED_TO_PARSE = "TARGET_FAILED_TO_PARSE"    # target exists in source but was not decoded
    UNRESOLVED_REFERENCE = "UNRESOLVED_REFERENCE"        # plausible reference, target not found
    AMBIGUOUS = "AMBIGUOUS"                              # several candidates; never auto-picked
    NOT_CARRIED = "NOT_CARRIED"                          # the source dump does not carry this reference
    QUARANTINED = "QUARANTINED"                          # target known but its family is not trusted


UNRESOLVED_STATES = frozenset(r for r in Resolution if r is not Resolution.RESOLVED)


@dataclass(frozen=True)
class RelationshipType:
    name: str
    source_type: type
    target_type: type
    cardinality: Cardinality
    required: bool
    ordered: bool = False
    description: str = ""


@dataclass(frozen=True)
class Edge:
    rel: RelationshipType
    source: SourceRef
    target: SourceRef | None
    resolution: Resolution
    raw_target: Any = None
    ordinal: int | None = None
    attributes: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    provenance: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        if type(self.source) is not self.rel.source_type:
            raise InvalidIdentity(f"{self.rel.name}: source must be {self.rel.source_type.__name__}, "
                                  f"got {type(self.source).__name__}")
        if not isinstance(self.resolution, Resolution):
            raise InvalidIdentity(f"{self.rel.name}: resolution must be a Resolution")
        if self.resolution is Resolution.RESOLVED:
            if type(self.target) is not self.rel.target_type:
                raise InvalidIdentity(f"{self.rel.name}: RESOLVED edge needs a {self.rel.target_type.__name__} "
                                      f"target, got {type(self.target).__name__}")
        elif self.target is not None and self.resolution not in (Resolution.QUARANTINED,):
            raise InvalidIdentity(f"{self.rel.name}: a {self.resolution.value} edge must not carry a target "
                                  f"(an unresolved target is never substituted)")
        if self.rel.ordered and (self.ordinal is None or self.ordinal < 0):
            raise InvalidIdentity(f"{self.rel.name}: ordered relationship needs a non-negative ordinal")

    @property
    def resolved(self) -> bool:
        return self.resolution is Resolution.RESOLVED


@dataclass(frozen=True)
class IntegrityReport:
    relationship: str
    required: bool
    total: int
    by_resolution: Mapping[str, int]
    allowlisted: int
    dangling: int                    # unresolved and not allowlisted

    @property
    def ok(self) -> bool:
        return not (self.required and self.dangling)


class RelationshipSet:
    """All edges of one relationship type, validated and indexed. Immutable."""

    __slots__ = ("rel", "edges", "source_trust", "allowlist", "_out", "_in", "_sealed")
    rel: RelationshipType
    edges: tuple[Edge, ...]
    source_trust: TrustState
    allowlist: Mapping[tuple[str, str], str]
    _out: Mapping[SourceRef, tuple[Edge, ...]]
    _in: Mapping[SourceRef, tuple[Edge, ...]]
    _sealed: bool

    def __init__(self, rel: RelationshipType, edges: Iterable[Edge], *, source_trust: TrustState,
                 allowlist: Mapping[tuple[str, str], str] | None = None):
        edges = tuple(edges)
        for e in edges:
            if e.rel is not rel:
                raise InvalidIdentity(f"edge of {e.rel.name!r} added to set {rel.name!r}")
        out: dict[SourceRef, list[Edge]] = defaultdict(list)
        inc: dict[SourceRef, list[Edge]] = defaultdict(list)
        for e in edges:
            out[e.source].append(e)
            if e.target is not None:
                inc[e.target].append(e)
        _check_cardinality(rel, out, inc)
        if rel.ordered:
            for src, es in out.items():
                ords = [e.ordinal for e in es]
                if len(set(ords)) != len(ords):
                    raise InvalidIdentity(f"{rel.name}: duplicate ordinal for {src.key()}")
        if allowlist:
            for (skey, raw), reason in allowlist.items():
                if not reason or not str(reason).strip():
                    raise InvalidIdentity(f"{rel.name}: allowlist entry {skey}/{raw} needs a reason")
        object.__setattr__(self, "rel", rel)
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "source_trust", source_trust)
        object.__setattr__(self, "allowlist", MappingProxyType(dict(allowlist or {})))
        object.__setattr__(self, "_out", MappingProxyType({k: tuple(sorted(v, key=_order)) for k, v in out.items()}))
        object.__setattr__(self, "_in", MappingProxyType({k: tuple(sorted(v, key=_order)) for k, v in inc.items()}))
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        raise AttributeError("RelationshipSet is read-only")

    # --- queries ----------------------------------------------------------------------
    def outgoing(self, source: SourceRef) -> tuple[Edge, ...]:
        """Every edge from ``source``, resolved or not, in source order."""
        return self._out.get(source, ())

    def incoming(self, target: SourceRef) -> tuple[Edge, ...]:
        return self._in.get(target, ())

    def resolved_targets(self, source: SourceRef) -> tuple[SourceRef, ...]:
        """Targets of ``source``. For a required relationship an unresolved, non-allowlisted
        edge raises instead of being silently left out."""
        es = self.outgoing(source)
        bad = [e for e in es if not e.resolved and not self._allowlisted(e)]
        if bad and self.rel.required:
            raise RelationshipIntegrityFailure(
                f"{self.rel.name}: {source.key()} has {len(bad)} unresolved required edge(s) "
                f"({sorted({e.resolution.value for e in bad})})", relationship=self.rel.name, source=source.key())
        return tuple(e.target for e in es if e.resolved and e.target is not None)

    def unresolved(self) -> tuple[Edge, ...]:
        return tuple(e for e in self.edges if not e.resolved)

    def sources(self) -> tuple[SourceRef, ...]:
        return tuple(sorted(self._out, key=lambda r: r.key()))

    def integrity(self) -> IntegrityReport:
        counts: dict[str, int] = defaultdict(int)
        allow = dangling = 0
        for e in self.edges:
            counts[e.resolution.value] += 1
            if not e.resolved:
                if self._allowlisted(e):
                    allow += 1
                else:
                    dangling += 1
        return IntegrityReport(self.rel.name, self.rel.required, len(self.edges),
                               MappingProxyType(dict(sorted(counts.items()))), allow, dangling)

    def require_integrity(self) -> IntegrityReport:
        rep = self.integrity()
        if not rep.ok:
            raise RelationshipIntegrityFailure(
                f"{self.rel.name}: {rep.dangling} dangling required edge(s) {dict(rep.by_resolution)}",
                relationship=self.rel.name, dangling=rep.dangling)
        return rep

    def resolve_targets(self, exists: Callable[[SourceRef], bool]) -> "RelationshipSet":
        """Cross-family check: RESOLVED edges whose target does not exist become UNRESOLVED_REFERENCE."""
        edges = []
        for e in self.edges:
            t = e.target
            if e.resolved and t is not None and not exists(t):
                e = Edge(e.rel, e.source, None, Resolution.UNRESOLVED_REFERENCE, raw_target=t.key(),
                         ordinal=e.ordinal, attributes=e.attributes, provenance=e.provenance)
            edges.append(e)
        return RelationshipSet(self.rel, edges, source_trust=self.source_trust, allowlist=self.allowlist)

    def find_cycles(self) -> tuple[tuple[SourceRef, ...], ...]:
        """Cycles over resolved edges (reported, never repaired)."""
        WHITE, GREY, BLACK = 0, 1, 2
        color: dict[SourceRef, int] = defaultdict(int)
        stack: list[SourceRef] = []
        cycles: list[tuple[SourceRef, ...]] = []

        def visit(n: SourceRef):
            color[n] = GREY
            stack.append(n)
            for e in self.outgoing(n):
                t = e.target
                if not e.resolved or t is None:
                    continue
                if color[t] == GREY:
                    cycles.append(tuple(stack[stack.index(t):]))
                elif color[t] == WHITE:
                    visit(t)
            stack.pop()
            color[n] = BLACK

        for s in self.sources():
            if color[s] == WHITE:
                visit(s)
        return tuple(cycles)

    def _allowlisted(self, e: Edge) -> bool:
        return (e.source.key(), str(e.raw_target)) in self.allowlist


def _order(e: Edge):
    return (e.ordinal if e.ordinal is not None else -1, e.target.key() if e.target else "", str(e.raw_target))


def _check_cardinality(rel, out, inc) -> None:
    c = rel.cardinality
    if c in (Cardinality.ONE_TO_ONE, Cardinality.MANY_TO_ONE):
        for src, es in out.items():
            if len(es) > 1:
                raise InvalidIdentity(f"{rel.name} ({c.value}): {src.key()} has {len(es)} edges")
    if c in (Cardinality.ONE_TO_ONE, Cardinality.ONE_TO_MANY):
        for tgt, es in inc.items():
            if len(es) > 1:
                raise InvalidIdentity(f"{rel.name} ({c.value}): {tgt.key()} has {len(es)} incoming edges")


# --- schema-level adapters ----------------------------------------------------------------

def tree_relationship_types(node_type: type) -> dict[str, RelationshipType]:
    return {
        "tree_contains_node": RelationshipType(
            "tree_contains_node", SkillTreeId, node_type, Cardinality.ONE_TO_MANY, required=True, ordered=True,
            description="tree -> its nodes, in source order"),
        "node_requires_node": RelationshipType(
            "node_requires_node", node_type, node_type, Cardinality.MANY_TO_MANY, required=True, ordered=True,
            description="SkillTreeNode.requirements: 0..n prerequisite edges, each with points_required"),
        "tree_ability": RelationshipType(
            "tree_ability", SkillTreeId, AbilityId, Cardinality.MANY_TO_ONE, required=False,
            description="SkillTree.ability PPtr; resolves to an ability id once the Ability view exists (R2-P04)"),
    }


def _tree_sets(view) -> dict[str, RelationshipSet]:
    from .schemas import node_identity
    kind = view.document["_meta"]["kind"]
    probe = node_identity(kind, SkillTreeId("x"), 0)
    types = tree_relationship_types(type(probe))
    trust = view.declaration.trust
    contains, requires, ability = [], [], []
    for ti, t in enumerate(view.document["trees"]):
        tid = SkillTreeId(t["tree_id"])
        for ni, n in enumerate(t["nodes"]):
            nid = node_identity(kind, tid, n["node_id"])
            contains.append(Edge(types["tree_contains_node"], tid, nid, Resolution.RESOLVED, ordinal=ni,
                                 provenance=MappingProxyType({"family": view.family_id,
                                                              "path": f"trees[{ti}].nodes[{ni}]"})))
            for ri, q in enumerate(n["requirements"]):
                if q.get("resolution") not in Resolution.__members__:
                    raise SchemaReviewRequired(f"{view.family_id}: unknown requirement resolution "
                                               f"{q.get('resolution')!r} at trees[{ti}].nodes[{ni}]")
                res = Resolution(q["resolution"])
                target = node_identity(kind, tid, q["node_id"]) if res is Resolution.RESOLVED else None
                requires.append(Edge(
                    types["node_requires_node"], nid, target, res, raw_target=q.get("node_path_id"), ordinal=ri,
                    attributes=MappingProxyType({"points_required": q.get("points_required")}),
                    provenance=MappingProxyType({"family": view.family_id,
                                                 "path": f"trees[{ti}].nodes[{ni}].requirements[{ri}]"})))
        ref = t.get("ability_ref")
        if not isinstance(ref, Mapping):
            raise SchemaReviewRequired(f"{view.family_id}: trees[{ti}] has no ability_ref")
        status = ref.get("status")
        # PRESENT carries a path id that resolves to an ability id only through the Ability view (R2-P04).
        ab_res = {"NOT_IN_RAW_DUMP": Resolution.NOT_CARRIED, "NULL_REFERENCE": Resolution.NULL_REFERENCE,
                  "PRESENT": Resolution.UNRESOLVED_REFERENCE}.get(status) if isinstance(status, str) else None
        if ab_res is None:
            raise SchemaReviewRequired(f"{view.family_id}: unknown ability_ref status {status!r} at trees[{ti}]")
        ability.append(Edge(types["tree_ability"], tid, None, ab_res, raw_target=ref.get("path_id"),
                            provenance=MappingProxyType({"family": view.family_id, "path": f"trees[{ti}]",
                                                         "ability_ref_status": status})))
    return {
        "tree_contains_node": RelationshipSet(types["tree_contains_node"], contains, source_trust=trust),
        "node_requires_node": RelationshipSet(types["node_requires_node"], requires, source_trust=trust),
        "tree_ability": RelationshipSet(types["tree_ability"], ability, source_trust=trust),
    }


AFFIX_HAS_PROPERTY = RelationshipType(
    "affix_has_property", AffixId, AffixPropertyId, Cardinality.ONE_TO_MANY, required=True, ordered=True,
    description="affix -> its properties (index 0 top-level, then extra rolls)")
AFFIX_PROPERTY_STAT = RelationshipType(
    "affix_property_stat", AffixPropertyId, PropertyId, Cardinality.MANY_TO_ONE, required=True,
    description="affix property -> SP stat property")


def _affix_sets(view) -> dict[str, RelationshipSet]:
    trust = view.declaration.trust
    has, stat = [], []
    for ai, a in enumerate(view.document["affixes"]):
        aid = AffixId(a["affix_id"])
        for pi, p in enumerate(a["properties"]):
            pid = AffixPropertyId(aid, p["index"])
            prov = MappingProxyType({"family": view.family_id, "path": f"affixes[{ai}].properties[{pi}]"})
            has.append(Edge(AFFIX_HAS_PROPERTY, aid, pid, Resolution.RESOLVED, ordinal=pi, provenance=prov))
            prop = p.get("property")
            if not isinstance(prop, Mapping):
                raise SchemaReviewRequired(f"{view.family_id}: affixes[{ai}].properties[{pi}] has no property")
            raw = prop.get("raw")
            if prop.get("decode") == "GAME_ENUM" and isinstance(raw, int) and not isinstance(raw, bool):
                stat.append(Edge(AFFIX_PROPERTY_STAT, pid, PropertyId(PropertyNamespace.SP, raw),
                                 Resolution.RESOLVED, raw_target=raw, provenance=prov))
            else:
                stat.append(Edge(AFFIX_PROPERTY_STAT, pid, None, Resolution.UNRESOLVED_REFERENCE, raw_target=raw,
                                 provenance=MappingProxyType({**prov, "decode": prop.get("decode")})))
    return {
        "affix_has_property": RelationshipSet(AFFIX_HAS_PROPERTY, has, source_trust=trust),
        "affix_property_stat": RelationshipSet(AFFIX_PROPERTY_STAT, stat, source_trust=trust),
    }


_ADAPTERS = {"tree": _tree_sets, "affixes": _affix_sets}


def relationships_for_family(view) -> Mapping[str, RelationshipSet]:
    adapter = _ADAPTERS.get(view.spec.family_kind)
    return MappingProxyType(adapter(view) if adapter else {})
