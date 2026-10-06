# R2 Canonical Consumption Contract (R2-02)

**Status: design only. Nothing here is implemented.** This contract defines the single handoff from R1 (last-epoch-data) into The Forge.

## Principles

1. **One producer of meaning.** last-epoch-data is the only place that interprets game bytes:
   - raw TypeTree envelopes;
   - binary walkers;
   - enum and property decoding.

   The Forge consumes **canonical schemas only**. It never parses raw extraction formats, never re-derives scale, and never re-resolves references by name.
2. **One dataset at a time.** A running Forge instance consumes exactly one `CanonicalDataManifest`. Every family it serves comes from that manifest, or the instance refuses to start (see R2_MIXED_PATCH_POLICY.md).
3. **Byte-identical carriage.** The sync step copies canonical family files unchanged and verifies their hashes. Any transformation the Forge needs happens in typed, tested adapters at load time. Each adapter declares its derivations (R2_CONTRACT_TEST_PLAN.md T2), and never persists a second authority.
4. **Trust travels with data.** The R1 trust state is part of the payload of every family, every API envelope and every saved build. It can be narrowed (for example, QUARANTINED shown as advisory), never widened.
5. **Fail closed, never fall back.** Missing, unknown, wrong-schema or mixed-provenance data is an explicit error or an explicit unsupported state. It never becomes stale legacy data, `0`, `"Unknown"` or "first match".

## Where the inputs come from (R1 artifacts)

| R1 artifact | Path in last-epoch-data | Provides |
| --- | --- | --- |
| Raw snapshot manifest | `snapshots/raw/<snapshot_id>.json` | `snapshot_id`, `content_hash`, `source_identity` (version, build, Unity, GameAssembly and metadata sha256, `identity_status`) |
| Extraction run manifest | `snapshots/runs/<snapshot_id>.json` | extractor commit and dirty state, tool versions, `canonical_exports[]` (path, sha256, content_sha256, record counts), `canonical_content_hash`, unknown/failed lists. Canonical inventory added in `7dc1ad6`; R1 contract defect found during R2 prep. |
| Reproduction report | `snapshots/runs/<snapshot_id>.reproduce.json` | Extract-stage reproduction status |
| Trust manifest | `exports_canonical/TRUST_MANIFEST.json` | Per family: `consumer_state`, reasons, `trusted_calculation_eligible`, coverage/relationship/semantic status, patch |
| Certification report | `docs/generated/r1_certification_report.json` | `certified`, criteria, `certified_exports`, `report_hash` |
| Canonical families | `exports_canonical/*.json`, `exports_canonical/typetree/**` | Data; each carries `_meta.schema` and `identity_contract` |
| Coverage / relationships | `docs/generated/r1_coverage_metrics.json`, `r1_field_survival_report.json` | Per-family relationship and field-coverage state |

The Forge never reads `exports_json/` (legacy) once R2 lands; see R2_LEGACY_RETIREMENT_PLAN.md.

## Types

### SourceIdentity

```json
{
  "game_version": "1.5.x",
  "build_id": "<steam build>",
  "unity_version": "6000.x",
  "game_assembly_sha256": "<64 hex>",
  "global_metadata_sha256": "<64 hex>",
  "identity_status": "AUTHORITATIVE | COMPLETE_CROSS_CHECKED"
}
```

This is copied verbatim from the raw snapshot manifest. `PARTIAL` or `INCOMPLETE` identities are rejected for TRUSTED and ADVISORY consumption.

### DataVersion

`data_version = "<game_version>_<build_id>+<snapshot_id>+<canonical_content_hash[0:12]>"`

It is a server-side string, derived only from the manifest and never typed by a person. It is the key persisted on builds (R2_DATABASE_PROVENANCE_PLAN.md). Two datasets with identical canonical content from the same snapshot share a `data_version`.

### TrustState

```json
{
  "consumer_state": "CERTIFIED | QUARANTINED | PRESERVED_ONLY | UNSUPPORTED | UNKNOWN",
  "reasons": ["..."],
  "trusted_calculation_eligible": true
}
```

These values come from the R1 trust manifest unchanged. The Forge may derive `served_as`:
- `TRUSTED` only if `consumer_state == CERTIFIED`;
- `ADVISORY` if QUARANTINED;
- never served if UNKNOWN or UNSUPPORTED.

### RelationshipState

