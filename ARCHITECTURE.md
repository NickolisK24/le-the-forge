# The Forge -- Architecture

---

## System Overview

The Forge is a simulation-driven analysis platform for Last Epoch. The backend is the single source of truth for all calculations -- the frontend sends input, receives results, and renders UI.

The system follows a layered architecture:

```
Game Data (JSON) --> Data Pipeline --> Registries
                                         |
Player Input --> Routes --> Services --> Engines --> Results
                              |                       |
                           Database              Frontend
```

---

## Backend Architecture

### App Factory and Blueprint Registration

The Flask application uses the app factory pattern (`create_app()` in `app/__init__.py`). Extensions initialized at startup: SQLAlchemy, Flask-Migrate, JWTManager, Flask-Limiter (Redis-backed with in-memory fallback), and CORS.

At startup, the data pipeline loads game data into registries: `AffixRegistry`, `SkillRegistry`, `EnemyRegistry`.

**25 registered blueprints:**

| Blueprint | URL Prefix | Purpose |
|-----------|-----------|---------|
| `auth_bp` | `/api/auth` | Discord OAuth2, JWT, user session |
| `builds_bp` | `/api/builds` | Build CRUD, voting, simulation, optimization |
| `import_bp` | `/api/import` | Build import from external tools |
| `craft_bp` | `/api/craft` | Crafting sessions, actions, prediction |
| `ref_bp` | `/api/ref` | Static game data (classes, affixes, skills, items, etc.) |
| `passives_bp` | `/api/passives` | Passive tree node queries |
| `profile_bp` | `/api/profile` | User profiles, build/session history |
| `simulate_bp` | `/api/simulate` | Stateless stat/combat/defense/build simulation |
| `optimize_bp` | `/api/optimize` | Full build optimization with variant generation |
| `rotation_bp` | `/api/simulate` | Skill rotation simulation |
| `conditional_bp` | `/api/simulate` | Conditional modifier evaluation |
| `multi_target_bp` | `/api/simulate` | Multi-target encounter simulation |
| `load_bp` | `/api/load` | Hot-reload game data |
| `admin_bp` | `/api/admin` | Affix management, import failure monitoring |
| `jobs_bp` | `/api/jobs` | Async job status polling |
| `version_bp` | `/api/version` | Version metadata |
| `bis_bp` | `/api/bis` | Best-in-slot search |
| `skills_bp` | `/api/` | Skill tree data and node allocation |
| `analysis_bp` | `/api/builds` | Boss encounter, corruption scaling, gear upgrades |
| `entities_bp` | `/api/entities` | Boss profile listing |
| `compare_bp` | `/api/compare` | Build comparison engine |
| `meta_bp` | `/api/meta` | Meta analytics and trending builds |
| `views_bp` | `/api/builds` | View tracking |
| `report_bp` | `/api/builds` | Shared build reports |
| `health_bp` | `/api` | Liveness probe (`/api/health`) used by Render health check and external monitors; returns `{status, version, patch_version, uptime_seconds}`, unauthenticated, rate-limited 60/min |

### Engine Layer

Engines are pure calculation modules -- no database access, no HTTP, no side effects. They accept typed inputs (usually `BuildStats` dataclass or dicts) and return typed outputs (dataclasses with `.to_dict()` methods).

