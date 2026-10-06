# 12 — Frontend / Product Reality Audit (Phase 10)

- Repo HEAD: `1efcef76ba03f82711b5d6f11eedbc48d5ccbefa` (2026-05-14)
- Audit date: 2026-10-06
- Scope: `frontend/` (Vite + React + TS), router, API client, importer UX, trust labeling, frontend game-data copies, vitest coverage. Electron shell checked only briefly.
- Mode: audit only. No repo files were changed except this report. All scratch output is in the session scratchpad (`.../scratchpad/fe/`).

---

## 0. Headline facts

1. **Production API base URL is missing `/api` (P0, static + simulated proof).** `render.yaml:95-96` sets `VITE_API_BASE_URL=https://api.epochforge.gg`. `frontend/src/lib/api.ts:51-54` uses that value as the base, and every client path is written relative to `/api` (`/builds`, `/auth/me`, `/import/build`, ...). Every Flask blueprint is mounted under `/api/...` (`backend/app/__init__.py:222-250`). A production-mode build made with the render.yaml value contains the literal `https://api.epochforge.gg/auth/discord`. Driving that build with Playwright showed **100% of API requests going to un-prefixed paths** (`GET /builds`, `POST /import/build`, `POST /builds`, ...). The backend answers these with its JSON 404 handler (`backend/app/__init__.py:266-269`). The repo's own docs expect `https://api.epochforge.gg/api/...` (`docs/production_setup.md:94`). `docker-compose.yml:66` includes `/api`, which is correct. Whether the live Render dashboard overrides this value is **UNKNOWN**: production could not be reached (the egress proxy refused CONNECT with 403, which is the proxy's response, not the site's).
2. **Sign-in is affected too.** The "Sign In" links (`TopBar.tsx:69-71`, `BuildPlannerPage.tsx:1187`) render as `https://api.epochforge.gg/auth/discord`. That path has no route; the only route is `/api/auth/discord`.
3. **The v2.5 "trust" debug pages cannot work on the static site.** Eight public routes (`App.tsx:267-276`) call `fetch()` with root-relative `/experimental/v2/...` or `/api/experimental/...` and never use the API base. On Render, the `/* → /index.html` rewrite (`render.yaml:101-102`) returns HTML with status 200. This was observed: "Debug endpoint unavailable — Backend returned an unreadable response (200)." These paths only work through the Vite dev proxy (`vite.config.ts` proxies `/api` and `/experimental`).
4. **Importer UX:** a Maxroll 403 is shown as red text saying the build "may be expired, or Maxroll may have changed their format (attempts: HTTP 403; ...)". There is no fallback for Maxroll: the JSON tab accepts only Last Epoch Tools `window.buildInfo` or Forge JSON. The Last Epoch Tools (LET) bookmarklet and paste path exists and is well explained. However, the "Import URL" tab still accepts and submits LET URLs, and the "Quick Fetch" tab is permanently disabled.
5. **Anonymous user dead ends:** anonymous saving is allowed. But anonymous or imported builds have no Edit button (`isOwner` requires an author), there is no share or copy-link control, and no UI can change `is_public`. Imported builds are forced private (`import_route.py:592`), so they can never be published from the UI. The `/workspace/*` editor has no save path at all.
6. **Trust labeling stops at the trust pages.** The trust components (`components/v2/*`) are imported only by the `/trusted-data/*` and `/debug/v2*` pages. The production DPS, EHP and letter-grade surfaces (planner "Analyze Build", `/encounter`, `/optimizer`, `/rotation`, `/conditional`, `/multi-target`, `/monte-carlo`, `/crafting`) show numbers without trust or experimental badges. The only caveats are a benchmark disclaimer and a footer "known limitations" link.
7. **Tests:** 49 vitest files and 916 tests; 17 failed and 899 passed (a concurrent run on the same HEAD). Failures are stale navigation and GlobalSearch expectations. **There are zero tests** for `BuildImportModal`, planner save/edit, `lib/api.ts` base-URL composition, or the v2 debug pages' fetch base.

---

## 1. Method and commands

