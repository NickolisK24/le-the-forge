# 18 — Dead Code and Architectural Drift

Audit date: 2026-10-06
Scope: Phase 16. Abandoned systems, duplicate implementations, old extractors, legacy schemas, compatibility shims, unused endpoints/components, obsolete flags, old generated data, and TODO markers.
Mode: read-only classification. Nothing was deleted or changed. The terms "dead", "test-only" and "orphan" below are classifications, not removal decisions.

---

## 1. Summary

- The backend has **31 top-level Python packages** besides `tests`, `scripts` and `migrations`, covering **553 non-test modules**. Static import-graph analysis from the runtime entry points (`wsgi.py`, `app`, `config`) gives:
  - **283 modules runtime-reachable**
  - **237 modules imported only by tests or scripts** (192 tests-only, 45 tests plus scripts)
  - **33 modules imported by nothing**
- There are **at least five combat/fight simulator implementations**. Only one path is wired to the HTTP API: `simulation_service` → `app/engines/{stat_engine, combat_engine, defense_engine}` plus `builds/build_stats_engine` plus `encounter/`. The other four are test-only or orphaned.
- There are **at least four affix data paths**: legacy `data/items/affixes.json` (read directly by four or more modules), the Forge-safe export (env path), the Forge-safe bundle (env path), and v2 bundles in `docs/generated`. Feature flags select between them, and every flag defaults to off, so legacy is authoritative in production. The parallel paths make it ambiguous which one is canonical.
- `/monte-carlo` is a routed frontend page that **produces mock, unseeded `Math.random` results client-side** while presenting itself as a stochastic damage simulation. Meanwhile the backend Monte Carlo package (`backend/simulation`, 17 modules) is fully orphaned.
- Code markers are almost unused: **1 TODO, 0 FIXME/XXX/HACK** across backend, scripts and frontend source. Debt lives in Markdown docs instead: 9 root `.md` files and 43 entries in `docs/`.

---

## 2. Method and commands

```bash
# module-level import graph (AST; absolute and relative imports; lazy in-function imports included)
python3 scratch/modgraph.py scratch/mod_class.json      # roots: wsgi, app, config; tests/*; scripts/*
python3 scratch/imports.py  scratch/import_graph.json   # package-level edges
grep -rn "importlib\|__import__" backend/app             # 0 hits -> no dynamic imports to miss
grep -n "register_blueprint" backend/app/__init__.py      # 28 blueprints, all route files registered
# generated-file references
for f in docs/generated/*; do grep -rl "<stem>" backend/app backend/data frontend/src | backend/scripts scripts | backend/tests; done
# frontend
grep -rlw <Name> frontend/src --include=*.ts --include=*.tsx
# markers
grep -rnwE "TODO|FIXME|XXX|HACK" backend scripts frontend/src electron
```

Limitations of the method: static AST only. "Runtime-reachable" means importable from the app's entry points, **not** that the code executes on a request path. String-based dispatch, `getattr` plugin patterns and subprocess calls are not modeled.

---

## 3. Backend package classification (module level)

