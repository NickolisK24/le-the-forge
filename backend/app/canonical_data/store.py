"""Read-only canonical data store (AUDIT-R2 P02).

One store = one verified bundle = one snapshot. After ``load`` it is
immutable: records are deep-frozen (mappings and tuples), attributes cannot be
set, and there is no API to add, replace or merge data. Lookups are by typed
source identity; a miss raises ``CanonicalRecordMissing``.

Trust is enforced on access: ``family(..., mode=TRUSTED_CALCULATION)`` admits
only CERTIFIED families with classified fields and no dangling relationships
(B2: uncertified required data never enters trusted calculations).

The store reads only files declared in its own bundle. It never reads the
legacy ``data/`` tree, ``exports_json``, frontend copies or another bundle,
and it has no fallback of any kind. It is not wired into the app factory; it
becomes the production authority only at the R2 cutover (R2-P20).
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, ClassVar, Mapping

from .errors import (
    CanonicalRecordMissing, DuplicateCanonicalId, FamilyMissing, ForeignSource, HashMismatch, ManifestInvalid,
    ManifestMissing, MixedPatch, MixedSnapshot, StoreImmutable, UnsupportedCanonicalSchema,
)
from .hashing import content_sha256_of, sha256_bytes
from .ids import SourceRef
from .manifest import FAMILIES_DIR, MANIFEST_FILE, CanonicalDataManifest, CompatibilityMode, FamilyDeclaration
from .schemas import REQUIRED_FAMILIES, SchemaSpec, spec_for, unknown_fields
from .trust import ConsumptionMode, CoverageState, check_admitted


def freeze(value: Any) -> Any:
    """Deep, read-only copy: dict -> MappingProxyType, list -> tuple."""
    if isinstance(value, dict):
        return MappingProxyType({k: freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(freeze(v) for v in value)
    return value


def thaw(value: Any) -> Any:
    """Plain JSON-compatible copy of a frozen value (for serialization only)."""
    if isinstance(value, Mapping):
        return {k: thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [thaw(v) for v in value]
    return value


@dataclass(frozen=True)
class BoundRef:
    """A source identity bound to the dataset that defined it."""

    data_version: str
    ref: SourceRef


@dataclass(frozen=True)
class Found:
    ref: SourceRef
    record: Mapping[str, Any]


@dataclass(frozen=True)
class Missing:
    ref: SourceRef
    family_id: str
    data_version: str
    reason: str = "REFERENCE_NOT_FOUND"


class FamilyView:
    """Read-only view of one family. Obtain through ``CanonicalDataStore.family``."""

    __slots__ = ("declaration", "spec", "data_version", "document", "_index", "unknown_fields", "_sealed")

    def __init__(self, declaration: FamilyDeclaration, spec: SchemaSpec, data_version: str, document: Mapping,
                 index: Mapping[SourceRef, Mapping], unknown: Mapping[str, tuple[str, ...]]):
        self.declaration = declaration
        self.spec = spec
        self.data_version = data_version
        self.document = document
        self._index = index
        self.unknown_fields = unknown
        self._sealed = True

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise StoreImmutable(f"FamilyView is read-only ({name})")
        object.__setattr__(self, name, value)

    @property
    def family_id(self) -> str:
        return self.declaration.family_id

    @property
    def review_required(self) -> bool:
        return bool(self.unknown_fields)

    @property
    def effective_coverage(self) -> CoverageState:
        # Unknown fields narrow coverage; they never widen it.
        return CoverageState.FIELDS_UNKNOWN if self.review_required else self.declaration.coverage

    def lookup(self, ref: SourceRef | BoundRef) -> Found | Missing:
        r = self._unbind(ref)
        rec = self._index.get(r)
        return Found(r, rec) if rec is not None else Missing(r, self.family_id, self.data_version)

    def require(self, ref: SourceRef | BoundRef) -> Mapping[str, Any]:
        r = self._unbind(ref)
        rec = self._index.get(r)
        if rec is None:
            raise CanonicalRecordMissing(f"{r.key()} not in family {self.family_id!r} ({self.data_version})",
                                         ref=r.key(), family=self.family_id, data_version=self.data_version)
        return rec

    def ids(self, id_type: type | None = None) -> tuple[SourceRef, ...]:
        return tuple(sorted((r for r in self._index if id_type is None or type(r) is id_type),
                            key=lambda r: (type(r).__name__, r.key())))

    def __contains__(self, ref: object) -> bool:
        return ref in self._index

    def _unbind(self, ref):
        if isinstance(ref, BoundRef):
            if ref.data_version != self.data_version:
                raise MixedSnapshot(f"reference {ref.ref.key()} belongs to {ref.data_version!r}, this family is "
                                    f"{self.data_version!r}", ref=ref.ref.key())
            return ref.ref
        if not isinstance(ref, SourceRef):
            raise TypeError(f"lookup needs a typed source identity, got {type(ref).__name__} {ref!r}")
        return ref


class CanonicalDataStore:
    """Immutable store over one verified bundle."""

    __slots__ = ("manifest", "bundle_dir", "_families", "_sealed")

    def __init__(self, manifest: CanonicalDataManifest, bundle_dir: Path, families: Mapping[str, FamilyView]):
        self.manifest = manifest
        self.bundle_dir = bundle_dir
        self._families = MappingProxyType(dict(families))
        self._sealed = True

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise StoreImmutable(f"CanonicalDataStore is read-only ({name})")
        object.__setattr__(self, name, value)

    @property
    def data_version(self) -> str:
        return self.manifest.data_version

    @property
    def family_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._families))

    # --- trust-aware access -----------------------------------------------------------
    def family(self, family_id: str, *, mode: ConsumptionMode) -> FamilyView:
        view = self._families.get(family_id)
        if view is None:
            raise FamilyMissing(f"family {family_id!r} is not in dataset {self.data_version}", family=family_id)
        d = view.declaration
        check_admitted(family_id, mode, d.trust, d.trust_reasons, view.effective_coverage, d.relationships)
        return view

    def require(self, family_id: str, ref: SourceRef | BoundRef, *, mode: ConsumptionMode) -> Mapping[str, Any]:
        return self.family(family_id, mode=mode).require(ref)

    def bind(self, ref: SourceRef) -> BoundRef:
        if not isinstance(ref, SourceRef):
            raise TypeError(f"bind needs a typed source identity, got {type(ref).__name__}")
        return BoundRef(self.data_version, ref)

    def relationships(self, family_id: str, *, mode: ConsumptionMode):
        """Relationship sets carried by a family (P09). Trust is checked like ``family``."""
        from .relationships import relationships_for_family
        return relationships_for_family(self.family(family_id, mode=mode))

    def contract_view(self, family_id: str) -> FamilyView:
        """Unchecked view for contract checks and diagnostics only (never for consumption).

        A static test forbids calling this outside ``app.canonical_data`` and tests.
        """
        view = self._families.get(family_id)
        if view is None:
            raise FamilyMissing(f"family {family_id!r} is not in dataset {self.data_version}", family=family_id)
        return view

    # --- loading --------------------------------------------------------------------
    @classmethod
    def load(cls, bundle_dir: Path, *, required_families: frozenset[str] = REQUIRED_FAMILIES) -> "CanonicalDataStore":
        bundle_dir = Path(bundle_dir)
        mpath = bundle_dir / MANIFEST_FILE
        if not mpath.is_file():
            raise ManifestMissing(f"no {MANIFEST_FILE} in {bundle_dir}", path=str(bundle_dir))
        try:
            doc = json.loads(mpath.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ManifestInvalid(f"{mpath} is not valid JSON: {e}") from e
        manifest = CanonicalDataManifest.parse(doc)
        if manifest.compatibility is not CompatibilityMode.SINGLE_SNAPSHOT:
            raise UnsupportedCanonicalSchema(f"compatibility mode {manifest.compatibility.value} is not supported "
                                             f"by this store (only SINGLE_SNAPSHOT)")
        if bundle_dir.name != manifest.data_version:
            raise MixedSnapshot(f"bundle directory {bundle_dir.name!r} is not named after its data_version "
                                f"{manifest.data_version!r}")
        root = (bundle_dir / FAMILIES_DIR).resolve()
        declared = {f.path for f in manifest.families}
        _reject_undeclared_files(root, declared)
        present = {f.family_id for f in manifest.families}
        missing = sorted(set(required_families) - present)
        if missing:
            raise FamilyMissing(f"required families missing: {missing}", missing=missing)
        families = {f.family_id: _load_family(root, f, manifest) for f in manifest.families}
        return cls(manifest, bundle_dir, families)


def _reject_undeclared_files(root: Path, declared: set[str]) -> None:
    if not root.is_dir():
        raise ManifestMissing(f"bundle has no {FAMILIES_DIR}/ directory")
    for p in root.rglob("*"):
        if p.is_symlink():
            raise ForeignSource(f"symlink in bundle: {p}")
        if p.is_file() and p.relative_to(root).as_posix() not in declared:
            raise ForeignSource(f"undeclared file in bundle: {p.relative_to(root).as_posix()}")


def _load_family(root: Path, decl: FamilyDeclaration, manifest: CanonicalDataManifest) -> FamilyView:
    path = (root / decl.path).resolve()
    if root not in path.parents:
        raise ForeignSource(f"family {decl.family_id!r} path escapes the bundle", family=decl.family_id)
    if not path.is_file():
        raise ManifestMissing(f"family file missing: {decl.path}", family=decl.family_id)
    raw = path.read_bytes()
    if sha256_bytes(raw) != decl.sha256:
        raise HashMismatch(f"family {decl.family_id!r} file hash differs from the manifest", family=decl.family_id)
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ManifestInvalid(f"family {decl.family_id!r} is not valid JSON: {e}") from e
    if content_sha256_of(doc) != decl.content_sha256:
        raise HashMismatch(f"family {decl.family_id!r} content hash differs from the manifest",
                           family=decl.family_id)
    spec = spec_for(decl.schema, decl.family_id)
    if (doc.get("_meta") or {}).get("schema") != decl.schema:
        raise UnsupportedCanonicalSchema(f"family {decl.family_id!r} declares {decl.schema!r} but carries "
                                         f"{(doc.get('_meta') or {}).get('schema')!r}", family=decl.family_id)
    build = spec.build_identity(doc) if spec.build_identity else None
    if build is not None and build != manifest.source_identity.game_assembly_sha256:
        raise MixedPatch(f"family {decl.family_id!r} is from another build", family=decl.family_id)
    if decl.build_binding == "SELF_DECLARED" and build is None:
        raise ManifestInvalid(f"family {decl.family_id!r} is declared SELF_DECLARED but carries no build identity")
    frozen_doc = freeze(doc)
    index: dict[SourceRef, Mapping] = {}
    if spec.index is not None:
        for ref, rec, where in spec.index(frozen_doc):
            if ref in index:
                raise DuplicateCanonicalId(f"{ref.key()} appears twice in family {decl.family_id!r} ({where})",
                                           ref=ref.key(), family=decl.family_id)
            index[ref] = rec
    unknown = {k: tuple(v) for k, v in unknown_fields(spec, frozen_doc).items()}
    return FamilyView(decl, spec, manifest.data_version, frozen_doc, MappingProxyType(index),
                      MappingProxyType(unknown))


class StoreRegistry:
    """Process-wide, thread-safe cache: at most one store per bundle directory.

    Gunicorn workers each build their own store at startup; threads inside a
    worker share it read-only. Loading is serialized by a lock so a bundle is
    verified once per process.
    """

    _lock = threading.Lock()
    _stores: ClassVar[dict[Path, CanonicalDataStore]] = {}

    @classmethod
    def get(cls, bundle_dir: Path, *, required_families: frozenset[str] = REQUIRED_FAMILIES) -> CanonicalDataStore:
        key = Path(bundle_dir).resolve()
        with cls._lock:
            store = cls._stores.get(key)
            if store is None:
                store = CanonicalDataStore.load(key, required_families=required_families)
                cls._stores[key] = store
            return store

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._stores.clear()
