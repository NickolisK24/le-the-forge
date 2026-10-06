"""Canonical bundle importer: R1 output -> immutable Forge bundle (AUDIT-R2 P01).

Inputs (all inside one last-epoch-data checkout, ``r1_root``):

    snapshots/runs/<snapshot_id>.json          extraction run manifest (canonical_exports, extractor)
    snapshots/raw/<snapshot_id>.json           raw snapshot manifest (source identity)
    snapshots/runs/<snapshot_id>.reproduce.json  extract-stage reproduction (optional; recorded)
    exports_canonical/TRUST_MANIFEST.json      per-family trust, coverage, relationship state
    docs/generated/r1_certification_report.json  certification verdict
    exports_canonical/**                       the canonical families

Output: ``<out_dir>/<data_version>/`` with ``CANONICAL_DATA_MANIFEST.json`` and
``families/<path>`` byte-identical copies.

The importer only verifies and copies. It never reads raw game files, never
applies a legacy transform, never repairs, rescales or renames anything, never
infers an identity from a name, and never reads the Forge ``data/`` tree.
Every failure raises a typed error from ``errors``; nothing is written unless
every check passes.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .errors import (
    CanonicalDataError, FamilyDeclarationInvalid, FamilyMissing, HashMismatch, ManifestInvalid, ManifestMissing,
    MixedPatch, MixedSnapshot, ProvenanceMissing,
)
from .hashing import canonical_json, content_sha256_of, document_hash, sha256_bytes, sha256_file
from .manifest import (
    ACCEPTED_IDENTITY_STATUS, FAMILIES_DIR, MANIFEST_FILE, MANIFEST_SCHEMA, CanonicalDataManifest, CompatibilityMode,
)
from .schemas import REQUIRED_FAMILIES, spec_for
from .trust import CoverageState, RelationshipState, TrustState, parse_enum

CANONICAL_PREFIX = "exports_canonical/"
TRUST_MANIFEST = "exports_canonical/TRUST_MANIFEST.json"
CERTIFICATION_REPORT = "docs/generated/r1_certification_report.json"


def _load_json(path: Path, what: str) -> Any:
    if not path.is_file():
        raise ManifestMissing(f"{what} not found: {path}", path=str(path))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ManifestInvalid(f"{what} is not valid JSON: {e}", path=str(path)) from e


def family_id_for(export_path: str) -> str:
    """``exports_canonical/affixes.json`` -> ``affixes``; envelopes keep their sub-path."""
    rel = export_path[len(CANONICAL_PREFIX):-len(".json")]
    return rel if "/" not in rel else rel.replace("\\", "/")


def _identity_from_snapshot(snap: dict) -> dict:
    si = snap.get("source_identity")
    if not isinstance(si, dict):
        raise ProvenanceMissing("raw snapshot has no source_identity")
    need = {
        "game_version": si.get("game_version"), "build_id": si.get("build_id"),
        "unity_version": si.get("unity_version"), "game_assembly_sha256": si.get("game_assembly_sha256"),
        "global_metadata_sha256": si.get("global_metadata_sha256"), "identity_status": si.get("identity_status"),
        "patch_label": si.get("patch_label"),
    }
    missing = sorted(k for k, v in need.items() if v in (None, ""))
    if missing:
        raise ProvenanceMissing(f"raw snapshot source_identity lacks {missing}", missing=missing)
    if need["identity_status"] not in ACCEPTED_IDENTITY_STATUS:
        raise ProvenanceMissing(f"snapshot identity_status {need['identity_status']!r} is not authoritative")
    return need


def _same_patch(identity: dict, other: dict | None, what: str) -> None:
    if not isinstance(other, dict):
        raise ProvenanceMissing(f"{what} carries no patch identity")
    pairs = [("game_assembly_sha256", "game_assembly_sha256"), ("build", "build_id"), ("patch", "game_version")]
    for theirs, ours in pairs:
        if theirs in other and other[theirs] not in (None, "") and str(other[theirs]) != str(identity[ours]):
            raise MixedPatch(f"{what} {theirs}={other[theirs]!r} differs from the snapshot {ours}="
                             f"{identity[ours]!r}", what=what)
    if not other.get("game_assembly_sha256"):
        raise ProvenanceMissing(f"{what} carries no game_assembly_sha256")


def build_manifest(r1_root: Path, run_manifest_path: Path,
                   required_families: frozenset[str] = REQUIRED_FAMILIES) -> tuple[dict, dict[str, Path]]:
    """Verify R1 output and return (manifest dict, {bundle path: source file})."""
    r1_root = r1_root.resolve()
    run = _load_json(run_manifest_path, "run manifest")
    if run.get("run_schema") != "r1_extraction_run/1":
        raise ManifestInvalid(f"run manifest schema {run.get('run_schema')!r} is not r1_extraction_run/1")
    raw_ref = run.get("raw_snapshot")
    if not isinstance(raw_ref, dict) or not raw_ref.get("snapshot_id"):
        raise ProvenanceMissing("run manifest references no raw snapshot (retroactive or exports-only run); "
                                "a canonical bundle needs an authoritative snapshot")
    snapshot_id = raw_ref["snapshot_id"]
    snap_path = r1_root / str(raw_ref.get("manifest") or f"snapshots/raw/{snapshot_id}.json")
    snap = _load_json(snap_path, "raw snapshot manifest")
    if snap.get("snapshot_id") != snapshot_id:
        raise MixedSnapshot(f"run manifest names snapshot {snapshot_id!r}, the snapshot file is "
                            f"{snap.get('snapshot_id')!r}")
    if snap.get("content_hash") != raw_ref.get("content_hash"):
        raise MixedSnapshot("run manifest snapshot content_hash differs from the snapshot file")
    identity = _identity_from_snapshot(snap)
    run_si = run.get("source_identity") or {}
    if run_si.get("game_assembly_sha256") != identity["game_assembly_sha256"]:
        raise MixedPatch("run manifest source identity differs from the raw snapshot")

    ext = run.get("extractor") or {}
    if not ext.get("commit"):
        raise ProvenanceMissing("run manifest has no extractor commit")
    if ext.get("dirty") is not False:
        raise ProvenanceMissing("extractor working tree was dirty during the run")

    canon = run.get("canonical_exports")
    if not isinstance(canon, list) or not canon:
        raise ProvenanceMissing("run manifest has no canonical_exports inventory (R1 run manifests before "
                                "7dc1ad6 cannot bind canonical data to a snapshot)")
    expected_cch = sha256_bytes(canonical_json(
        [{"path": e["path"], "content_sha256": e.get("content_sha256") or e["sha256"]} for e in canon]).encode())
    if run.get("canonical_content_hash") != expected_cch:
        raise HashMismatch("run manifest canonical_content_hash does not match its canonical_exports inventory")

    trust = _load_json(r1_root / TRUST_MANIFEST, "trust manifest")
    if trust.get("trust_schema") != "r1_trust_manifest/1":
        raise ManifestInvalid(f"trust manifest schema {trust.get('trust_schema')!r} is not r1_trust_manifest/1")
    _same_patch(identity, trust.get("patch"), "trust manifest")
    trust_families = trust.get("families")
    if not isinstance(trust_families, list):
        raise ManifestInvalid("trust manifest has no 'families' list")
    trust_by_family = {f.get("family"): f for f in trust_families}

    cert = _load_json(r1_root / CERTIFICATION_REPORT, "certification report")
    _same_patch(identity, {"game_assembly_sha256": (cert.get("source_identity") or {}).get("game_assembly_sha256"),
                           "build": (cert.get("source_identity") or {}).get("build"),
                           "patch": (cert.get("source_identity") or {}).get("patch")}, "certification report")
    certified = cert.get("certified")
    if not isinstance(certified, bool):
        raise ManifestInvalid("certification report has no boolean 'certified'")
    certified_exports = cert.get("certified_exports")
    if not isinstance(certified_exports, list):
        raise ManifestInvalid("certification report has no 'certified_exports' list")

    repro_path = run_manifest_path.with_name(f"{snapshot_id}.reproduce.json")
    repro = json.loads(repro_path.read_text(encoding="utf-8")).get("status") if repro_path.is_file() else "NOT_RUN"

    families, sources = [], {}
    for e in sorted(canon, key=lambda x: x["path"]):
        export_path = e["path"]
        if not export_path.startswith(CANONICAL_PREFIX) or not export_path.endswith(".json"):
            raise FamilyDeclarationInvalid(f"canonical export {export_path!r} is outside exports_canonical/")
        src = (r1_root / export_path).resolve()
        if r1_root not in src.parents:
            raise FamilyDeclarationInvalid(f"canonical export {export_path!r} escapes the R1 root")
        if not src.is_file():
            raise ManifestMissing(f"canonical export listed in the run manifest is missing: {export_path}")
        raw_bytes = src.read_bytes()
        if sha256_bytes(raw_bytes) != e.get("sha256"):
            raise HashMismatch(f"{export_path}: file sha256 differs from the run manifest", family=export_path)
        try:
            doc = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ManifestInvalid(f"{export_path} is not valid JSON: {exc}") from exc
        content = content_sha256_of(doc)
        if content != e.get("content_sha256"):
            raise HashMismatch(f"{export_path}: content hash differs from the run manifest", family=export_path)
        fid = family_id_for(export_path)
        schema = (doc.get("_meta") or {}).get("schema")
        spec = spec_for(schema, fid)
        declared_build = spec.build_identity(doc) if spec.build_identity else None
        if declared_build is not None and declared_build != identity["game_assembly_sha256"]:
            raise MixedPatch(f"{export_path} declares GameAssembly {declared_build[:12]}..., the snapshot is "
                             f"{identity['game_assembly_sha256'][:12]}...", family=fid)
        t = trust_by_family.get(export_path)
        if t is None:
            raise FamilyDeclarationInvalid(f"{export_path} has no entry in the trust manifest", family=fid)
        _same_patch(identity, t.get("patch"), f"trust entry for {export_path}")
        state = parse_enum(TrustState, t.get("consumer_state"), f"trust[{export_path}].consumer_state")
        if state is TrustState.CERTIFIED and (not certified or export_path not in certified_exports):
            raise ManifestInvalid(f"{export_path} is CERTIFIED in the trust manifest but not in the certification "
                                  f"report", family=fid)
        reasons = t.get("reasons")
        if not isinstance(reasons, list):
            raise ManifestInvalid(f"trust[{export_path}].reasons is missing or not a list", family=fid)
        bundle_path = export_path[len(CANONICAL_PREFIX):]
        families.append({
            "family_id": fid, "path": bundle_path, "schema": schema,
            "sha256": e["sha256"], "content_sha256": content,
            "trust": state.value, "trust_reasons": [str(r) for r in reasons],
            "coverage": parse_enum(CoverageState, t.get("coverage_status"), f"trust[{export_path}].coverage").value,
            "relationships": parse_enum(RelationshipState, t.get("relationship_status"),
                                        f"trust[{export_path}].relationship_status").value,
            "build_binding": "SELF_DECLARED" if declared_build else "RUN_MANIFEST",
            "required": fid in required_families,
        })
        sources[bundle_path] = src

    present = {f["family_id"] for f in families}
    missing = sorted(required_families - present)
    if missing:
        raise FamilyMissing(f"required families missing from the run: {missing}", missing=missing)

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "data_version": CanonicalDataManifest.make_data_version(
            identity["game_version"], identity["build_id"], snapshot_id, run["canonical_content_hash"]),
        "source_identity": identity,
        "snapshot": {"snapshot_id": snapshot_id, "content_hash": snap.get("content_hash")},
        "extractor": {"repository": ext.get("repository") or "last-epoch-data", "commit": ext["commit"],
                      "dirty": False},
        "run_manifest": {"manifest_content_hash": run.get("manifest_content_hash"),
                         "canonical_content_hash": run["canonical_content_hash"],
                         "extract_reproduction": repro},
        "certification": {"certified": certified, "report_hash": cert.get("report_hash"),
                          "certified_exports": certified_exports},
        "trust_manifest": {"trust_schema": trust["trust_schema"], "report_hash": trust.get("report_hash")},
        "compatibility": {"mode": CompatibilityMode.SINGLE_SNAPSHOT.value},
        "families": families,
    }
    manifest["manifest_hash"] = document_hash(manifest, "manifest_hash")
    CanonicalDataManifest.parse(manifest)  # the same strict parser the store uses
    return manifest, sources


def import_bundle(r1_root: Path, run_manifest_path: Path, out_dir: Path, *, dry_run: bool = False,
                  required_families: frozenset[str] = REQUIRED_FAMILIES) -> dict:
    """Verify and (unless ``dry_run``) write ``<out_dir>/<data_version>/``. Returns the manifest."""
    manifest, sources = build_manifest(r1_root, run_manifest_path, required_families)
    if dry_run:
        return manifest
    target = out_dir / manifest["data_version"]
    payload = json.dumps(manifest, indent=1, sort_keys=True) + "\n"
    if target.exists():
        existing = target / MANIFEST_FILE
        if existing.is_file() and existing.read_text(encoding="utf-8") == payload:
            return manifest  # identical bundle already present: idempotent
        raise CanonicalDataError(f"bundle {target} exists with different content; bundles are immutable")
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".import-", dir=out_dir))
    try:
        for bundle_path, src in sources.items():
            dest = tmp / FAMILIES_DIR / bundle_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            if sha256_file(dest) != next(f["sha256"] for f in manifest["families"] if f["path"] == bundle_path):
                raise HashMismatch(f"copy of {bundle_path} does not match its source hash")
        (tmp / MANIFEST_FILE).write_text(payload, encoding="utf-8")
        os.replace(tmp, target)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return manifest


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="Import a certified R1 canonical bundle (AUDIT-R2 P01).")
    ap.add_argument("--r1-root", type=Path, required=True, help="last-epoch-data checkout")
    ap.add_argument("--run-manifest", type=Path, required=True, help="snapshots/runs/<snapshot_id>.json")
    ap.add_argument("--out", type=Path, default=Path("data/canonical"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        m = import_bundle(args.r1_root, args.run_manifest, args.out, dry_run=args.dry_run)
    except CanonicalDataError as e:
        print(json.dumps(e.to_dict(), indent=1, default=str), file=sys.stderr)
        return 2
    print(f"{'verified' if args.dry_run else 'imported'} {m['data_version']}: {len(m['families'])} families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
