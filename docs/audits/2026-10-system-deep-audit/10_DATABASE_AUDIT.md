# 10 — Database / Data Model Audit (Phase 8)

Audit date: 2026-10-06. Code: `HEAD 1efcef7` (2026-05-14). Audit only — no repo code, migrations, or production systems were changed.

## 1. Method and commands

All scratch work ran under the session scratchpad (`$S`), never in the repo or against production.

| Step | Command (abbreviated) | Result |
|---|---|---|
| venv | `python3 -m venv $S/venv && $S/venv/bin/pip install -r backend/requirements.txt` | OK. SQLAlchemy resolved to **2.1.3**, alembic 1.20.0 (both unpinned, transitive) |
| Local Postgres | `initdb`/`pg_ctl` from `/usr/lib/postgresql/16/bin` | **Not possible**: the scratchpad's parent dirs are mode 700 (root), so the `postgres` user cannot reach them, and the environment policy blocked changing those permissions. No online Postgres test was run |
| Migration graph | `flask db heads`, `flask db history` (`DATABASE_URL=postgresql+psycopg2://x:y@127.0.0.1:1/none`) | 1 head (`dd1840cac963`), 15 revisions, 1 branchpoint + 1 mergepoint |
| Offline Postgres DDL | `flask db upgrade --sql > $S/upgrade_offline_pg.sql` | rc=0, 350 lines. The full chain renders as valid Postgres DDL |
| Online replay (SQLite) | copied `backend/migrations` to `$S/migrations_copy`, removed the Postgres-only `'[]'::json` casts, and skipped the `3ffd55fa24ac` FK rename (a no-op on PG). Then `flask db upgrade -d $S/migrations_copy` with `DATABASE_URL=sqlite:///$S/mig.sqlite` | Chain applies cleanly with those 2 patches. **The unmodified chain fails on SQLite** (`ValueError: No such constraint: 'build_skills_build_id_fkey'`) |
| Model↔migration drift | `alembic.autogenerate.compare_metadata(..., compare_type=True, compare_server_default=True)` against the migrated SQLite DB (`$S/compare.py`) | **5 diffs, all `modify_default`** (server defaults in DB, not in models). No table, column, nullability, index, FK, or unique drift |
| Delete-cascade test | `$S/del_test.py`: create a Build, add a BuildView, call `build_service.delete_build` (SQLite with `PRAGMA foreign_keys=ON`) | **`IntegrityError: NOT NULL constraint failed: build_views.build_id`** |
| Payload tests | `$S/poison.py` (test client, testing config, in-memory SQLite) | see §6 |

## 2. Headline numbers

| Item | Count |
|---|---|
| ORM models / tables (excluding `alembic_version`) | **11**: users, builds, build_skills, votes, craft_sessions, craft_steps, item_types, affix_defs, passive_nodes, import_failures, build_views |
| Tables ever created and later dropped | 2 (`loot_filters`, `filter_rules`, dropped in `3ffd55fa24ac`) |
| Migration files | **15** (`backend/migrations/versions/*.py`) |
| Heads | **1** (`dd1840cac963`) |
| Branch / merge points | 1 branch (`a1b2c3d4e5f6` → `b2f8a3d1c7e9` and `f8953bcaab80`), merged by `e2f3a4b5c6d1` |
| `down_revision` inconsistencies | 0 (every `down_revision` resolves; `flask db history` renders the full graph) |
| Structural drift (model vs migrated schema) | 0 |
| Server-default drift | 5 (`import_failures.missing_fields/created_at/updated_at`, `passive_nodes.requires`, `users.is_admin`) |
| JSON columns | 14 (all `JSON`, none `JSONB`; none carry a schema version) |
| CHECK constraints | 0 |
| Enum types | 0 (all enumerations are free `String` columns) |
| Soft-delete columns | 0 |
| FKs with `ON DELETE` behaviour | 0 (all default `NO ACTION`) |

Migration chain (linear except the branch/merge):

