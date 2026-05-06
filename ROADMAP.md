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

### Phase 9 -- Deploy & Launch (v0.8.1, 2026-04-21)

Production deployment to [epochforge.gg](https://epochforge.gg) on Render + Cloudflare. Delivered:

- Render Blueprint (`render.yaml`) provisioning Postgres, Redis, API, and static frontend in one pass
- Cloudflare DNS with proxied CNAMEs and Full (not Strict) SSL
- `/api/health` liveness probe blueprint used by Render health check and external monitors
- `ProductionConfig.validate()` hard-fails startup if production secrets are still dev defaults
- Production CORS allowlist (`epochforge.gg`, `www.epochforge.gg`)
- Production/dev log-level split with stdout routing
- GitHub Actions deploy workflow triggered on merges to `main` via Render deploy hook
- CI expanded to run on PRs into both `dev` and `main`
- 15 deployment-readiness tests (`backend/tests/test_deployment_readiness.py`) guarding the deploy invariants
- Documentation bundle: `docs/deployment.md`, `docs/production_setup.md`, `docs/rollback.md`, `docs/deployment_readiness.md`
- Post-launch transparency document at `docs/KNOWN_LIMITATIONS.md`

Issues closed in the launch window: [#223](https://github.com/NickolisK24/le-the-forge/issues/223) (craft-engine determinism), [#155](https://github.com/NickolisK24/le-the-forge/issues/155) (LE Tools gear import). New issues opened from the post-launch audit: [#246](https://github.com/NickolisK24/le-the-forge/issues/246) (armor-shred stacking), [#247](https://github.com/NickolisK24/le-the-forge/issues/247) (LE Tools residual ID resolution).

---

## Post-Launch Priorities

Ordered by impact on simulation accuracy and user-visible behaviour.

1. **Passive Node Coverage Expansion** -- grow the 39.2% numeric stat-key coverage in `backend/app/services/passive_stat_resolver.py` toward parity with in-game tooltips ([#156](https://github.com/NickolisK24/le-the-forge/issues/156))
2. **Conditional DPS Integration** -- wire Layer 8 conditional bonuses into the combat simulation path ([#158](https://github.com/NickolisK24/le-the-forge/issues/158))
3. **Minion Damage Engine** -- per-minion-type damage modeling for summoner builds ([#157](https://github.com/NickolisK24/le-the-forge/issues/157))
4. **Armor-Shred Stack Accumulation** -- model shred stacks over fight duration in the combat simulator ([#246](https://github.com/NickolisK24/le-the-forge/issues/246))
5. **Skill Base-Damage Community Validation** -- gather in-game dummy benchmarks for the 34 estimated skills ([#148](https://github.com/NickolisK24/le-the-forge/issues/148))

## Future Phases

- **Native desktop packaging** -- Electron wrapper already scaffolded in `electron/`, needs production bundling with PyInstaller for the backend
- **Advanced crafting prediction models** -- machine learning or probabilistic models for craft outcome prediction beyond Monte Carlo
- **Encounter-specific optimization** -- recommend stat changes targeting specific boss fights
- **Patch auto-sync pipeline** -- GitHub Actions workflow to automatically sync game data when new patches release
- **"Ask The Forge" AI-powered build Q&A** -- natural language build analysis and recommendations