| Engine | Purpose |
|--------|---------|
| `stat_engine.py` | 8-layer stat pipeline: base stats, flat, increased, more, conversions, derived, registry-derived, conditional |
| `combat_engine.py` | DPS calculation, crit weighting, ailment DPS, Monte Carlo variance, enemy-aware DPS with armor/resist/penetration |
| `defense_engine.py` | EHP calculation, resistance capping (75%), armor mitigation, dodge, block, endurance, ward, survivability scoring |
| `craft_engine.py` | Crafting action application (add, upgrade, seal, unseal, remove), FP consumption, outcome resolution |
| `craft_simulator.py` | Monte Carlo craft simulation across thousands of attempts, strategy comparison |
| `optimization_engine.py` | Multi-objective stat upgrade optimization with composite scoring and Pareto front |
| `build_optimizer.py` | Single-value upgrade ranking with DPS-first sorting and contextual explanations |
| `sensitivity_analyzer.py` | Tests 50+ stats with +10% delta, reports DPS/EHP gain and weighted impact score |
| `efficiency_scorer.py` | Affix upgrade candidate scoring factoring DPS gain, EHP gain, and FP cost |
| `upgrade_ranker.py` | Re-weights sensitivity results by mode (balanced/offense/defense) |
| `boss_encounter.py` | Multi-phase boss simulation with per-phase DPS, TTK, survival scoring, and enrage detection |
| `corruption_scaler.py` | Corruption scaling curve analysis with non-linear health/damage multipliers |
| `gear_upgrade_ranker.py` | Per-slot gear candidate evaluation with cross-slot top-10 ranking |
| `comparison_engine.py` | Two-build comparison with DPS/EHP deltas, stat diffs, skill comparison, weighted overall winner |
| `combat_simulator.py` | Time-based combat loop with rotation, cooldowns, and mana gating |
| `stat_resolution_pipeline.py` | 8-layer stat resolution with derived stat expansion and constants |
| `affix_engine.py` | Affix data loading, filtering by type/slot, registry integration |
| `base_engine.py` | Base item data, FP range management, random/manual/fixed FP modes |
| `item_engine.py` | Item creation with base properties and affix containers |
| `fp_engine.py` | Forging potential cost rolling and validation |
| `build_serializer.py` | Build data serialization for engine consumption |
| `validators.py` | Input validation for engine parameters |

### Service Layer

Services orchestrate between engines, database, and external systems.

| Service | Purpose |
|---------|---------|
| `build_analysis_service.py` | Full simulation pipeline: passive resolution, skill tree resolution, unique item extraction, stat aggregation, DPS, Monte Carlo, defense, optimization |
| `build_service.py` | Build CRUD, listing with filters, voting with tier recalculation, meta snapshot |
| `simulation_service.py` | Stateless engine delegation for raw data (no DB models) |
| `craft_service.py` | Craft session management with undo stack, action application, session summary |
| `skill_tree_resolver.py` | Parses spec tree node descriptions into build stat bonuses and skill modifiers |
| `passive_stat_resolver.py` | Batch-loads passive nodes from DB, maps human-readable stat keys to BuildStats fields |
| `meta_analytics_service.py` | Class/mastery distribution, popular skills/affixes, trending builds, snapshot caching |
| `build_report_service.py` | Generates shareable build reports with OpenGraph meta tags |
| `multi_target_encounter.py` | Multi-target encounter orchestration with target selection and lifecycle |
| `state_encounter_integration.py` | Conditional modifier evaluation against simulation state |
| `discord_notifier.py` | Fire-and-forget webhook alerts for import failures |

### Data Pipeline

Game data flows from extraction to engines:

```
Last Epoch game files
  --> scripts/sync_game_data.py (extraction + normalization)
    --> /data/ directory (canonical JSON files)
      --> app/game_data/ loader (startup)
        --> AffixRegistry, SkillRegistry, EnemyRegistry
          --> Engines (pure calculation)
```

The `flask validate-data` CLI command validates all JSON files in `/data/`, checking required files exist with correct types and minimum entry counts.

### Database Schema