```
cf57d3c33180 initial → 3ffd55fa24ac drop loot filters → 8d9b7a5c2e11 affix metadata → b4c1f0f6d2aa widen
→ e07407b85e20 widen → 93e06c1a641f widen → 21bc975a3016 craft_steps.affixes_before
→ f1a2b3c4d5e6 drop instability/fracture → a1b2c3d4e5f6 DROP+RECREATE passive_nodes (string ids)
   ├─ b2f8a3d1c7e9 users.is_admin + import_failures
   └─ f8953bcaab80 FK indexes → d1e2f3a4b5c6 build_views + builds.last_viewed_at
→ e2f3a4b5c6d1 merge → 654f2ebcd332 builds.blessings → dd1840cac963 passive_nodes.requires (HEAD)
```

## 3. Table inventory (final schema = models in `backend/app/models/__init__.py`)

| Table | PK | Key columns / types | Nullability notes | Indexes / uniques | FKs | JSON blobs | Timestamps | Owner |
|---|---|---|---|---|---|---|---|---|
| users (`:52`) | `id` String(36) uuid4 | discord_id S64, username S64, discriminator S8, avatar_url S512, is_active Bool, is_admin Bool | discriminator/avatar nullable | `ix_users_discord_id` UNIQUE | — | — | created/updated (ORM-side) | self |
| builds (`:76`) | `id` S36 | slug S64, name S120, description Text, character_class S32, mastery S32, level SmallInt, patch_version S16 (default "1.2.1"), cycle S16 (default "1.2"), tier S1, vote_count Int, view_count Int, last_viewed_at, is_public, is_ssf/is_hc/is_ladder_viable/is_budget | author_id nullable (anonymous builds) | `ix_builds_slug` UNIQUE, `ix_builds_author_id` | author_id→users | passive_tree, gear, blessings | created/updated, last_viewed_at | author_id or none |
| build_skills (`:140`) | `id` S36 | slot SmallInt, skill_name S64, points_allocated | — | `uq_build_skill_slot(build_id,slot)` | build_id→builds | spec_tree | none | via build |
| votes (`:165`) | `id` S36 | direction SmallInt | — | `uq_user_build_vote(user_id,build_id)`, `ix_votes_build_id` | user_id→users, build_id→builds | — | created/updated | user |
| craft_sessions (`:183`) | `id` S36 | slug S64, item_type S32, item_name S120, item_level, rarity S16, forge_potential | user_id nullable | `ix_craft_sessions_slug` UNIQUE, `ix_craft_sessions_user_id` | user_id→users | affixes | created/updated | user_id or none |
| craft_steps (`:213`) | `id` S36 | step_number, timestamp, action S32, affix_name S64, tier_before/after, roll Float, outcome S16, fp_before/after | — | `ix_craft_steps_session_id` | session_id→craft_sessions | affixes_before | timestamp | via session |
| item_types (`:249`) | `id` Int autoinc | name S64, category S32, base_implicit S120 | — | UNIQUE(name) | — | — | none | reference |
| affix_defs (`:260`) | `id` Int autoinc | name S256, affix_type S16, stat_key S256, class_requirement S128 | — | **no unique on name** (seed dedups by query) | — | tier_ranges, applicable_types, tags | none | reference |
| passive_nodes (`:281`) | `id` S16 (namespaced, e.g. `ac_0`) | raw_node_id Int, character_class, mastery, mastery_index, mastery_requirement, name S64, node_type S16, x, y, max_points, ability_granted, icon | — | PK only (no index on character_class, though `simulate.py:76` filters on it) | — | connections, requires, stats | none | reference |
| import_failures (`:322`) | `id` S36 | source S32, raw_url S2048, error_message S1024 | user_id nullable | **none** (no index on user_id or created_at, though the admin list orders by created_at) | user_id→users | missing_fields, partial_data | created/updated (server default now()) | user_id or none |
| build_views (`:345`) | `id` S36 | viewed_at, viewer_ip_hash S64 (unsalted SHA-256) | — | `ix_build_views_build_id` | build_id→builds | — | viewed_at | via build |

