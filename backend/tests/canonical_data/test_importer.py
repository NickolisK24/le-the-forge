"""P01 canonical bundle importer: success path and fail-closed negatives."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.canonical_data import errors as E
from app.canonical_data.hashing import content_sha256_file, sha256_file
from app.canonical_data.importer import build_manifest, import_bundle
from app.canonical_data.manifest import MANIFEST_FILE, CanonicalDataManifest

from .conftest import SLICE, SNAPSHOT_ID, run_manifest_path


def _jw(p: Path, doc):
    p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def _jr(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def test_hashing_matches_r1_implementation():
    """content_sha256 must equal what R1's own r1_snapshot computes (pinned at fixture build time)."""
    prov = _jr(SLICE / "FIXTURE_PROVENANCE.json")
    for rel, expected in prov["r1_content_sha256"].items():
        assert content_sha256_file(SLICE / rel) == expected, rel


def test_import_writes_byte_identical_bundle(r1_output, tmp_path):
    root = r1_output()
    m = import_bundle(root, run_manifest_path(root), tmp_path / "out")
    b = tmp_path / "out" / m["data_version"]
    for f in m["families"]:
        assert (b / "families" / f["path"]).read_bytes() == (root / "exports_canonical" / f["path"]).read_bytes()
        assert sha256_file(b / "families" / f["path"]) == f["sha256"]
    parsed = CanonicalDataManifest.parse(_jr(b / MANIFEST_FILE))
    assert parsed.data_version == m["data_version"] and parsed.snapshot_id == SNAPSHOT_ID
    assert {f.family_id for f in parsed.families} >= {"affixes", "passive_trees", "skill_trees", "weaver_tree",
                                                       "property_definitions"}


def test_import_is_idempotent_and_bundles_immutable(r1_output, tmp_path):
    root = r1_output()
    m1 = import_bundle(root, run_manifest_path(root), tmp_path / "out")
    m2 = import_bundle(root, run_manifest_path(root), tmp_path / "out")
    assert m1 == m2
    mf = tmp_path / "out" / m1["data_version"] / MANIFEST_FILE
    mf.write_text(mf.read_text().replace('"families"', '"families" '), encoding="utf-8")
    with pytest.raises(E.CanonicalDataError):
        import_bundle(root, run_manifest_path(root), tmp_path / "out")


def test_dry_run_writes_nothing(r1_output, tmp_path):
    root = r1_output()
    import_bundle(root, run_manifest_path(root), tmp_path / "out", dry_run=True)
    assert not (tmp_path / "out").exists()


def test_failed_import_leaves_no_partial_bundle(r1_output, tmp_path, monkeypatch):
    root = r1_output()
    import shutil as _sh

    def boom(src, dst):
        raise OSError("disk full")
    monkeypatch.setattr(_sh, "copyfile", boom)
    with pytest.raises(OSError):
        import_bundle(root, run_manifest_path(root), tmp_path / "out")
    assert [p for p in (tmp_path / "out").iterdir()] == []


def test_real_146_run_manifest_is_rejected():
    """The committed 1.4.6 record is retroactive: no raw snapshot, so it can never be a bundle (B7)."""
    with pytest.raises(E.ProvenanceMissing):
        build_manifest(SLICE, SLICE / "snapshots/runs/1.4.6_22986002.retroactive.json")


def test_quarantined_trust_is_carried_unchanged(r1_output):
    root = r1_output()
    m, _ = build_manifest(root, run_manifest_path(root))
    trust = {f["family"]: f for f in _jr(root / "exports_canonical/TRUST_MANIFEST.json")["families"]}
    for f in m["families"]:
        t = trust[f"exports_canonical/{f['path']}"]
        assert f["trust"] == t["consumer_state"] and f["trust_reasons"] == t["reasons"]


# --- negatives ------------------------------------------------------------------------------

def _mutate_file(rel, fn):
    def m(root):
        p = root / rel
        d = _jr(p)
        fn(d)
        _jw(p, d)
    return m