| Package | Runtime | Tests/scripts only | Unreferenced | Classification |
|---|---|---|---|---|
| `app` | 177 | 74 | 5 | Core. 74 modules are diagnostic or experimental and test-only (section 4) |
| `bis` | 16 | 13 | 0 | Partly live (`/api/bis`) |
| `builds` | 6 | 2 | 0 | Live (simulation_service, optimize) |
| `encounter` | 11 | 1 | 0 | Live (simulation_service boss encounter) |
| `rotation` | 9 | 2 | 0 | Live (`/api/simulate` rotation) |
| `optimization` | 10 | 0 | 0 | Live (`/api/optimize`) |
| `targets` | 7 | 1 | 0 | Live (multi_target) |
| `data` | 18 | 4 | 0 | Live (forge-safe loaders, VersionedLoader) |
| `conditions`, `modifiers`, `state`, `events`, `skills`, `damage` | 4/4/3/2/3/2 | 1/0/3/0/0/2 | 0 | Live via conditional and multi-target routes |
| `metrics`, `services`, `debug` | 2/2/2 | 2/6/7 | 1/1/1 | Mostly test-only |
| `crafting` | 3 | 20 | 0 | **Parallel crafting stack.** Only `crafting.models.craft_state` is reachable (via `bis`). Runtime crafting is `app/engines/craft_engine.py` and `fp_engine.py` |
| `buffs` | 0 | 10 | 0 | **Test-only system** |
| `movement` | 0 | 22 | 0 | **Test-only system** (pathfinding, kiting, behaviours) |
| `spatial` | 0 | 12 | 0 | **Test-only system** |
| `projectiles` | 0 | 6 | 0 | **Test-only system** |
| `status` | 0 | 5 | 0 | **Test-only system** |
| `visualization` | 0 | 17 | 0 | **Test-only system** |
| `integration` | 0 | 15 | 4 | **Test-only plus orphan** (external API, share links, `import/build_import_parser` unreferenced) |
| `build` (singular) | 0 | 7 | 0 | **Test-only.** It duplicates `builds` (plural: `gear_aggregator`, `passive_aggregator`, `rotation_engine`) |
| `stats` | 0 | 2 | 0 | **Test-only** (`stat_data_integration`) |
| `combat` | 0 | 3 | 4 | **Test-only plus orphan** (`combat/crit/critical_engine`, `combat/proc/proc_resolver` unreferenced) |
| `simulation` | 0 | 0 | **17** | **Fully orphaned** Monte Carlo stack (runner, parallel executor, seed manager, confidence intervals, result store) |

Non-Python items inside `backend/`:
- `backend/src/constants/*.ts` (14 TS files) is the frontend's `@constants` alias (`frontend/vite.config.ts:34`, `frontend/tsconfig.json:26-27`, mounted read-only in `docker-compose.yml:71`). It is mirrored in Python by `backend/app/constants/` (`__init__.py:3`: "Mirrors backend/src/constants/"). That is **two hand-synchronized copies of game constants**, plus `frontend/src/constants/` (4 more files).
- `backend/error_log.txt` (74 bytes, tracked since `c3324f9` 2026-04-12) contains a single Windows venv error line: `../.venv/Scripts/python: No such file or directory`. It is a stale artifact.

---

## 4. Duplicate implementations

### 4.1 Combat / fight simulation
| Implementation | File | Reachability | Self-description |
|---|---|---|---|
| **Runtime path** | `app/services/simulation_service.py:10-15` → `app/engines/stat_engine.py`, `combat_engine.py`, `defense_engine.py`, `optimization_engine.py`; lazy `builds.build_stats_engine` (`:313-314`), `encounter.*` (`:343-348`) | Runtime (`/api/simulate`, `/api/builds/*`) | Authoritative by wiring |
| Monte Carlo combat simulator "Upgrade 2" | `app/engines/combat_simulator.py` | Tests only | "Simulates real combat behavior via seeded Monte Carlo" |
| Deterministic tick combat simulator | `app/combat/combat_simulator.py` (+ `combat_scenario.py`) | Tests only | "deterministic time-based execution loop" |
| "Realistic Fight Simulation (Step 10)" | `app/domain/fight_simulator.py` plus `combat_timeline.py`, `full_combat_loop.py`, `timeline.py`, `enemy_behavior.py` | Tests and `backend/scripts/validate_simulation.py` only | top-level `simulate_fight()` |
| Hit-resolution / crit / proc engines | `backend/combat/*` | Tests only (crit/proc unreferenced) | — |
| Monte Carlo framework | `backend/simulation/*` (17 modules) plus `services/monte_carlo_integration.py`, `debug/monte_carlo_logger.py`, `metrics/statistical_metrics.py` | **Nothing** | — |
| Frontend Monte Carlo | `frontend/src/pages/MonteCarloPage.tsx:6,31-32,49-80` (route `App.tsx:245`) | Routed. No nav link found | "Generates mock results client-side using a Box-Muller normal approximation". Unseeded `Math.random` |

Ambiguity: five non-runtime simulators each claim to be the "full", "realistic" or "deterministic" simulator. A contributor reading `app/engines/combat_simulator.py` (which sits next to the live `combat_engine.py` in the same directory) has no in-code signal that it is unused.

