# AUDIT-R2 Foundation Implementation

**Status: R2 FOUNDATION READY — WAITING FOR R1 CURRENT SNAPSHOT.**

Only snapshot-independent infrastructure is built. Nothing is wired into the running application, the reference-data authority is unchanged, and nothing is merged or deployed.

| Item | Value |
| --- | --- |
| Branch | `feat/audit-r2-foundation` |
| Base | `5c75ac4` (`docs/audit-r2-preparation`, the R2 plan), which sits on the R1 branch `fix/audit-r1-extraction-consumption` @ `d92e4d8` |
| last-epoch-data | `0111f1e` (fixtures sliced from this commit) |
| Production | `main` @ `80bd559`, untouched |
| R1 | Not certified. The real 1.4.6 run has no raw snapshot (B7), so it cannot form a bundle and is rejected with `PROVENANCE_MISSING`. |
| Packages built | P17, P01, P02, P03, P09 (relationship primitives), P15, P16 |
| Not started | P04, P05, P06, P07, P08, P10, P11, P12, P13, P14, P18, P19, P20; R3 |

## Isolation from production

- `backend/app/canonical_data/` is a new package. It is not imported by `create_app`, a route, a service or an engine. `test_app_factory_does_not_load_canonical_data` checks this in a subprocess.
- The package never reads `data/`, `exports_json` or any other legacy path. Static tests scan the importer and the store for this.
- No configuration flag is needed to keep it off, because nothing loads it. Wiring it in is R2-P14's job, behind its own flag.
- `ADVISORY_CALCULATION_ENABLED = False` is a constant. No code path admits uncertified data into a trusted calculation (B2).
- No migration file and no model was changed. The PostgreSQL tests add a test-only config subclass at runtime and remove it afterwards.
- The fallback gate only reads source files.
- CI runs on `dev`, `feat/audit-r2-**` and pull requests. It deploys nothing.

## Package results

### P17: canonical contract tests

| | |
| --- | --- |
| Status | Done |
| Files | `app/canonical_data/contracts.py`; `tests/canonical_data/test_contracts.py`, `test_contract_plan.py`, `conftest.py`; `scripts/build_r2_fixtures.py`; `tests/fixtures/canonical/r1_1.4.6_slice/` (1.4 MB) |
| Production change | None |

**Contracts.** There are 14 executable contracts, plus `BUNDLE_LOADS` for bundles that fail to load:

| Area | Contracts |
| --- | --- |
| Manifest | MANIFEST_PROVENANCE |
| Family | FAMILY_UNIQUE, FAMILY_SCHEMA, FAMILY_HASH, FAMILY_TRUST_STATE, FAMILY_COVERAGE_STATE |
| Identity | IDENTITY_ROUNDTRIP, IDENTITY_NOT_POSITIONAL, IDENTITY_NOT_NAME |
| Trust and patch | TRUST_POLICY, PATCH_CONSISTENT |
| Fields | FIELD_SURVIVAL |
| Relationships | RELATIONSHIP_EXPLICIT, RELATIONSHIP_DECLARED |

**How the contracts work:**
- They assert invariants, never record counts. Running them on the 1.5 bundle needs no edits: set `CANONICAL_CONTRACT_BUNDLE=<dir>`, or run `python -m app.canonical_data.contracts <dir>`.
- `IDENTITY_NOT_POSITIONAL` re-indexes a shuffled copy of the document; the identities must not change.
- `IDENTITY_NOT_NAME` re-indexes with every name field blanked; again, the identities must not change.
- Two tests check the checks themselves. A deliberately name-keyed adapter must fail `IDENTITY_NOT_NAME`, and a position-keyed one must fail `IDENTITY_NOT_POSITIONAL`.

**Fixtures:**
- They are real R1 1.4.6 canonical exports at `0111f1e`, sliced:
  - 51 affixes;
  - the Acolyte and Mage passive trees;
  - 8 skill trees, including `fi9` and `rf1azz` with their incorrect metadata unchanged;
  - the weaver tree;
  - 25 property definitions per family.
- `FIXTURE_PROVENANCE.json` records the source commit and the original hashes. It also records content hashes computed by R1's own `r1_snapshot` code, and the importer is tested against those.
- Success paths use a synthetic snapshot and run manifest, labelled `SYNTHETIC-TEST-…`, because no real snapshot exists yet.

