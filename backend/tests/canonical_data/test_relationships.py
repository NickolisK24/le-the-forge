"""P09 relationship and graph primitives."""
from __future__ import annotations

import json

import pytest

from app.canonical_data import errors as E
from app.canonical_data.ids import (
    AbilityId, AffixId, AffixPropertyId, PropertyId, PropertyNamespace, SkillTreeId, TreeNodeId, UniqueId,
)
from app.canonical_data.relationships import (
    AFFIX_PROPERTY_STAT, Cardinality, Edge, RelationshipSet, RelationshipType, Resolution,
)
from app.canonical_data.store import CanonicalDataStore
from app.canonical_data.trust import ConsumptionMode, TrustState

ADVISORY = ConsumptionMode.ADVISORY_DISPLAY
TRUSTED = ConsumptionMode.TRUSTED_CALCULATION
N = lambda t, n: TreeNodeId(SkillTreeId(t), n)  # noqa: E731
REQ = RelationshipType("node_requires_node", TreeNodeId, TreeNodeId, Cardinality.MANY_TO_MANY, required=True,
                       ordered=True)
OPT = RelationshipType("optional_link", TreeNodeId, TreeNodeId, Cardinality.MANY_TO_MANY, required=False)


def _e(src, tgt, res=Resolution.RESOLVED, ordinal=0, rel=REQ, raw=None):
    return Edge(rel, src, tgt, res, raw_target=raw, ordinal=ordinal)


# --- graph shape ---------------------------------------------------------------------------------------

def test_node_with_multiple_prerequisites_keeps_every_edge():
    rs = RelationshipSet(REQ, [_e(N("t", 7), N("t", 3), ordinal=0), _e(N("t", 7), N("t", 5), ordinal=1),
                               _e(N("t", 3), N("t", 0), ordinal=0)], source_trust=TrustState.CERTIFIED)
    assert rs.resolved_targets(N("t", 7)) == (N("t", 3), N("t", 5))
    assert [e.ordinal for e in rs.outgoing(N("t", 7))] == [0, 1]
    assert rs.incoming(N("t", 3))[0].source == N("t", 7)
    assert rs.resolved_targets(N("t", 0)) == ()           # zero prerequisites is representable
    assert not hasattr(rs, "parent_id") and not hasattr(Edge, "parent_id")


def test_real_fixture_has_multi_prerequisite_nodes(bundle):
    s = CanonicalDataStore.load(bundle())
    req = s.relationships("skill_trees", mode=ADVISORY)["node_requires_node"]
    multi = [src for src in req.sources() if len(req.outgoing(src)) > 1]
    assert multi, "fixture must exercise nodes with several prerequisites"
    raw = json.loads((s.bundle_dir / "families/skill_trees.json").read_text())
    by_node = {(t["tree_id"], n["node_id"]): len(n["requirements"]) for t in raw["trees"] for n in t["nodes"]}
    for src in multi:
        assert len(req.outgoing(src)) == by_node[(src.tree.value, src.node_id)]   # nothing collapsed


# --- unresolved edges are explicit ---------------------------------------------------------------------

def test_unresolved_required_edge_raises_instead_of_vanishing():
    rs = RelationshipSet(REQ, [_e(N("t", 1), N("t", 2), ordinal=0),
                               _e(N("t", 1), None, Resolution.NULL_REFERENCE, ordinal=1, raw=0)],
                         source_trust=TrustState.CERTIFIED)
    with pytest.raises(E.RelationshipIntegrityFailure):
        rs.resolved_targets(N("t", 1))
    assert rs.unresolved()[0].resolution is Resolution.NULL_REFERENCE
    with pytest.raises(E.RelationshipIntegrityFailure):
        rs.require_integrity()


def test_optional_unresolved_edges_stay_explicit():
    rs = RelationshipSet(OPT, [_e(N("t", 1), None, Resolution.UNRESOLVED_REFERENCE, rel=OPT, raw=99)],
                         source_trust=TrustState.CERTIFIED)
    assert rs.resolved_targets(N("t", 1)) == ()            # optional: no target, no error
    rep = rs.integrity()
    assert rep.ok and rep.dangling == 1 and rep.by_resolution["UNRESOLVED_REFERENCE"] == 1


