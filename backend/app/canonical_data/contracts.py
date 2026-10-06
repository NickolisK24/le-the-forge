"""Executable canonical contracts (AUDIT-R2 P17).

``check_bundle(bundle_dir)`` loads a bundle through the real store and checks
invariants that hold for any correct canonical dataset. No check depends on
record counts or on a particular patch, so the same contracts run unchanged
against the certified 1.5 bundle.

Usage:
    python -m app.canonical_data.contracts <bundle_dir>
Exit code 0 only when there is no violation. Loading failures (a bundle the
store refuses) are reported as a single violation with the error code.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from .errors import CanonicalDataError
from .hashing import content_sha256_of, sha256_file
from .ids import parse_key
from .manifest import FAMILIES_DIR
from .relationships import relationships_for_family
from .store import CanonicalDataStore, thaw
from .trust import ADMITTED, ConsumptionMode, CoverageState, RelationshipState, TrustState


@dataclass(frozen=True)
class Violation:
    contract: str
    family: str | None
    detail: str


CONTRACTS = (
    "MANIFEST_PROVENANCE", "FAMILY_UNIQUE", "FAMILY_SCHEMA", "FAMILY_HASH", "FAMILY_TRUST_STATE",
    "FAMILY_COVERAGE_STATE", "IDENTITY_ROUNDTRIP", "IDENTITY_NOT_POSITIONAL", "IDENTITY_NOT_NAME",
    "TRUST_POLICY", "PATCH_CONSISTENT", "FIELD_SURVIVAL", "RELATIONSHIP_EXPLICIT", "RELATIONSHIP_DECLARED",
)


def check_bundle(bundle_dir: Path) -> list[Violation]:
    try:
        store = CanonicalDataStore.load(Path(bundle_dir))
    except CanonicalDataError as e:
        return [Violation("BUNDLE_LOADS", None, f"{e.code}: {e}")]
    return check_store(store)


def check_store(store: CanonicalDataStore) -> list[Violation]:
    v: list[Violation] = []
    m = store.manifest
    si = m.source_identity

    # MANIFEST_PROVENANCE: every provenance field present (the parser enforces it; re-assert the result)
    for name, val in (("game_version", si.game_version), ("build_id", si.build_id),
                      ("game_assembly_sha256", si.game_assembly_sha256), ("snapshot_id", m.snapshot_id),
                      ("extractor_commit", m.extractor_commit), ("canonical_content_hash", m.canonical_content_hash),
                      ("data_version", m.data_version)):
        if not val:
            v.append(Violation("MANIFEST_PROVENANCE", None, f"{name} is empty"))
    if not all(f.content_sha256 and f.sha256 for f in m.families):
        v.append(Violation("MANIFEST_PROVENANCE", None, "a family lacks content hashes"))

    ids = [f.family_id for f in m.families]
    if len(ids) != len(set(ids)):
        v.append(Violation("FAMILY_UNIQUE", None, "duplicate family ids"))

    for decl in m.families:
        fid = decl.family_id
        view = store.contract_view(fid)
        path = store.bundle_dir / FAMILIES_DIR / decl.path
        original = json.loads(path.read_text(encoding="utf-8"))

        if original.get("_meta", {}).get("schema") != decl.schema:
            v.append(Violation("FAMILY_SCHEMA", fid, "declared schema differs from the payload"))
        if sha256_file(path) != decl.sha256 or content_sha256_of(original) != decl.content_sha256:
            v.append(Violation("FAMILY_HASH", fid, "payload hash differs from the declaration"))
        if decl.trust not in TrustState:
            v.append(Violation("FAMILY_TRUST_STATE", fid, f"invalid trust {decl.trust!r}"))
        if decl.trust is TrustState.CERTIFIED and not m.certified:
            v.append(Violation("FAMILY_TRUST_STATE", fid, "CERTIFIED family in an uncertified snapshot"))
        if decl.coverage not in CoverageState:
            v.append(Violation("FAMILY_COVERAGE_STATE", fid, f"invalid coverage {decl.coverage!r}"))

        # IDENTITY_ROUNDTRIP: every identity formats and parses back to itself
        for ref in view.ids():
            try:
                if parse_key(ref.key()) != ref:
                    v.append(Violation("IDENTITY_ROUNDTRIP", fid, f"{ref.key()} does not round-trip"))
            except CanonicalDataError as e:
                v.append(Violation("IDENTITY_ROUNDTRIP", fid, f"{ref!r}: {e}"))

        # IDENTITY_NOT_POSITIONAL: identities do not depend on record order
        if view.spec.index is not None:
            v.extend(_permutation_check(view, original))

        # IDENTITY_NOT_NAME: display names have no influence on identity
        v.extend(_name_check(view, original))

        # TRUST_POLICY: TRUSTED access succeeds exactly for CERTIFIED + classified + not dangling
        for mode in ConsumptionMode:
            expected = decl.trust in ADMITTED[mode] and (
                mode is not ConsumptionMode.TRUSTED_CALCULATION or (
                    view.effective_coverage is CoverageState.FIELDS_CLASSIFIED
                    and decl.relationships is not RelationshipState.DANGLING))
            try:
                store.family(fid, mode=mode)
                got = True
            except CanonicalDataError:
                got = False
            if got != expected:
                v.append(Violation("TRUST_POLICY", fid, f"{mode.value}: admitted={got}, expected={expected}"))

        # PATCH_CONSISTENT: a self-declared build equals the manifest build
        if view.spec.build_identity is not None:
            b = view.spec.build_identity(original)
            if b is not None and b != si.game_assembly_sha256:
                v.append(Violation("PATCH_CONSISTENT", fid, "family declares another build"))
            if decl.build_binding == "SELF_DECLARED" and b is None:
                v.append(Violation("PATCH_CONSISTENT", fid, "SELF_DECLARED family carries no build"))

        # FIELD_SURVIVAL: the store holds the payload unchanged; unknown fields are surfaced, not dropped
        if thaw(view.document) != original:
            v.append(Violation("FIELD_SURVIVAL", fid, "stored document differs from the payload"))
        if view.unknown_fields and view.effective_coverage is not CoverageState.FIELDS_UNKNOWN:
            v.append(Violation("FIELD_SURVIVAL", fid, "unknown fields did not narrow coverage"))

        # RELATIONSHIP_*: unresolved edges are explicit; declared state never hides dangling edges
        for name, rs in relationships_for_family(view).items():
            for edge in rs.edges:
                if edge.resolved and edge.target is None:
                    v.append(Violation("RELATIONSHIP_EXPLICIT", fid, f"{name}: RESOLVED edge without target"))
                if not edge.resolved and edge.target is not None and edge.resolution.value != "QUARANTINED":
                    v.append(Violation("RELATIONSHIP_EXPLICIT", fid, f"{name}: unresolved edge carries a target"))
            # Targets of the family's own identity types must exist in the family.
            own_types = {type(r) for r in view.ids()}
            intra = rs.resolve_targets(view.__contains__) if rs.rel.target_type in own_types else rs
            if intra.integrity().dangling > rs.integrity().dangling:
                v.append(Violation("RELATIONSHIP_EXPLICIT", fid, f"{name}: a RESOLVED edge points at a target "
                                                                 f"that is not in the family"))
            rep = intra.integrity()
            if rs.rel.required and rep.dangling and decl.relationships is RelationshipState.RESOLVED_OR_ALLOWLISTED:
                v.append(Violation("RELATIONSHIP_DECLARED", fid, f"{name}: {rep.dangling} dangling required edges "
                                                                 f"but the family claims RESOLVED_OR_ALLOWLISTED"))
    return v


def _permutation_check(view, original) -> list[Violation]:
    spec = view.spec
    shuffled = json.loads(json.dumps(original))
    rng = random.Random(0)
    for key in ("affixes", "trees"):
        if isinstance(shuffled.get(key), list):
            rng.shuffle(shuffled[key])
    for fam in (shuffled.get("families") or {}).values():
        if isinstance(fam, list):
            rng.shuffle(fam)
    a = {ref: rec for ref, rec, _ in spec.index(original)}
    b = {ref: rec for ref, rec, _ in spec.index(shuffled)}
    if a != b:
        return [Violation("IDENTITY_NOT_POSITIONAL", view.family_id, "identity map changes with record order")]
    return []


NAME_FIELDS = frozenset({"name", "names", "display_name", "title", "enum_name", "stat_name", "alt_text",
                         "description", "node_description", "lore_text", "name_key", "alt_text_key", "ability_key",
                         "loot_filter_override_name", "mod_display_name"})


def _blank_names(value):
    if isinstance(value, dict):
        return {k: ("X" if k in NAME_FIELDS else _blank_names(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_blank_names(x) for x in value]
    return value


def _name_check(view, original) -> list[Violation]:
    """Display names have no influence on identity: blanking them leaves the identity set unchanged."""
    if view.spec.index is None:
        return []
    a = [ref for ref, _rec, _ in view.spec.index(original)]
    b = [ref for ref, _rec, _ in view.spec.index(_blank_names(original))]
    if a != b:
        return [Violation("IDENTITY_NOT_NAME", view.family_id, "identities change when display names change")]
    return []


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Run the R2 canonical contracts against a bundle.")
    ap.add_argument("bundle", type=Path)
    args = ap.parse_args(argv)
    vs = check_bundle(args.bundle)
    for x in vs:
        print(f"[{x.contract}] {x.family or '-'}: {x.detail}")
    print(f"{len(vs)} violation(s)")
    return 1 if vs else 0


if __name__ == "__main__":
    raise SystemExit(main())