| Step | Command / action |
|---|---|
| Router | `sed -n 1,300p frontend/src/App.tsx` |
| Frontend API paths | `grep -rnoE "(get|post|patch|del|apiGet|apiPost)...\(['\"\`]/..."` over `frontend/src` (excluding `__tests__`); manual read of `lib/api.ts:140-677` and `services/*.ts` |
| Backend routes (static) | AST script `scratchpad/fe/routes.py` over `backend/app/routes/*.py` and `register_blueprint(..., url_prefix=)` → `scratchpad/fe/backend_routes.tsv` (171 rules) |
| Backend routes (live URL map) | Reused another investigator's `scratchpad/urlmap.json` (`create_app("testing").url_map`, 172 rules). Static and live differ only by `/static/<path>`, so the static extraction is exact. |
| Prod-config build | `VITE_API_BASE_URL=https://api.epochforge.gg npx vite build --outDir scratchpad/fe/dist` (exit 0). `grep -o "https://api.epochforge.gg..." dist/assets/*.js` |
| Behavior simulation | `scratchpad/fe/pw.cjs` and `pw2.cjs` (Playwright 1.56.1, Chromium from `/opt/pw-browsers`). A Node static server mimics the Render rewrite. Requests to `api.epochforge.gg` are intercepted (never sent): un-prefixed paths get the backend's 404 JSON body, and `/api/*` gets 503 "unmodeled". 20 routes were visited, plus the importer flow. Outputs: `scratchpad/fe/pw-out/pw-results.json`, `pw2-prodcfg.json`, `pw2-hypo403.json`, and screenshots. |
| Production reachability | `curl https://epochforge.gg/` and `curl https://api.epochforge.gg/api/health` both returned `CONNECT tunnel failed, response 403` (proxy policy; see `$HTTPS_PROXY/__agentproxy/status` recentRelayFailures). **UNKNOWN** live state. |
| Data comparison | Python regex over `frontend/src/data/{passiveTrees,skillTrees}/index.ts` vs `data/classes/{passives,skills_with_trees}.json` |
| Bookmarklet parity | Node: parse the inline `LET_BOOKMARKLET` literal and compare it with `public/bookmarklets/let-import.bookmarklet.txt`: **identical (781 chars)** |
| Orphans | grep of `import ... '/<Basename>'` across `src` (excluding tests) |
| Tests | Read `scratchpad/vitest.log` (concurrent `npx vitest run`, same HEAD; this investigator did not rerun, to avoid racing). `frontend/node_modules` already existed; no `npm ci` was run by this investigator. |

---

## 2. Route table

Legend:
- **Code status** assumes the API base is correct (`.../api`): **works**, **partial**, **stale** (unlinked or superseded), or **dead** (cannot function).
- **Prod-config sim** is the behavior observed under the render.yaml value.
- **Nav** means the route is linked from the Sidebar (`Sidebar.tsx:165-174`).
- All listed frontend API paths exist in the backend URL map once `/api` is prepended. No frontend-called path is missing from the backend.

