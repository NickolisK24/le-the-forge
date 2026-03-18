# Changelog

All notable changes to The Forge are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

- **Backend engine layer** — `backend/app/engines/` module:
  - `stat_engine.py` — aggregates class base stats, mastery bonuses, passive node bonuses, gear affixes, and attribute scaling into a `BuildStats` dataclass
  - `combat_engine.py` — calculates DPS (hit damage, crit scaling, attack/cast speed) and runs Monte Carlo variance simulations
  - `defense_engine.py` — calculates effective health pool (EHP), resistance capping, survivability score, and weakness/strength detection
  - `optimization_engine.py` — ranks stat upgrades by DPS gain percentage to power the Upgrade Advisor
  - `craft_engine.py` — pure crafting math extracted from `craft_service.py` (fracture risk, optimal path search, Monte Carlo simulation, strategy comparison)

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

---

## [0.1.0] — 2026-03-16

### Added

- Discord OAuth2 authentication with JWT tokens
- Build Planner with passive tree canvas, skill selection, gear slot editor
- Frontend simulation engine (`simulation.ts`) — DPS, EHP, upgrade advisor running live in-browser
- Craft Simulator with real-time fracture risk, Monte Carlo simulation, strategy comparison
- Loot Filter builder with condition editor, preview panel, and `.filter` file export
- Meta Tracker with class distribution, tier breakdown, and trending builds
- User profile page with build/session history
- Reference API (`/api/ref/`) for classes, affixes, item types, and passive nodes
- Docker Compose development environment (Flask + PostgreSQL + Redis + Vite)
- Flask CLI commands: `flask seed`, `flask seed-builds`
- 40 tests across build CRUD, voting, and crafting engine