| Model | Key Fields | Purpose |
|-------|-----------|---------|
| `User` | id, discord_id, username, avatar_url, is_admin | Discord-authenticated user |
| `Build` | id, slug, name, character_class, mastery, level, passive_tree (JSON), gear (JSON), vote_count, view_count, tier, is_public | Build definition |
| `BuildSkill` | id, build_id, slot, skill_name, points_allocated, spec_tree (JSON) | Skill slot (max 5 per build) |
| `Vote` | id, user_id, build_id, direction (+1/-1) | User vote on build (unique per user+build) |
| `CraftSession` | id, slug, item_type, item_level, rarity, forge_potential, affixes (JSON), user_id | Saved craft simulation |
| `CraftStep` | id, session_id, step_number, action, affix_name, tier_before, tier_after, roll, outcome, fp_before, fp_after | Immutable audit log entry |
| `ItemType` | id, name, category, base_implicit | Reference item type |
| `AffixDef` | id, name, affix_type, stat_key, tier_ranges (JSON), applicable_types, tags | Reference affix definition |
| `PassiveNode` | id, raw_node_id, character_class, mastery, node_type, x, y, connections (JSON), stats (JSON) | Reference passive tree node |
| `ImportFailure` | id, source, raw_url, missing_fields, error_message, user_id | Import failure tracking |
| `BuildView` | id, build_id, viewed_at, viewer_ip_hash | Time-series view tracking |

### Redis Usage

| Cache Key Pattern | TTL | Purpose |
|-------------------|-----|---------|
| `forge:builds:list:{hash}` | 30s | Build listing results |
| `forge:builds:meta:*` | 120s | Legacy meta snapshot |
| `forge:optimize:{slug}:{mode}` | 1800s | Optimization results |
| `forge:analysis:boss:{slug}:{boss_id}:{corruption}` | 1800s | Boss encounter analysis |
| `forge:analysis:corruption:{slug}:{boss_id}` | 1800s | Corruption scaling curve |
| `forge:analysis:gear:{slug}:{slot}` | 1800s | Gear upgrade ranking |
| `forge:sim:{prefix}:{hash}` | 300s | Simulation results |
| `forge:skill_tree:{skill_id}` | 86400s | Skill tree data |
| `forge:compare:{slug_a}:{slug_b}` | 1200s | Build comparison (alphabetically sorted slugs) |
| `forge:meta:snapshot` | 21600s | Full meta analytics |
| `forge:meta:trending` | 3600s | Trending builds |
| `forge:report:{slug}` | 3600s | Shared build report |
| `forge:view:{ip_hash}:{slug}` | 3600s | View rate limit (1/hr per IP per build) |
| `ref:*` | 86400s | Static reference data |
| `entities:bosses` | 86400s | Boss list |

### Rate Limiting

Flask-Limiter with Redis storage (falls back to in-memory). Limits are per-IP by default, with custom key functions for authenticated users on import endpoints.

Rate limit categories:
- **Read endpoints**: generally unlimited or high limits (30-60/min)
- **Simulation endpoints**: 10-30/min depending on computational cost
- **Write/mutation endpoints**: 10-30/min
- **Auth endpoints**: 20/min
- **Optimization**: 5/min (most expensive)
- **View tracking**: 60/min (with additional 1/hr per IP per build via Redis)

### Response Envelope

All API responses follow a consistent JSON envelope:

```json
{
  "data": <payload or null>,
  "meta": <pagination or null>,
  "errors": [{"message": "...", "field": "..."}] or null
}
```

Helper functions: `ok()`, `created()`, `no_content()`, `error()`, `not_found()`, `forbidden()`, `unauthorized()`, `validation_error()`.

---

## Frontend Architecture

### Page Structure

The app uses React Router with `AppLayout` providing sidebar, top bar, and footer. Key routes:

| Route | Component | Purpose |
|-------|-----------|---------|
| `/builds` | `BuildsPage` | Community builds browser |
| `/build`, `/build/:slug` | `BuildPlannerPage` | Create/edit builds |
| `/compare` | `BuildComparisonPage` | Side-by-side build comparison |
| `/meta` | `MetaSnapshotPage` | Meta analytics dashboard |
| `/report/:slug` | `ReportPage` | Shareable build report |
| `/craft`, `/craft/:slug` | `CraftSimulatorPage` | Crafting simulator |
| `/passives` | `PassiveTreePage` | Interactive passive tree |
| `/encounter` | `SimulationPage` | Encounter simulation |
| `/rotation` | `RotationBuilderPage` | Skill rotation builder |
| `/conditional` | `ConditionalBuilderPage` | Conditional modifier tester |
| `/multi-target` | `MultiTargetSimulatorPage` | Multi-target encounter sim |
| `/bis-search` | `BisSearchPage` | Best-in-slot search |
| `/classes` | `ClassesPage` | Class reference |
| `/data-manager` | `DataManagerPage` | Game data pipeline admin |
| `/profile` | `UserProfilePage` | User profile |
| `/monte-carlo` | `MonteCarloPage` | Monte Carlo visualizer |

