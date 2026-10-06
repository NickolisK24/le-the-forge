# R2 Database Provenance and Reference Data Plan (R2-08, R2-09)

**Status: design only.** Findings: DB-3, DB-4, DB-5, DRIFT-3, SYS-3, DOC-3, REL-23, REL-16 (affix rows).

## Current state (le-the-forge `9e1356a`, evidence with file:line in R2_CURRENT_CONSUMPTION_GRAPH.md)

- **Builds have no data provenance.**
  - `Build.patch_version` defaults to `"1.2.1"` and `cycle` to `"1.2"` (`models/__init__.py:107-108`, `schemas/__init__.py:90-91`, `build_service.py:67-68`, `buildWorkspace.ts:96-97`).
  - Both fields are free client text; owners can rewrite them (`schemas/__init__.py:132`).
  - The planner omits them, so every new build gets `1.2.1` and is shown "Outdated" against the hard-coded `CURRENT_PATCH = "1.4.3"` (`config.py:44`, `BuildPlannerPage.tsx:472-485`).
  - Imports bypass the schema and discard `_source_code` / `_import_meta` (`import_route.py:603`).
- **Builds reference game data by names and raw ints inside JSON:**
  - class and mastery by name;
  - `skill_name` strings;
  - gear affixes by name;
  - passives as raw node ints.

  There is no foreign key to any reference table.
- **Patch identity disagrees across surfaces:**
  - `1.2.1`: DB default.
  - `1.4.3`: config, `/api/version`, dashboard, seed builds, docs.
  - `"unknown"`: `data/version.json`, `/api/health`, `pipeline.py:467-471`, VersionedLoader, import diagnostics.
  - `1.0.0`: `DATA_VERSION`.

  None is derived from the data.
- **Reference tables are a second, divergent authority:**
  - Render runs only `flask db upgrade`, never seeds (`render.yaml:43`).
  - `flask seed` is insert-only and keyed by name, so it keeps ≤1,104 of 1,228 affixes and never updates.
  - `reseed-affixes` keeps 1,228. Affix ids are DB autoincrement on one read path and JSON slugs on the fallback path (`ref.py:282`).
  - Seeded affix rows lack `class_requirement` and `tags` (REL-23).
  - Empty tables silently fall back to JSON on read paths, while analysis silently loses passive stats.
- **Migrations:** 17 revisions with a single head `c5d8e2b7a913`. They use Postgres-only `::json` defaults and include:
  - a named-FK drop;
  - downgrades that call `drop_constraint(None)`;
  - a lossy passive-node rebuild.

  CI runs `create_all` on SQLite and never `flask db upgrade` (DB-5).
- **Trust is never read at runtime.** `upstream_trust` is written by the sync only, and `data/version.json` predates it.

## R2-09 decision: reference data comes from immutable canonical bundles (option B)

| Option | Correctness | Operational simplicity | Verdict |
| --- | --- | --- | --- |
| A. DB-seeded reference tables | Two authorities (JSON and rows) that already diverge. Seeding is a deploy step that Render skips. Autoincrement ids are not game ids. Reseeds prune or renumber. | Needs seed orchestration, idempotent upserts, and drift checks on every deploy | Rejected |
| **B. Immutable canonical bundles loaded in memory** | One authority: the bundle in `data/canonical/<data_version>/`, hash-verified at startup. Ids are game ids. Nothing to drift. | Startup load only. The bundle ships with the code commit, so deploy = code. | **Chosen** |
| C. DB populated from the bundle at startup (cache) | Same authority as B, but adds a copy | Extra moving part with no consumer that needs SQL over reference data | Not needed now |

