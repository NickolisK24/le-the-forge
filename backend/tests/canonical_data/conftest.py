"""Fixtures for the AUDIT-R2 canonical foundation tests.

``r1_output(tmp_path, ...)`` builds an R1-shaped output tree from the real
1.4.6 canonical slice (tests/fixtures/canonical/r1_1.4.6_slice) and adds a
SYNTHETIC raw snapshot and run manifest. 1.4.6 has no raw snapshot, so the
synthetic provenance exists only so that the success paths can be tested; it
is labelled as such in every field a human might read, and the real 1.4.6
run manifest is tested separately to prove it is rejected.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Callable

import pytest

from app.canonical_data.hashing import canonical_json, content_sha256_file, sha256_bytes, sha256_file
from app.canonical_data.importer import import_bundle

SLICE = Path(__file__).resolve().parents[1] / "fixtures" / "canonical" / "r1_1.4.6_slice"
SNAPSHOT_ID = "SYNTHETIC-TEST-1.4.6_22986002"
SYNTHETIC_METADATA_SHA = "5" * 64   # synthetic: 1.4.6 global-metadata hash was never recorded
SYNTHETIC_COMMIT = "c" * 40


def _read(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _write(p: Path, doc) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def build_r1_output(root: Path, *, certify: tuple[str, ...] = (), mutate: Callable[[Path], None] | None = None,
                    run_mutate: Callable[[dict], None] | None = None,
                    snapshot_mutate: Callable[[dict], None] | None = None) -> Path:
    """Copy the slice to ``root`` and write a synthetic snapshot + run manifest that bind it."""
    shutil.copytree(SLICE, root)
    trust = _read(root / "exports_canonical/TRUST_MANIFEST.json")
    patch = trust["patch"]
    if certify:
        for f in trust["families"]:
            if f["family"] in certify:
                f.update(consumer_state="CERTIFIED", coverage_status="FIELDS_CLASSIFIED",
                         relationship_status="RESOLVED_OR_ALLOWLISTED", reasons=[], trusted_calculation_eligible=True)
        _write(root / "exports_canonical/TRUST_MANIFEST.json", trust)
        cert = _read(root / "docs/generated/r1_certification_report.json")
        cert.update(certified=True, certified_exports=sorted(certify), verdict="R1 CERTIFIED (SYNTHETIC TEST)")
        _write(root / "docs/generated/r1_certification_report.json", cert)
    if mutate:
        mutate(root)
    identity = {
        "game_version": patch["patch"], "build_id": patch["build"], "unity_version": patch["unity_version"],
        "game_assembly_sha256": patch["game_assembly_sha256"], "global_metadata_sha256": SYNTHETIC_METADATA_SHA,
        "identity_status": "AUTHORITATIVE", "patch_label": f"{patch['patch']}_{patch['build']}",
        "_synthetic": "TEST FIXTURE ONLY: 1.4.6 has no raw snapshot",
    }
    snapshot = {"snapshot_id": SNAPSHOT_ID, "content_hash": "a" * 64, "source_identity": identity}
    if snapshot_mutate:
        snapshot_mutate(snapshot)
    _write(root / f"snapshots/raw/{SNAPSHOT_ID}.json", snapshot)
    canon = []
    for p in sorted((root / "exports_canonical").rglob("*.json")):
        if p.name == "TRUST_MANIFEST.json":
            continue
        canon.append({"path": p.relative_to(root).as_posix(), "sha256": sha256_file(p),
                      "content_sha256": content_sha256_file(p), "record_counts": {}})
    run = {
        "run_schema": "r1_extraction_run/1", "run_kind": "extraction",
        "source_identity": identity,
        "raw_snapshot": {"snapshot_id": SNAPSHOT_ID, "content_hash": snapshot["content_hash"],
                         "manifest": f"snapshots/raw/{SNAPSHOT_ID}.json"},
        "extractor": {"repository": "last-epoch-data", "commit": SYNTHETIC_COMMIT, "dirty": False,
                      "dirty_paths": []},
        "canonical_exports": canon,
        "canonical_content_hash": sha256_bytes(canonical_json(
            [{"path": e["path"], "content_sha256": e["content_sha256"]} for e in canon]).encode()),
        "manifest_content_hash": "b" * 64, "exports": [],
    }
    if run_mutate:
        run_mutate(run)
    _write(root / f"snapshots/runs/{SNAPSHOT_ID}.json", run)
    return root


@pytest.fixture
def r1_output(tmp_path):
    def make(**kw) -> Path:
        return build_r1_output(tmp_path / "r1", **kw)
    return make


@pytest.fixture
def bundle(tmp_path):
    """Import a synthetic-provenance bundle; returns its directory."""
    def make(**kw) -> Path:
        root = build_r1_output(tmp_path / "r1", **kw)
        m = import_bundle(root, root / f"snapshots/runs/{SNAPSHOT_ID}.json", tmp_path / "bundles")
        return tmp_path / "bundles" / m["data_version"]
    return make


def run_manifest_path(root: Path) -> Path:
    return root / f"snapshots/runs/{SNAPSHOT_ID}.json"


CANONICAL_FAMILY_PATHS = (
    "exports_canonical/affixes.json", "exports_canonical/passive_trees.json",
    "exports_canonical/property_definitions.json", "exports_canonical/skill_trees.json",
    "exports_canonical/weaver_tree.json",
)
