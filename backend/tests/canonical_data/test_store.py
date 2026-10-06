"""P02 canonical data store: immutability, one snapshot, trust, no fallback."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from app.canonical_data import errors as E
from app.canonical_data.hashing import document_hash
from app.canonical_data.ids import (
    AffixId, PassiveNodeId, PropertyId, PropertyNamespace, SkillTreeId, TreeNodeId, UniqueId,
)
from app.canonical_data.manifest import MANIFEST_FILE, CanonicalDataManifest
from app.canonical_data.store import BoundRef, CanonicalDataStore, Found, Missing, StoreRegistry
from app.canonical_data.trust import ADMITTED, ADVISORY_CALCULATION_ENABLED, ConsumptionMode, TrustState

TRUSTED = ConsumptionMode.TRUSTED_CALCULATION
ADVISORY = ConsumptionMode.ADVISORY_DISPLAY
BACKEND = Path(__file__).resolve().parents[2]


def _jr(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _rewrite_manifest(bundle_dir: Path, fn) -> None:
    p = bundle_dir / MANIFEST_FILE
    d = _jr(p)
    fn(d)
    d["manifest_hash"] = document_hash(d, "manifest_hash")
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")


# --- loading and identity ----------------------------------------------------------------------

def test_store_loads_and_indexes_by_source_identity(bundle):
    s = CanonicalDataStore.load(bundle())
    v = s.contract_view("affixes")
    rec = v.require(AffixId(14))
    assert rec["affix_id"] == 14
    assert isinstance(v.lookup(AffixId(999999)), Missing)
    assert isinstance(v.lookup(AffixId(14)), Found)
    pt = s.contract_view("passive_trees")
    assert any(isinstance(r, PassiveNodeId) for r in pt.ids())
    st = s.contract_view("skill_trees")
    assert SkillTreeId("wo42") in st and any(isinstance(r, TreeNodeId) for r in st.ids())
    pd = s.contract_view("property_definitions")
    assert PropertyId(PropertyNamespace.SP, 0) in pd


def test_missing_record_is_an_explicit_error(bundle):
    v = CanonicalDataStore.load(bundle()).contract_view("affixes")
    with pytest.raises(E.CanonicalRecordMissing) as ei:
        v.require(AffixId(999999))
    assert ei.value.code == "REFERENCE_NOT_FOUND"


@pytest.mark.parametrize("bad", ["Void Penetration", 14, "affix:14", None])
def test_lookup_requires_typed_identity(bundle, bad):
    v = CanonicalDataStore.load(bundle()).contract_view("affixes")
    with pytest.raises(TypeError):
        v.lookup(bad)


def test_wrong_type_identity_is_a_miss_not_a_coercion(bundle):
    v = CanonicalDataStore.load(bundle()).contract_view("affixes")
    assert isinstance(v.lookup(UniqueId(14)), Missing)


# --- immutability ------------------------------------------------------------------------------------

def test_store_and_records_are_immutable(bundle):
    s = CanonicalDataStore.load(bundle())
    with pytest.raises(E.StoreImmutable):
        s.manifest = None
    v = s.contract_view("affixes")
    with pytest.raises(E.StoreImmutable):
        v.document = {}
    rec = v.require(AffixId(14))
    with pytest.raises(TypeError):
        rec["affix_id"] = 1
    with pytest.raises(TypeError):
        v.document["affixes"][0]["names"]["name"] = "x"
    with pytest.raises(AttributeError):
        v.document["affixes"].append({})


# --- one snapshot ----------------------------------------------------------------------------------------

def test_bound_reference_from_another_dataset_is_rejected(bundle, tmp_path):
    s = CanonicalDataStore.load(bundle())
    ref = s.bind(AffixId(14))
    assert s.contract_view("affixes").require(ref)["affix_id"] == 14
    foreign = BoundRef("1.5.1_99999999+OTHER+000000000000", AffixId(14))
    with pytest.raises(E.MixedSnapshot):
        s.contract_view("affixes").require(foreign)


def test_bundle_directory_must_match_its_data_version(bundle, tmp_path):
    b = bundle()
    moved = b.with_name("1.4.6_22986002+OTHER+000000000000")
    b.rename(moved)
    with pytest.raises(E.MixedSnapshot):
        CanonicalDataStore.load(moved)


def test_no_merge_or_add_api():
    for name in ("merge", "add", "update", "add_family", "replace", "load_legacy", "fallback"):
        assert not hasattr(CanonicalDataStore, name)


# --- trust ---------------------------------------------------------------------------------------------------

def test_b2_lock_no_advisory_calculations():
    assert ADMITTED[TRUSTED] == frozenset({TrustState.CERTIFIED})
    assert ADVISORY_CALCULATION_ENABLED is False
    for state in (TrustState.QUARANTINED, TrustState.PRESERVED_ONLY, TrustState.UNKNOWN, TrustState.UNSUPPORTED):
        assert state not in ADMITTED[TRUSTED]
    for state in (TrustState.PRESERVED_ONLY, TrustState.UNKNOWN, TrustState.UNSUPPORTED):
        assert all(state not in ADMITTED[m] for m in ConsumptionMode)


def test_quarantined_family_never_enters_trusted_consumption(bundle):
    s = CanonicalDataStore.load(bundle())
    with pytest.raises(E.UntrustedFamily) as ei:
        s.family("affixes", mode=TRUSTED)
    assert ei.value.context["reasons"]  # R1 reasons travel with the refusal
    assert s.family("affixes", mode=ADVISORY).family_id == "affixes"
    with pytest.raises(E.UntrustedFamily):
        s.require("affixes", AffixId(14), mode=TRUSTED)


@pytest.mark.parametrize("state", ["UNKNOWN", "PRESERVED_ONLY", "UNSUPPORTED"])
def test_non_consumable_states_rejected_in_every_mode(bundle, state):
    b = bundle()
    _rewrite_manifest(b, lambda d: d["families"][0].update(trust=state))
    s = CanonicalDataStore.load(b)
    fid = s.manifest.families[0].family_id
    for mode in ConsumptionMode:
        with pytest.raises(E.UntrustedFamily):
            s.family(fid, mode=mode)


def test_certified_family_is_trusted_only_when_classified_and_resolved(bundle):
    b = bundle(certify=("exports_canonical/affixes.json",))
    s = CanonicalDataStore.load(b)
    assert s.manifest.certified is True
    assert s.family("affixes", mode=TRUSTED).family_id == "affixes"     # CERTIFIED is explicit
    with pytest.raises(E.UntrustedFamily):
        s.family("skill_trees", mode=TRUSTED)                           # still QUARANTINED


def test_certified_but_unmeasured_coverage_is_refused(bundle):
    b = bundle(certify=("exports_canonical/affixes.json",))
    _rewrite_manifest(b, lambda d: next(f for f in d["families"] if f["family_id"] == "affixes")
                      .update(coverage="FIELDS_UNMEASURED"))
    with pytest.raises(E.CoverageInsufficient):
        CanonicalDataStore.load(b).family("affixes", mode=TRUSTED)


def test_certified_but_dangling_relationships_is_refused(bundle):
    b = bundle(certify=("exports_canonical/affixes.json",))
    _rewrite_manifest(b, lambda d: next(f for f in d["families"] if f["family_id"] == "affixes")
                      .update(relationships="DANGLING"))
    with pytest.raises(E.RelationshipIntegrityFailure):
        CanonicalDataStore.load(b).family("affixes", mode=TRUSTED)


def test_certified_family_in_uncertified_snapshot_is_invalid(bundle):
    b = bundle()
    _rewrite_manifest(b, lambda d: d["families"][0].update(trust="CERTIFIED"))
    with pytest.raises(E.ManifestInvalid):
        CanonicalDataStore.load(b)


# --- field survival / schema evolution --------------------------------------------------------------

def _patch_family(b: Path, family_id: str, fn) -> None:
    """Change a family payload and re-seal hashes, as a newer R1 would (schema review, not tampering)."""
    from app.canonical_data.hashing import content_sha256_file, sha256_file
    m = _jr(b / MANIFEST_FILE)
    decl = next(f for f in m["families"] if f["family_id"] == family_id)
    p = b / "families" / decl["path"]
    d = _jr(p)
    fn(d)
    p.write_text(json.dumps(d, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    _rewrite_manifest(b, lambda dd: next(f for f in dd["families"] if f["family_id"] == family_id).update(
        sha256=sha256_file(p), content_sha256=content_sha256_file(p)))


def test_unknown_fields_are_kept_and_force_review(bundle):
    b = bundle(certify=("exports_canonical/affixes.json",))
    _patch_family(b, "affixes", lambda d: d["affixes"][0].update(new_patch_field={"x": 1}))
    s = CanonicalDataStore.load(b)
    v = s.contract_view("affixes")
    assert v.review_required and "new_patch_field" in v.unknown_fields["affix"]
    first = v.document["affixes"][0]
    assert first["new_patch_field"]["x"] == 1                  # carried, never dropped
    with pytest.raises(E.CoverageInsufficient):
        s.family("affixes", mode=TRUSTED)                      # explicit review state blocks trust


def test_unsupported_schema_version_rejected(bundle):
    b = bundle()
    _rewrite_manifest(b, lambda d: d["families"][0].update(schema="r1_canonical_affix/2"))
    with pytest.raises(E.UnsupportedCanonicalSchema):
        CanonicalDataStore.load(b)


def test_duplicate_canonical_ids_fail(bundle):
    b = bundle()
    _patch_family(b, "affixes", lambda d: d["affixes"].append(dict(d["affixes"][0])))
    with pytest.raises(E.DuplicateCanonicalId):
        CanonicalDataStore.load(b)


# --- tampering, foreign sources, no fallback -------------------------------------------------------

def test_tampered_family_rejected(bundle):
    b = bundle()
    p = b / "families" / "weaver_tree.json"
    p.write_text(p.read_text() + "\n", encoding="utf-8")
    with pytest.raises(E.HashMismatch):
        CanonicalDataStore.load(b)


def test_tampered_manifest_rejected(bundle):
    b = bundle()
    p = b / MANIFEST_FILE
    d = _jr(p)
    d["families"][0]["trust"] = "CERTIFIED"   # without re-sealing the manifest hash
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(E.ManifestInvalid):
        CanonicalDataStore.load(b)


def test_undeclared_file_in_bundle_rejected(bundle):
    b = bundle()
    (b / "families" / "affixes_legacy.json").write_text("{}", encoding="utf-8")
    with pytest.raises(E.ForeignSource):
        CanonicalDataStore.load(b)


@pytest.mark.skipif(os.name == "nt", reason="symlinks")
def test_symlinked_family_rejected(bundle, tmp_path):
    b = bundle()
    p = b / "families" / "weaver_tree.json"
    real = tmp_path / "elsewhere.json"
    real.write_bytes(p.read_bytes())
    p.unlink()
    p.symlink_to(real)
    with pytest.raises(E.ForeignSource):
        CanonicalDataStore.load(b)


def test_missing_manifest_is_an_error_not_a_fallback(tmp_path):
    with pytest.raises(E.ManifestMissing):
        CanonicalDataStore.load(tmp_path)


def test_missing_required_family_rejected(bundle):
    b = bundle()
    with pytest.raises(E.FamilyMissing):
        CanonicalDataStore.load(b, required_families=frozenset({"affixes", "classes"}))


def test_package_never_reads_legacy_sources():
    pkg = BACKEND / "app" / "canonical_data"
    forbidden = ("app.game_data", "game_data_loader", "from ..game_data", "data/items", "data/classes",
                 "data/progression", "data/combat", "sync_game_data", "frontend/src", "docs/generated/v2_",
                 "GameDataPipeline", "VersionedLoader")
    hits = [(p.name, f) for p in pkg.glob("*.py") for f in forbidden if f in p.read_text(encoding="utf-8")]
    assert hits == []


def test_contract_view_only_used_inside_package_and_tests():
    users = []
    for p in (BACKEND / "app").rglob("*.py"):
        if "canonical_data" in p.parts:
            continue
        if "contract_view" in p.read_text(encoding="utf-8", errors="replace"):
            users.append(str(p))
    assert users == []


def test_app_factory_does_not_load_canonical_data():
    """Production is untouched: creating the app never imports the canonical package."""
    code = ("from app import create_app; import sys; create_app('testing'); "
            "print(any(m.startswith('app.canonical_data') for m in sys.modules))")
    env = {**os.environ, "FLASK_ENV": "testing", "SECRET_KEY": "x" * 32, "JWT_SECRET_KEY": "x" * 32}
    out = subprocess.run([sys.executable, "-c", code], cwd=BACKEND, capture_output=True, text=True, env=env,
                         timeout=300, check=False)
    assert out.returncode == 0, out.stderr[-2000:]
    assert out.stdout.strip().splitlines()[-1] == "False"


# --- concurrency / determinism -------------------------------------------------------------------------

def test_registry_loads_once_across_threads(bundle, monkeypatch):
    b = bundle()
    StoreRegistry.clear()
    calls = []
    real = CanonicalDataStore.load.__func__

    def counting(cls, *a, **k):
        calls.append(1)
        return real(cls, *a, **k)
    monkeypatch.setattr(CanonicalDataStore, "load", classmethod(counting))
    got = []
    threads = [threading.Thread(target=lambda: got.append(StoreRegistry.get(b))) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert len(calls) == 1 and len({id(s) for s in got}) == 1
    StoreRegistry.clear()


def test_initialization_is_deterministic(bundle):
    b = bundle()
    a, c = CanonicalDataStore.load(b), CanonicalDataStore.load(b)
    assert a.manifest == c.manifest
    for fid in a.family_ids:
        assert a.contract_view(fid).ids() == c.contract_view(fid).ids()


# --- manifest parsing -------------------------------------------------------------------------------------

MANIFEST_NEGATIVES = {
    "unknown_top_key": (lambda d: d.update(extra=1), E.ManifestInvalid),
    "schema": (lambda d: d.update(schema="forge_canonical_data_manifest/2"), E.UnsupportedCanonicalSchema),
    "data_version_mismatch": (lambda d: d.update(data_version="1.4.6_x+y+z"), E.ManifestInvalid),
    "missing_snapshot_id": (lambda d: d["snapshot"].update(snapshot_id=""), E.ProvenanceMissing),
    "missing_patch": (lambda d: d["source_identity"].update(game_version=""), E.ProvenanceMissing),
    "missing_build": (lambda d: d["source_identity"].update(build_id=None), E.ProvenanceMissing),
    "partial_identity": (lambda d: d["source_identity"].update(identity_status="PARTIAL"), E.ProvenanceMissing),
    "short_commit": (lambda d: d["extractor"].update(commit="abc"), E.ProvenanceMissing),
    "dirty_extractor": (lambda d: d["extractor"].update(dirty=True), E.ProvenanceMissing),
    "bad_sha": (lambda d: d["source_identity"].update(game_assembly_sha256="xyz"), E.ManifestInvalid),
    "cross_build_mode": (lambda d: d["compatibility"].update(mode="CROSS_BUILD"), E.ManifestInvalid),
    "no_families": (lambda d: d.update(families=[]), E.ManifestInvalid),
    "duplicate_family": (lambda d: d["families"].append(dict(d["families"][0])), E.FamilyDeclarationInvalid),
    "path_traversal": (lambda d: d["families"][0].update(path="../../etc/passwd.json"),
                       E.FamilyDeclarationInvalid),
    "absolute_path": (lambda d: d["families"][0].update(path="/tmp/x.json"), E.FamilyDeclarationInvalid),
    "family_unknown_key": (lambda d: d["families"][0].update(note="x"), E.ManifestInvalid),
    "family_missing_hash": (lambda d: d["families"][0].pop("content_sha256"), E.FamilyDeclarationInvalid),
    "family_bad_trust": (lambda d: d["families"][0].update(trust="TRUSTED"), E.ManifestInvalid),
    "family_bad_binding": (lambda d: d["families"][0].update(build_binding="GUESSED"), E.FamilyDeclarationInvalid),
}


@pytest.mark.parametrize("name", sorted(MANIFEST_NEGATIVES))
def test_manifest_rejections(name, bundle):
    fn, exc = MANIFEST_NEGATIVES[name]
    b = bundle()
    _rewrite_manifest(b, fn)
    with pytest.raises(exc):
        CanonicalDataManifest.parse(_jr(b / MANIFEST_FILE))


@pytest.mark.parametrize("family,damage", [
    ("affixes", lambda d: d.pop("affixes")),
    ("affixes", lambda d: d["affixes"][0].pop("properties")),
    ("skill_trees", lambda d: d.pop("trees")),
    ("skill_trees", lambda d: d["trees"][0].pop("nodes")),
    ("skill_trees", lambda d: d["trees"][0]["nodes"][0].pop("requirements")),
    ("weaver_tree", lambda d: d.update(trees={})),
    ("property_definitions", lambda d: d.pop("families")),
    ("property_definitions", lambda d: d["families"].pop("player_properties")),
])
def test_missing_record_container_is_not_an_empty_family(bundle, family, damage):
    """No silent empty family: a schema-valid payload without its record container needs review."""
    b = bundle()
    _patch_family(b, family, damage)
    with pytest.raises(E.SchemaReviewRequired):
        CanonicalDataStore.load(b)