**Contract-test plan coverage** (`test_contract_plan.py`):

| Tests | Status |
| --- | --- |
| T3, T6, T7 (store half), T10 (gate), T11, T12 (migrations half) | Implemented |
| T1, T2, T4 (per-family), T5, T8, T9, T13, T14 | xfail, each naming the unbuilt package that owns it |

**Acceptance:**
- Every T-test is either wired or marked xfail with its owner: met.
- Fixtures regenerate from the pinned commit with `build_r2_fixtures.py`: met.

### P01: canonical bundle importer

| | |
| --- | --- |
| Status | Done |
| Files | `app/canonical_data/importer.py`, `manifest.py`, `hashing.py`, `schemas.py`, `errors.py`, `trust.py`; `tests/canonical_data/test_importer.py` |
| Production change | None. It is an offline CLI: `python -m app.canonical_data.importer --r1-root … --run-manifest … --out … [--dry-run]` |

**Checks, in order.** Each failure raises a typed error with a stable code. The importer fails closed, does no repair, rescaling or name inference, and never falls back to `data/`.

1. Run schema.
2. Raw snapshot present (`PROVENANCE_MISSING` if not).
3. Snapshot id and content hash (`MIXED_SNAPSHOT`).
4. Authoritative, complete game identity.
5. Run identity equals snapshot identity (`MIXED_PATCH`).
6. Clean extractor commit.
7. `canonical_exports` inventory and `canonical_content_hash` (`CONTENT_HASH_MISMATCH`).
8. Trust manifest schema, patch, `families` list and per-family `reasons`.
9. Certification report patch, `certified`, and the `certified_exports` list.
10. Per export:
    - the path stays inside `exports_canonical/`;
    - the file sha256 and the content sha256 both match;
    - the schema is accepted (`SCHEMA_VERSION_UNSUPPORTED`);
    - the self-declared build matches;
    - a trust entry exists with the same patch;
    - CERTIFIED appears only if it is in the certification report.
11. Required families present.
12. The manifest is sealed and re-parsed by the strict parser.

**Output and acceptance:**
- The bundle is written to `data/canonical/<data_version>/`, atomically (temp dir and rename). The import is idempotent: different content for an existing version is refused.
- The real 1.4.6 retroactive run manifest is rejected with `PROVENANCE_MISSING`, even in `--dry-run`.
- Importing the same input twice gives an identical bundle and `manifest_hash`: met.
- Every rejection is tested offline with its error code: met.
- 1.4.6 cannot be written: met (it is rejected outright).

### P02: canonical data store

| | |
| --- | --- |
| Status | Done |
| Files | `app/canonical_data/store.py`; `tests/canonical_data/test_store.py` |
| Production change | None (not wired in) |

**API.** `CanonicalDataStore.load(bundle_dir)` returns an immutable, single-snapshot store:
- `manifest`, `data_version`, `family_ids`;
- `family(id, mode=…)`;
- `get` / `require` (via `FamilyView.lookup` / `require` and `store.require`);
- `relationships(id, mode=…)`;
- `bind(ref)`.

**Behaviour:**
- **Fail-closed load.** These are all rejected:
  - a directory name that differs from `data_version` (`MIXED_SNAPSHOT`);
  - an undeclared file or a symlink in the bundle (`FOREIGN_SOURCE`);
  - a hash or content-hash mismatch;
  - a schema or build mismatch;
  - duplicate ids;
  - a missing manifest or a missing required family.
- **Missing record containers.** A schema-valid payload without its record list is `SCHEMA_REVIEW_REQUIRED`, never an empty family.
- **No lookup fallback.** A miss is an explicit `Missing` or `CanonicalRecordMissing`. Lookups take only typed identities: a string or int raises `TypeError`, and a reference from another dataset raises `MIXED_SNAPSHOT`.
- **No mixing.** There is no merge, add or cross-snapshot API, and no `SAME_SNAPSHOT_REBUILD` support.
- **Trust-aware.** `family()` applies `check_admitted` (see P03/trust below).
- **Threads.** `StoreRegistry` loads each bundle once under a lock; tested with 8 threads. Records are frozen (`MappingProxyType` and tuples).
- **Unknown fields** are kept, narrow coverage to `FIELDS_UNKNOWN`, and set `review_required`.

**Acceptance:**
- Every rejection yields its error and no data: met.
- QUARANTINED is reachable only in `ADVISORY_DISPLAY`: met.
- No fallback path (T11): met.

