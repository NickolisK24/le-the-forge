# Frontend Backend Gameplay Route Audit

## Purpose

This diagnostics phase audits the frontend/backend gameplay data loading path after trust visibility routes were confirmed healthy. It is not v4.6 work and does not add planner authority, gameplay recommendations, ranking, scoring, production enablement, runtime mutation, or fake data.

## Root Cause

The frontend Docker service used `VITE_API_BASE_URL=http://backend:5000/api`. That hostname is valid between containers, but the browser runs on the host and cannot resolve `backend`. Gameplay pages such as `/classes` and `/passives` loaded the SPA over `localhost:5173`, then failed during client-side data fetching with the visible message `Network error - check your connection`.

Direct backend and Vite proxy probes showed that the gameplay endpoints were mounted and reachable:

- `GET http://localhost:5050/api/ref/classes`
- `GET http://localhost:5050/api/passives/Acolyte`
- `GET http://localhost:5173/api/ref/classes`
- `GET http://localhost:5173/api/passives/Acolyte`

The break was the browser-facing API base URL, not missing classes/passives data.

## Fix Applied

The fix separates the two meanings that were previously collapsed into one environment variable:

- Browser-facing API base: `/api`
- Container-internal Vite proxy target: `http://backend:5000`

`docker-compose.yml` now sets `VITE_API_BASE_URL=/api` and `VITE_API_PROXY_TARGET=http://backend:5000`. `frontend/vite.config.ts` now reads `VITE_API_PROXY_TARGET` for the dev server proxy while preserving the existing local default of `http://localhost:5050`.

Post-fix Docker/browser verification loaded `/classes`, `/passives`, `/builds`, `/meta`, and `/trusted-data/frontend-trust` without browser error logs. `/classes` rendered all 5 classes, and `/passives` rendered the Acolyte passive tree.

## Route Inventory

The audit covers these frontend routes and their data paths:

- `/classes` -> `GET /api/ref/classes`
- `/passives` -> `GET /api/passives/<class>`
- `/builds` -> `GET /api/builds`
- `/build` -> version, build, simulate, optimize, and view endpoints as page state requires
- `/craft` -> ref data, craft sessions, craft actions, and craft summaries
- `/crafting` -> `POST /api/craft/predict` and affix reference data
- `/bis-search` -> affix reference data and `POST /api/bis/search`
- `/simulation` -> alias to `/encounter`
- `/encounter` -> encounter simulation endpoints
- `/meta` -> `GET /api/meta/snapshot` and `GET /api/meta/trending`
- `/trusted-data` -> static trusted-data explanation surface
- `/trusted-data/frontend-trust` -> `GET /api/trust/visibility`

The requested names `/build-planner` and `/crafting-lab` are not currently registered routes. The real routes are `/build` and `/craft` or `/crafting`.

## Backend Route Inventory

The audited backend routes are mounted under `/api`:

- `/api/health`
- `/api/trust/visibility`
- `/api/ref/classes`
- `/api/passives`
- `/api/passives/Acolyte`
- `/api/builds`
- `/api/craft/predict`
- `/api/bis/search`
- `/api/simulate/encounter`
- `/api/meta/snapshot`

The audit did not add mutation routes and did not change backend gameplay semantics.

## Gameplay Data Source Result

Class data is served from backend `CLASS_META`. Passive data is seeded into the database and retains the existing JSON fallback at `data/classes/passives.json`. The audit did not introduce fake classes, fake passive trees, fake builds, fake craft results, or fake simulation data.

## Remaining Limitations

POST-backed routes such as BIS search, craft prediction, and encounter simulation still require page-specific payload validation if a separate issue appears after connectivity is restored. This phase only fixes the shared browser/backend connectivity break.

## Preserved Boundaries

This phase remains diagnostics and stabilization only. It preserves:

- no planner execution
- no build recommendations
- no ranking
- no scoring
- no automatic optimization
- no production enablement
- no runtime mutation
- no mutable trust state
- no fake gameplay data
- no broad frontend redesign
- no broad backend rewrite