def test_allowlist_needs_a_reason():
    edges = [_e(N("t", 1), None, Resolution.IMPLAUSIBLE_REFERENCE, raw=1684808296038400)]
    rs = RelationshipSet(REQ, edges, source_trust=TrustState.CERTIFIED,
                         allowlist={(N("t", 1).key(), "1684808296038400"): "decoder fault, EXT-12"})
    assert rs.integrity().ok and rs.integrity().allowlisted == 1
    with pytest.raises(E.InvalidIdentity):
        RelationshipSet(REQ, edges, source_trust=TrustState.CERTIFIED,
                        allowlist={(N("t", 1).key(), "1684808296038400"): " "})


@pytest.mark.parametrize("make", [
    lambda: Edge(REQ, N("t", 1), None, Resolution.RESOLVED, ordinal=0),                 # resolved needs target
    lambda: Edge(REQ, N("t", 1), N("t", 0), Resolution.NULL_REFERENCE, ordinal=0),      # never substitute
    lambda: Edge(REQ, N("t", 1), UniqueId(1), Resolution.RESOLVED, ordinal=0),          # wrong target type
    lambda: Edge(REQ, UniqueId(1), N("t", 1), Resolution.RESOLVED, ordinal=0),          # wrong source type
    lambda: Edge(REQ, N("t", 1), N("t", 2), Resolution.RESOLVED),                       # ordered needs ordinal
    lambda: Edge(REQ, N("t", 1), N("t", 2), "RESOLVED", ordinal=0),                     # typed resolution
])
def test_edge_invariants(make):
    with pytest.raises(E.InvalidIdentity):
        make()


def test_quarantined_edge_may_name_its_target():
    e = Edge(OPT, N("t", 1), N("t", 2), Resolution.QUARANTINED)
    assert not e.resolved and e.target == N("t", 2)


# --- cardinality and order -------------------------------------------------------------------------------

def test_cardinality_enforced():
    one = RelationshipType("one", TreeNodeId, TreeNodeId, Cardinality.ONE_TO_ONE, required=True)
    with pytest.raises(E.InvalidIdentity):
        RelationshipSet(one, [_e(N("t", 1), N("t", 2), rel=one), _e(N("t", 1), N("t", 3), rel=one)],
                        source_trust=TrustState.CERTIFIED)
    with pytest.raises(E.InvalidIdentity):
        RelationshipSet(one, [_e(N("t", 1), N("t", 3), rel=one), _e(N("t", 2), N("t", 3), rel=one)],
                        source_trust=TrustState.CERTIFIED)
    m2o = RelationshipType("m2o", TreeNodeId, TreeNodeId, Cardinality.MANY_TO_ONE, required=True)
    with pytest.raises(E.InvalidIdentity):
        RelationshipSet(m2o, [_e(N("t", 1), N("t", 2), rel=m2o), _e(N("t", 1), N("t", 3), rel=m2o)],
                        source_trust=TrustState.CERTIFIED)
    o2m = RelationshipType("o2m", TreeNodeId, TreeNodeId, Cardinality.ONE_TO_MANY, required=True)
    RelationshipSet(o2m, [_e(N("t", 1), N("t", 2), rel=o2m), _e(N("t", 1), N("t", 3), rel=o2m)],
                    source_trust=TrustState.CERTIFIED)


def test_ordered_relationship_rejects_duplicate_ordinals():
    with pytest.raises(E.InvalidIdentity):
        RelationshipSet(REQ, [_e(N("t", 1), N("t", 2), ordinal=0), _e(N("t", 1), N("t", 3), ordinal=0)],
                        source_trust=TrustState.CERTIFIED)


def test_edges_of_another_relationship_rejected():
    with pytest.raises(E.InvalidIdentity):
        RelationshipSet(REQ, [_e(N("t", 1), N("t", 2), rel=OPT)], source_trust=TrustState.CERTIFIED)


def test_relationship_set_is_read_only():
    rs = RelationshipSet(REQ, [], source_trust=TrustState.CERTIFIED)
    with pytest.raises(AttributeError):
        rs.edges = ()