```json
{
  "relationships": [
    {"name": "tree_prerequisite", "required": true, "discovered": 254, "resolved": 254,
     "dangling_unallowlisted": 0, "allowlisted": [{"ref": "...", "reason": "..."}]}
  ],
  "status": "RESOLVED | DANGLING_ALLOWLISTED | DANGLING"
}
```

`required` is declared by the Forge per family (table below), not by R1. A family with any `required` relationship in `DANGLING` cannot be served TRUSTED.

### FieldCoverageState

```json
{"status": "FIELDS_CLASSIFIED | UNKNOWN_FIELDS | BLOCKED", "unknown_paths": [], "blocked_domains": []}
```

It comes from R1 field survival for the family's domains.

### DataFamilyManifest

```json
{
  "family_id": "affixes",
  "canonical_path": "affixes.json",
  "schema": "r1_canonical_affix/1",
  "accepted_schemas": ["r1_canonical_affix/1"],
  "content_sha256": "<= run manifest canonical_exports[].content_sha256>",
  "sha256": "<file bytes>",
  "record_count": 1112,
  "identity_contract": "affix_id is identity; names are presentation",
  "source_identity_ref": "manifest",
  "trust": "TrustState",
  "relationships": "RelationshipState",
  "field_coverage": "FieldCoverageState",
  "consumers": ["affix_registry", "craft_service", "ref_api"]
}
```

### CanonicalDataManifest

```json
{
  "schema": "forge_canonical_data_manifest/1",
  "data_version": "1.5.1_12345678+<snapshot_id>+<hash12>",
  "source_identity": "SourceIdentity",
  "snapshot": {"snapshot_id": "...", "content_hash": "..."},
  "extractor": {"repository": "last-epoch-data", "commit": "<40 hex>", "dirty": false},
  "run_manifest": {"manifest_content_hash": "...", "canonical_content_hash": "...", "reproduced": "REPRODUCED"},
  "certification": {"certified": true, "report_hash": "...", "certified_exports": ["..."]},
  "trust_manifest": {"trust_schema": "r1_trust_manifest/1", "report_hash": "..."},
  "compatibility": {"mode": "SINGLE_SNAPSHOT"},
  "families": ["DataFamilyManifest"],
  "manifest_hash": "<sha256 of canonical JSON without manifest_hash>"
}
```

Bundle layout (immutable, one directory per `data_version`):

```
data/canonical/<data_version>/
  CANONICAL_DATA_MANIFEST.json
  families/affixes.json  passive_trees.json  skill_trees.json  weaver_tree.json
           property_definitions.json  typed/<family>.json  (typed views built in last-epoch-data, see below)
data/canonical/CURRENT        -> one line: the active data_version
```

## Producer rule: typed views are built upstream

R1 provides only lossless TypeTree envelopes (`exports_canonical/typetree/<Class>.json`) for these families:
- items;
- uniques;
- sets;
- classes;
- masteries;
- abilities;
- ailments;
- blessings.

A typed view (for example `canonical_uniques/1` with numeric `unique_id`, `base_type_id`, `sub_type_id`, structured `mods[]`) **is built in last-epoch-data**, beside the envelope, with its own schema, identity contract, field survival and trust entry. The Forge consumes the typed view.

This keeps a single interpreter of game formats; R2_EXECUTIVE_PLAN.md lists these upstream builders as R2 packages. Their field lists cannot be designed before the 1.5 TypeTree dumps exist (R2_IMPLEMENTATION_PACKAGES.json: blocked on the certified snapshot).

## Consumption modes

| Mode | Used by | Allowed `consumer_state` | Labelled |
| --- | --- | --- | --- |
| TRUSTED | Stat engine, DPS/EHP, craft simulation, build validation | CERTIFIED | `trust: CERTIFIED` |
| ADVISORY | Reference browsing, planner display of QUARANTINED data | CERTIFIED, QUARANTINED | `trust: QUARANTINED` + reasons, visibly |
| NONE | anything | UNKNOWN, UNSUPPORTED, PRESERVED_ONLY | Not served: the endpoint returns an explicit unsupported state |

A calculation that needs a family not available as TRUSTED returns `UNSUPPORTED_DATA` with the family and reason. It never computes with advisory data silently. If the product decides to allow advisory calculations, the output must carry `trust: ADVISORY` end to end (CALC-15 belongs to R6, but the contract reserves the field now).

## Loader rejections (fail closed at startup or bundle import)