Consequences:
- **Retired tables:** `affix_defs`, `passive_nodes` and `item_types` stop being authorities. Their readers switch to `CanonicalDataStore`. The tables are dropped in R2-P18, after one release in which they are unused (rollback safety).
- **Retired commands:** `flask seed`, `reseed-affixes` and `seed-passives` are retired. `seed-builds` (demo builds) stays as a dev-only command, with demo builds stamped by the server like any other build.
- **New `datasets` table:** this is not a copy of game data. One row per `data_version` the server has ever loaded. It gives persisted builds a referential anchor:

  ```
  datasets(
    data_version        TEXT PRIMARY KEY,         -- from CanonicalDataManifest
    manifest_hash       TEXT NOT NULL,
    game_version        TEXT, game_build TEXT,    -- NULL only for LEGACY_UNKNOWN
    game_assembly_sha256 TEXT,
    snapshot_id         TEXT,
    canonical_schema    TEXT NOT NULL,            -- forge_canonical_data_manifest/1
    status              TEXT NOT NULL,            -- ACTIVE | RETAINED | ARCHIVED | LEGACY_UNKNOWN
    first_loaded_at     TIMESTAMP NOT NULL
  )
  ```

  - **Startup upsert:** at startup the server inserts its active dataset row if absent. This is idempotent and deterministic from the manifest.
  - **Legacy sentinel:** the sentinel row `LEGACY_UNKNOWN` is inserted by migration. All of its identity columns are NULL; they are never fabricated.

## Deterministic initialization and rebuild

1. **Startup (every process):** `CanonicalDataStore.load(CURRENT)` applies checks L1–L11 (R2_CANONICAL_CONSUMPTION_CONTRACT.md).
   - **On failure:** game-data endpoints return `503 DATASET_UNAVAILABLE`, and `/api/health` reports `dataset: {status: REJECTED, reason}`. Render's health check fails, so a bad bundle never takes traffic. There is no JSON or legacy fallback.
2. **Dataset registration:** upsert the `datasets` row for the active `data_version`. This is the only DB write derived from game data.
3. **Deploy:** `render.yaml` keeps `flask db upgrade` as `preDeployCommand`. There is no seed step, because there is nothing to seed. Entrypoints stop masking failures (`entrypoint.sh` `2>/dev/null || echo`).
4. **Rebuild from scratch:** an empty DB plus `flask db upgrade` plus process start gives the complete system. Reference data is never missing, because it is never in the DB.
5. **CI:** a Postgres service container runs `flask db upgrade` from base to head, then `downgrade` / `upgrade` for every reversible revision. Irreversible revisions must declare it explicitly and raise. The SQLite `create_all` path remains for unit tests only (DB-5, R2-P15).

## R2-08: server-controlled build provenance

### Schema changes (one migration, R2-P13)

| Column | Type | Set by | Notes |
| --- | --- | --- | --- |
| `data_version` | TEXT NOT NULL FK → `datasets.data_version` | **Server**, at create, update or import: the active dataset | Never accepted from the request; payload values are ignored and logged |
| `provenance_status` | TEXT NOT NULL | Server | `VALIDATED` (all references resolved under `data_version` at save), `LEGACY_UNKNOWN`, `REQUIRES_REVALIDATION`, `INVALID_UNDER_CURRENT` |
| `reference_scheme` | TEXT NOT NULL | Server | Identity scheme of the stored references, for example `forge_build_refs/1` (passives `(class_id,node_id)`, skills `ability_id` + `tree_id`, affixes `affix_id`, items `(base_type_id,sub_type_id)`, uniques `unique_id`) or `legacy_names/0` |
| `source` | TEXT NOT NULL | Server | `planner`, `lastepochtools`, `maxroll`, `seed` |
| `source_ref` | TEXT NULL | Server, from the importer | External build code or URL (R4 consumes it) |
| `importer_version` | TEXT NULL | Server | |
| `declared_patch` | TEXT NULL | Renamed from `patch_version` | Kept verbatim for history, labelled *client-declared, unverified*, never used for logic |
| `cycle` | dropped as an input | — | Derived for display from `datasets` when known; otherwise absent |

`game_patch`, `game_build`, `canonical_schema_version` and `snapshot_id` live on `datasets` and are joined through `data_version`. They are stored once, never per build, and never client-supplied.

### Write path