def test_cross_family_resolution_marks_missing_targets():
    rs = RelationshipSet(AFFIX_PROPERTY_STAT, [
        Edge(AFFIX_PROPERTY_STAT, AffixPropertyId(AffixId(1), 0), PropertyId(PropertyNamespace.SP, 59),
             Resolution.RESOLVED),
        Edge(AFFIX_PROPERTY_STAT, AffixPropertyId(AffixId(2), 0), PropertyId(PropertyNamespace.SP, 9999),
             Resolution.RESOLVED)], source_trust=TrustState.CERTIFIED)
    checked = rs.resolve_targets(lambda t: t == PropertyId(PropertyNamespace.SP, 59))
    assert checked.integrity().dangling == 1
    bad = checked.unresolved()[0]
    assert bad.target is None and bad.raw_target == "prop:SP:9999"


def test_cycles_reported_not_repaired():
    rs = RelationshipSet(REQ, [_e(N("t", 1), N("t", 2)), _e(N("t", 2), N("t", 1))],
                         source_trust=TrustState.CERTIFIED)
    assert rs.find_cycles()
    assert len(rs.edges) == 2


# --- adapters on real canonical schemas -----------------------------------------------------------------

def test_tree_adapter_carries_r1_resolutions(bundle):
    s = CanonicalDataStore.load(bundle())
    req = s.relationships("skill_trees", mode=ADVISORY)["node_requires_node"]
    rep = req.integrity()
    assert rep.by_resolution.get("RESOLVED", 0) > 0
    for e in req.edges:
        assert (e.target is not None) == e.resolved
        assert "points_required" in e.attributes and e.provenance["family"] == "skill_trees"
    # every RESOLVED target exists in the same family
    view = s.contract_view("skill_trees")
    assert req.resolve_targets(lambda t: t in view).integrity().dangling == rep.dangling


def test_tree_ability_link_is_not_carried_for_146(bundle):
    s = CanonicalDataStore.load(bundle())
    ab = s.relationships("skill_trees", mode=ADVISORY)["tree_ability"]
    assert {e.resolution for e in ab.edges} == {Resolution.NOT_CARRIED}
    assert all(e.target is None for e in ab.edges)       # never joined by skill name
    assert ab.rel.target_type is AbilityId


def test_affix_adapter_links_properties_by_id(bundle):
    s = CanonicalDataStore.load(bundle())
    rels = s.relationships("affixes", mode=ADVISORY)
    has = rels["affix_has_property"]
    multi = [a for a in has.sources() if len(has.outgoing(a)) > 1]
    assert multi                                               # multi-property affixes keep every property
    stat = rels["affix_property_stat"]
    assert all(isinstance(e.target, PropertyId) for e in stat.edges if e.resolved)


def test_quarantined_relationships_refused_for_trusted_use(bundle):
    s = CanonicalDataStore.load(bundle())
    with pytest.raises(E.UntrustedFamily):
        s.relationships("skill_trees", mode=TRUSTED)


def test_unknown_resolution_vocabulary_requires_review(bundle):
    from app.canonical_data.relationships import relationships_for_family
    from .test_store import _patch_family
    b = bundle()
    _patch_family(b, "skill_trees",
                  lambda d: next(n for t in d["trees"] for n in t["nodes"] if n["requirements"])
                  ["requirements"][0].update(resolution="PROBABLY_FINE"))
    view = CanonicalDataStore.load(b).contract_view("skill_trees")
    with pytest.raises(E.SchemaReviewRequired):
        relationships_for_family(view)


@pytest.mark.parametrize("family,damage", [
    ("skill_trees", lambda d: d["trees"][0].pop("ability_ref")),
    ("affixes", lambda d: next(a for a in d["affixes"] if a["properties"])["properties"][0].pop("property")),
])
def test_missing_relationship_source_requires_review(bundle, family, damage):
    """A missing reference container is a schema problem, not an empty or unresolved edge."""
    from app.canonical_data.relationships import relationships_for_family
    from .test_store import _patch_family
    b = bundle()
    _patch_family(b, family, damage)
    view = CanonicalDataStore.load(b).contract_view(family)
    with pytest.raises(E.SchemaReviewRequired):
        relationships_for_family(view)