| Route | Component | Nav | Frontend API calls (→ backend `/api` + path) | Code status | Prod-config sim | Notes |
|---|---|---|---|---|---|---|
| `/` | DashboardPage | Y | GET /builds, /meta/snapshot, /ref/affixes, /ref/skills, /version | works | **misleading**: "0 COMMUNITY BUILDS · 0 SKILLS · 0 AFFIXES", "No builds yet", "Season 4 · Patch 1.4.3" | Hardcoded fallbacks at `DashboardPage.tsx:159,192-193` |
| `/home` | HomePage | N | none | stale | static | Unlinked marketing page; features hardcoded as `status: "Live"` (`HomePage.tsx:11,21,31`) |
| `/builds` | BuildsPage | Y | GET /builds | works | "No builds found — Be the first to share a build" | API failure looks the same as an empty catalog |
| `/build` | BuildPlannerPage (create) | Y | GET /passives/:class, /ref/blessings, /version; POST /builds; POST /import/build, /import/let/json, /import/url | works | Save → toast "Not found"; Import → "Not found" | See §3 |
| `/build/:slug` | BuildPlannerPage (BuildSummary) | via links | GET /builds/:slug, POST /builds/:slug/view, POST /builds/:slug/simulate, GET /builds/:slug/optimize, /analysis/*, /entities/bosses, /skills/:id/tree, /builds/:slug/skills, PATCH node, POST vote | partial | "Build not found" | No Edit for anonymous or imported builds (§3); untrusted DPS grade (§4) |
| `/workspace/new`, `/workspace/:slug` | UnifiedBuildPage | N | GET /builds/:slug, POST /simulate/build (debounced) | partial (no save) | renders; analysis would fail | Store `store/buildWorkspace.ts` has no persist; no create/update call anywhere in workspace |
| `/craft`, `/craft/:slug` | CraftSimulatorPage | Y | GET /ref/affixes, /ref/base-items, /ref/fp-ranges; craft session CRUD | works (local sim + server sessions) | renders local sim | Labeled "LOCAL / Simulating locally". FP mirror matches `data/items/crafting_rules.json` |
| `/affixes` | AffixEditorPage | N | GET /admin/affixes, PATCH /admin/affixes/:id | works | "Not found" | **Unauthenticated admin write** (`admin.py:66-69` has no auth decorator; writes `affixes.json`). No frontend gate either. |
| `/affix-catalog` | AffixCatalogPage | N | GET /affixes/catalog, /affixes/catalog/summary | works | error | Unlinked |
| `/passives` | PassiveTreePage | Y | GET /passives/:class (+ bundled tree data) | works | "Error loading passive tree — Not found" | |
| `/compare` | BuildComparisonPage | via links | GET /builds/:a, /builds/:b | works | n/a | `compareApi` (`/compare/:a/:b`) is defined but unused |
| `/report/:slug` | ReportPage | N | GET /builds/:slug/report | works | n/a | 0 in-app links found |
| `/meta` | MetaSnapshotPage | Y | GET /meta/snapshot, /meta/trending | works | header only, no data, no error | Silent empty state |
| `/encounter` (`/simulation` alias) | SimulationPage → BuildEditorPage / EncounterSimulatorPage | Y | POST /simulate/encounter-build, /simulate/encounter | works | renders form | DPS shown with no trust label |
| `/build-editor` | BuildEditorPage | N | POST /simulate/encounter-build | stale (duplicate of `/encounter` Build mode) | | |
| `/optimizer` | OptimizerPage | N | POST /optimize/build | works | | Unlinked; no trust label |
| `/rotation` | RotationBuilderPage | N | POST /simulate/rotation | works | | Unlinked; no trust label |
| `/conditional` | ConditionalBuilderPage | N | POST /simulate/conditional | works | | Unlinked; no trust label |
| `/multi-target` | MultiTargetSimulatorPage | N | POST /simulate/multi-target | works | | Unlinked; no trust label |
| `/data-manager` | DataManagerPage | N | POST /load/game-data | works | | Unlinked; `load.py` route has only a rate limit and no auth |
| `/monte-carlo` | MonteCarloPage | N | none (client-side Box-Muller on toy inputs) | stale or misleading | renders | Claims to "characterise build consistency"; inputs are not a build; comparison panel is a placeholder |
| `/crafting` | CraftingPage | N | POST /craft/predict | partial or misleading | | Fabricated ±5% "confidence interval" and `fracture_rate = 1 - completion` (`CraftingPage.tsx:100-105`) |
| `/classes` | ClassesPage | Y | GET /ref/classes | works | "Error loading classes — Not found" | |
| `/bis-search` | BisSearchPage | Y | POST /bis/search, GET /ref/affixes | works | renders form | |
| `/crafting-workspace` | CraftingWorkspace | N | POST /craft/predict | stale | | Unlinked |
| `/profile` | UserProfilePage | Y | GET /profile, /profile/builds, /profile/sessions | works (auth) | redirects to `/` | Anonymous users are silently redirected (`UserProfilePage.tsx:311`), with no explanation |
| `/trusted-data` | TrustedDataExplanationPage | footer/debug | none (static copy) | works | works | |
| `/trusted-data/support` | TrustedDataSupportMatrixPage | — | none | works | works | Says "Production planner consumption is false" |
| `/trusted-data/pre-v3-readiness` | PreV3MechanicalReadinessPage | — | none | works | works | |
| `/debug/v2` | V2DebugNavigationPage | — | none | works | works | Links to the 8 pages below |
| `/debug/forge-safe-affixes` (`/debug/v2-affixes` alias) | ForgeSafeAffixesDebugPage | — | fetch `/experimental/v2/affixes` (root-relative) | **dead in prod** | (not visited; same pattern) | `ForgeSafeAffixesDebugPage.tsx:48,56` |
| `/debug/v2-items` | V2ItemsDebugPage | — | fetch `/experimental/v2/items/*` | **dead in prod** | | `:37,41` |
| `/debug/v2-unique-sets` | V2UniqueSetDebugPage | — | fetch `/experimental/v2/{uniques,sets}` | **dead in prod** | | `:38,42` |
| `/debug/v2-idols` | V2IdolsDebugPage | — | fetch `/experimental/v2/idols*` | **dead in prod** | | `:35,39` |
| `/debug/v2-classes` | V2ClassMasteryDebugPage | — | fetch `/experimental/v2/{classes,masteries}` | **dead in prod** | | `:35,39` |
| `/debug/v2-passives` | V2PassivesDebugPage | — | fetch `/experimental/v2/passives` | **dead in prod** | | `:36,40` |
| `/debug/v2-skills` | V2SkillsDebugPage | — | fetch `/experimental/v2/skills` | **dead in prod** | **observed**: "Backend returned an unreadable response (200)" | `:36,40` |
| `/debug/v2-stats-modifiers` | V2StatsModifiersDebugPage | — | fetch `/api/experimental/v2/modifiers/debug` | **dead in prod** | **observed**: same message | `:33` |
| `/movement-debug`, `/viz-debug`, `/craft-debug`, `/debug`, `/data-flow` | dev-only (`IS_DEV`) | — | various | dev only | 404 in prod build | `App.tsx:278-287` |
| `/passive-tree`, `/planner` | aliases | — | — | works | | |
| `/auth/callback` | AuthCallbackPage | — | GET /auth/me | works | | |
| `*` | NotFoundPage | — | — | works | | `/builds/:slug` (GlobalSearch result link) lands here (observed) |

Counts: 52 `<Route>` elements in `App.tsx` (`grep -c "<Route "`): 1 layout route, 1 index route and 50 path routes. The path routes include 3 legacy aliases, 1 debug alias, 5 dev-only routes, `/auth/callback` and the catch-all. 10 routes are in the Sidebar. 17 non-debug routes have no in-app link (grep count 0, or only self/test references): `/home`, `/affix-catalog`, `/report/:slug`, `/optimizer`, `/rotation`, `/conditional`, `/multi-target`, `/data-manager`, `/monte-carlo`, `/crafting`, `/crafting-workspace`, `/build-editor`, `/workspace/*`, `/affixes` (linked only from 5 internal refs to `?q=` search), and others. The list is approximate; see the command in §1.

**Orphan source (not imported anywhere outside tests):** `pages/shared/SharedBuildPage.tsx` (126 lines), `pages/library/BuildLibraryPage.tsx` (142), `pages/user/UserBuildDashboard.tsx` (132), `pages/debug/IntegrationDebugPage.tsx` (252), `pages/bis/BisWorkspace.tsx` (267, uses `Math.random` scores), `pages/build/BuildWorkspace.tsx` (219), `components/features/build/SimulationDashboard.tsx` (739), `UniqueItemPicker.tsx` (247), `PassiveTreeGraph.tsx` (752), `SkillTreeGraph.tsx` (471), `lib/simulation.ts` (client-side DPS/EHP formulas, e.g. `Armor/(Armor+1000)`; unreferenced). `App.tsx:38-40` comments say several of these were "Removed", but the files remain. Test-only modules (`services/sharing/build_import_service.ts`, `services/build/build_manager.ts`, `services/presets/preset_manager.ts`, `components/comparison/*`, `components/history/*`, `components/diagnostics/PerformancePanel`) have 0 production importers. 8 of the 49 test files (`phase-ui-plus/*`) mostly exercise this unused code.

---

## 3. User journey (anonymous user), with dead ends

| # | Step | What happens (code) | Under render.yaml config (simulated) | Dead end? |
|---|---|---|---|---|
| 1 | Land on `/` | Dashboard: stats, top classes, CTA "Start planning" → `/build` | Shows **0 / 0 / 0** and "No builds yet" with no error. Season and patch fall back to hardcoded "4 / 1.4.3". | Misleading (looks like an empty, healthy site) |
| 2 | Click Sign In (TopBar or planner banner) | `href = ${VITE_API_BASE_URL}/auth/discord` | `https://api.epochforge.gg/auth/discord` → backend JSON 404 | **DE-1** (prod config) |
| 3 | `/build` → "Import Build" → **Import URL** tab, paste Maxroll URL | `POST /import/build`; anonymous allowed, rate limit **2/min** (`import_route.py:496-503`) | Red text: "Not found" | **DE-2** (prod config) |
| 3a | Same, routing fixed, Maxroll returns 403 (hypothetical, message copied verbatim from `maxroll_importer.py:716-719`) | Red text: "Could not fetch build data from Maxroll. The build may be expired, or Maxroll may have changed their format. (attempts: HTTP 403; HTTP 403; HTTP 403)" | observed in `pw2-hypo403.json` | **DE-3**: the cause is shown as expiry or format change, and nothing points to an alternative. The JSON tab does not accept Maxroll data. The "This issue has been reported" footer (`BuildImportModal.tsx:560`) checks `importError.includes("422")`, but backend messages never contain "422", so it never renders (even though the backend does record and alert). |
| 3b | Paste a LET URL in the Import URL tab | Accepted (`detectSource` returns `lastepochtools`; button stays enabled, verified) and POSTed. The inline hint says "Use JSON tab for LET". The validation message (`:93`) still lists LET as supported. | "Not found" | Contradictory copy. With correct routing, the backend fetches LET server-side, which the modal itself says cannot work. |
| 3c | **Quick Fetch** tab | Input and button are hard-disabled (`:419,432`) with the label "Temporarily Unavailable" | — | **DE-4**: permanent dead tab |
| 3d | **JSON** tab + bookmarklet | Bookmarklet link (draggable; copy is identical to `public/bookmarklets/let-import.bookmarklet.txt`); `copy(window.buildInfo)` fallback; auto-detect; `POST /import/let/json` | "Not found" | Workable path once routing is correct; best-explained path in the modal |
| 4 | Import success (URL) | Backend creates the build immediately (anonymous, `is_public=False`), modal offers "Open Build" → `/build/:slug` | — | — |
| 4b | Import success (JSON) | Applies the build to the create form; user must Save | — | — |
| 5 | Save (create) | `POST /builds`; anonymous allowed ("will be saved anonymously", `BuildPlannerPage.tsx:1431-1435`). Schema default `is_public=True` (`schemas/__init__.py:92`), so an anonymous save is public immediately. | toast "Not found" | DE-5 (prod config) |
| 6 | Edit saved or imported build | `BuildSummary` shows **Edit** only if `user && build.author?.id === user.id` (`:257,495-497`). Anonymous builds have no author, so there is no Edit button for anyone, even though the backend lets *anyone* PATCH an authorless build (`builds.py:206-213`). | — | **DE-6**: the user cannot edit their own anonymous or imported build in the UI |
| 7 | Make public / share | No `is_public` control anywhere in the frontend (grep: only type definitions). No share or copy-link button in BuildSummary; only "Export JSON" to the clipboard. Imported builds are forced private (`import_route.py:592`) but readable by anyone with the slug (`builds.py:178-196` has no `is_public` check). | — | **DE-7**: imported builds can never be published; sharing means copying the address bar by hand |
| 8 | Alternative editor `/workspace/:slug` | Loads the build into a Zustand store and runs a debounced `/simulate/build` | — | **DE-8**: no save; store not persisted; not linked from nav |
| 9 | Search a build (Ctrl+K) → click result | GlobalSearch links to `/builds/${slug}` (`GlobalSearch.tsx:155`); no such route | NotFound page (observed) | **DE-9** |
| 10 | `/profile` while anonymous | `<Navigate to="/" replace />` (`UserProfilePage.tsx:311`) | Silent bounce to the dashboard | Minor dead end |

---

## 4. Fallback and misleading-display inventory

Counts are over `frontend/src`, excluding tests.

| Pattern | Count | Notes |
|---|---|---|
| `?? 0` | 179 | 37 of these are on DPS, EHP, armor, crit or resistance values (see the list below) |
| `\|\| 0` | 5 | |
| `?? / \|\| "Unknown"` | 6 | `ImportPanel.tsx:33` (`character_class ?? "Unknown"`); `BaseItemSelector.tsx:36,47`; error strings |
| `?? / \|\| "—"/"-"/"N/A"` | 53 | mostly display placeholders (acceptable) |
| `Math.random` | 29 | CraftSimulator local sim (labeled LOCAL); MonteCarlo (unlabeled); BisWorkspace (orphan) |
| `mock` word | 14 | `CraftOutcomeChart.tsx:4` "mock normal-distribution outcome spread"; `CraftingPage.tsx:7` "client-side mock simulation" (comment, while the code now calls `/craft/predict`) |

High-impact fallbacks and misleading displays:

| ID | Location | Behavior | Trust label? |
|---|---|---|---|
| M1 | `BuildPlannerPage.tsx:634` → `simulation/BuildScoreCard.tsx:43-63` | Letter grade S–D from hardcoded caps (20,000 DPS, 8,000 EHP, survivability /100; weights 40/30/30). DPS `?? 0` means missing DPS produces a "D" grade. | **No** |
| M2 | `simulation/OffenseDefenseSplit.tsx:98-100,211-213` | DPS, crit and multiplier `?? 0`; benchmark bars | Only "Benchmarks are approximate…" plus a known-limitations link |
| M3 | `build-workspace/analysis/{OffenseCard:82-98, DefenseCard:100-103, BuildScoreCard:384-386, PrimarySkillBreakdown:53-54,148, SkillsSummaryTable:322}` | Missing fields render as 0 (for example "0 EHP", "0% armor") rather than "unavailable" | No |
| M4 | `DashboardPage.tsx:159,192-193` | `buildsTotal ?? 0`; patch `?? "1.4.3"`, season `?? 4` | No; shown even when `/version` fails (observed) |
| M5 | `MonteCarloPage.tsx` | Toy stochastic model presented as build consistency analysis | No |
| M6 | `CraftingPage.tsx:100-105` | `confidence_interval = completion ± 0.05` (made up); `fracture_rate = 1 - completion` (inferred) | No |
| M7 | `/encounter`, `/optimizer`, `/rotation`, `/conditional`, `/multi-target` results panels | DPS and damage numbers | No |
| M8 | `HomePage.tsx:11,21,31` | Every feature hardcoded as "Live" | n/a |
| M9 | `/builds`, `/meta`, `/` empty states | API failure shown as "No builds yet / be the first" | No error surfaced |

Where trust labeling **does** exist: `components/v2/{V2TrustBadge, V2StatusBadgeGroup, V2LimitationNotice, V2TrustSummaryPanels, V2PlannerAdapterStatusPanel, V2EnvelopePanels}`. These are used only by `pages/Trusted*`, `PreV3MechanicalReadinessPage` and `pages/debug/V2*`. `V2PlannerAdapterStatusPanel` is rendered only on `/debug/v2-stats-modifiers` (`V2StatsModifiersDebugPage.tsx:114`), which is itself dead in prod (§0.3). Elsewhere: the sidebar "BETA" pill (`Sidebar.tsx:237-239`) and the footer "known limitations" link (`AppLayout.tsx:103-111`) to GitHub. The trust pages state that no v2 data drives production planner output. Production planner numbers do not link back to those pages.

---

## 5. Frontend game data vs backend `data/`

| Asset | Frontend | Backend | Delta |
|---|---|---|---|
| Passive nodes | `src/data/passiveTrees/index.ts` (137 KB): 541 nodes, 535 distinct names | `data/classes/passives.json`: 541 entries, 537 names | Same count; **55 FE-only and 57 BE-only names** (for example FE "Blood Armour" vs BE "Blood Armor", "Argent Veil", "Berserker"). Spelling and patch drift. |
| Skill trees | `src/data/skillTrees/index.ts` (1.06 MB): 133 trees, 3,863 nodes | `data/classes/skills_with_trees.json`: 184 skills, 137 with `skillTree`, 3,875 nodes | **4 trees and 12 nodes missing in FE** |
| Raw tree metadata | `src/data/raw/{skill,char}-tree-{metadata,layout}.json` (3.85 MB) | No same-named file outside `frontend/` | Frontend-only source; provenance header only says "Auto-generated by merge script" (no version or patch stamp) |
| Skill damage table | `lib/gameData.ts:405+` `SKILL_STATS` (108 entries with `baseDamage`, `levelScaling`) | backend skill registry | Used only by orphan `lib/simulation.ts` (dead) |
| Class and mastery constants | `@constants` alias → `backend/src/constants` (`vite.config.ts`) | same files | Shared, no drift (by construction) |
| Crafting FP costs | `CraftSimulatorPage.tsx:49-55` | `data/items/crafting_rules.json` | Identical values |
| `frontend/public` | 460 files: 400 passive icons, 54 skill icons, 1 sprite webp, 2 bookmarklet files, `_redirects`, favicon, manifest. **No JSON game data.** | — | — |
| `data/version.json` | — | `patch_version: "unknown"`, synced 2026-04-26 | The frontend has no data-version marker at all |

---

## 6. Frontend tests (vitest)

- 49 test files and 916 tests (from `scratchpad/vitest.log`): **17 failed, 899 passed**. Two files fail:
  - `components/navigation.test.tsx`: 11 failures. The test expects "Data Manager" in the sidebar (removed) and an old GlobalSearch placeholder.
  - `integration/layout.test.tsx`: 6 failures (GlobalSearch open/close).
  - These failures are stale tests, not detected regressions.
- Coverage by area:
  - v2 debug and trust pages: 14 page tests plus 4 component tests. All of them mock `fetch` with relative URLs, so none would catch the production base-URL problem.
  - Workspace store and pages: 3 files.
  - Analysis cards: 6 files.
  - Hooks: 3 files.
  - `config/vite-proxy-routing.test.ts` asserts only that `vite.config.ts` contains `"/api"` and not `"/debug"`.
- **Not covered:**
  - `BuildImportModal` (0 references in tests)
  - `BuildPlannerPage` save, edit and ownership logic
  - `lib/api.ts` URL composition and the render.yaml env combination
  - GlobalSearch link targets vs routes
  - `AffixEditorPage` and its admin auth
  - Craft, BIS and simulation pages
- `tsc --noEmit` (another investigator's `scratchpad/tsc.log`) printed no diagnostics. The exit code was not captured: **UNKNOWN**.

---

## 7. Electron (brief)

`electron/main.js:20-22,113,154-157`: loads `http://localhost:5173` in dev and health-checks `http://localhost:5050/api/health`. This was not exercised. Whether a packaged Electron build points at the correct API base is **UNKNOWN**.

---

## 8. UNKNOWNs

- U1. The live production frontend bundle and the actual Render dashboard value of `VITE_API_BASE_URL`. Could differ from `render.yaml`; production was unreachable from this container (proxy 403).
- U2. Whether `api.epochforge.gg` sits behind a proxy or rewrite that adds `/api`. Nothing in the repo indicates one.
- U3. Whether Maxroll currently returns 403 to the backend. The UX for that case was simulated with the backend's own message string.
- U4. Real end-to-end import, save and simulation with a running backend. Not executed: a local backend was not started for this phase, and requests were intercepted.
- U5. `tsc` exit status (log has timing only).

## 9. What this does NOT prove

- It does not prove production is broken today. It proves that the committed deploy config plus the committed client code produce un-prefixed API URLs, and that a build made with that config fails exactly as described. A dashboard override would invalidate FE-1 and FE-2 in production (but not the repo defect).
- It does not validate any DPS, EHP or crafting number. It only shows where numbers are displayed without trust context. Calculation correctness is covered in `13_CALCULATION_TRUST_MATRIX.md`.
- The Playwright runs used a stubbed API, so page behavior *with real data* (rendering bugs, data-shape mismatches) is not covered.
- Route reachability counts come from grep and may miss dynamically built links.
- The vitest results come from a concurrent run on the same HEAD, not rerun by this investigator.

---

## Reconciliation note (cross-report review)

The FE-1/FE-2 analysis above is correct **for the committed configuration**: `frontend/src/lib/api.ts:51-54,88` builds `${VITE_API_BASE_URL}${path}`, the paths are `/api`-relative, and `render.yaml:95-96` sets `https://api.epochforge.gg` without `/api`.

Production evidence contradicts this as a *live* outage. The 2026-10 Discord import alert can only come from the backend handler behind `POST /api/import/build` (see 08_LAST_EPOCH_TOOLS_IMPORT_FORENSICS.md). So at least one production request reached the correctly prefixed route. The likely explanation is a Render-dashboard value that differs from the blueprint, but that is UNKNOWN until the dashboard is checked.

Final classification used in AUDIT_EVIDENCE.json:
- **FE-1:** P1, "committed blueprint drifts from production; re-applying it would break all API calls and Discord login".
- **FE-2:** merged into FE-1.

This note is not a confirmed live P0 outage.
