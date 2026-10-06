# 14 — Test Suite Quality Audit

Audit date: 2026-10-06. Scope: `le-the-forge` at `main` HEAD `1efcef7` (2026-05-14, the commit Render last deployed) plus CI history for `dev` (`558557c`), and `last-epoch-data` at `main` HEAD `73e2ab0` (2026-05-31). This is a read-only audit. Nothing in either repository was modified. All test runs used throwaway copies (`git archive` / `git clone`) in a scratch directory.

## 1. Headline answers

| Question | Answer |
|---|---|
| Does a green backend suite say anything about extraction completeness? | **Very little.** No test reads the live upstream extractor output (`last-epoch-data`). The only "real bundle" test is hard-wired to a Windows path (`D:\Forge\...`) and always skips. The bundle snapshot guard skips unless `FORGE_DATA_BUNDLE_DIR` is set, and CI never sets it. Completeness tests for enemies and items skip on every run (303 skips). What is tested is a vendored, committed snapshot inside `le-the-forge` (for example the pinned `19398` modifier-row counts). |
| Is the importer's HTTP layer exercised for real? | **No.** Every LET and Maxroll fetch is replaced with `unittest.mock.patch` and a hand-written HTML/JSON body (`tests/test_importers.py:159-283`, 76 `patch(` sites in `tests/test_build_import.py`). The suite has no recorded real page, no live canary and no contract test against the current LET page shape. HTTP 403 handling is tested as a mocked status code (`test_build_import.py:3508-3519`), so the production 403 alert counts as "expected" behaviour. |
| Is CI currently green? | **No, and it has not been for months.** `dev`: **261 consecutive failed push runs** since run #527 (2026-05-09, PR #306). The last green push run was #525. All 40 most recent CI runs failed. In the latest run (`26659275258`) only "Backend Tests" failed; type-check and data validation passed. |
| Does the current `main` tree pass today? | **No, on a fresh install.** Running Python 3.11 with `pip install -r requirements.txt` resolves **SQLAlchemy 2.1.3**, which is unpinned and comes in transitively. In SQLAlchemy 2.1, `postgresql://` defaults to the `psycopg` (v3) driver, which is not installed. Result: `tests/test_deployment_readiness.py` errors (6 tests) and `pytest -x` stops after 3 passes and 1 error. See INFRA-1 in report 16. |
| `last-epoch-data` tests | 181 test files and about 2,319 test functions exist. **CI runs only 16 of them** (`tools/scripts/test_regeneration_gate.py`) plus the regeneration gate. The gate fails on `main` (62 consecutive failing `main` pushes since 2026-05-29, PR #155). Reproduced locally: `drift=7`. |

## 2. Method and commands

```
git ls-files backend/tests | wc -l                       # 357 tracked files, 337 test_*.py
grep -rhoE "^\s*(async )?def test_\w+" backend/tests | wc -l   # 7,225 test functions (static)
grep -rnE "pytest\.mark\.skip|pytest\.skip\(|skipif|importorskip|xfail" backend/tests   # 11 sites / 8 files
# full run (Python 3.13 venv; repeated for the key file with Python 3.11):
git archive HEAD | tar -x -C <scratch>/forge
FLASK_ENV=testing SECRET_KEY=.. JWT_SECRET_KEY=.. python -m pytest tests/ -q -p no:cacheprovider --junitxml=junit.xml
# fixture age
git log -1 --format=%ci -- <fixture>; git log --diff-filter=A --format=%ci -- <fixture>
# CI history (GitHub API, read-only): actions_list list_workflow_runs ci.yml branch=dev (300 runs paged)
# last-epoch-data
git clone <local> <scratch>/c/last-epoch-data
python tools/scripts/regeneration_gate.py --strict
python -m pytest tools/scripts -q --continue-on-collection-errors
```

## 3. Result of the full local run (`le-the-forge` main @1efcef7)

`11415 passed, 379 skipped, 7 errors` (Python 3.13, about 6 minutes; the process was later OOM-killed during teardown on the first run).

| Errors | Cause |
|---|---|
| 6 × `tests/test_deployment_readiness.py::test_*_cors_*` | `create_app("production"/"development")` → `ModuleNotFoundError: No module named 'psycopg'` (SQLAlchemy 2.1.3 default PG driver). Reproduced on Python 3.11 with CI's env vars. |
| 1 × `tests/test_weaver_tree_scaffold.py::TestValidator::test_load_accepts_wellformed_nodes` | Teardown cascade on the session `app` fixture (`sqlite3.ProgrammingError: Cannot operate on a closed database`) after the failure above. |

These are the same kind of failures CI's `pytest -x` would stop on. The CI logs for runs older than the retention window return `410 Gone`, so the exact failing test in the historical dev runs is **UNKNOWN**.

## 4. Skips: what is silently not tested

From the JUnit XML (379 skipped):

| Count | File | Skip reason | Condition | Ever runs in CI? |
|---|---|---|---|---|
| 292 + 3 | `test_game_data_completeness.py`, `test_architecture_determinism.py` | `enemies.json removed — data consolidated…` | file missing (permanent) | **Never** |
| 16 | `test_combat_simulator.py:292,460` | `enemies.json not present` | file missing | **Never** |
| 7 + 2 + 1 | `test_game_data_completeness.py:197`, `test_architecture_determinism.py:37` | `items.json` / `affixes.json` removed | file missing | **Never** |
| 56 | `test_api_contracts.py:34` | needs seeded PostgreSQL | `psycopg2.connect` to localhost fails | **Never** (CI has no Postgres service) |
| 1 | `test_bundle_item_adapter_report.py:169` | needs `FORGE_DATA_BUNDLE_DIR` | env var | **Never** (CI does not set it) |
| 1 | `test_forge_safe_affix_bundle_loader.py:12,28` | `D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json` | Windows absolute path | **Never** on Linux |
| 0 (conditional) | `test_passive_tree_validator.py:169`, `test_optimization_api.py:90`, `test_api_contracts.py:299` | data-dependent skip inside test | runtime | Can turn a regression into a skip |

Plus **6 whole files excluded** by `backend/pytest.ini:13-19` (`--ignore=`): `test_affix_engine.py` (29 tests), `test_base_engine.py` (8), `test_craft_engine.py` (27), `test_craft.py` (17), `test_combat_engine.py` (57), `test_calculation_snapshots.py` (9). That is **147 tests**, last touched 2026-03-31 to 2026-04-15, and they are excluded because the code under test changed. The excluded `test_calculation_snapshots.py` is the only value-level calculation snapshot. It is excluded because "snapshot expected values are stale after calc refactor" (`pytest.ini:12`).

**321 of the 379 skips (85%) target data files that no longer exist.** As a result, the tests that claim to check enemy and item completeness check nothing on any machine.

## 5. What the tests prove, by area (heuristic filename classification)

| Area | Files | Test fns | What they prove | What they do NOT prove |
|---|---|---|---|---|
| Combat / simulation / stats engines | 121 | ~2,495 | Internal arithmetic consistency on synthetic inputs and determinism | That the inputs match the game (constants are hand-entered and the value snapshot file is ignored) |
| Uncategorised engine / misc | 91 | ~2,121 | Same as above (AoE, cooldowns, conditions, etc.) | Same |
| v2 trust / governance / diagnostic reports | 68 | ~620 | Report schemas are stable, keys exist, and counts are pinned (`19398` rows, `2070` stats). The planner is "non-calculating" (0 calculable modifiers) | Correctness of any extracted value. Several tests assert that a report generator's output matches counts derived from the same committed snapshot (self-referential) |
| Game data / validation / loaders | 26 | ~655 | `data/*.json` loads and constants have positive values. `len(affixes) > 1000` (`test_data_loading_performance.py:46`), `>= 1000` (`test_api_contracts.py:105`, which always skips) | Completeness against upstream. Weak lower bounds would still pass after a large drop (for example, 1,100 affixes out of 1,300+) |
| Crafting | 11 | ~621 | Craft rules on current data | Real FP/tier mechanics. The original craft engine tests are excluded |
| Importers (LET / Maxroll) | 5 (+ parts of others) | ~237 | Parser behaviour on **hand-authored** HTML/JSON and error mapping (404/403/500/timeout) | Behaviour against the **current** real LET/Maxroll pages, anti-automation protection, or field-level completeness of a real build |
| API / routes / auth | 15 | ~476 | Route wiring on SQLite in-memory | Postgres behaviour (56 contract tests skip) and production config (errors above) |

### Specific quality findings

1. **Mocked-away importer risk.** `test_importers.py:159-171` asserts only `character_class`, `mastery` and `len(skills) == 1`. A regression that dropped gear, affix rolls, passives or idols would still pass this test. `test_build_import.py` has more gear assertions, but its inputs are all synthetic `window["buildInfo"] = {...}` blocks (`test_build_import.py:60-64, 828-829`). The fixture files `le_tools_offline_buildinfo_*_sample.json` (added 2026-05-11) are small hand-curated samples of 2–4 KB. They are not real captured pages.
2. **Golden baselines are scaffolds, not goldens.** `tests/fixtures/v2/golden_baselines/*.json` (7 files, 231–377 bytes, added 2026-05-13) contain field-name lists and flags (`"mechanical_calculation_involved": false`). `test_v2_golden_baseline_plan.py` only checks that the paths exist and are unique. These files cannot detect a value regression.
3. **Pinned-count tests are useful but local.** `test_v2_stat_modifier_dry_run.py:31-64`, `test_v2_planner_metadata_remap.py:40` and `test_v2_experimental_planner_adapter_mode.py:32` pin `19398` and `2070`. They do detect drift of the committed snapshot in this repo. They cannot detect upstream patch drift, because upstream is never read.
4. **No round-trip or relationship tests against real data.** Examples of missing tests: import a real LET build, export it, and compare the result. Check that every affix referenced by uniques or items resolves in the affix catalog. A `grep` for such cross-file resolution in tests found only diagnostic-report key checks.
5. **Few negative cases for data loss.** No test asserts that a missing field produces a warning or `missing_fields` entry for real-shaped input (only synthetic shapes).
6. **Fixture ages.** `sample_character.json` was last changed 2026-03-31. All LET fixtures date from 2026-05-11 and the goldens from 2026-05-13. Nothing has been refreshed since the last deploy (2026-05-14), even though the 403 alert shows that the upstream behaviour changed.
7. **Frontend tests are not in CI.** There are 49 vitest files with about 916 `it/test` blocks, but CI runs only `npx tsc --noEmit` (`.github/workflows/ci.yml:81`). CI also does not run `vite build`.
8. **CI stops at the first failure** (`pytest -x`, `ci.yml:44`). One environment break hides every other failure, and the reported "passed" count is then meaningless.

## 6. `last-epoch-data` tests

| Item | Value |
|---|---|
| Test files | 181 (`tools/scripts/test_*.py`) |
| Test functions (static) | ~2,319 |
| Files with skip logic | 96 |
| Run in CI | **only** `tools/scripts/test_regeneration_gate.py` (16 tests) + `regeneration_gate.py --strict` (`.github/workflows/regeneration-gate.yml`) |
| Full local run (Python 3.13, jsonschema+pytest only) | `9 failed, 2293 passed, 1 skipped, 5 errors` (collection errors: `UnityPy` / `pefile` missing, which are extraction-host deps) |
| The 9 failures | Committed-report vs regenerated-report mismatches (same root cause as the gate drift) |
| Regeneration gate on clean clone @73e2ab0 | `total=185 drift=7 match=163 skipped_no_generator=15` → **GATE FAILED** |
| Drifting artifacts | `affixes_/items_/passive_nodes_/skills_trusted_subset_remediation_report.json`, `items_certification_reevaluation_report.json` (`schema_validation_result`), `domain_gap_closure_planning_report.json`, `extraction_coverage_gap_certification_report.json` (`…present` flags) |
| CI history | 62 consecutive failing `main` pushes since 2026-05-29 (#155). The last green run was #61 (PR #154). The `main` branch is **not protected**. |

Environment sensitivity observed: when run from a directory not named `last-epoch-data`, the gate reported 93 drifts (`$.repository_context.repository_name`). When run without `.git` it reported 4 errors (generators read `git show HEAD:`). The `…present` drifts depend on which gitignored local files exist on the machine that generated the report. The governance reports therefore pass only on the author's extraction host.

## 7. UNKNOWNs

- The exact first failing test in the historical `dev` CI runs (logs expired, `410 Gone`).
- Whether CI on GitHub currently resolves SQLAlchemy 2.1.x. It is highly likely because pip installs fresh with only the pip-download cache, but this was not observed in a CI log.
- Whether any manual or real-page importer testing happens outside the repo.
- Frontend vitest pass/fail status (another investigator runs the suite; not run here).

## 8. What this audit does NOT prove

- It does not prove that the engine math is wrong. It shows only that the tests cannot confirm it matches the game.
- The heuristic category counts come from filename regexes and are approximate.
- The local runs used Python 3.13 (full suite) and 3.11 (targeted). CI uses 3.11.
- A passing gate in `last-epoch-data` would show only that the reports are self-consistent, not that the extraction is complete.