### P03: typed identity infrastructure

| | |
| --- | --- |
| Status | Done |
| Files | `app/canonical_data/ids.py`; `tests/canonical_data/test_ids.py` |
| Production change | None |

**The 16 types:**

| Kind | Types |
| --- | --- |
| Single integer | `ClassId`, `AbilityId`, `AffixId`, `BaseTypeId`, `UniqueId`, `SetId`, `AilmentId` |
| String code | `SkillTreeId` |
| Composite | `MasteryRef(class_id, mastery_index)`, `SkillId(ability)`, `TreeNodeId(tree, node_id)`, `PassiveNodeId(tree, node_id)`, `AffixPropertyId(affix, property_index)`, `BaseItemId(base_type, sub_type_id)`, `BlessingId(item)`, `PropertyId(namespace, index, ability?)` |

**Design rules:**
- Every type is frozen, ordered and slotted, with `key()` / `parse_key()` round trips.
- Values are validated: bools, negative numbers and non-canonical integers are rejected.
- There is **no `MasteryId`**. Mastery identity is the composite `(class_id, mastery_index)` with `is_base_class` (B3).
- No type has a name or slug constructor; a static test checks for `from_name` and `by_name`.

**Deviations:**
- `PassiveNodeId` is keyed by the passive tree code, not by `(class_id, node_id)` as the identity policy suggests. The canonical export has no `characterClassID` on passive trees. Deriving one would mean guessing, so the tree code, which is the source key, is used instead.
- The planned "registry factories" (constructors that reject non-store inputs) arrive with the first consumer package, P04. `FOREIGN_SOURCE` is already enforced at the bundle level.

**Acceptance:**
- Round trips: met.
- Uniqueness per family is asserted when the 1.4.6 fixtures load: met.

### P09: canonical relationship primitives and integrity infrastructure

| | |
| --- | --- |
| Status | Done |
| Files | `app/canonical_data/relationships.py`; `tests/canonical_data/test_relationships.py` |
| Production change | None |

**Scope.** P09 was redefined for the foundation. The plan's P09 (the reference API on the store) is not built. This package provides the relationship model and integrity checks only.

**The model:**
- **Cardinalities:** `ONE_TO_ONE`, `ONE_TO_MANY`, `MANY_TO_ONE`, `MANY_TO_MANY`, validated per set.
- **Shape:** ordered (unique ordinals per source); required or optional.
- **Resolution states:**
  - `RESOLVED`;
  - `NULL_REFERENCE`, `IMPLAUSIBLE_REFERENCE`, `TARGET_FAILED_TO_PARSE`, `UNRESOLVED_REFERENCE`, `AMBIGUOUS`, `NOT_CARRIED`, `QUARANTINED`.
- **Edges.** Every edge keeps its source, target, type, resolution, raw target, ordinal, attributes and provenance.

**Graph behaviour:**
- There is no `parentId`. A node may have several prerequisites; the 1.4.6 fixtures contain real multi-prerequisite nodes, and these are tested.
- A required unresolved edge raises unless it is allowlisted, and an allowlist entry needs a reason.
- An optional unresolved edge stays visible.
- Nothing is mapped to 0, the first match, or None-as-success.
- Cross-family resolution is available through `resolve_targets(exists)`.
- Cycles are detected and reported, never repaired.

**Adapters** (built over existing 1.4.6 canonical families):
- `tree_contains_node`;
- `node_requires_node`, with a `points_required` attribute;
- `tree_ability`, where `NOT_IN_RAW_DUMP` becomes `NOT_CARRIED`;
- `affix_has_property`, `affix_property_stat`.

Unknown vocabulary, or a missing `ability_ref` / `property`, raises `SCHEMA_REVIEW_REQUIRED`. Prerequisite AND/OR semantics are deliberately not encoded, because the source does not state them. No 1.5 relationships are populated.

**Skill-tree metadata (preserved):**
- `fi9`, `en6`, `me27` and `rf1azz` carry wrong names.
- Fireball, Meteor, Elemental Nova and Reaper Form are missing.
- The fixtures keep this metadata unchanged, and identities do not depend on it: `IDENTITY_NOT_NAME` blanks every name field and requires identical identities.

### P15: database migration and PostgreSQL CI foundation

