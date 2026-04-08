# Changelog

All notable changes to The Forge are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.8.0] -- 2026-04-08

### Added

- **Build Comparison Engine** -- `ComparisonEngine` accepting two build slugs, running full combat and defense simulations, returning structured comparison with DPS/EHP/stat deltas, per-category winners, and weighted overall winner (60% DPS / 40% EHP)
- **Meta Analytics Service** -- class/mastery distribution, popular skills and affixes, average stats by class, trending builds by view velocity, and patch breakdown
- **Build View Tracking** -- `BuildView` model for time-series view tracking with SHA-256 hashed IPs (raw IPs never stored), 1 view per IP per build per hour rate limit via Redis
- **Shared Build Reports** -- `BuildReportService` generating full report with identity, stats, DPS, EHP, top 3 upgrades, skills, gear, and OpenGraph meta tags for Discord link previews
- **SimulationComparison frontend component** -- fetches and displays DPS/EHP/skill comparison between two builds with winner badges and stat cards
- **Enhanced MetaSnapshotPage** -- clickable class distribution bars, mastery breakdown panel, popular skills and affixes charts, trending builds grid, summary strip
- **ReportPage** -- shareable build report page at `/report/:slug` with dynamic document title and OG meta tags
- **View tracking integration** -- fire-and-forget view tracking on build page load
- **Community Marshmallow schemas** -- `ComparisonSchema`, `MetaSnapshotSchema`, `BuildReportSchema` for response validation
- **`flask refresh-meta` CLI command** -- force-refresh meta analytics caches
- New API endpoints:
  - `GET /api/compare/<slug_a>/<slug_b>` -- build comparison with Redis cache (20min TTL, alphabetically sorted key)
  - `GET /api/meta/snapshot` -- full meta analytics (6hr TTL)
  - `GET /api/meta/trending` -- trending builds by view velocity (1hr TTL)
  - `POST /api/builds/<slug>/view` -- view tracking
  - `GET /api/builds/<slug>/report` -- shareable build report (1hr TTL)
- TypeScript interfaces for all community tool response shapes
- 23 new tests covering comparison engine, meta analytics, view tracking, build reports, and BuildView model

---

## [0.7.0] -- 2026-04-06

### Added

- **Boss Encounter Simulation** -- multi-phase boss fights with per-phase DPS, time-to-kill, survival scoring, mana sustainability checks, and enrage detection
- **Corruption Scaling Analysis** -- non-linear health/damage multiplier curves, DPS efficiency tracking across breakpoints, recommended max corruption with configurable survival threshold
- **Gear Upgrade Ranker** -- per-slot candidate generation from affix registry, affix combo synthesis, FP cost estimation, cross-slot top-10 ranking
- **Boss encounter API** -- `GET /api/builds/<slug>/analysis/boss/<boss_id>` with corruption parameter
- **Corruption scaling API** -- `GET /api/builds/<slug>/analysis/corruption` with configurable breakpoints
- **Gear upgrade API** -- `GET /api/builds/<slug>/analysis/gear-upgrades` with slot filtering
- **Entities API** -- `GET /api/entities/bosses` for boss profile listing
- **BossEncounterPanel** -- frontend component for boss selection and phase result display
- **CorruptionScalingPanel** -- corruption curve visualization
- **Analysis Marshmallow schemas** -- `BossPhaseResultSchema`, `BossSummarySchema`, `BossAnalysisResponseSchema`, `CorruptionAnalysisResponseSchema`, `GearUpgradeCandidateSchema`
- Boss and corruption analysis caching with 30-minute TTL
- Enemy profiles data file (`data/entities/enemy_profiles.json`)

---

## [0.6.0] -- 2026-04-04

### Added