### JSON blob contents (from model comments and services; **no blob carries a schema/version marker**)

| Column | Shape (documented) | Enforced by |
|---|---|---|
| builds.passive_tree | list of node ids; **mixed legacy integers and namespaced strings** (`schemas/__init__.py:80-82`, `routes/builds.py:142-155` skips integer ids) | `fields.List(fields.Raw())`. Integers are never validated |
| builds.gear | list of `{slot, item_name, rarity, affixes:[...]}` | `fields.List(fields.Dict())`. Inner shape unvalidated |
| builds.blessings | list of `{timeline_id, blessing_id, is_grand, value}` | `fields.List(fields.Dict())` |
| build_skills.spec_tree | list of allocated node ids/points within the skill tree | none at create; `skills.py` PATCH rewrites it |
| craft_sessions.affixes / craft_steps.affixes_before | `[{name, tier, sealed}]` | service layer |
| affix_defs.tier_ranges/applicable_types/tags | `{"1":[min,max],...}` / list / list | seed command |
| passive_nodes.connections/requires/stats | id lists / `[{parent_id, points}]` / `[{key,value}]` | seed command |
| import_failures.missing_fields/partial_data | list / free dict | none |

## 4. Provenance / versioning (Phase 8 focus)

* `builds.patch_version` is the only provenance field. It is **client-supplied free text**: `BuildCreateSchema.patch_version = fields.Str(load_default="1.2.1")` (`schemas/__init__.py:90`), with no length validation (the column is `String(16)`). The frontend workspace default is also `"1.2.1"` (`frontend/src/store/buildWorkspace.ts:96`). Meanwhile the server tracks `CURRENT_PATCH=1.4.3` (`config.py:27`), and the seeded demo builds use `"1.4.3"` (`utils/cli.py:146`). New builds and all imported builds (the importer never sets it) are stamped `1.2.1` whatever data they were built with.
* `builds.cycle` defaults to `"1.2"`.
* There is **no data-bundle / game-data version** stored on builds, build_skills, craft sessions, or import_failures. The runtime data version is `'unknown'` anyway. `GameDataPipeline._detect_version` reads `_version` from `affixes.json`, which is a bare list (`pipeline.py:467-471`). `data/version.json` has `"patch_version": "unknown"`. `/api/health` returns `patch_version: unknown`. `/api/version` returns the env default `data_version: 1.0.0`.
* `passive_tree` stores raw node ids. Migration `a1b2c3d4e5f6` **dropped and recreated `passive_nodes`** (Integer ids → String ids). Builds saved before then hold integer ids that no longer match any PK. The create route explicitly skips validating them (`routes/builds.py:149-151`). Later, `flask seed-passives` **deletes** passive_nodes rows not present in the current JSON (`utils/cli.py:256-266`). Saved builds referencing those ids are not updated or flagged, and there is no FK from JSON ids. **The meaning of a saved passive tree cannot be reconstructed from the schema alone.** It depends on whichever `passives.json` was seeded at that time, and that version is not recorded.
* `affix_defs` (DB, seeded once and skip-if-name-exists, `utils/cli.py:73-97`) and `data/items/affixes.json` (read by the runtime pipeline) are **two sources of truth** for affix definitions. `/api/ref/affixes` serves the DB copy (`routes/ref.py:230`); simulations use the JSON copy. Re-running `flask seed` never updates existing rows.

## 5. Reconstructability of a clean database