| | |
| --- | --- |
| Status | Done (foundation). Known chain debt is declared, not fixed. |
| Files | `tests/postgres/conftest.py`, `migration_registry.py`, `test_migrations_postgres.py`; `pytest.ini` (marker); `.github/workflows/r2-foundation.yml` (job `postgres-migrations`, `postgres:16` service) |
| Production change | None. No migration file or model was changed. |

**Tests (23).** Every test gets a fresh database, which is dropped afterwards.
- Single head and a complete graph.
- A clean database upgrades to head (`c5d8e2b7a913`).
- Model/schema drift is ratcheted in both directions.
- Foreign-key delete rules match the models.
- FK behaviour: `build_views` cascade with the build; votes block a raw delete.
- Downgrade/upgrade round trip for each of the 16 revisions.
- The known broken downgrade still fails (`CompileError`).
- The lossy downgrade is declared.

**Measured debt** (`migration_registry.py`):
- `3ffd55fa24ac`: the downgrade calls `drop_constraint(None)`, so it is broken (xfail).
- `a1b2c3d4e5f6`: the downgrade rebuilds `passive_nodes`, so it loses data.
- 5 server-default drifts.

**Results.** Locally on PostgreSQL 16: 22 passed, 1 xfailed. Without `FORGE_PG_TEST_URL` the tests are skipped, so the default SQLite suite is unaffected.

**Acceptance:**
- Single head: met.
- Base to head on PostgreSQL: met.
- "Every downgrade works or raises an explicit irreversible error": **partially met.** One downgrade raises a SQLAlchemy `CompileError`, not an explicit irreversible error. Fixing it means editing a migration file, which is left to an explicit later change. The ratchet fails as soon as that is fixed, so the registry must be updated then.

### P16: dangerous fallback certification gate

| | |
| --- | --- |
| Status | Done (ratchet). It counts debt; removing debt belongs to the owning packages. |
| Files | `scripts/fallback_gate/scanner.py`, `gate.py`, `registry.jsonl`, `baseline.json`; `tests/fallback_gate/test_gate.py`; CI job `fallback-gate` |
| Production change | None. The gate is read-only and also runs inside the backend suite. |

**Scanner.** It ports the census extractor exactly. Run against the base tree, it reproduces all 2,217 census candidates, with 0 extra and 0 missing.

**Registry** (`registry.jsonl`, 2,241 entries). Every candidate is matched on a content fingerprint (file, pattern, normalised line), so moving lines is free.

| Classification | Entries |
| --- | --- |
| DANGEROUS_SILENT_FALLBACK | 744 |
| SAFE_PRESENTATION_FALLBACK | 693 |
| EXPLICIT_UNSUPPORTED_STATE | 120 |
| NOT_A_FALLBACK | 684 (665 census exclusions plus 19 reviewed hits in the new package) |

Five census records come from manual patterns the scanner cannot see; they are tracked by their source line. Every dangerous entry records:
- census id, file, line, symbol and pattern;
- data family, owner package and reason;
- replacement requirement (from the R2 replacement rules);
- status: `OPEN`, `REMOVED`, `REPLACED_WITH_EXPLICIT_UNSUPPORTED`, or `PROVEN_SAFE` (which needs a `proof`).

**Gate `check` fails when:**
- there is a new unclassified candidate;
- a dangerous entry no longer matches the code;
- an entry is marked removed but its code is still present;
- an entry is invalid;
- the OPEN count rises for any owner, including when debt moves to another owner;
- the OPEN count falls without `gate.py tighten`, which locks the gain in.

**Annotations.** Inline `# fallback: SAFE_PRESENTATION | EXPLICIT_UNSUPPORTED | NOT_A_FALLBACK — <reason>` annotations are accepted. A dangerous fallback cannot be annotated away.

**Cutover.** `gate.py cutover-check` is the R2-P20 precondition: zero OPEN R2-owned records. Today it fails, as intended, with 675 records.

**New code.** The new package was put through the gate too. Six real silent defaults were found and fixed:
- record containers in `schemas.py`;
- `ability_ref` and `property` in the relationship adapters;
- the trust `families` list, trust `reasons` and `certified_exports` in the importer.

The remaining 19 hits fail closed or are not data reads, and are registered with reasons.

**R2-P16's own six records.** These are in `scripts/build_sprite_map.py`, legacy tooling that writes into the current `data/` authority. They stay OPEN, because changing legacy production tooling is outside the foundation scope.