NEGATIVES = {
    "missing_run_manifest": (dict(), lambda root: run_manifest_path(root).unlink(), E.ManifestMissing),
    "run_schema": (dict(run_mutate=lambda r: r.update(run_schema="other/1")), None, E.ManifestInvalid),
    "no_raw_snapshot": (dict(run_mutate=lambda r: r.update(raw_snapshot=None)), None, E.ProvenanceMissing),
    "snapshot_file_missing": (dict(), lambda root: (root / f"snapshots/raw/{SNAPSHOT_ID}.json").unlink(),
                              E.ManifestMissing),
    "snapshot_id_mismatch": (dict(snapshot_mutate=lambda s: s.update(snapshot_id="OTHER")), None, E.MixedSnapshot),
    "snapshot_hash_mismatch": (dict(run_mutate=lambda r: r["raw_snapshot"].update(content_hash="f" * 64)), None,
                               E.MixedSnapshot),
    "identity_partial": (dict(snapshot_mutate=lambda s: s["source_identity"].update(identity_status="PARTIAL")),
                         None, E.ProvenanceMissing),
    "identity_missing_build": (dict(snapshot_mutate=lambda s: s["source_identity"].update(build_id="")), None,
                               E.ProvenanceMissing),
    "run_identity_other_build": (dict(run_mutate=lambda r: r.update(source_identity={"game_assembly_sha256":
                                                                                     "e" * 64})),
                                 None, E.MixedPatch),
    "extractor_dirty": (dict(run_mutate=lambda r: r["extractor"].update(dirty=True)), None, E.ProvenanceMissing),
    "extractor_no_commit": (dict(run_mutate=lambda r: r["extractor"].update(commit=None)), None,
                            E.ProvenanceMissing),
    "no_canonical_inventory": (dict(run_mutate=lambda r: r.update(canonical_exports=[])), None,
                               E.ProvenanceMissing),
    "canonical_hash_tampered": (dict(run_mutate=lambda r: r.update(canonical_content_hash="0" * 64)), None,
                                E.HashMismatch),
    "family_bytes_changed": (dict(), lambda root: (root / "exports_canonical/weaver_tree.json").write_text(
        (root / "exports_canonical/weaver_tree.json").read_text() + " "), E.HashMismatch),
    "family_missing_on_disk": (dict(), lambda root: (root / "exports_canonical/weaver_tree.json").unlink(),
                               E.ManifestMissing),
    "trust_patch_other_build": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                                         lambda d: d["patch"].update(build="99999999"))),
                                None, E.MixedPatch),
    "trust_family_missing": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                                      lambda d: d.update(families=d["families"][1:]))),
                             None, E.FamilyDeclarationInvalid),
    "trust_state_invalid": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                                     lambda d: d["families"][0].update(consumer_state="TRUSTED"))),
                            None, E.ManifestInvalid),
    "coverage_state_invalid": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                                        lambda d: d["families"][0].update(coverage_status="OK"))),
                               None, E.ManifestInvalid),
    "trust_schema": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                              lambda d: d.update(trust_schema="r1_trust_manifest/9"))),
                     None, E.ManifestInvalid),
    "certified_without_certification": (dict(mutate=_mutate_file(
        "exports_canonical/TRUST_MANIFEST.json", lambda d: d["families"][0].update(consumer_state="CERTIFIED"))),
        None, E.ManifestInvalid),
    "certification_other_build": (dict(mutate=_mutate_file(
        "docs/generated/r1_certification_report.json",
        lambda d: d["source_identity"].update(game_assembly_sha256="e" * 64))), None, E.MixedPatch),
    "trust_families_missing": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                                        lambda d: d.pop("families"))), None, E.ManifestInvalid),
    "trust_reasons_missing": (dict(mutate=_mutate_file("exports_canonical/TRUST_MANIFEST.json",
                                                       lambda d: d["families"][0].pop("reasons"))),
                              None, E.ManifestInvalid),
    "certified_exports_missing": (dict(mutate=_mutate_file("docs/generated/r1_certification_report.json",
                                                           lambda d: d.pop("certified_exports", None))),
                                  None, E.ManifestInvalid),
    "certification_missing": (dict(mutate=lambda root: (root / "docs/generated/r1_certification_report.json")
                                   .unlink()), None, E.ManifestMissing),
    "unsupported_schema": (dict(mutate=_mutate_file("exports_canonical/weaver_tree.json",
                                                    lambda d: d["_meta"].update(schema="r1_canonical_tree/2"))),
                           None, E.UnsupportedCanonicalSchema),
    "family_other_build": (dict(mutate=_mutate_file("exports_canonical/affixes.json",
                                                    lambda d: d["_meta"]["source"].update(
                                                        game_assembly_sha256="e" * 64))), None, E.MixedPatch),
    "required_family_missing": (dict(mutate=lambda root: (root / "exports_canonical/weaver_tree.json").unlink()
                                     or _drop_trust(root, "exports_canonical/weaver_tree.json")),
                                None, E.FamilyMissing),
}


def _drop_trust(root, fam):
    p = root / "exports_canonical/TRUST_MANIFEST.json"
    d = _jr(p)
    d["families"] = [f for f in d["families"] if f["family"] != fam]
    _jw(p, d)


@pytest.mark.parametrize("name", sorted(NEGATIVES))
def test_import_fails_closed(name, r1_output, tmp_path):
    kw, after, exc = NEGATIVES[name]
    root = r1_output(**kw)
    if after:
        after(root)
    with pytest.raises(exc):
        import_bundle(root, run_manifest_path(root), tmp_path / "out")
    assert not (tmp_path / "out").exists() or not any((tmp_path / "out").iterdir())


def test_export_path_outside_canonical_dir_rejected(r1_output, tmp_path):
    root = r1_output(run_mutate=lambda r: r["canonical_exports"].append(
        {"path": "exports_json/affixes.json", "sha256": "0" * 64, "content_sha256": "0" * 64}))
    with pytest.raises(E.CanonicalDataError):
        import_bundle(root, run_manifest_path(root), tmp_path / "out")


def test_importer_never_reads_legacy_forge_data():
    src = Path(build_manifest.__code__.co_filename).read_text(encoding="utf-8")
    for forbidden in ("data/items", "data/classes", "exports_json/", "game_data", "sync_game_data"):
        assert forbidden not in src.replace('"exports_json/affixes.json"', ""), forbidden


def test_malformed_family_json_rejected(r1_output, tmp_path):
    """A listed family whose bytes match the run manifest but are not JSON fails closed."""
    import hashlib
    from app.canonical_data.hashing import canonical_json, sha256_bytes
    root = r1_output()
    bad = root / "exports_canonical/extra.json"
    bad.write_text("{", encoding="utf-8")
    rm = run_manifest_path(root)
    run = _jr(rm)
    run["canonical_exports"].append({"path": "exports_canonical/extra.json",
                                     "sha256": hashlib.sha256(b"{").hexdigest(), "content_sha256": "0" * 64})
    run["canonical_content_hash"] = sha256_bytes(canonical_json(
        [{"path": e["path"], "content_sha256": e["content_sha256"]} for e in run["canonical_exports"]]).encode())
    _jw(rm, run)
    with pytest.raises(E.ManifestInvalid):
        import_bundle(root, rm, tmp_path / "out")
