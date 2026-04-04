# Changelog

All notable changes to The Forge are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.3.0] — 2026-03-30

### Added

- **Passive tree leveling path tracker** — `PassiveProgressBar` component records allocation order as a scrollable, horizontal timeline
  - Each step chip shows step number, node name, and color-coded node type
  - Hover tooltip: name, type, estimated level, description
  - Click any chip (edit mode) to rewind the passive allocation to that point
  - Level ruler shows points spent vs. 113 max with milestone markers at 28 / 56 / 85 pts
  - Wired into view, edit, and create modes in `BuildPlannerPage`

- **Passive tree static auto-fit layout** — removed pan/zoom; tree now scales to fill the panel automatically based on the actual bounding box of all nodes

- **Real game passive tree positions** — all node x/y coordinates match actual in-game layout loaded from exported `char-tree-layout.json`

- **Passive tree connection rendering** — SVG lines drawn between connected nodes; path validation (BFS) ensures only reachable nodes can be allocated

- **Hexagonal node visuals with stone texture background** — themed passive tree SVG with hexagonal node shapes and a dark stone-texture panel background

- **`scripts/extract_images.py`** — UnityPy-based extraction attempt for passive node icon sprites (note: `a-r-*` icon IDs are custom export IDs and do not map to Unity sprite names in game files)

- **Backend engine layer** — `backend/app/engines/` module:
  - `stat_engine.py` — aggregates class base stats, mastery bonuses, passive node bonuses, gear affixes, and attribute scaling into a `BuildStats` dataclass
  - `combat_engine.py` — calculates DPS (hit damage, crit scaling, attack/cast speed) and runs Monte Carlo variance simulations
  - `defense_engine.py` — calculates effective health pool (EHP), resistance capping, survivability score, and weakness/strength detection
  - `optimization_engine.py` — ranks stat upgrades by DPS gain percentage to power the Upgrade Advisor
  - `craft_engine.py` — pure crafting math extracted from `craft_service.py` (optimal path search, Monte Carlo simulation, strategy comparison)

- **Build simulation API** — `POST /api/builds/<slug>/simulate`
  - Returns `{ stats, dps, monte_carlo, defense, stat_upgrades }` for any saved build
  - No authentication required

- **Engine test suite** — 4 new test files covering stat aggregation, DPS calculation, EHP formulas, and upgrade ranking

- **Expanded affix seed data** — `AFFIX_SEED_DATA` in `ref.py` now covers all 34 affixes with correct `stat_key` mappings (up from 12)

- **`CONTRIBUTING.md`** — setup instructions, branch conventions, architecture overview, PR checklist

- **`CHANGELOG.md`** — this file

- **`LICENSE`** — MIT

### Changed

- `craft_service.py` refactored to import pure math from `craft_engine.py`; service now handles orchestration only (DB operations, session management)
- `passiveTree: number[]` now stores allocation history in order (append on allocate, remove last occurrence on dealloc) rather than a flat id list — preserves leveling path
- `PassiveTreeGraph` migrated from radial layout → real game positions → static auto-fit; pan/zoom removed

### Fixed

- Horizontal overflow caused by leveling path progress bar pushing page layout wider — fixed via `min-w-0`/`overflow-hidden` across grid/flex container chain and `overflow-x-hidden` on `<main>`
- Passive allocation order was being destroyed on every toggle (was doing filter+fill; now appends/removes single entry)
- Syntax error in generated `passiveTrees/index.ts`
- Missing `getSkillTree` export causing blank screen crash
- Lowercase character class key lookup mismatch in `PassiveTreeGraph`

---

## [0.1.0] — 2026-03-16

### Added

- Discord OAuth2 authentication with JWT tokens
- Build Planner with passive tree canvas, skill selection, gear slot editor
- Frontend simulation engine (`simulation.ts`) — DPS, EHP, upgrade advisor running live in-browser
- Craft Simulator with real-time Monte Carlo simulation and strategy comparison
- Loot Filter builder with condition editor, preview panel, and `.filter` file export
- Meta Tracker with class distribution, tier breakdown, and trending builds
- User profile page with build/session history
- Reference API (`/api/ref/`) for classes, affixes, item types, and passive nodes
- Docker Compose development environment (Flask + PostgreSQL + Redis + Vite)
- Flask CLI commands: `flask seed`, `flask seed-builds`
- 40 tests across build CRUD, voting, and crafting engine

### Removed

- Instability and fracture mechanics — removed entirely to align with modern Last Epoch game design (as of 1.0)
