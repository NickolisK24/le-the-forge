# v2.5 Main Release Readiness

## Summary

- Branch: `release/v2.5-trust-foundation`
- Main baseline observed locally: `ae85d01c215424c17719bfa636f12fee74ebdd35`
- Release branch base commit: `112de29a652b3d908301a2f40d5305e9fb2431ee`
- Candidate v2.5 cutoff commit: `112de29a652b3d908301a2f40d5305e9fb2431ee`
- Recommendation: READY for main

`112de29a652b3d908301a2f40d5305e9fb2431ee` appears to be the final v2.5 cutoff because it merges PR #364, `v2.5/release-readiness-ux-qa`, and is immediately followed by PR #365, `v3/mechanical-intelligence-planning`. The release branch excludes the later v3 planning delta.

## Files Changed

- `.env.example`
- `backend/app/routes/ref.py`
- `backend/app/services/affix_catalog_service.py`
- `backend/app/services/importers/lastepochtools_importer.py`
- `backend/app/utils/cache.py`
- `backend/config.py`
- `backend/tests/test_affix_catalog_routes.py`
- `backend/tests/test_affix_catalog_service.py`
- `backend/tests/test_deployment_readiness.py`
- `backend/tests/test_passives_api.py`
- `backend/tests/test_v2_golden_baseline_plan.py`
- `docs/release/V2_5_MAIN_RELEASE_READINESS.md`

## Root Causes Found

- `/api/ref/passives` depended on seeded DB rows and returned empty local data when the database was unseeded. It now falls back to `data/classes/passives.json` while preserving DB-backed behavior when rows exist.
- Affix catalog route/service tests used the old fixture shape while the forge-safe loader requires the current read-only export contract: `records`, `summary`, and `export_policy`. Fixtures now match the loader contract and remain explicitly non-production-consuming.
- Missing forge-safe catalog export files raised `FileNotFoundError` outside the service’s clean unavailable path. Read-only/active catalog mode now returns controlled 503 behavior for missing or invalid exports.
- Last Epoch Tools importer JSON reads used the platform default encoding. On Windows, `uniques.json` could fail to decode and leave unique-name resolution empty. The importer now reads project JSON files as UTF-8.
- The deployment readiness env scan included `.venv` package code and `.env.example` was missing real app-level trusted-data variables. The scan now excludes virtualenv source and the referenced variables are documented.
- v2 golden baseline fixture paths were repo-root-relative, but the backend test ran from `backend`. The test now resolves those release fixture paths from the repository root and still requires relative, existing fixture references.
- View tracking tests could reuse a process-global Redis cache client initialized before the testing app was active. Testing config now disables external Redis cache state, and the cache helper respects the active app cache URL.

## Data Population Status

Local Flask test-client verification on the release branch:

| Surface | Route | Status | Population |
| --- | --- | ---: | ---: |
| Classes | `/api/ref/classes` | 200 | 5 |
| Skills | `/api/ref/skills` | 200 | 179 |
| Affixes | `/api/ref/affixes` | 200 | 1113 |
| Base items | `/api/ref/base-items` | 200 | 115 grouped slots/items |
| Uniques | `/api/ref/uniques` | 200 | 403 |
| Passive trees | `/api/passives` | 200 | 541 nodes |
| Reference passives | `/api/ref/passives` | 200 | 541 nodes |
| v2 classes | `/api/experimental/v2/classes` | 200 | 5 |
| v2 masteries | `/api/experimental/v2/masteries` | 200 | 15 |
| v2 passive trees | `/api/experimental/v2/passives` | 200 | 5 trees |
| v2 skills | `/api/experimental/v2/skills` | 200 | 184 total |
| v2 affixes | `/api/experimental/v2/affixes` | 200 | 1098 total |
| v2 item bases | `/api/experimental/v2/items/bases` | 200 | 542 total |
| v2 item implicits | `/api/experimental/v2/items/implicits` | 200 | 1182 total |
| v2 uniques | `/api/experimental/v2/uniques` | 200 | 409 total |
| v2 sets | `/api/experimental/v2/sets` | 200 | 23 total |
| v2 idols | `/api/experimental/v2/idols` | 200 | 71 total |
| v2 idol affixes | `/api/experimental/v2/idols/affixes` | 200 | 483 total |

## Manual QA Routes

- `/classes`
- `/passives`
- `/trusted-data`
- `/trusted-data/support`
- `/trusted-data/pre-v3-readiness`
- `/debug/v2`
- `/debug/v2-classes`
- `/debug/v2-passives`
- `/debug/v2-skills`
- `/debug/v2-items`
- `/debug/v2-unique-sets`
- `/debug/v2-idols`
- `/debug/v2-stats-modifiers`
- `/affix-catalog` only if the forge-safe catalog is intentionally enabled

## Tests Run

- PASS: `backend`: `python -m pytest tests\test_passives_api.py tests\test_v2_5_release_readiness.py tests\test_v2_experimental_planner_adapter_mode.py tests\test_forge_safe_production_non_consumption.py -q`
  - 42 passed
- PASS: `frontend`: `npm run type-check`
- PASS: `frontend`: focused v2.5 page tests
  - 7 files passed
  - 43 tests passed
- PASS: `backend`: `python -m pytest tests\test_affix_catalog_routes.py tests\test_affix_catalog_service.py tests\test_build_import.py tests\test_deployment_readiness.py tests\test_v2_golden_baseline_plan.py -q`
  - 229 passed
  - 4 warnings
- PASS: `backend`: `python -m pytest tests\test_community_tools.py::TestViewTracking -q`
  - 5 passed
- PASS: `backend`: `python -m pytest -q`
  - 11477 passed
  - 323 skipped
  - 18 warnings

## Remaining Failures

None in the backend suite when run from `backend`.

Known non-blocking note: running pytest from the repository root still hits pre-existing collection path assumptions in older backend tests. The supported backend command for this release is from `backend` with `PYTHONPATH=.`.

## Release Safety Confirmations

- Affix catalog behavior remains read-only and production-safe: forge-safe catalog fixtures and service responses preserve `production_consumer: false`, and the catalog is still controlled by disabled-by-default config flags.
- Unique item importer loading uses real `data/items/uniques.json` records with UTF-8 decoding; no guessed unique mappings were added.
- Environment variable readiness is fixed by documenting real app-referenced trusted-data variables and excluding virtualenv package code from the app source scan.
- v2 golden baseline fixture references remain relative and are verified to exist from the repository root.
- Production planner math is unchanged. No DPS, crafting, stat aggregation, simulation, combat, optimizer, or planner calculation behavior was modified.
- v3 mechanical behavior is not enabled. Existing pre-v3 readiness and v2 debug surfaces remain documentation/debug-only and are not production-consumed.

## Known Remaining Risks

- Local route population was verified through Flask test client, not browser screenshots.
- The full backend suite passes from `backend`; root-level pytest invocation still has legacy collection assumptions and should not be used as the release gate.

## Final Recommendation

READY for main. The trusted-data population blocker and the remaining backend test failures have been resolved, the full supported backend suite is green, frontend typecheck and focused frontend trusted-data tests are green, production planner math is unchanged, and v3 mechanical behavior is not enabled.
