"""CanonicalDataManifest: the single handoff from R1 into the Forge (AUDIT-R2 P01).

Strict by design: unknown keys, missing provenance, malformed hashes and
inconsistent trust are errors. A manifest that does not parse is never
partially used.

See docs/audits/2026-10-system-deep-audit/r2/R2_CANONICAL_CONSUMPTION_CONTRACT.md.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from collections.abc import Set
from typing import Any, ClassVar

from .errors import FamilyDeclarationInvalid, ManifestInvalid, ProvenanceMissing, UnsupportedCanonicalSchema
from .hashing import document_hash
from .trust import CoverageState, RelationshipState, TrustState, parse_enum

MANIFEST_SCHEMA = "forge_canonical_data_manifest/1"
MANIFEST_FILE = "CANONICAL_DATA_MANIFEST.json"
FAMILIES_DIR = "families"

SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
FAMILY_ID = re.compile(r"^[a-z][a-z0-9_]*(/[A-Za-z0-9_.\-]+)*$")
ACCEPTED_IDENTITY_STATUS = frozenset({"AUTHORITATIVE", "COMPLETE_CROSS_CHECKED"})


class CompatibilityMode(str, Enum):
    SINGLE_SNAPSHOT = "SINGLE_SNAPSHOT"
    SAME_SNAPSHOT_REBUILD = "SAME_SNAPSHOT_REBUILD"
    # CROSS_BUILD is deliberately absent: two game builds never form one dataset.


def _req(d: dict, key: str, where: str, exc=ProvenanceMissing) -> Any:
    v = d.get(key) if isinstance(d, dict) else None
    if v is None or v == "":
        raise exc(f"{where}.{key} is missing", field=f"{where}.{key}")
    return v


def _keys(d: Any, allowed: Set[str], where: str) -> dict:
    if not isinstance(d, dict):
        raise ManifestInvalid(f"{where} must be an object", field=where)
    extra = set(d) - allowed
    if extra:
        raise ManifestInvalid(f"{where} has unknown keys {sorted(extra)} (schema evolution needs a new schema "
                              f"version)", field=where, unknown=sorted(extra))
    return d


def _sha(v: Any, where: str) -> str:
    if not isinstance(v, str) or not SHA256.fullmatch(v):
        raise ManifestInvalid(f"{where} is not a sha256 hex digest: {v!r}", field=where)
    return v


@dataclass(frozen=True)
class SourceIdentity:
    game_version: str
    build_id: str
    unity_version: str
    game_assembly_sha256: str
    global_metadata_sha256: str
    identity_status: str
    patch_label: str

    @classmethod
    def parse(cls, d: Any) -> "SourceIdentity":
        d = _keys(d, set(cls.__dataclass_fields__), "source_identity")
        vals = {k: _req(d, k, "source_identity") for k in cls.__dataclass_fields__}
        for k in ("game_version", "build_id", "unity_version", "identity_status", "patch_label"):
            if not isinstance(vals[k], str):
                raise ManifestInvalid(f"source_identity.{k} must be a string", field=k)
        _sha(vals["game_assembly_sha256"], "source_identity.game_assembly_sha256")
        _sha(vals["global_metadata_sha256"], "source_identity.global_metadata_sha256")
        if vals["identity_status"] not in ACCEPTED_IDENTITY_STATUS:
            raise ProvenanceMissing(f"source_identity.identity_status {vals['identity_status']!r} is not one of "
                                    f"{sorted(ACCEPTED_IDENTITY_STATUS)}", field="identity_status")
        return cls(**vals)

    def patch_key(self) -> tuple[str, str, str]:
        return (self.game_version, self.build_id, self.game_assembly_sha256)


@dataclass(frozen=True)
class FamilyDeclaration:
    family_id: str
    path: str                       # relative to <bundle>/families/
    schema: str
    sha256: str
    content_sha256: str
    trust: TrustState
    trust_reasons: tuple[str, ...]
    coverage: CoverageState
    relationships: RelationshipState
    build_binding: str              # SELF_DECLARED | RUN_MANIFEST
    required: bool

    FIELDS = ("family_id", "path", "schema", "sha256", "content_sha256", "trust", "trust_reasons", "coverage",
              "relationships", "build_binding", "required")

    @classmethod
    def parse(cls, d: Any, where: str) -> "FamilyDeclaration":
        d = _keys(d, set(cls.FIELDS), where)
        for k in cls.FIELDS:
            if k not in d:
                raise FamilyDeclarationInvalid(f"{where}.{k} is missing", field=f"{where}.{k}")
        fid, path = d["family_id"], d["path"]
        if not isinstance(fid, str) or not FAMILY_ID.fullmatch(fid):
            raise FamilyDeclarationInvalid(f"{where}.family_id {fid!r} is invalid")
        if (not isinstance(path, str) or not path.endswith(".json") or path.startswith(("/", "\\"))
                or ".." in path.replace("\\", "/").split("/") or ":" in path):
            raise FamilyDeclarationInvalid(f"{where}.path {path!r} must be a relative .json path inside the bundle")
        if not isinstance(d["schema"], str):
            raise UnsupportedCanonicalSchema(f"{where}.schema must be a string")
        if d["build_binding"] not in ("SELF_DECLARED", "RUN_MANIFEST"):
            raise FamilyDeclarationInvalid(f"{where}.build_binding {d['build_binding']!r} is invalid")
        reasons = d["trust_reasons"]
        if not isinstance(reasons, list) or not all(isinstance(r, str) for r in reasons):
            raise FamilyDeclarationInvalid(f"{where}.trust_reasons must be a list of strings")
        if not isinstance(d["required"], bool):
            raise FamilyDeclarationInvalid(f"{where}.required must be a boolean")
        return cls(
            family_id=fid, path=path, schema=d["schema"],
            sha256=_sha(d["sha256"], f"{where}.sha256"),
            content_sha256=_sha(d["content_sha256"], f"{where}.content_sha256"),
            trust=parse_enum(TrustState, d["trust"], f"{where}.trust"),
            trust_reasons=tuple(reasons),
            coverage=parse_enum(CoverageState, d["coverage"], f"{where}.coverage"),
            relationships=parse_enum(RelationshipState, d["relationships"], f"{where}.relationships"),
            build_binding=d["build_binding"], required=d["required"],
        )

    def to_dict(self) -> dict:
        return {"family_id": self.family_id, "path": self.path, "schema": self.schema, "sha256": self.sha256,
                "content_sha256": self.content_sha256, "trust": self.trust.value,
                "trust_reasons": list(self.trust_reasons), "coverage": self.coverage.value,
                "relationships": self.relationships.value, "build_binding": self.build_binding,
                "required": self.required}


@dataclass(frozen=True)
class CanonicalDataManifest:
    data_version: str
    source_identity: SourceIdentity
    snapshot_id: str
    snapshot_content_hash: str
    extractor_repository: str
    extractor_commit: str
    run_manifest_content_hash: str
    canonical_content_hash: str
    extract_reproduction: str
    certified: bool
    certification_report_hash: str
    certified_exports: tuple[str, ...]
    trust_schema: str
    trust_report_hash: str
    compatibility: CompatibilityMode
    families: tuple[FamilyDeclaration, ...]
    manifest_hash: str

    TOP: ClassVar[frozenset[str]] = frozenset({
        "schema", "data_version", "source_identity", "snapshot", "extractor", "run_manifest", "certification",
        "trust_manifest", "compatibility", "families", "manifest_hash"})

    @staticmethod
    def make_data_version(game_version: str, build_id: str, snapshot_id: str, canonical_content_hash: str) -> str:
        return f"{game_version}_{build_id}+{snapshot_id}+{canonical_content_hash[:12]}"

    @classmethod
    def parse(cls, doc: Any) -> "CanonicalDataManifest":
        if not isinstance(doc, dict):
            raise ManifestInvalid("manifest must be a JSON object")
        if doc.get("schema") != MANIFEST_SCHEMA:
            raise UnsupportedCanonicalSchema(f"manifest schema {doc.get('schema')!r} is not {MANIFEST_SCHEMA}",
                                             schema=doc.get("schema"))
        _keys(doc, cls.TOP, "manifest")
        mh = _sha(_req(doc, "manifest_hash", "manifest", ManifestInvalid), "manifest.manifest_hash")
        if document_hash(doc, "manifest_hash") != mh:
            raise ManifestInvalid("manifest_hash does not match the manifest content", field="manifest_hash")
        si = SourceIdentity.parse(_req(doc, "source_identity", "manifest"))
        snap = _keys(_req(doc, "snapshot", "manifest"), {"snapshot_id", "content_hash"}, "snapshot")
        snapshot_id = _req(snap, "snapshot_id", "snapshot")
        ext = _keys(_req(doc, "extractor", "manifest"), {"repository", "commit", "dirty"}, "extractor")
        commit = _req(ext, "commit", "extractor")
        if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
            raise ProvenanceMissing(f"extractor.commit {commit!r} is not a full git commit", field="commit")
        if ext.get("dirty") is not False:
            raise ProvenanceMissing("extractor.dirty must be false (extractor source had uncommitted changes)",
                                    field="dirty")
        run = _keys(_req(doc, "run_manifest", "manifest"),
                    {"manifest_content_hash", "canonical_content_hash", "extract_reproduction"}, "run_manifest")
        cert = _keys(_req(doc, "certification", "manifest"),
                     {"certified", "report_hash", "certified_exports"}, "certification")
        if not isinstance(cert.get("certified"), bool):
            raise ManifestInvalid("certification.certified must be a boolean")
        tm = _keys(_req(doc, "trust_manifest", "manifest"), {"trust_schema", "report_hash"}, "trust_manifest")
        comp = _keys(_req(doc, "compatibility", "manifest"), {"mode"}, "compatibility")
        mode = parse_enum(CompatibilityMode, comp.get("mode"), "compatibility.mode")
        fams_raw = _req(doc, "families", "manifest", ManifestInvalid)
        if not isinstance(fams_raw, list) or not fams_raw:
            raise ManifestInvalid("manifest.families must be a non-empty list")
        fams = tuple(FamilyDeclaration.parse(f, f"families[{i}]") for i, f in enumerate(fams_raw))
        ids = [f.family_id for f in fams]
        if len(set(ids)) != len(ids):
            raise FamilyDeclarationInvalid(f"duplicate family ids {sorted({i for i in ids if ids.count(i) > 1})}")
        paths = [f.path for f in fams]
        if len(set(paths)) != len(paths):
            raise FamilyDeclarationInvalid("two families declare the same path")
        cch = _sha(_req(run, "canonical_content_hash", "run_manifest"), "run_manifest.canonical_content_hash")
        dv = _req(doc, "data_version", "manifest", ManifestInvalid)
        expected = cls.make_data_version(si.game_version, si.build_id, snapshot_id, cch)
        if dv != expected:
            raise ManifestInvalid(f"data_version {dv!r} != derived {expected!r}", field="data_version")
        certified_exports = tuple(cert.get("certified_exports") or ())
        for f in fams:
            if f.trust is TrustState.CERTIFIED and not cert["certified"]:
                raise ManifestInvalid(f"family {f.family_id!r} is CERTIFIED but the snapshot is not certified")
        return cls(
            data_version=dv, source_identity=si, snapshot_id=snapshot_id,
            snapshot_content_hash=_sha(_req(snap, "content_hash", "snapshot"), "snapshot.content_hash"),
            extractor_repository=_req(ext, "repository", "extractor"), extractor_commit=commit,
            run_manifest_content_hash=_sha(_req(run, "manifest_content_hash", "run_manifest"),
                                           "run_manifest.manifest_content_hash"),
            canonical_content_hash=cch,
            extract_reproduction=_req(run, "extract_reproduction", "run_manifest"),
            certified=cert["certified"],
            certification_report_hash=_sha(_req(cert, "report_hash", "certification"), "certification.report_hash"),
            certified_exports=certified_exports,
            trust_schema=_req(tm, "trust_schema", "trust_manifest"),
            trust_report_hash=_sha(_req(tm, "report_hash", "trust_manifest"), "trust_manifest.report_hash"),
            compatibility=mode, families=fams, manifest_hash=mh,
        )

    def family(self, family_id: str) -> FamilyDeclaration | None:
        return next((f for f in self.families if f.family_id == family_id), None)