### 4.2 Stat engines
| Engine | File | Reachability |
|---|---|---|
| `BuildStats` / stat engine | `app/engines/stat_engine.py` | Runtime |
| Stat resolution pipeline | `app/engines/stat_resolution_pipeline.py` | Runtime |
| `BuildStatsEngine` | `builds/build_stats_engine.py` | Runtime (lazy, simulation_service `:313`) |
| Stat calculator | `app/domain/calculators/stat_calculator.py` | Runtime |
| Conditional/derived stats | `app/stats/*` | Runtime |
| Gear/passive aggregators | `build/gear_aggregator.py`, `build/passive_aggregator.py` | Tests only |
| Stat data integration | `stats/stat_data_integration.py` | Tests only |
| v2 stat registry / modifier dry run | `app/normalization/v2/stat_registry.py`, `app/planner_adapters/v2/stat_modifier_dry_run.py` | Registry runtime-importable. Planner adapter tests/scripts only |

At least **four reachable stat-aggregation code paths** exist (stat_engine, stat_resolution_pipeline, build_stats_engine, stat_calculator). Which one is canonical for a given endpoint is not documented in code.

### 4.3 Affix data loaders
| Path | Source file | Reader(s) | Default state |
|---|---|---|---|
| Legacy | `data/items/affixes.json` | `app/engines/affix_engine.py:30`, `app/game_data/pipeline.py:45` → `AffixRegistry`, `app/engines/stat_engine.py:398`, `app/services/importers/lastepochtools_importer.py:182` (direct file read), `app/services/forge_safe_affix_comparison_service.py:163`, `app/utils/cli.py:101` (DB seed) | **Authoritative in production** |
| Forge-safe export | `$FORGE_SAFE_AFFIX_EXPORT_PATH` | `data/loaders/forge_safe_affixes_loader.py`, `app/services/affix_catalog_service.py:112`, `/debug` | Off (`FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=false`, mode `shadow`) |
| Forge-safe bundle | `$FORGE_SAFE_AFFIX_BUNDLE_PATH` | `data/loaders/forge_safe_affix_bundle_loader.py`, `routes/experimental.py:1122-1210` | Off |
| v2 bundle | `docs/generated/v2_affix_bundle.json` | `app/repositories/v2/affix_repository.py` via `paths.py:11`, `routes/experimental.py:44` | Experimental routes only (`metadata.production_safe: false`) |
| Controlled resolver prototypes | `app/game_data/controlled_affix_resolver_*`, `controlled_modifier_resolver_*` | Tests/scripts only | — |

`affix_catalog_service.py:3` calls itself "the single selection point between legacy affix data and the …", but four other modules read `affixes.json` directly and bypass it.

### 4.4 Other duplicates
| Domain | Implementations | Notes |
|---|---|---|
| Optimizer | `optimization/` (runtime), `app/engines/optimization_engine.py` (runtime), `app/engines/build_optimizer.py` (tests only), `crafting/optimization/*` (tests only) | Two live, two dormant |
| Crafting | `app/engines/craft_engine.py`, `fp_engine.py` (runtime); `app/engines/craft_simulator.py` (tests only); `crafting/engines/*` (tests only; forging potential, fracture, glyph, rune, instability) | Dormant parallel crafting engine |
| Build model | `builds/` (runtime) vs `build/` (tests only) | Near-identical names |
| Constants | `backend/src/constants/*.ts`, `backend/app/constants/*.py`, `frontend/src/constants/*.ts` | Manual mirror |
| Game data on frontend | `frontend/src/lib/gameData.ts` ("patch 1.2.x", fandom/maxroll sources), `frontend/src/data/skillTrees/index.ts` (4334 lines), `frontend/src/data/raw/*.json` (2026-03-31) vs backend `data/` | Two sources of truth for skill and passive identity |
| Versioning | `data/version.json` (health), `config.CURRENT_PATCH` (version route), `data/versioning/versioned_loader.py` (load route), `integration/versioning/version_compatibility.py` (tests only) | See report 07 §3.1 |

---

## 5. Obsolete or inconsistent feature flags

