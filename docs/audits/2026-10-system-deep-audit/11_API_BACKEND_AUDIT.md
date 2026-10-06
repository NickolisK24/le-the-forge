# 11 — API / Backend Audit (Phase 9)

Audit date: 2026-10-06. Code: `HEAD 1efcef7` (2026-05-14). Audit only. Nothing in the repo was changed apart from these report files, and production (`api.epochforge.gg`) was not contacted.

## 1. Method and commands

| Step | Command / script (in the session scratchpad `$S`) | Purpose |
|---|---|---|
| URL map | `$S/urlmap.py`: `create_app("testing")`, iterate `app.url_map`, resolve each view to `file:line` via `inspect` | Endpoint inventory (171 rules + static) |
| Rate limits | `$S/lim.py`: `create_app("development")`, read `limiter.limit_manager._decorated_limits` / `_default_limits` | Per-route limits (46 decorated) and default limits |
| Auth/ownership probes | `$S/admin_test.py`, `$S/poison.py`, `$S/err.py` (Flask test client, `testing` config, in-memory SQLite; `admin.AFFIXES_PATH` monkeypatched to a **scratch copy** so no repo file was written; `git status` confirmed clean) | Verify unauthenticated access and IDOR |
| CPU/memory probes | `$S/cpu.py`, `$S/v2_timing.py`, `$S/rss.py` (in-process test client, `ulimit -v 3000000` guard) | Measure wall time / peak RSS of expensive endpoints |
| Frontend usage | `grep -rnoE` over `frontend/src` for `"/<prefix>..."` literals (excluding tests), stored at `$S/fe_paths.txt` | Which endpoints the SPA calls |
| Deploy config | `render.yaml`, `backend/Procfile`, `backend/entrypoint.sh`, `backend/config.py` | Runtime: `gunicorn wsgi:app --workers=4 --threads=2 --timeout=120 --preload`, starter plan |

Measurements are single-process, on this audit machine, not on Render hardware. Treat absolute numbers as order-of-magnitude.

## 2. Headline numbers

| Item | Count |
|---|---|
| URL rules (excl. `static`) | **171** |
| Distinct view functions | **130** (the `experimental` blueprint is registered twice, at `/experimental` and `/api/experimental`, giving 41 duplicate rules) |
| Blueprints registered | 28 (29 registrations) |
| Methods | GET 138, POST 28, PATCH 3, DELETE 2 |
| Rules requiring login | **7** (`auth.me`, builds delete/vote, profile ×3, admin import-failures (+is_admin)) |
| Rules with optional JWT (anonymous allowed) | 10 |
| Rules with **no auth at all** | **154**, including **all 3 mutating "admin/load" endpoints** (`PATCH /api/admin/affixes/<id>`, `GET /api/admin/affixes`, `POST /api/load/game-data`) |
| Unauthenticated CPU-heavy compute endpoints | 25 (11 `/api/simulate/*`, `/api/optimize/build`, `/api/bis/search`, `/api/craft/{predict,simulate}`, 7 `/api/builds/<slug>/{simulate,optimize×2,report,analysis×3}`, `/api/compare/...`, `/api/load/game-data`) |
| Unauthenticated, **not env-gated** v2 bundle endpoints that re-parse large JSON from disk per request | 76 (38 × 2 mounts). Bundles up to 37 MB (`v2_modifier_registry.json`) |
| Routes with an explicit `@limiter.limit` | 46. All others get production default `1000/day;200/hour;30/minute` per key per route |
| Endpoints the frontend calls (grep) | 77 rules. Not called: the 41 `/experimental/*` duplicates, `/api/simulate/{stats,combat,defense,optimize,sensitivity}`, `/api/jobs/<id>`, `/api/craft/{simulate,<slug>/undo, DELETE <slug>}`, `POST /api/builds/<slug>/optimize`, 6 `/api/ref/*` detail routes, `/api/admin/import-failures`, forge-safe experimental routes, `/debug/forge-safe-affixes`, `/api/health` (Render probe) |

## 3. Cross-cutting backend behaviour

