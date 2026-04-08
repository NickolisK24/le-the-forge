# The Forge -- Development Roadmap

---

## Completed

### Phase 1 -- Core Foundation (v0.1.0)
Character data model, stat calculation engine, base damage simulation, defensive stat modeling, crafting simulator with Monte Carlo, community builds browser, Discord OAuth2, Docker Compose environment.

### Phase 2 -- Crafting Simulation (v0.1.0)
Affix tier system with full seed data, forging potential tracking and RNG cost model, crafting probability modeling, Monte Carlo across thousands of craft attempts, strategy comparison and optimal path search.

### Phase 3 -- Passive Tree & System Polish (v0.3.0)
Real game node coordinates, SVG connection rendering, BFS path validation, hexagonal nodes with stone texture, leveling path tracker, 8-layer stat engine, combat/defense/craft engine extraction, full system audit and structural polish.

### Phase 4 -- Optimization Engine (v0.4.0)
Stat sensitivity analyzer with 50+ stat coverage and weighted impact scoring, upgrade efficiency scorer factoring DPS/EHP gain and FP cost, multi-objective optimization with Pareto front, best-in-slot search engine.

### Phase 5 -- Skill Tree UI (v0.5.0)
Interactive skill specialization tree with node graph renderer, BFS path validation for skill trees, spec tree stat resolver parsing node descriptions into build stat bonuses and skill modifiers.

### Phase 6 -- Build Import (v0.6.0)
Build import from Last Epoch Tools and Maxroll URLs, partial import with gap reporting, import failure tracking with Discord webhook alerts.

### Phase 7 -- Advanced Analysis (v0.7.0)
Boss encounter simulation with multi-phase transitions and enrage timers, corruption scaling curve analysis with recommended max corruption, per-slot gear upgrade ranking.

### Phase 8 -- Community Tools (v0.8.0)
Build comparison engine with weighted DPS/EHP scoring, meta analytics with class/mastery distribution and trending builds, view tracking with privacy-safe IP hashing, shared build reports with OpenGraph meta tags.

---

## In Progress

### Phase 9 -- Deploy & Launch

- CI/CD pipeline with GitHub Actions (lint, test, type-check, deploy)
- Production deployment (hosting platform TBD)
- Domain and SSL configuration
- Production environment configuration (Gunicorn, production database)
- Performance audit and Redis caching verification
- Mobile responsiveness audit
- Community launch (r/LastEpoch, Last Epoch Discord)
- Demo video walkthrough

---

## Future Phases

- **Native desktop packaging** -- Electron wrapper already scaffolded in `electron/`, needs production bundling with PyInstaller for the backend
- **Advanced crafting prediction models** -- machine learning or probabilistic models for craft outcome prediction beyond Monte Carlo
- **Encounter-specific optimization** -- recommend stat changes targeting specific boss fights
- **Patch auto-sync pipeline** -- GitHub Actions workflow to automatically sync game data when new patches release
- **"Ask The Forge" AI-powered build Q&A** -- natural language build analysis and recommendations