* **Postgres:** the offline render (`flask db upgrade --sql`) is complete and deterministic: 350 lines, a single head, no data-dependent branching in any upgrade. Online application to an empty PG 15 was **UNKNOWN / not executed** (no runnable Postgres in this environment).
* **Non-Postgres:** the chain is Postgres-only (`'[]'::json` casts in `8d9b7a5c2e11:24` and `654f2ebcd332:25`; a named FK drop in `3ffd55fa24ac:26-32`). Tests use `db.create_all()` on SQLite (`config.py:139`), and `.github/workflows/ci.yml` has no Postgres service and no `flask db upgrade` step. **The migration chain is not exercised by CI.**
* **Schema only, not data.** On Render, `preDeployCommand` runs only `flask db upgrade` (`render.yaml`). The seed steps (`flask seed`, `seed-passives`) exist only in `backend/entrypoint.sh` (the Docker path). A rebuilt production DB would have empty `passive_nodes`/`affix_defs`/`item_types`. `create_build` validates string passive ids against `passive_nodes` (`routes/builds.py:142-155`), so every planner save with namespaced ids would be rejected until someone seeds manually. Whether production was seeded manually: **UNKNOWN**.
* **Downgrades are not reliable:** `3ffd55fa24ac.downgrade` calls `drop_constraint(None, ...)`, which fails. `f1a2b3c4d5e6.downgrade` adds NOT NULL columns without a server default (fails on non-empty tables). `a1b2c3d4e5f6.downgrade` drops passive data. Rollback must be done by restoring the DB, not with `flask db downgrade`.
* **Driver drift:** `SQLAlchemy` is not pinned. A fresh `pip install -r requirements.txt` resolved 2.1.3, whose default `postgresql://` dialect is **psycopg (v3)**, while only `psycopg2-binary` is installed. Verified: `create_app` raised `ModuleNotFoundError: No module named 'psycopg'` with a plain `postgresql://` URL. Render builds with `pip install -r requirements.txt` on every deploy and injects a `postgresql://...` connection string, so the next deploy would likely fail at `flask db upgrade` (preDeploy) before serving. Whether the currently running production build resolved SQLAlchemy 2.0.x or 2.1.x: **UNKNOWN**.

## 6. Integrity, constraints and runtime data behaviour

| # | Observation | Evidence |
|---|---|---|
| a | **Deleting any viewed build fails.** `BuildView.build` uses a plain `backref="views"` (no cascade, no `ON DELETE`). On `session.delete(build)` the ORM tries to null `build_views.build_id` (NOT NULL), which raises IntegrityError and returns 500. Every build opened in the UI gets a BuildView (`POST /api/builds/<slug>/view`), so in practice most builds cannot be deleted | `models/__init__.py:353-360`; `$S/del_test.py` output `IntegrityError ... build_views.build_id` |
| b | `import_failures.user_id → users` and all other FKs have no `ON DELETE`. There is no user-deletion path at all (no endpoint or CLI) | grep `delete` in routes/cli |
| c | No CHECK constraints: `votes.direction`, `builds.tier`, `builds.level`, `craft_steps.outcome`, `affix_defs.affix_type`, `passive_nodes.node_type` are free values enforced (if at all) only by marshmallow | models |
| d | Over-length strings: `patch_version` (S16), `cycle` (S16) and `mastery` have no length validation. A 40-char `patch_version` was accepted (201) on SQLite. On Postgres it raises `StringDataRightTruncation` → 500 | `$S/poison.py` |
| e | Malformed JSON accepted and later breaks aggregate readers: an anonymous `POST /api/builds` with `gear:[{"affixes":["not-a-dict"]}]` returned 201, and on the next cache miss `GET /api/meta/snapshot` returned **500 for every visitor** (`'str' object has no attribute 'get'`, `meta_analytics_service.py:85-90`) | `$S/poison.py` output `snapshot after 500` |
| f | Counter lost updates: `vote_count` and `view_count` are Python read-modify-write (`build_service.py:88-90,196-210`, `views.py:43`), not `UPDATE ... SET x = x + 1`. Concurrent votes/views can be lost. `tier` derives from `vote_count` | code |
| g | Slug race: `_unique_slug` checks then inserts (`build_service.py:32-37`). Concurrent same-name creates can hit the unique index and return 500. Slugs are derived from the build name (predictable). See API audit for private-build exposure | code |
| h | Indexing gaps: no index on `passive_nodes.character_class` (filtered on every `/api/simulate/stats|build`), `import_failures.created_at`, `build_views.viewed_at` (time-series reads), `builds.is_public`/`vote_count`/`created_at` (list sorting). Impact at current scale: UNKNOWN (row counts unknown) | models |
| i | Unbounded growth: `build_views` (one row per IP per build per hour, no retention), `import_failures` (anonymous writers via `/api/import/let/json`, no retention), and `craft_sessions` (anonymous creation) | routes |
| j | `viewer_ip_hash` is an unsalted SHA-256 of the IPv4 address, which is reversible by brute force over 2^32. If Render's proxy address is what `remote_addr` sees (no ProxyFix, see API audit), all rows hash the same value | `views.py:20-22,34` |
| k | `users.is_active` exists but is never checked by `login_required`/`get_current_user` | `utils/auth.py:78-94` |
| l | `build_skills.slot` comment says 0-4, but the service writes 1-5 (`build_service.py:69,108`) | code |
| m | Ownership model: builds/craft sessions with `author_id/user_id = NULL` are "anonymous" and **mutable by anyone** (see API audit). There is no claim/transfer flow and no soft delete | routes |
| n | Auth/session state: stateless JWT only (no session or token table, no revocation). JWT lifetime 3600 s (`config.py:9-11`) | — |
| o | Connection budget: production pool 10 + 20 overflow per process × 4 gunicorn workers = up to 120 connections, plus preDeploy and CLI. The Render Postgres starter connection limit is **UNKNOWN** | `config.py:86-91`, `render.yaml` |

