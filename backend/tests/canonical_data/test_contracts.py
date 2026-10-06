"""P17 canonical contracts: count-independent invariants, runnable against any bundle.

Set ``CANONICAL_CONTRACT_BUNDLE=<bundle dir>`` to run the same contracts against
a real bundle (for example the certified 1.5 bundle) without editing tests.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from app.canonical_data.contracts import CONTRACTS, check_bundle, check_store, main
from app.canonical_data.store import CanonicalDataStore

from .test_store import _patch_family, _rewrite_manifest


def test_contract_catalogue_is_complete():
    assert set(CONTRACTS) >= {"MANIFEST_PROVENANCE", "FAMILY_UNIQUE", "FAMILY_SCHEMA", "FAMILY_HASH",
                              "FAMILY_TRUST_STATE", "FAMILY_COVERAGE_STATE", "IDENTITY_ROUNDTRIP",
                              "IDENTITY_NOT_POSITIONAL", "IDENTITY_NOT_NAME", "TRUST_POLICY", "PATCH_CONSISTENT",
                              "FIELD_SURVIVAL", "RELATIONSHIP_EXPLICIT", "RELATIONSHIP_DECLARED"}


def test_synthetic_146_bundle_satisfies_every_contract(bundle):
    assert check_bundle(bundle()) == []


def test_certified_variant_satisfies_every_contract(bundle):
    b = bundle(certify=("exports_canonical/affixes.json", "exports_canonical/weaver_tree.json"))
    assert check_bundle(b) == []


@pytest.mark.parametrize("damage,code", [
    (lambda b: (b / "families/affixes.json").write_text("{}"), "BUNDLE_LOADS"),
    (lambda b: (b / "CANONICAL_DATA_MANIFEST.json").unlink(), "BUNDLE_LOADS"),
    (lambda b: _rewrite_manifest(b, lambda d: d["snapshot"].update(snapshot_id="")), "BUNDLE_LOADS"),
])
def test_broken_bundles_fail_contracts(bundle, damage, code):
    b = bundle()
    damage(b)
    vs = check_bundle(b)
    assert [v.contract for v in vs] == [code]


def test_relationship_state_cannot_hide_dangling_edges(bundle):
    b = bundle()
    _rewrite_manifest(b, lambda d: next(f for f in d["families"] if f["family_id"] == "skill_trees")
                      .update(relationships="RESOLVED_OR_ALLOWLISTED"))
    vs = check_bundle(b)
    assert any(v.contract == "RELATIONSHIP_DECLARED" and v.family == "skill_trees" for v in vs)


def test_identity_not_positional_and_not_name_on_real_records(bundle):
    s = CanonicalDataStore.load(bundle())
    vs = [v for v in check_store(s) if v.contract in ("IDENTITY_NOT_POSITIONAL", "IDENTITY_NOT_NAME")]
    assert vs == []


def test_name_derived_identity_would_be_caught(bundle, monkeypatch):
    """Guard the guard: an adapter that keyed records by name must fail IDENTITY_NOT_NAME."""
    from app.canonical_data import schemas
    from app.canonical_data.ids import SkillTreeId
    spec = schemas.SCHEMAS["r1_canonical_tree/1"]

    def by_name(doc):
        for i, t in enumerate(doc.get("trees", [])):
            yield SkillTreeId("n" + str(abs(hash(str(t["nodes"][0]["name"]))) % 10**8)), t, f"trees[{i}]"
    bad = schemas.SchemaSpec(spec.schema, spec.family_kind, spec.known_fields, by_name, spec.records,
                             spec.build_identity)
    monkeypatch.setitem(schemas.SCHEMAS, "r1_canonical_tree/1", bad)
    vs = check_bundle(bundle())
    assert any(v.contract == "IDENTITY_NOT_NAME" for v in vs)


def test_position_derived_identity_would_be_caught(bundle, monkeypatch):
    from app.canonical_data import schemas
    from app.canonical_data.ids import AffixId
    spec = schemas.SCHEMAS["r1_canonical_affix/1"]

    def by_position(doc):
        for i, r in enumerate(doc.get("affixes", [])):
            yield AffixId(i), r, f"affixes[{i}]"
    bad = schemas.SchemaSpec(spec.schema, spec.family_kind, spec.known_fields, by_position, spec.records,
                             spec.build_identity)
    monkeypatch.setitem(schemas.SCHEMAS, "r1_canonical_affix/1", bad)
    vs = check_bundle(bundle())
    assert any(v.contract == "IDENTITY_NOT_POSITIONAL" for v in vs)


def test_field_survival_contract_holds_with_unknown_fields(bundle):
    b = bundle()
    _patch_family(b, "weaver_tree", lambda d: d["trees"][0].update(added_by_new_patch=True))
    vs = [v for v in check_bundle(b) if v.contract == "FIELD_SURVIVAL"]
    assert vs == []           # carried and surfaced as review, which is the contract


def test_cli_exit_codes(bundle, tmp_path, capsys):
    assert main([str(bundle())]) == 0
    assert main([str(tmp_path)]) == 1


@pytest.mark.skipif(not os.environ.get("CANONICAL_CONTRACT_BUNDLE"),
                    reason="set CANONICAL_CONTRACT_BUNDLE to run the contracts against a real bundle")
def test_external_bundle_satisfies_contracts():
    vs = check_bundle(Path(os.environ["CANONICAL_CONTRACT_BUNDLE"]))
    assert vs == [], json.dumps([v.__dict__ for v in vs], indent=1)