- **Create and import:** the server stamps `data_version = active` and validates every reference through `CanonicalDataStore`.
  - **All resolve:** `provenance_status = VALIDATED`, `reference_scheme = forge_build_refs/1`.
  - **Any fails:** the request is rejected with the list of unresolved references. Importers return the same list to the user (R4 handles importer UX). Nothing is saved with silently dropped references. Today PATCH and import bypass validation (`builds.py:200-216`, `import_route.py:603`); R2 routes both through the same validator.
- **Update:** re-validates under the active dataset and re-stamps `data_version`. An update can therefore never mix references from two datasets.

### Existing builds: LEGACY_UNKNOWN (no fabrication)

The migration sets these values on every existing row:
- `data_version = 'LEGACY_UNKNOWN'`;
- `provenance_status = 'LEGACY_UNKNOWN'`;
- `reference_scheme = 'legacy_names/0'`;
- `source = 'planner'` if unknown, otherwise from evidence in the row (`ImportFailure.partial_data.slug` link where present);
- `declared_patch = old patch_version`.

**It never writes a historical `data_version`.** The 1.2.1, 1.4.3 or unknown string a build carries today says nothing about which data interpreted it.

Degraded behaviour for `LEGACY_UNKNOWN` builds:

| Operation | Behaviour |
| --- | --- |
| View | Allowed, with a visible banner: "Saved before data versioning; original game data unknown. Shown with data `<active data_version>`." |
| Reference resolution | Done under the active dataset by `LegacyReferenceResolver`. It is explicit, never silent. |
| Passive raw ints | Accepted as `(class_id, node_id)` when the node exists in the active tree. Raw ints are the source `SkillTreeNode.id`. |
| Skill names | Resolved to `ability_id` only when the name is unique among the class's abilities. Otherwise `AMBIGUOUS` (REL-6: 184 skills collapse to 161 names). |
| Gear affix names | Resolved only when exactly one `affix_id` has that name for that item type. 98 names are duplicated, so the rest are `AMBIGUOUS`. |
| Result | The resolver writes nothing. It returns `resolved` / `ambiguous` / `missing` lists. |
| Calculations | Run only if every reference resolved. Output is labelled `interpreted_under: <active data_version>, provenance: LEGACY_UNKNOWN`. With any ambiguous or missing reference: `UNSUPPORTED_DATA` listing them; never a partial DPS with zeros. |
| Save by owner | The owner confirms the resolved references. The build is re-stamped `VALIDATED` under the active dataset, with `reference_scheme = forge_build_refs/1`. |
| Meta analytics, public listing | `LEGACY_UNKNOWN` builds are grouped separately and never counted as current-patch builds |

### When the active dataset changes (new patch)

A build stamped with an older `data_version` is `REQUIRES_REVALIDATION`:
- references are re-resolved by id under the new dataset;
- ids that vanished or changed meaning are reported (patch diff, R1.10);
- calculations follow the same rules as above.

Stamping a new `data_version` on a build requires an owner save. The server never silently migrates it.

### Craft sessions and steps

They store affixes by name today (`models:208,233`). R2 stores `affix_id` and `(affix_id, property_index)` rolls with `data_version`. Existing sessions are `LEGACY_UNKNOWN`, read-only.

## Version surfaces after R2 (one source)

| Surface | Today | After R2 |
| --- | --- | --- |
| `/api/version` `current_patch`, `season`, `data_version` | Hard-coded 1.4.3 / 4 / 1.0.0 | From the active manifest (`game_version`, `build_id`, `data_version`). Season derived only if the manifest carries it, otherwise omitted. |
| `/api/health` | `patch_version: unknown` | `dataset: {data_version, status, trust_summary}` |
| Build banner "Outdated" | Compares client text | Compares `build.data_version` with the active one |
| Dashboard hero | Fallback 1.4.3 / season 4 | From `/api/version`. On failure: explicit "version unavailable", never a hard-coded patch. |
| `pipeline.data_version`, VersionedLoader, import diagnostics `data_version` / `extractor_version` | `unknown` | From the manifest. VersionedLoader is retired. |
| README / KNOWN_LIMITATIONS / deployment docs (DOC-3) | Claim 1.4.3 from `version.json` | Generated "data version" section, or a pointer to `/api/version`; no hand-written patch claims |