### Component Organization

- `components/features/` -- domain-specific components grouped by feature (build, builds, craft, encounter, optimizer, bis, etc.)
- `components/ui/` -- shared reusable UI components (Panel, Button, Badge, Modal, Skeleton, Tooltip, ProgressIndicator, etc.)
- `pages/` -- route-level page components for standalone pages

### State Management

**Zustand stores:**
- `useAuthStore` -- user, token, isLoading, login/logout actions
- `useCraftStore` -- crafting UI state (item type, level, rarity, FP, affixes, session slug)

**TanStack Query** handles all server state with:
- Query key factory (`qk`) for consistent cache keys
- `staleTime: Infinity` for reference data (classes, affixes, item types, base items)
- 30-second stale time for profile data
- Automatic cache invalidation on mutations

### API Client

`src/lib/api.ts` provides typed request helpers (`get<T>()`, `post<T>()`, `patch<T>()`, `del<T>()`) wrapping fetch with JWT token injection. API namespaces: `authApi`, `buildsApi`, `craftApi`, `refApi`, `profileApi`, `adminApi`, `simulateApi`, `skillsApi`, `analysisApi`, `importApi`, `uniquesApi`, `compareApi`, `metaApi`, `reportApi`, `viewApi`, `gameDataApi`, `versionApi`.

All responses are typed as `ApiResponse<T>` matching the backend envelope: `{ data: T | null, meta: PaginationMeta | null, errors: ApiError[] | null }`.

---

## Data Architecture

### /data/ Directory Structure

```
data/
├── classes/            Class definitions, passives, skill trees, skill metadata
├── combat/             Damage types, ailments, monster modifiers
├── entities/           Enemy and boss profiles
├── items/              Affixes, base items, uniques, crafting rules, rarities, implicits
├── localization/       Game string tables (ability, affix, item, quest, etc.)
├── progression/        Blessings
└── world/              Zones, timelines, dungeons, quests, loot tables
```

### Data Sync Pipeline

`scripts/sync_game_data.py` transforms raw exports from `last-epoch-data/` into normalized JSON files in `/data/`. It handles:
- Affix normalization (1,160+ equipment + idol affixes with tier conversion)
- Passive tree node generation with namespaced IDs and layout coordinates
- Skill metadata extraction
- Patch version detection from source metadata

### Validation

`flask validate-data` checks all `/data/` JSON files for:
- Valid JSON structure
- Correct root type (array or object)
- Minimum entry counts for required files
- Required files: affixes.json, enemy_profiles.json, passives.json, skills_metadata.json, uniques.json, rarities.json, damage_types.json, implicit_stats.json, base_items.json, crafting_rules.json

---

## Security

### Authentication
Discord OAuth2 flow: frontend redirects to Discord, callback exchanges code for access token, backend fetches Discord profile, upserts user, issues signed JWT. Frontend stores JWT in memory (not localStorage).

### Authorization
- `login_required` decorator for protected endpoints
- Owner checks for build update/delete (author_id == current user)
- Admin checks for admin endpoints (user.is_admin)

### Rate Limiting
Per-endpoint rate limits via Flask-Limiter with Redis storage. Dynamic rate limiting on import endpoints (higher limits for authenticated users).

### Privacy
View tracking uses SHA-256 hashed IPs -- raw IP addresses are never stored in the database. Rate limiting for views uses Redis keys with TTL rather than database queries.

### Admin Protection
Admin-only endpoints (`/api/admin/*`) require both authentication and admin role verification.