## 7. Findings summary

| ID | Sev | Title |
|---|---|---|
| DB-1 | P1 | Build delete fails (500) for any build with a BuildView row (missing cascade) |
| DB-2 | P1 | Unpinned SQLAlchemy resolves to 2.1 → `postgresql://` needs psycopg3 (not installed) → app/migrations fail on fresh build |
| DB-3 | P1 | Builds carry no data-bundle version; `patch_version` is client free text defaulting to stale "1.2.1"; passive ids reinterpreted/pruned across reseeds |
| DB-4 | P2 | Render deploy runs migrations only; reference tables (passive_nodes/affix_defs/item_types) need manual seeding; create_build depends on them |
| DB-5 | P2 | Migration chain Postgres-only and untested in CI; downgrades broken |
| DB-6 | P2 | Unvalidated JSON blobs persisted; a single malformed anonymous build 500s `/api/meta/snapshot` sitewide |
| DB-7 | P2 | Over-length strings (patch_version/cycle/mastery) reach DB → 500 on Postgres |
| DB-8 | P3 | Counter lost updates (vote_count/view_count), slug check-then-insert race |
| DB-9 | P3 | Dual affix source of truth (affix_defs table vs affixes.json); seed never updates |
| DB-10 | P3 | No CHECK/enum constraints, no FK ON DELETE, missing indexes, unbounded build_views/import_failures growth, server-default drift (5) |
| DB-11 | P3 | `users.is_active` never enforced; weak IP pseudonymisation |

## 8. UNKNOWNs

* Production row counts, real data, whether prod reference tables are seeded, the production `alembic_version` value.
* Which SQLAlchemy version the currently running production image installed.
* Online behaviour of the chain on real Postgres 15 (only the offline SQL render was produced).
* Render Postgres connection limit and plan memory.

## 9. What this does NOT prove

* It does not prove the production schema equals the migration head. Production was not contacted.
* The SQLite-based drift comparison cannot detect Postgres-specific type differences (e.g. `JSON` vs `JSONB`, timestamp precision). It covers tables, columns, nullability, indexes, uniques and FKs.
* The BuildView delete failure was reproduced on SQLite with FK enforcement. On Postgres the same ORM behaviour (null-out of a NOT NULL column) is expected but was not executed.
* It does not quantify how many saved builds hold stale or legacy passive ids. That needs production data.