| Flag | Location | Issue |
|---|---|---|
| `FORGE_SAFE_AFFIX_CATALOG_ENABLED` | `backend/config.py:42` **and** `:61` (same class `Config`) | The second definition silently overrides the first. Their semantics differ: `== "true"` vs `in {"1","true","yes","on"}`. Line 42 is dead |
| `FORGE_SAFE_AFFIX_EXPORT_PATH` | `backend/config.py:44` **and** `:65` | Duplicate definition |
| `FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED`, `…_CONSUMPTION_MODE="shadow"`, `…_BUNDLE_ENABLED`, `…_DEBUG_ENDPOINT_ENABLED` | `config.py:43,45,57,66` | All default off. Production behaviour equals legacy only |
| `CURRENT_PATCH="1.4.3"`, `CURRENT_SEASON=4`, `DATA_VERSION="1.0.0"` | `config.py:26-30` | Stale defaults (report 07) |

---

## 6. Unused or test-only app modules (selected from 74)

- **Whole `app/planner_adapters/v2/` package** (13 modules: adapter, contracts, eligibility, golden_baselines, experimental_mode, …): tests/scripts only. The experimental routes use `app/repositories/v2`, not the adapter.
- **25 `app/game_data/*` diagnostic modules** (`bundle_item_*`, `controlled_*_resolver_*`, `le_tools_*sidecar*`, `malformed_tier_value_shape_validator`, `missing_modifier_reference_mapping_validator`, `modifier_unresolved_category_triage`, `affix_diagnostic_consumer`, `bundle_compat`): tests/scripts only. These are report generators kept inside the runtime package.
- `app/domain/{ailment_duration_scaling, ailment_scaling, aoe_falloff, buff_duration_scaling, buff_snapshot, cooldown, mana, proc_chain, rotation, speed_scaling, stability, triggers, ward, ailment_stacking, ailments, resistance_shred, status_interactions}`: tests only.
- `app/engines/{build_optimizer, build_serializer, combat_simulator, craft_simulator, validators}`, `app/enemies/enemy_defense`, `app/skills/skill_execution`, `app/utils/profiling`, `app/schemas/api_contracts`: tests only.
- **Unreferenced by anything:** `app/domain/multi_target.py`, `app/domain/stat_groups.py`, `app/schemas/{analysis, community, sensitivity}.py`.

Endpoints: all 28 blueprint modules in `app/routes/` are registered (`app/__init__.py:193-250`). `experimental_bp` is registered twice, under `/experimental` and `/api/experimental` (`:249-250`). No unregistered route file was found.

## 7. Frontend
- Routed but mock: `/monte-carlo` (section 4.1).
- Six service modules are imported only by `__tests__`: `services/presets/preset_manager.ts`, `services/session/session_restore.ts`, `services/keyboard/shortcut_manager.ts`, `services/build/build_manager.ts`, `services/favorites/favorite_manager.ts`, `services/sharing/build_import_service.ts`.
- Not imported anywhere (name grep): `logic/parseSkillTree.ts`, `logic/computeSkillStats.ts`.
- A broader filename heuristic flagged 44 candidates, but spot checks showed false positives (pages imported in `App.tsx` under other paths). The frontend component-level dead-code count is therefore **UNKNOWN** and needs a bundler-based analysis (e.g. a `vite build` module graph or `ts-prune`), which was not run.

## 8. Old extractors, legacy schemas, generated data

| Item | Status | Evidence |
|---|---|---|
| `/home/user/le-parser` | Archived JS parser, single commit `5135ce4` 2026-03-26 | Not referenced by Forge code except `.dockerignore:15-16`, `.gitignore:81`, `backend/scripts/report_v2_source_inventory.py:39` |
| `le-parser.worktrees/copilot-worktree-2026-03-31T22-17-24` | Gitlink (mode 160000 → `5135ce4`) with **no `.gitmodules`**. The directory is empty | Orphan submodule pointer. `git submodule` commands will error |
| `scripts/sync_game_data.py` | The only data-sync path. Hard-codes `<forge>/last-epoch-data/exports_json` (`:21`) | Last effective run 2026-04-26 |
| `scripts/generate_tree_data.py` | Same nested `SRC_DIR` convention | Generated `frontend/src/data/*` |
| `docs/generated/` (80 files) | 28 referenced from `backend/app`/`backend/data`/`frontend/src` (often from test-only modules or docstrings), 36 script-only, 1 test-only, **15 referenced by nothing** | The 15 are all diagnostic reports dated 2026-05-11: `affix_diagnostic_consumer_report.{json,md}`, `controlled_affix_resolver_comparison_report.{json,md}`, `fresh_le_tools_sidecar_diagnostic_report.md`, 7× `le_tools_*` reports, `modifier_unresolved_category_triage_report.{json,md}` |
| Root docs | `ACCURACY_AUDIT.md` (2026-04-15), `GAMEPLAY_EXPANSION.md` (04-02), `POLISH_REPORT.md` (04-08), `CONTRIBUTING.md` (04-08), `ARCHITECTURE.md`/`CHANGELOG.md`/`README.md`/`ROADMAP.md` (04-22) | None updated after 2026-04-22, although the v2/forge-safe architecture landed in May |
| Version files | `VERSION` 0.8.0 (served by `/api/version`), root `package.json` 0.3.0, `frontend/package.json` 0.1.0 | Three app versions |