* **Auth model:** Discord OAuth2 → JWT (HS256, 1 h, `config.py:9-11`) returned to the SPA **in the redirect URL query string** (`routes/auth.py:144-146`). The SPA keeps it in memory and sends a Bearer header (`frontend/src/lib/api.ts:81-83`). The OAuth authorize URL carries **no `state` parameter** (`routes/auth.py:49-55`), so login CSRF is possible. Logout is a no-op and tokens cannot be revoked. `users.is_active` is never checked. `owner_required` (`utils/auth.py:97-125`) is unused and would raise a NameError (`unauthorized` is not imported in its scope).
* **Dev login:** `GET /api/auth/dev-login` is gated by `current_app.debug`. Production config sets `DEBUG=False`, and the testing probe returned 404. Production `wsgi.py` defaults `FLASK_ENV=production`, so this is safe unless `FLASK_ENV=development` is set on Render (`render.yaml` sets `production`).
* **Admin:** there is **no admin decorator**. Only `/api/admin/import-failures` checks `is_admin`. `/api/admin/affixes` (GET, PATCH) and `/api/load/game-data` have **no authentication**. The frontend ships an anonymous "Affix Editor" at SPA route `/affixes` (`frontend/src/App.tsx:232`) and a Data Manager at `/data-manager` (`App.tsx:244`) that call them.
* **Rate limiting:** Flask-Limiter 3.7, `key_func=get_remote_address` (`app/__init__.py:16`), storage `REDIS_URL`. If the Redis ping fails at boot it silently falls back to `memory://` (`app/__init__.py:31-45`), which gives per-worker counters (×4 effective). **No `ProxyFix` / `X-Forwarded-For` handling exists anywhere in the backend** (grep). Behind Render's proxy, `request.remote_addr` is expected to be the proxy's address. That would make every limit a **sitewide shared bucket** (one heavy user can 429 everyone, e.g. 30/min across all users on undecorated routes, or `2 per minute` for all anonymous imports). It would also collapse `build_views` dedupe to a single hash. Whether Render presents the client IP as the TCP peer: **UNKNOWN (likely not)**. This must be verified in production logs (`rate_limit_exceeded ip=` lines).
* **Error handling:** `@app.errorhandler(Exception)` (`app/__init__.py:260-264`) also catches werkzeug `HTTPException`s. Verified: a 405 (POST to `/api/health`) and a 400 (malformed JSON body to `POST /api/builds` / `/api/bis/search`) both return **500 "Internal server error"** and are logged as unhandled exceptions. Several routes echo raw exception text to clients (`load.py:41`, `optimize.py:68`, `import_route.py:357,488,603`, the v2 routes' `message: str(exc)` with absolute server paths).
* **Request size:** `MAX_CONTENT_LENGTH` is not set. JSON bodies are unbounded (limited only by the gunicorn/Render proxy). The lists `gear`, `passive_tree`, `skills`, `blessings`, `affixes`, `targets` and `steps` have no length caps in several schemas.
* **Timeouts:** gunicorn `--timeout 120`. There are no per-request compute budgets. The async job mode (`"async": true` on `/api/simulate/combat` and `/build`) submits to a per-worker `ThreadPoolExecutor(max_workers=4)` with an **unbounded queue** (`utils/jobs.py:24`), so it bypasses the request timeout. Job ids are 8 hex chars and readable by anyone. Jobs are lost on worker restart.
* **Caching:** Redis cache helpers (`utils/cache.py`). `delete_pattern` uses Redis **`KEYS`** (`cache.py:72`), which is O(N) and blocking, and is called on every build create/update/delete/vote and skill PATCH. Build list is cached 30 s, meta 120 s, optimize 30 min, ref data via `cached_route`.
* **Observability:** stdlib logging, JSON in production. Slow-request warning at more than 500 ms (`app/__init__.py:170-175`), `X-Response-Time` header, 429 logging. No request id, no error tracker (no Sentry), no metrics. `/api/health` returns `ok` without checking DB or Redis. `/api/version` forks `git rev-parse` on every call (`version.py:47-55`).
* **External network:** Discord OAuth (10 s timeouts), Discord webhook for import failures (synchronous in the request, 10 s), LastEpochTools fetch (15 s), Maxroll importer that tries **7 API URLs + 1 HTML URL sequentially, each with a 15 s timeout** (`maxroll_importer.py:275-281,749-790`). The worst case of ~120 s+ reaches the gunicorn worker timeout. All outbound hosts are hard-coded and no SSRF was found (`import/url` and the importers build URLs from a regex-captured code only).
* **"fix: expose v2 debug routes" (9f38e8e):** this commit changed **only the frontend** (`frontend/src/App.tsx`, plus one test). It moved 10 SPA routes (`/debug/v2`, `/debug/forge-safe-affixes`, `/debug/v2-{affixes,items,unique-sets,idols,classes,passives,skills,stats-modifiers}`) out of the `IS_DEV` guard so they render in production builds. The backend endpoints they call (`/api/experimental/v2/...`) were **already unauthenticated and not env-gated**. Only the forge-safe catalog routes (`FORGE_SAFE_AFFIX_CATALOG_ENABLED`) and `/debug/forge-safe-affixes` (`FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED`) are env-gated, and `render.yaml` sets neither, so they return 404 in production. The practical effect is that public SPA pages now drive the heaviest read endpoints in the API (`/api/experimental/v2/modifiers/debug`: ~2.6 s and ~135 MB transient RSS per call, measured). They also expose absolute server file paths (`source_path`) and internal validation reports to any visitor.

## 4. Verified security / reliability findings

| ID | Sev | Finding | Evidence (verified unless noted) |
|---|---|---|---|
| API-1 | **P0** | Unauthenticated write to server game data: `PATCH /api/admin/affixes/<id>` rewrites `data/items/affixes.json` on disk. `POST /api/load/game-data` (also no auth) hot-reloads the pipeline from disk, so tampered affixes feed simulations and crafting for that worker until redeploy. A malformed value can also make `load_all()` raise after it has cleared the cache, leaving the worker with empty data | `admin.py:68-90`, `load.py:21-41`, `pipeline.py:110-148`. Probe: anon PATCH → 200, scratch file name changed to `AUDIT-TAMPER` |
| API-2 | **P1** | Unauthenticated memory/CPU exhaustion: `POST /api/simulate/multi-target` has no upper bounds on `max_duration`, `tick_size` or number of `targets`, and returns every damage event. One request (3600 s / 0.01 tick / 10 targets) took 17.3 s and **1.66 GB RSS**. A larger input was **SIGKILLed** (rc 137). The starter-plan instance (4 workers) would be OOM-killed | `multi_target.py:40-70,122-135`; `$S/cpu.py mt` |
| API-3 | P1 | Unauthenticated, ungated v2 endpoints re-read and parse multi-MB bundles on every request (modifiers 37 MB: ~2.7 s, about +135 MB; skills 20 MB: ~1.6 s). Two concurrent modifiers calls peaked at 384 MB RSS. They are now linked from public SPA pages (9f38e8e). 76 such rules, rate limit default 30/min per key | `experimental.py:1304-1350`; `$S/v2_timing.py`, `$S/rss.py` |
| API-4 | P1 | IDOR: `PATCH /api/builds/<slug>/skills/<skill_id>/nodes/<node_id>` has **no auth or ownership check**. An anonymous caller changed the skill allocation of another user's *private* build (200) | `skills.py:281-375`; `$S/poison.py` |
| API-5 | P1 | Anonymous builds are writable by anyone (`PATCH /api/builds/<slug>`, `builds.py:205-212`) and **deletable by any logged-in user** (`builds.py:239`, verified 204). Anonymous craft sessions likewise (`craft.py:139-142,166-169,207-209`) | `$S/poison.py` |
| API-6 | P1 | Private builds (`is_public=False`, including every imported build, forced private at `import_route.py:592`) are fully readable via `GET /api/builds/<slug>`, `/simulate`, `/skills`, `/optimize`, `/analysis/*` and `/api/compare/...`. Only `/report` checks. Slugs are derived from the build name (`build_service.py:26-37`), so they are guessable | verified 200 on GET, simulate and skills; 403 on report |
| API-7 | P1 | No ProxyFix: rate limits, import anon limits and view dedupe key on `remote_addr`, which on Render is probably the proxy (UNKNOWN), giving sitewide shared buckets / ineffective per-client limiting | grep (no `ProxyFix`/`X-Forwarded`) |
| API-8 | P1 | `DELETE /api/builds/<slug>` returns 500 for any build that has a view record (see DB-1) | `$S/del_test.py` |
| API-9 | P2 | HTTP errors (400/405/415...) are converted to 500 by the catch-all handler, and logged as unhandled exceptions | `$S/err.py` |
| API-10 | P2 | OAuth: no `state` (login CSRF), JWT in URL query (history/logs/Referer), no revocation, `is_active` ignored | `auth.py:49-55,144-146,193-196` |
| API-11 | P2 | A malformed `gear` blob from an anonymous create makes `/api/meta/snapshot` return 500 sitewide (see DB-6) | `$S/poison.py` |
| API-12 | P2 | Async job mode: unbounded per-worker queue, 4 extra compute threads per worker, results world-readable by 8-hex id, no auth | `utils/jobs.py`, `simulate.py:139-152,306-321` |
| API-13 | P2 | Bounded but heavy anonymous compute: `/api/simulate/encounter` worst case 11.7 s, `/api/optimize/build` (1000 variants × depth 10) 8.3 s, `/api/simulate/rotation` 7.6 s. 8 request threads per instance means a handful of anonymous clients can saturate it | `$S/cpu.py` |
| API-14 | P2 | Maxroll import can hold a worker for more than 120 s (8 sequential fetches × 15 s, plus a sync Discord webhook), reaching the gunicorn timeout | `maxroll_importer.py:749-790` |
| API-15 | P2 | Anonymous callers can create unbounded `import_failures` rows and Discord webhook alerts (`/api/import/let/json`, 20/min/key) | `import_route.py:455-474` |
| API-16 | P2 | `/api/import/build` bypasses `BuildCreateSchema` and passive validation (calls `build_service.create_build` directly) and stamps `patch_version` "1.2.1" | `import_route.py:590-605` |
| API-17 | P3 | Redis `KEYS` in hot write paths; `/api/version` subprocess per call; `/api/health` without dependency checks; `/api/profile/sessions` has unbounded `per_page`, N+1 on `steps`, and returns 500 on a non-integer `page`; `create_build` does one query per passive id | code |
| API-18 | P3 | Dead / legacy surface: 41 duplicate `/experimental/*` rules, 5 unused `/api/simulate/*` stateless routes, `POST /api/builds/<slug>/optimize`, `/api/jobs`, craft simulate/undo/delete, unused `owner_required`, `admin.list_import_failures` (no UI) | grep |

## 5. Endpoint inventory

Columns: **Auth** = none / optional JWT (anonymous allowed) / required. **Rate limit** = the explicit decorator, or "default" (prod: `1000/day;200/hour;30/minute` per key). **FE uses** = a literal path found in `frontend/src` (non-test). This is grep-based and may miss dynamically built paths. **Source** is relative to `backend/`.

| # | Method | Path | Endpoint | Auth | Rate limit | FE uses | Source | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | GET | `/api/admin/affixes` | admin.list_affixes | none | default | yes | app/routes/admin.py:41 | NO AUTH; dumps full affixes.json (1.2MB) |
| 2 | PATCH | `/api/admin/affixes/<affix_id>` | admin.update_affix | none | 30 per 1 minute | yes | app/routes/admin.py:68 | **NO AUTH; writes data/items/affixes.json on server disk** (verified) |
| 3 | GET | `/api/admin/import-failures` | admin.list_import_failures | required+admin | 60 per 1 minute | no (grep) | app/routes/admin.py:96 | login + is_admin check in body |
| 4 | GET | `/api/affixes/catalog` | affixes.list_catalog_affixes | none | default | yes | app/routes/affixes.py:25 |  |
| 5 | GET | `/api/affixes/catalog/<affix_id>` | affixes.catalog_affix_detail | none | default | yes | app/routes/affixes.py:59 |  |
| 6 | GET | `/api/affixes/catalog/summary` | affixes.catalog_summary | none | default | yes | app/routes/affixes.py:47 |  |
| 7 | GET | `/api/affixes/experimental/forge-safe-affixes` | affixes.experimental_forge_safe_affixes | none | default | no (grep) | app/routes/affixes.py:74 |  |
| 8 | GET | `/api/auth/dev-login` | auth.dev_login | none | default | yes | app/routes/auth.py:150 | 404 unless app.debug |
| 9 | GET | `/api/auth/discord` | auth.discord_login | none | 20 per 1 minute | yes | app/routes/auth.py:29 |  |
| 10 | GET | `/api/auth/discord/authorized` | auth.discord_authorized | none | 20 per 1 minute | yes | app/routes/auth.py:59 | no OAuth state param; JWT returned in URL query |
| 11 | POST | `/api/auth/logout` | auth.logout | none | default | no (grep) | app/routes/auth.py:193 | stateless no-op |
| 12 | GET | `/api/auth/me` | auth.me | required | default | yes | app/routes/auth.py:184 |  |
| 13 | POST | `/api/bis/search` | bis.bis_search | none | 15 per 1 minute | yes | app/routes/bis_search.py:52 |  |
| 14 | GET | `/api/builds` | builds.list_builds | none | default | yes | app/routes/builds.py:69 | per_page capped 100; cached 30s |
| 15 | POST | `/api/builds` | builds.create_build | optional JWT | 20 per 1 minute | yes | app/routes/builds.py:154 | validates passive IDs one query per node (N queries) |
| 16 | GET | `/api/builds/<slug>` | builds.get_build | optional JWT | default | yes | app/routes/builds.py:178 | no is_public check (verified); view_count RMW |
| 17 | PATCH | `/api/builds/<slug>` | builds.update_build | optional JWT | 20 per 1 minute | yes | app/routes/builds.py:199 | anon-authored builds editable by anyone (verified) |
| 18 | DELETE | `/api/builds/<slug>` | builds.delete_build | required | 10 per 1 minute | yes | app/routes/builds.py:230 | any logged-in user can delete anon builds (verified); 500 if build has views (verified) |
| 19 | GET | `/api/builds/<slug>/analysis/boss/<boss_id>` | analysis.boss_analysis | none | 10 per 1 minute | yes | app/routes/analysis.py:89 | no is_public check |
| 20 | GET | `/api/builds/<slug>/analysis/corruption` | analysis.corruption_analysis | none | 10 per 1 minute | yes | app/routes/analysis.py:145 | no is_public check |
| 21 | GET | `/api/builds/<slug>/analysis/gear-upgrades` | analysis.gear_upgrades | none | 10 per 1 minute | yes | app/routes/analysis.py:181 | no is_public check |
| 22 | POST | `/api/builds/<slug>/optimize` | builds.optimize_build | none | 10 per 1 minute | no (grep) | app/routes/builds.py:267 | no is_public check; not called by FE |
| 23 | GET | `/api/builds/<slug>/optimize` | builds.optimize_build_v2 | none | 10 per 1 minute | yes | app/routes/builds.py:286 | no is_public check; cached 30 min |
| 24 | GET | `/api/builds/<slug>/report` | report.get_report | none | 20 per 1 minute | yes | app/routes/report.py:21 | checks is_public/owner (verified 403) |
| 25 | POST | `/api/builds/<slug>/simulate` | builds.simulate_build | none | 10 per 1 minute | yes | app/routes/builds.py:252 | no is_public check (verified) |
| 26 | GET | `/api/builds/<slug>/skills` | skills.get_build_skills | none | 20 per 1 minute | yes | app/routes/skills.py:218 | no is_public check (verified) |
| 27 | PATCH | `/api/builds/<slug>/skills/<skill_id>/nodes/<int:node_id>` | skills.allocate_skill_node | none | 30 per 1 minute | yes | app/routes/skills.py:281 | **NO ownership check: anon can edit any build (verified)** |
| 28 | POST | `/api/builds/<slug>/view` | views.track_view | none | 60 per 1 minute | yes | app/routes/views.py:27 | writes BuildView row; IP hash keyed on remote_addr |
| 29 | POST | `/api/builds/<slug>/vote` | builds.vote | required | 30 per 1 minute | yes | app/routes/builds.py:363 |  |
| 30 | GET | `/api/builds/meta/snapshot` | builds.meta_snapshot | none | default | yes | app/routes/builds.py:120 |  |
| 31 | GET | `/api/compare/<slug_a>/<slug_b>` | compare.compare | none | 15 per 1 minute | yes | app/routes/compare.py:33 | no is_public check |
| 32 | POST | `/api/craft` | craft.create_session | optional JWT | 30 per 1 minute | yes | app/routes/craft.py:45 |  |
| 33 | GET | `/api/craft/<slug>` | craft.get_session | none | default | yes | app/routes/craft.py:120 |  |
| 34 | DELETE | `/api/craft/<slug>` | craft.delete_session | optional JWT | 10 per 1 minute | no (grep) | app/routes/craft.py:201 | anon sessions deletable by anyone with slug |
| 35 | POST | `/api/craft/<slug>/action` | craft.apply_action | optional JWT | 60 per 1 minute | yes | app/routes/craft.py:129 | anon sessions mutable by anyone with slug (slug=token_urlsafe(8)) |
| 36 | GET | `/api/craft/<slug>/summary` | craft.get_summary | none | default | yes | app/routes/craft.py:193 |  |
| 37 | POST | `/api/craft/<slug>/undo` | craft.undo_action | optional JWT | 30 per 1 minute | no (grep) | app/routes/craft.py:157 | same as action |
| 38 | POST | `/api/craft/predict` | craft.predict | none | 30 per 1 minute | yes | app/routes/craft.py:58 |  |
| 39 | POST | `/api/craft/simulate` | craft.simulate | none | 20 per 1 minute | no (grep) | app/routes/craft.py:99 |  |
| 40 | GET | `/api/entities/bosses` | entities.list_bosses | none | default | yes | app/routes/entities.py:17 |  |
| 41 | GET | `/api/experimental/forge-safe-affixes` | api_experimental.forge_safe_affix_catalog | none | default | no (grep) | app/routes/experimental.py:78 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 42 | GET | `/api/experimental/forge-safe-affixes/<affix_id>` | api_experimental.forge_safe_affix_detail | none | default | no (grep) | app/routes/experimental.py:170 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 43 | GET | `/api/experimental/forge-safe-affixes/compare-legacy` | api_experimental.compare_forge_safe_affixes_to_legacy | none | default | no (grep) | app/routes/experimental.py:102 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 44 | GET | `/api/experimental/v2/affixes` | api_experimental.v2_affix_catalog | none | default | yes | app/routes/experimental.py:197 | NOT env-gated; parses bundle JSON from disk per request |
| 45 | GET | `/api/experimental/v2/affixes/<path:affix_id>` | api_experimental.v2_affix_detail | none | default | no (grep) | app/routes/experimental.py:241 | NOT env-gated; parses bundle JSON from disk per request |
| 46 | GET | `/api/experimental/v2/affixes/debug` | api_experimental.v2_affix_debug | none | default | no (grep) | app/routes/experimental.py:279 | NOT env-gated; parses bundle JSON from disk per request |
| 47 | GET | `/api/experimental/v2/classes` | api_experimental.v2_classes | none | default | yes | app/routes/experimental.py:691 | NOT env-gated; parses bundle JSON from disk per request |
| 48 | GET | `/api/experimental/v2/classes/<path:class_id>` | api_experimental.v2_class_detail | none | default | no (grep) | app/routes/experimental.py:721 | NOT env-gated; parses bundle JSON from disk per request |
| 49 | GET | `/api/experimental/v2/classes/debug` | api_experimental.v2_class_mastery_debug | none | default | no (grep) | app/routes/experimental.py:708 | NOT env-gated; parses bundle JSON from disk per request |
| 50 | GET | `/api/experimental/v2/idols` | api_experimental.v2_idols | none | default | yes | app/routes/experimental.py:599 | NOT env-gated; parses bundle JSON from disk per request |
| 51 | GET | `/api/experimental/v2/idols/<path:idol_id>` | api_experimental.v2_idol_detail | none | default | no (grep) | app/routes/experimental.py:623 | NOT env-gated; parses bundle JSON from disk per request |
| 52 | GET | `/api/experimental/v2/idols/affixes` | api_experimental.v2_idol_affixes | none | default | yes | app/routes/experimental.py:639 | NOT env-gated; parses bundle JSON from disk per request |
| 53 | GET | `/api/experimental/v2/idols/affixes/<path:affix_id>` | api_experimental.v2_idol_affix_detail | none | default | no (grep) | app/routes/experimental.py:662 | NOT env-gated; parses bundle JSON from disk per request |
| 54 | GET | `/api/experimental/v2/idols/debug` | api_experimental.v2_idol_debug | none | default | no (grep) | app/routes/experimental.py:678 | NOT env-gated; parses bundle JSON from disk per request |
| 55 | GET | `/api/experimental/v2/items/bases` | api_experimental.v2_item_bases | none | default | yes | app/routes/experimental.py:308 | NOT env-gated; parses bundle JSON from disk per request |
| 56 | GET | `/api/experimental/v2/items/bases/<path:item_base_id>` | api_experimental.v2_item_base_detail | none | default | no (grep) | app/routes/experimental.py:345 | NOT env-gated; parses bundle JSON from disk per request |
| 57 | GET | `/api/experimental/v2/items/debug` | api_experimental.v2_item_debug | none | default | no (grep) | app/routes/experimental.py:416 | NOT env-gated; parses bundle JSON from disk per request |
| 58 | GET | `/api/experimental/v2/items/implicits` | api_experimental.v2_item_implicits | none | default | yes | app/routes/experimental.py:383 | NOT env-gated; parses bundle JSON from disk per request |
| 59 | GET | `/api/experimental/v2/masteries` | api_experimental.v2_masteries | none | default | yes | app/routes/experimental.py:737 | NOT env-gated; parses bundle JSON from disk per request |
| 60 | GET | `/api/experimental/v2/masteries/<path:mastery_id>` | api_experimental.v2_mastery_detail | none | default | no (grep) | app/routes/experimental.py:754 | NOT env-gated; parses bundle JSON from disk per request |
| 61 | GET | `/api/experimental/v2/modifiers` | api_experimental.v2_modifiers | none | default | no (grep) | app/routes/experimental.py:987 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 62 | GET | `/api/experimental/v2/modifiers/<path:modifier_id>` | api_experimental.v2_modifier_detail | none | default | no (grep) | app/routes/experimental.py:1035 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 63 | GET | `/api/experimental/v2/modifiers/debug` | api_experimental.v2_modifier_debug | none | default | yes | app/routes/experimental.py:1021 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 64 | GET | `/api/experimental/v2/passives` | api_experimental.v2_passives | none | default | yes | app/routes/experimental.py:770 | NOT env-gated; parses bundle JSON from disk per request |
| 65 | GET | `/api/experimental/v2/passives/<path:tree_id>` | api_experimental.v2_passive_detail | none | default | no (grep) | app/routes/experimental.py:806 | NOT env-gated; parses bundle JSON from disk per request |
| 66 | GET | `/api/experimental/v2/passives/<path:tree_id>/nodes/<path:node_id>` | api_experimental.v2_passive_node_detail | none | default | no (grep) | app/routes/experimental.py:825 | NOT env-gated; parses bundle JSON from disk per request |
| 67 | GET | `/api/experimental/v2/passives/debug` | api_experimental.v2_passive_debug | none | default | no (grep) | app/routes/experimental.py:793 | NOT env-gated; parses bundle JSON from disk per request |
| 68 | GET | `/api/experimental/v2/sets` | api_experimental.v2_sets | none | default | yes | app/routes/experimental.py:518 | NOT env-gated; parses bundle JSON from disk per request |
| 69 | GET | `/api/experimental/v2/sets/<path:set_id>` | api_experimental.v2_set_detail | none | default | no (grep) | app/routes/experimental.py:547 | NOT env-gated; parses bundle JSON from disk per request |
| 70 | GET | `/api/experimental/v2/sets/debug` | api_experimental.v2_set_debug | none | default | no (grep) | app/routes/experimental.py:592 | NOT env-gated; parses bundle JSON from disk per request |
| 71 | GET | `/api/experimental/v2/skills` | api_experimental.v2_skills | none | default | yes | app/routes/experimental.py:841 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 72 | GET | `/api/experimental/v2/skills/<path:skill_id>` | api_experimental.v2_skill_detail | none | default | no (grep) | app/routes/experimental.py:931 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 73 | GET | `/api/experimental/v2/skills/<path:skill_id>/tree` | api_experimental.v2_skill_tree_by_skill | none | default | no (grep) | app/routes/experimental.py:912 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 74 | GET | `/api/experimental/v2/skills/debug` | api_experimental.v2_skill_debug | none | default | no (grep) | app/routes/experimental.py:864 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 75 | GET | `/api/experimental/v2/skills/trees/<path:tree_id>` | api_experimental.v2_skill_tree_detail | none | default | no (grep) | app/routes/experimental.py:877 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 76 | GET | `/api/experimental/v2/skills/trees/<path:tree_id>/nodes/<path:node_id>` | api_experimental.v2_skill_node_detail | none | default | no (grep) | app/routes/experimental.py:896 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 77 | GET | `/api/experimental/v2/stats` | api_experimental.v2_stats | none | default | no (grep) | app/routes/experimental.py:947 | NOT env-gated; parses bundle JSON from disk per request |
| 78 | GET | `/api/experimental/v2/stats/<path:stat_id>` | api_experimental.v2_stat_detail | none | default | no (grep) | app/routes/experimental.py:971 | NOT env-gated; parses bundle JSON from disk per request |
| 79 | GET | `/api/experimental/v2/uniques` | api_experimental.v2_uniques | none | default | yes | app/routes/experimental.py:445 | NOT env-gated; parses bundle JSON from disk per request |
| 80 | GET | `/api/experimental/v2/uniques/<path:unique_id>` | api_experimental.v2_unique_detail | none | default | no (grep) | app/routes/experimental.py:482 | NOT env-gated; parses bundle JSON from disk per request |
| 81 | GET | `/api/experimental/v2/uniques/debug` | api_experimental.v2_unique_debug | none | default | no (grep) | app/routes/experimental.py:585 | NOT env-gated; parses bundle JSON from disk per request |
| 82 | GET | `/api/health` | health.health | none | 60 per 1 minute | no (grep) | app/routes/health.py:49 | no DB/Redis check |
| 83 | POST | `/api/import/build` | import.import_build | optional JWT | 2 per 1 minute | no (grep) | app/routes/import_route.py:502 | external fetch (LET/Maxroll up to 8x15s); writes Build+ImportFailure; Discord webhook sync |
| 84 | POST | `/api/import/let/json` | import.import_let_from_json | optional JWT | 20 per 1 minute | no (grep) | app/routes/import_route.py:421 | anon can create ImportFailure rows + Discord alerts |
| 85 | POST | `/api/import/url` | import.import_from_url | optional JWT | 20 per 1 minute | no (grep) | app/routes/import_route.py:306 | external fetch LET (15s timeout) |
| 86 | GET | `/api/jobs/<job_id>` | jobs.get_job | none | default | no (grep) | app/routes/jobs.py:29 | 8-hex job id; any caller can read any job |
| 87 | POST | `/api/load/game-data` | load.load_game_data | none | 5 per 1 minute | yes | app/routes/load.py:21 | **NO AUTH; hot-reloads pipeline from disk; leaks exception text** |
| 88 | GET | `/api/meta/snapshot` | meta.snapshot | none | 30 per 1 minute | yes | app/routes/meta.py:17 |  |
| 89 | GET | `/api/meta/trending` | meta.trending | none | 30 per 1 minute | yes | app/routes/meta.py:24 |  |
| 90 | POST | `/api/optimize/build` | optimize.optimize_build | none | 5 per 1 minute | yes | app/routes/optimize.py:30 | max_variants<=1000; 8.3s measured |
| 91 | GET | `/api/passives` | passives.list_passives | none | default | yes | app/routes/passives.py:98 |  |
| 92 | GET | `/api/passives/<character_class>` | passives.get_class_tree | none | default | yes | app/routes/passives.py:132 |  |
| 93 | GET | `/api/passives/<character_class>/<mastery>` | passives.get_mastery_tree | none | default | yes | app/routes/passives.py:151 |  |
| 94 | GET | `/api/profile` | profile.get_profile | required | default | yes | app/routes/profile.py:25 |  |
| 95 | GET | `/api/profile/builds` | profile.profile_builds | required | default | yes | app/routes/profile.py:77 | per_page capped 100 in service |
| 96 | GET | `/api/profile/sessions` | profile.profile_sessions | required | default | yes | app/routes/profile.py:98 | per_page unbounded; N+1 on steps; int() ValueError->500 |
| 97 | GET | `/api/ref/affix-categories` | ref.get_affix_categories_endpoint | none | default | no (grep) | app/routes/ref.py:295 |  |
| 98 | GET | `/api/ref/affixes` | ref.get_affixes | none | default | yes | app/routes/ref.py:204 |  |
| 99 | GET | `/api/ref/base-items` | ref.get_base_items_endpoint | none | default | yes | app/routes/ref.py:389 |  |
| 100 | GET | `/api/ref/base-items/<base_type>` | ref.get_base_item_endpoint | none | default | no (grep) | app/routes/ref.py:420 |  |
| 101 | GET | `/api/ref/blessings` | ref.get_blessings_endpoint | none | default | yes | app/routes/ref.py:575 |  |
| 102 | GET | `/api/ref/classes` | ref.get_classes | none | default | yes | app/routes/ref.py:170 |  |
| 103 | GET | `/api/ref/crafting-rules` | ref.get_crafting_rules_endpoint | none | default | yes | app/routes/ref.py:382 |  |
| 104 | GET | `/api/ref/damage-types` | ref.get_damage_types_endpoint | none | default | yes | app/routes/ref.py:470 |  |
| 105 | GET | `/api/ref/enemy-profiles` | ref.get_enemy_profiles_endpoint | none | default | yes | app/routes/ref.py:452 |  |
| 106 | GET | `/api/ref/enemy-profiles/<enemy_id>` | ref.get_enemy_profile_endpoint | none | default | no (grep) | app/routes/ref.py:460 |  |
| 107 | GET | `/api/ref/fp-ranges` | ref.get_fp_ranges_endpoint | none | default | yes | app/routes/ref.py:430 |  |
| 108 | GET | `/api/ref/fp-ranges/<rarity>` | ref.get_fp_range_endpoint | none | default | no (grep) | app/routes/ref.py:437 |  |
| 109 | GET | `/api/ref/implicit-stats` | ref.get_implicit_stats_endpoint | none | default | yes | app/routes/ref.py:486 |  |
| 110 | GET | `/api/ref/implicit-stats/<item_type>` | ref.get_implicit_stat_endpoint | none | default | no (grep) | app/routes/ref.py:494 |  |
| 111 | GET | `/api/ref/item-types` | ref.get_item_types | none | default | yes | app/routes/ref.py:176 |  |
| 112 | GET | `/api/ref/passives` | ref.get_passives | none | default | no (grep) | app/routes/ref.py:301 |  |
| 113 | GET | `/api/ref/rarities` | ref.get_rarities_endpoint | none | default | yes | app/routes/ref.py:478 |  |
| 114 | GET | `/api/ref/skills` | ref.get_skills | none | default | yes | app/routes/ref.py:354 |  |
| 115 | GET | `/api/ref/uniques` | ref.get_uniques_endpoint | none | default | yes | app/routes/ref.py:525 |  |
| 116 | GET | `/api/ref/uniques/<slug>` | ref.get_unique_endpoint | none | default | yes | app/routes/ref.py:561 |  |
| 117 | POST | `/api/simulate/build` | simulate.simulate_build | none | 30 per 1 minute | yes | app/routes/simulate.py:281 | async mode -> job pool |
| 118 | POST | `/api/simulate/combat` | simulate.simulate_combat | none | 20 per 1 minute | no (grep) | app/routes/simulate.py:120 | n_simulations<=50k; async mode -> unbounded thread-pool queue |
| 119 | POST | `/api/simulate/conditional` | conditional.simulate_conditional | none | 30 per 1 minute | yes | app/routes/conditional.py:98 |  |
| 120 | POST | `/api/simulate/defense` | simulate.simulate_defense | none | 30 per 1 minute | no (grep) | app/routes/simulate.py:165 |  |
| 121 | POST | `/api/simulate/encounter` | simulate.simulate_encounter | none | 15 per 1 minute | yes | app/routes/simulate.py:244 | bounded; 11.7s worst case measured |
| 122 | POST | `/api/simulate/encounter-build` | simulate.simulate_encounter_from_build | none | 20 per 1 minute | yes | app/routes/simulate.py:261 |  |
| 123 | POST | `/api/simulate/multi-target` | multi_target.simulate_multi_target | none | 20 per 1 minute | yes | app/routes/multi_target.py:80 | **unbounded max_duration/tick/targets; 17s+1.6GB measured, larger inputs OOM-killed** |
| 124 | POST | `/api/simulate/optimize` | simulate.simulate_optimize | none | 10 per 1 minute | no (grep) | app/routes/simulate.py:186 |  |
| 125 | POST | `/api/simulate/rotation` | rotation.simulate_rotation | none | 10 per 1 minute | yes | app/routes/rotation.py:29 | 7.6s worst case measured |
| 126 | POST | `/api/simulate/sensitivity` | simulate.simulate_sensitivity | none | 10 per 1 minute | no (grep) | app/routes/simulate.py:217 |  |
| 127 | POST | `/api/simulate/stats` | simulate.simulate_stats | none | 60 per 1 minute | no (grep) | app/routes/simulate.py:86 |  |
| 128 | GET | `/api/skills/<skill_id>/tree` | skills.get_skill_tree | none | 30 per 1 minute | yes | app/routes/skills.py:180 |  |
| 129 | GET | `/api/version` | version.get_version | none | default | yes | app/routes/version.py:58 | spawns git subprocess per request |
| 130 | GET | `/debug/forge-safe-affixes` | debug.forge_safe_affixes | none | default | no (grep) | app/routes/debug.py:25 | env-gated (FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED); 404 by default |
| 131 | GET | `/experimental/forge-safe-affixes` | experimental.forge_safe_affix_catalog | none | default | no (dup mount) | app/routes/experimental.py:78 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 132 | GET | `/experimental/forge-safe-affixes/<affix_id>` | experimental.forge_safe_affix_detail | none | default | no (dup mount) | app/routes/experimental.py:170 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 133 | GET | `/experimental/forge-safe-affixes/compare-legacy` | experimental.compare_forge_safe_affixes_to_legacy | none | default | no (dup mount) | app/routes/experimental.py:102 | env-gated FORGE_SAFE_AFFIX_CATALOG_ENABLED (404 default) |
| 134 | GET | `/experimental/v2/affixes` | experimental.v2_affix_catalog | none | default | no (dup mount) | app/routes/experimental.py:197 | NOT env-gated; parses bundle JSON from disk per request |
| 135 | GET | `/experimental/v2/affixes/<path:affix_id>` | experimental.v2_affix_detail | none | default | no (dup mount) | app/routes/experimental.py:241 | NOT env-gated; parses bundle JSON from disk per request |
| 136 | GET | `/experimental/v2/affixes/debug` | experimental.v2_affix_debug | none | default | no (dup mount) | app/routes/experimental.py:279 | NOT env-gated; parses bundle JSON from disk per request |
| 137 | GET | `/experimental/v2/classes` | experimental.v2_classes | none | default | no (dup mount) | app/routes/experimental.py:691 | NOT env-gated; parses bundle JSON from disk per request |
| 138 | GET | `/experimental/v2/classes/<path:class_id>` | experimental.v2_class_detail | none | default | no (dup mount) | app/routes/experimental.py:721 | NOT env-gated; parses bundle JSON from disk per request |
| 139 | GET | `/experimental/v2/classes/debug` | experimental.v2_class_mastery_debug | none | default | no (dup mount) | app/routes/experimental.py:708 | NOT env-gated; parses bundle JSON from disk per request |
| 140 | GET | `/experimental/v2/idols` | experimental.v2_idols | none | default | no (dup mount) | app/routes/experimental.py:599 | NOT env-gated; parses bundle JSON from disk per request |
| 141 | GET | `/experimental/v2/idols/<path:idol_id>` | experimental.v2_idol_detail | none | default | no (dup mount) | app/routes/experimental.py:623 | NOT env-gated; parses bundle JSON from disk per request |
| 142 | GET | `/experimental/v2/idols/affixes` | experimental.v2_idol_affixes | none | default | no (dup mount) | app/routes/experimental.py:639 | NOT env-gated; parses bundle JSON from disk per request |
| 143 | GET | `/experimental/v2/idols/affixes/<path:affix_id>` | experimental.v2_idol_affix_detail | none | default | no (dup mount) | app/routes/experimental.py:662 | NOT env-gated; parses bundle JSON from disk per request |
| 144 | GET | `/experimental/v2/idols/debug` | experimental.v2_idol_debug | none | default | no (dup mount) | app/routes/experimental.py:678 | NOT env-gated; parses bundle JSON from disk per request |
| 145 | GET | `/experimental/v2/items/bases` | experimental.v2_item_bases | none | default | no (dup mount) | app/routes/experimental.py:308 | NOT env-gated; parses bundle JSON from disk per request |
| 146 | GET | `/experimental/v2/items/bases/<path:item_base_id>` | experimental.v2_item_base_detail | none | default | no (dup mount) | app/routes/experimental.py:345 | NOT env-gated; parses bundle JSON from disk per request |
| 147 | GET | `/experimental/v2/items/debug` | experimental.v2_item_debug | none | default | no (dup mount) | app/routes/experimental.py:416 | NOT env-gated; parses bundle JSON from disk per request |
| 148 | GET | `/experimental/v2/items/implicits` | experimental.v2_item_implicits | none | default | no (dup mount) | app/routes/experimental.py:383 | NOT env-gated; parses bundle JSON from disk per request |
| 149 | GET | `/experimental/v2/masteries` | experimental.v2_masteries | none | default | no (dup mount) | app/routes/experimental.py:737 | NOT env-gated; parses bundle JSON from disk per request |
| 150 | GET | `/experimental/v2/masteries/<path:mastery_id>` | experimental.v2_mastery_detail | none | default | no (dup mount) | app/routes/experimental.py:754 | NOT env-gated; parses bundle JSON from disk per request |
| 151 | GET | `/experimental/v2/modifiers` | experimental.v2_modifiers | none | default | no (dup mount) | app/routes/experimental.py:987 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 152 | GET | `/experimental/v2/modifiers/<path:modifier_id>` | experimental.v2_modifier_detail | none | default | no (dup mount) | app/routes/experimental.py:1035 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 153 | GET | `/experimental/v2/modifiers/debug` | experimental.v2_modifier_debug | none | default | no (dup mount) | app/routes/experimental.py:1021 | NOT env-gated; parses bundle JSON from disk per request; 37MB file, ~2.7s & ~135MB/request measured |
| 154 | GET | `/experimental/v2/passives` | experimental.v2_passives | none | default | no (dup mount) | app/routes/experimental.py:770 | NOT env-gated; parses bundle JSON from disk per request |
| 155 | GET | `/experimental/v2/passives/<path:tree_id>` | experimental.v2_passive_detail | none | default | no (dup mount) | app/routes/experimental.py:806 | NOT env-gated; parses bundle JSON from disk per request |
| 156 | GET | `/experimental/v2/passives/<path:tree_id>/nodes/<path:node_id>` | experimental.v2_passive_node_detail | none | default | no (dup mount) | app/routes/experimental.py:825 | NOT env-gated; parses bundle JSON from disk per request |
| 157 | GET | `/experimental/v2/passives/debug` | experimental.v2_passive_debug | none | default | no (dup mount) | app/routes/experimental.py:793 | NOT env-gated; parses bundle JSON from disk per request |
| 158 | GET | `/experimental/v2/sets` | experimental.v2_sets | none | default | no (dup mount) | app/routes/experimental.py:518 | NOT env-gated; parses bundle JSON from disk per request |
| 159 | GET | `/experimental/v2/sets/<path:set_id>` | experimental.v2_set_detail | none | default | no (dup mount) | app/routes/experimental.py:547 | NOT env-gated; parses bundle JSON from disk per request |
| 160 | GET | `/experimental/v2/sets/debug` | experimental.v2_set_debug | none | default | no (dup mount) | app/routes/experimental.py:592 | NOT env-gated; parses bundle JSON from disk per request |
| 161 | GET | `/experimental/v2/skills` | experimental.v2_skills | none | default | no (dup mount) | app/routes/experimental.py:841 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 162 | GET | `/experimental/v2/skills/<path:skill_id>` | experimental.v2_skill_detail | none | default | no (dup mount) | app/routes/experimental.py:931 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 163 | GET | `/experimental/v2/skills/<path:skill_id>/tree` | experimental.v2_skill_tree_by_skill | none | default | no (dup mount) | app/routes/experimental.py:912 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 164 | GET | `/experimental/v2/skills/debug` | experimental.v2_skill_debug | none | default | no (dup mount) | app/routes/experimental.py:864 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 165 | GET | `/experimental/v2/skills/trees/<path:tree_id>` | experimental.v2_skill_tree_detail | none | default | no (dup mount) | app/routes/experimental.py:877 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 166 | GET | `/experimental/v2/skills/trees/<path:tree_id>/nodes/<path:node_id>` | experimental.v2_skill_node_detail | none | default | no (dup mount) | app/routes/experimental.py:896 | NOT env-gated; parses bundle JSON from disk per request; 20MB tree bundle, ~1.6s/request |
| 167 | GET | `/experimental/v2/stats` | experimental.v2_stats | none | default | no (dup mount) | app/routes/experimental.py:947 | NOT env-gated; parses bundle JSON from disk per request |
| 168 | GET | `/experimental/v2/stats/<path:stat_id>` | experimental.v2_stat_detail | none | default | no (dup mount) | app/routes/experimental.py:971 | NOT env-gated; parses bundle JSON from disk per request |
| 169 | GET | `/experimental/v2/uniques` | experimental.v2_uniques | none | default | no (dup mount) | app/routes/experimental.py:445 | NOT env-gated; parses bundle JSON from disk per request |
| 170 | GET | `/experimental/v2/uniques/<path:unique_id>` | experimental.v2_unique_detail | none | default | no (dup mount) | app/routes/experimental.py:482 | NOT env-gated; parses bundle JSON from disk per request |
| 171 | GET | `/experimental/v2/uniques/debug` | experimental.v2_unique_debug | none | default | no (dup mount) | app/routes/experimental.py:585 | NOT env-gated; parses bundle JSON from disk per request |

## 6. UNKNOWNs

* Whether Render passes the real client IP as the TCP peer (decides API-7 severity). Check production logs for the `ip=` field in `rate_limit_exceeded` lines.
* Whether `REDIS_URL` was reachable at boot in production (otherwise the limiter is in-memory per worker).
* Render instance memory (starter is commonly 512 MB) and whether OOM restarts have occurred.
* Whether `docs/generated/*.json` bundles are present in the production checkout (`rootDir: backend`; the bundles live at the repo root `docs/generated/`). If they are absent, the v2 endpoints return 404 and API-3 does not apply.
* Whether production `data/items/affixes.json` has been modified through API-1. The filesystem is ephemeral per deploy, so tampering would not survive a redeploy, and there is no audit trail.
* Actual traffic and abuse volume. No production logs were read.

## 7. What this does NOT prove

* All probes ran against the `testing` config (rate limiting disabled, in-memory SQLite, no Redis) in a single process. They prove the code paths, not production behaviour under gunicorn/Render.
* Timing and RSS numbers come from this machine, not Render hardware.
* Frontend usage is grep-based. A route not found by grep may still be called through a dynamically assembled path.
* No production endpoint was called. The live presence of each route, the env flags, and the deployed commit were not verified (`/api/version` would report the commit but was not queried).
* This audit did not review the correctness of simulation math (covered elsewhere), dependency CVEs, or the frontend's own XSS surface.