**Acceptance:**
- The count can only decrease: met.
- The R2-owned count reaches 0 before R2 closes: enforced by `cutover-check` (owners P05–P19 and P18 retirement).

## Metrics

| Metric | Value |
| --- | --- |
| Canonical contracts (executable) | 14 (+ `BUNDLE_LOADS`); 13 contract tests; T-plan: 6 implemented, 8 xfail with owner |
| Canonical foundation tests | 203 collected: 194 passed, 1 skipped (external-bundle hook), 8 xfail (T-plan) |
| Loader negative tests | 69: importer 32 (29 parametrised fail-closed cases, malformed JSON, outside path, real 1.4.6 rejection); store 37 (19 manifest rejections, 8 missing containers, directory/version mismatch, duplicate ids, missing manifest, missing required family, symlink, tampered family, tampered manifest, undeclared file, unsupported schema, CERTIFIED family in an uncertified snapshot) |
| Trust-failure tests | 9: B2 lock; 3 non-consumable states; quarantined never trusted; certified but unmeasured coverage; certified but dangling; certified in an uncertified snapshot; quarantined relationships refused |
| Typed identity types | 16 (no `MasteryId`; mastery is `(class_id, mastery_index)`) |
| Relationship support | 4 cardinalities; ordered/unordered; required/optional; 8 resolution states; multi-prerequisite graphs; allowlist with reasons; cycle detection; 5 concrete relationship types |
| PostgreSQL CI tests | 23 (22 passed, 1 xfail: known broken downgrade) |
| Fallback baseline | 744 dangerous OPEN (575 runtime). 675 R2-owned: 512 for implementation packages, 163 retire with P18. 69 R6. |
| New unclassified fallbacks | 0 |
| Full backend suite | 11,910 passed, 403 skipped, 1 error. The base had 11,680 / 379 / 1, so this is +230 passed (foundation and gate) and +24 skipped (PostgreSQL without a server, external-bundle hook). The error is pre-existing and also on the base: `test_weaver_tree_scaffold` uses a closed SQLite database. This run was before `test_contract_plan.py` (+8 xfail) was added. |
| Type check | `mypy app/canonical_data`: no issues (11 files) |
| Lint | ruff E/F/W/B on all changed Python: clean |

## Exit gate

| # | Condition | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Contracts executable | Yes | `contracts.py` CLI and tests; external-bundle hook |
| 2 | Importer fails closed | Yes | 32 importer negatives; atomic write, no partial bundle |
| 3 | Store cannot mix snapshots | Yes | Single snapshot; directory/version check; `BoundRef` mismatch; no merge API |
| 4 | No legacy fallback | Yes | Static scans; `FOREIGN_SOURCE`; missing data raises |
| 5 | Identities independent of names | Yes | No name constructors; `IDENTITY_NOT_NAME` (with a check on the check) |
| 6 | Mastery identity follows source | Yes | `MasteryRef(class_id, mastery_index)`; no `MasteryId` |
| 7 | Multi-edge graphs | Yes | MANY_TO_MANY ordered prerequisites; real multi-prerequisite fixture nodes |
| 8 | Trust enforceable | Yes | `check_admitted`; B2 constant; 9 trust-failure tests |
| 9 | Mixed patch/snapshot fails | Yes | `MIXED_PATCH` / `MIXED_SNAPSHOT` at import and load |
| 10 | PostgreSQL migration tests in CI | Yes | `r2-foundation.yml` job `postgres-migrations` |
| 11 | Fallback baseline machine-readable | Yes | `registry.jsonl`, `baseline.json`, `gate.py report` |
| 12 | CI prevents debt increase | Yes | `gate.py check` in CI and in the backend suite |
| 13 | No production authority change | Yes | App factory isolation test; no runtime import |
| 14 | Nothing deployed | Yes | No deploy workflow touched; no merge |

## Deferred (needs the current snapshot or an unauthorised package)

- **A real bundle.** It needs an R1 run with a raw snapshot (B7). When one exists, run `importer` and then `contracts` on it with no code changes.
- **Remaining contract tests** (T1, T2, T4 per family, T5, T8, T9, T13, T14): the owning packages.
- **Downgrade fix** for `3ffd55fa24ac`: an explicit migration change.
- **Store wiring, the health check and 503 behaviour:** P14.
- **The reference API trust envelope:** the plan's P09 and P14.