### 8.1 Extractor repository (`last-epoch-data`) drift
- `tools/scripts/` holds **596 Python files**: 181 `test_*`, 179 `generate_*`, **338** with review/certification/governance/authorization/planning/blocker/readiness/policy in the name, and only ~31 extraction/processing scripts.
- Legacy/duplicate processors are kept next to the canonical ones: `process_affixes.py` vs `process_affixes_tt.py` (the canonical one in `run_all.py`), `extract_skill_trees_tt.py` vs `extract_skill_trees_fast.py`, `process_localization.py` vs `process_localization_unified.py`, `run_all.py` vs `run_all_safe.py`, and `extract_missing_mage_skills.py` (a one-off).
- `requirements.txt` pins `deepdiff` for "Patch-diff reporting (Phase 6)", but no patch-diff tool exists (report 07 §8).
- The last 50 commits on `main` (through 2026-05-31) are governance/planning documents and gates. **No data refresh or extraction-logic change happened after 2026-05-29.**

## 9. TODO / FIXME / XXX / HACK

| Marker | Python (backend + scripts) | TS/JS (frontend/src + electron) |
|---|---|---|
| TODO | 1 (`backend/tests/test_forge_safe_production_non_consumption.py:150`: "Add a planner-specific non-consumption guard when there is a stable…") | 0 |
| FIXME | 0 | 0 |
| XXX | 0 | 0 |
| HACK | 0 | 0 |

Interpretation: inline markers are not a usable debt signal here. Debt is tracked in Markdown (`docs/KNOWN_LIMITATIONS.md`, `FORGE_MIGRATION_TRACKER.md`, `V2_*`, and so on).

## 10. Does old code make the authoritative implementation ambiguous?

**Yes, in four areas:**
1. **Simulation.** Five non-runtime simulators sit alongside the live path, two of them in the same `app/engines` and `app/` trees.
2. **Affixes.** Legacy JSON is authoritative by default, yet three alternative pipelines are importable and four modules bypass the "single selection point" service.
3. **Version/patch identity.** Four different mechanisms give three different answers (`unknown`, `1.4.3`, `1.2.1`).
4. **Constants and game data.** There are three constant trees and a separate hand-maintained frontend game-data module labeled patch 1.2.x.

It is unambiguous for: route registration (all registered), Monte Carlo in the backend (wholly unreferenced, so clearly dormant), and test-only packages (`buffs`, `movement`, `spatial`, `projectiles`, `status`, `visualization`, `integration`, `build`, `stats`), which are isolated rather than competing.

## 11. UNKNOWNs
- Whether any test-only package is loaded through a path the AST scan cannot see (Celery tasks, CLI entry points outside `backend/`, Electron).
- Frontend component-level dead code (heuristic unreliable; no bundler graph).
- Which runtime stat engine each endpoint actually exercises per request (no execution tracing done).
- Whether the empty gitlink directory breaks deploys. `.dockerignore` excludes it.

## 12. What this does NOT prove
- "Runtime-reachable" means importable from the Flask app. It does not mean exercised by users.
- "Tests only" does not mean worthless. Several packages (`movement`, `buffs`, `crafting/engines`) may be deliberate work in progress.
- No deletion is recommended as an action already taken. The classification is input for a separate decision.
- Counts come from one static scan at HEAD `1efcef7`. Re-running `modgraph.py` after changes will shift them.