- **Build Import System** -- import from Last Epoch Tools and Maxroll URLs with automatic source detection and URL normalization
- **Partial import support** -- handles incomplete builds with gap reporting of missing fields
- **Import failure tracking** -- `ImportFailure` model recording source, URL, missing fields, error messages, and associated user
- **Discord webhook alerts** -- fire-and-forget background thread posting import failure notifications with severity-coded embeds (red for hard failures, orange for partial)
- **Admin import failures dashboard** -- `GET /api/admin/import-failures` with pagination for monitoring
- **Import API endpoints** -- `POST /api/import/url` for URL proxy-fetch and `POST /api/import/build` for full import pipeline
- **Dynamic rate limiting** -- 5/min for authenticated users, 2/min for anonymous on build import
- **ImportPanel frontend component** -- build import modal with URL input and status feedback

---

## [0.5.0] -- 2026-04-02

### Added

- **Skill Tree UI** -- interactive skill specialization tree with node graph renderer
- **BFS path validation for skill trees** -- only reachable nodes can be allocated, with orphan detection on deallocation
- **Skill tree node allocation API** -- `PATCH /api/builds/<slug>/skills/<skill_id>/nodes/<node_id>`
- **Skill tree data API** -- `GET /api/skills/<skill_id>/tree` with 24-hour cache
- **Build skill allocations API** -- `GET /api/builds/<slug>/skills`
- **Skill tree resolver service** -- parses spec tree node descriptions into build stat bonuses and skill modifiers (attack speed, cast speed, crit, more damage, added hits per cast)
- **SkillTreeGraph component** -- SVG node rendering with connection lines, point allocation, and mastery gates
- **SkillTreeDebugPanel** -- development inspection tool for skill tree state
- **Skill tree Marshmallow schemas** -- `SkillNodeSchema`, `SkillTreeResponseSchema`, `SkillAllocationSchema`, `NodeAllocateRequestSchema`
- `skill_tree_nodes.json` data file with parsed skill tree definitions
- `community_skill_trees.json` with community-sourced tree data

---

## [0.4.0] -- 2026-03-31

### Added

- **Stat Sensitivity Analyzer** -- tests 50+ stats with +10% delta, reports DPS and EHP gain percentages, weighted impact scoring with configurable offense/defense weights
- **Efficiency Scorer** -- evaluates affix upgrade candidates factoring DPS gain, EHP gain, and FP cost into a single efficiency score
- **Upgrade Ranker** -- re-weights sensitivity results by mode (balanced 60/40, offense 100/0, defense 0/100)
- **Multi-objective Optimization Engine** -- ranks stat upgrades with composite scoring, Pareto-optimal candidate detection
- **Best-in-slot search** -- incremental search with weighted affix targeting across gear slots
- **Optimization API** -- `GET /api/builds/<slug>/optimize` with mode parameter and 30-minute cache
- **BIS search API** -- `POST /api/bis/search` with slot selector, affix targets, and weight configuration
- **Sensitivity analysis API** -- `POST /api/simulate/sensitivity`
- **BisSearchPage frontend** -- slot selector, affix target panel, weight configuration, results table, comparison viewer, search visualization
- **Sensitivity and optimization Marshmallow schemas**
- Per-slot gear upgrade ranking with cross-slot top-10

### Changed

- `optimization_engine.py` expanded from single-stat ranking to multi-objective optimization with Pareto front
- Build optimizer now auto-resolves BuildStats from build dict via `stat_resolution_pipeline.quick_resolve()`

---

## [0.3.0] -- 2026-03-30

### Added