The loader (`CanonicalDataStore`, R2-P02) refuses the dataset, and the process does not serve game data, when any of these hold:

| # | Condition | Error |
| --- | --- | --- |
| L1 | `CANONICAL_DATA_MANIFEST.json` missing, unparsable, or `manifest_hash` mismatch | `MANIFEST_INVALID` |
| L2 | `schema` not `forge_canonical_data_manifest/1` | `MANIFEST_SCHEMA_UNSUPPORTED` |
| L3 | `source_identity.identity_status` not AUTHORITATIVE / COMPLETE_CROSS_CHECKED, or any SourceIdentity field missing | `PROVENANCE_MISSING` |
| L4 | `extractor.dirty` true or commit missing; `snapshot.snapshot_id` missing | `PROVENANCE_MISSING` |
| L5 | A family file hash differs from its manifest entry, or from the run manifest's `canonical_exports` | `CONTENT_HASH_MISMATCH` |
| L6 | A family `schema` not in the adapter's `accepted_schemas` | `SCHEMA_VERSION_UNSUPPORTED` |
| L7 | A family `_meta` patch/build/GameAssembly sha differs from the manifest's SourceIdentity | `MIXED_PATCH` |
| L8 | A REQUIRED family is absent | `FAMILY_MISSING` |
| L9 | A REQUIRED family is `UNKNOWN`/`UNSUPPORTED`, or not `CERTIFIED` while the instance is configured `TRUSTED_ONLY` (production default) | `TRUST_REJECTED` |
| L10 | A `required` relationship is DANGLING (not allowlisted with a reason) | `RELATIONSHIP_UNRESOLVED` |
| L11 | Any family loaded from outside `data/canonical/<data_version>/` (legacy path, frontend copy, hand-authored constant registered as game data) | `FOREIGN_SOURCE` |

There is **no fallback**. If the canonical dataset is rejected, the API returns `503 DATASET_UNAVAILABLE` for game-data endpoints and the health check reports the rejection reason. Legacy `data/` is never loaded instead.

## Required families and required relationships (Forge-declared)

| Family | Canonical source | Required for | Required relationships |
| --- | --- | --- | --- |
| affixes | `affixes.json` | items, craft, stats | property → SP (`affix_property->SP`); sub-property encodings (`affix.*Property`) when used |
| property_definitions | `property_definitions.json` | stat naming, tree stats | — |
| passive_trees | `passive_trees.json` | passives, builds | `tree_prerequisite[passive]`, node → mastery (via class typed view) |
| skill_trees | `skill_trees.json` | skills, builds | `tree_prerequisite[skill]`, tree → ability |
| weaver_tree | `weaver_tree.json` | weaver | `tree_prerequisite[weaver]` |
| classes / masteries | typed view from `CharacterClassList` envelope | everything character-side | class → masteries (by source index), mastery → abilities |
| abilities / skills | typed view from `Ability` / `AbilityManager` envelopes | skills, trees | ability → skill tree (by `abilityRef` path id) |
| items (base types) | typed view from `ItemList` envelope | gear, importer | base type → subtypes; implicit → property |
| uniques / sets | typed views from `UniqueList` / set envelopes | gear | unique → base type/subtype; set member → set |
| ailments | typed view from `AilmentList`/`Ailment` envelopes | stats, DPS (R6) | — |
| blessings | typed view (timeline/blessing envelopes) | gear | blessing → property |
| enums | `enums.json` via the R1 enum gate (C13) | decoding labels | referenced enums extracted |

A Forge feature whose family is not REQUIRED (for example monster mods) may be shipped only with `served_as: ADVISORY` or `UNSUPPORTED`.

## What replaces today's sync

`scripts/sync_game_data.py` today:
- transforms legacy exports (drops fields, rescales, remaps masteries by index);
- writes them into `data/`.

R2 replaces the game-data part with `scripts/import_canonical_bundle.py` (R2-P01). That script:
1. reads the R1 artifacts above from a pinned last-epoch-data commit;
2. verifies every hash, provenance rule and certification against L1–L11;
3. copies family files byte-identically into `data/canonical/<data_version>/`;
4. writes the manifest and updates `CURRENT` in the same commit.

It performs **no value or identity transformation**. The legacy sync stays only for files R2 has not migrated, and every file it still writes is listed in R2_LEGACY_RETIREMENT_PLAN.md.