- **Passive tree leveling path tracker** -- `PassiveProgressBar` component records allocation order as a scrollable timeline with color-coded chips, hover tooltips, level ruler, and click-to-rewind in edit mode
- **Passive tree static auto-fit layout** -- tree scales to fill panel automatically based on actual node bounding box; pan/zoom removed
- **Real game passive tree positions** -- all node x/y coordinates match actual in-game layout loaded from exported `char-tree-layout.json`
- **Passive tree connection rendering** -- SVG lines drawn between connected nodes; BFS path validation ensures only reachable nodes can be allocated
- **Hexagonal node visuals** -- themed passive tree SVG with hexagonal node shapes and dark stone-texture panel background
- **Backend engine layer** in `backend/app/engines/`:
  - `stat_engine.py` -- 8-layer stat pipeline aggregating class base stats, mastery bonuses, passive nodes, gear affixes, and attribute scaling into a `BuildStats` dataclass with 200+ fields
  - `combat_engine.py` -- DPS calculation (hit damage, crit scaling, attack/cast speed) and Monte Carlo variance simulation
  - `defense_engine.py` -- EHP calculation, resistance capping at 75%, survivability score, weakness/strength detection, endurance, ward, block, dodge
  - `craft_engine.py` -- pure crafting math (optimal path search, Monte Carlo simulation, strategy comparison) extracted from service layer
  - `optimization_engine.py` -- initial stat upgrade ranking by DPS gain percentage
- **Build simulation API** -- `POST /api/builds/<slug>/simulate` returning stats, DPS, Monte Carlo, defense, and stat upgrades
- **Simulation APIs** -- stateless `/api/simulate/stats`, `/combat`, `/defense`, `/optimize`, `/build` endpoints
- **Rotation builder API** -- `POST /api/simulate/rotation` for skill rotation simulation
- **Conditional modifier API** -- `POST /api/simulate/conditional` for conditional stat evaluation
- **Multi-target encounter API** -- `POST /api/simulate/multi-target` for AOE/chain damage simulation
- **Engine test suite** -- test files covering stat aggregation, DPS calculation, EHP formulas, and upgrade ranking
- **`flask validate-data` CLI command** -- validates all JSON files in `/data/`, checks required files, types, and minimum entry counts
- **`flask seed-passives` CLI command** -- upserts passive nodes from `data/classes/passives.json` into database
- **Expanded affix seed data** -- 34 affixes with correct `stat_key` mappings
- **Data version stamping** -- `scripts/sync_game_data.py` writes `data/version.json` with patch version, sync timestamp, and updated file list
- `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE` (MIT)

### Changed

- `craft_service.py` refactored to import pure math from `craft_engine.py`; service now handles orchestration only
- `passiveTree: number[]` stores allocation history in order (append on allocate, remove last occurrence on dealloc) rather than a flat id list
- `PassiveTreeGraph` migrated from radial layout to real game positions with static auto-fit
- All admin/ref/BIS error responses converted from raw `jsonify()` to structured `error()`/`not_found()` helpers
- Rate limits added to all write/mutation endpoints that previously lacked them
- `tsconfig.json` fixed to check all `src/` files with proper path aliases
- All 28 TypeScript errors across frontend source resolved
- `test_api_contracts.py` skip logic changed from env var check to actual PostgreSQL connectivity test

### Fixed

- Horizontal overflow from leveling path progress bar fixed via `min-w-0`/`overflow-hidden` chain
- Passive allocation order no longer destroyed on toggle
- Syntax error in generated `passiveTrees/index.ts`
- Missing `getSkillTree` export causing blank screen crash
- Lowercase character class key lookup mismatch in `PassiveTreeGraph`

---

## [0.1.0] -- 2026-03-16

### Added

- Discord OAuth2 authentication with JWT tokens
- Build Planner with passive tree canvas, skill selection, gear slot editor
- Community builds browser with filtering, voting, and pagination
- Craft Simulator with real-time Monte Carlo simulation, strategy comparison, and undo support
- Meta tracker with class distribution and tier breakdown
- User profile page with build and session history
- Reference API (`/api/ref/`) for classes, affixes, item types, passive nodes, skills, base items, enemy profiles, damage types, rarities, and uniques
- Docker Compose development environment (Flask + PostgreSQL + Redis + Vite)
- Flask CLI commands: `flask seed`, `flask seed-builds`, `flask create-admin`
- Initial test suite

### Removed

- Instability and fracture mechanics -- removed to align with modern Last Epoch game design (1.0+)
