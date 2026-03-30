# 🔥 THE FORGE — Master Blueprint: How to Make This the Best Last Epoch Tool the Game Has Ever Seen

Repository: NickolisK24/le-the-forge
Date: 2026-03-27
Status: Active Development — Phases 1–4 In Progress, Simulation Pipeline ~80% Complete
Last Updated: 2026-03-29

---

## Progress Legend

| Icon | Meaning |
|------|---------|
| ✅ | Done — implemented, tested, merged or ready to merge |
| 🔄 | In Progress — partially built, remaining work identified |
| 📋 | Planned — not yet started, scoped and ready |
| 🔴 | Blocked / Not Built |

---

## Table of Contents

1. Where You Stand Right Now
2. The Competitive Landscape & Your Edge
3. Immediate Priorities (Next 30 Days) — ✅ Complete
4. Short-Term Roadmap (30–90 Days) — 🔄 In Progress
5. Medium-Term Roadmap (90–180 Days) — 📋 Planned
6. Long-Term Vision (180+ Days) — 📋 Planned
7. Backend Architecture Hardening — 🔄 Partial
8. Frontend & UX Transformation — 🔄 Partial
9. Data Pipeline & Game Accuracy — 🔄 Partial
10. Simulation Engine Upgrades — 🔄 In Progress
11. Community & Social Features — 📋 Planned
12. Developer Experience & Infrastructure — 🔄 Partial
13. Performance & Scalability — 📋 Planned
14. Packaging & Distribution — 🔄 Scaffolded
15. Marketing & Community Growth — 📋 Planned
16. What Will Make This #1

---

## 1. Where You Stand Right Now

### ✅ What's Already Built

The Forge is not a concept — it's a working multi-engine simulation platform. Here's the verified inventory:

| System | Status | Key Files |
|--------|--------|-----------|
| Backend Architecture | ✅ Mature | routes/ → services/ → engines/ → models/ |
| 9 Specialized Engines | ✅ Active | stat_engine, combat_engine, defense_engine, craft_engine, optimization_engine, affix_engine, base_engine, item_engine, fp_engine |
| **325 Backend Tests** | ✅ Passing | test_stat_engine, test_combat_engine, test_defense_engine, test_craft_engine, test_optimization_engine, test_simulation_determinism, test_base_engine (8 tests), etc. |
| Full REST API | ✅ Documented | 30+ endpoints across auth, builds, craft sessions, simulation, reference data |
| Game Data Layer | ✅ Rich | 13 JSON data files including 1.1MB affixes.json, skills_metadata.json, enemy_profiles.json, skill_tree_nodes.json, base_items.json (110 named bases) |
| Crafting Simulator | ⚠️ Partial | Strategy comparison, optimal path search, FP tracking (backend Monte Carlo exists but not surfaced in frontend UI) |
| Build Planner | ✅ Complete | Passive tree (real game coords, BFS validation, leveling path), skill selection with spec trees, mastery gates, full gear editor, import system |
| Unique Items | ✅ Complete | 403 unique items (uniques.json), backend API with meta-slot expansion, paper-doll gear editor, hover item tooltips |
| **Crafted Items (Gear Editor)** | ✅ Complete | 110 named base items across 19 slots; ItemPicker with Unique/Crafted tabs; AffixEditorModal with slot-filtered dropdown, tier slider, sealed toggle; emerald color coding for crafted gear |
| Set Items | ✅ Exists | set_items.json extracted — set bonuses not yet surfaced in UI |
| Passive Tree | ✅ Advanced | Hexagonal SVG nodes, real game positions, connection rendering, BFS path validation, leveling path tracker, **integer→string ID mismatch fixed** |
| **Spec Tree Resolver** | ✅ Complete | skill_tree_resolver.py parses node descriptions (pipe-separated stats), routes to build_stat_bonuses or skill_modifiers; 132 trees, 2190 nodes in skill_tree_nodes.json |
| **Full Simulation Pipeline** | ✅ ~80% | Passives + spec tree + gear (uniques + crafted affixes) all flow into stat aggregation → DPS calculation |
| Build Comparison | ✅ Exists | Side-by-side comparison page |
| Community Builds | ✅ Exists | Browse, vote, filter, search, tier system |
| Meta Tracker | 🔴 Planned | Backend endpoint exists (GET /api/builds/meta/snapshot) but no frontend page built |
| Loot Filter Builder | 🔴 Planned | Not yet implemented — condition editor, preview, .filter export all needed |
| Discord OAuth | ✅ Working | JWT authentication, user profiles |
| Electron Desktop | ✅ Scaffolded | macOS/Windows/Linux targets, auto-launch backend+frontend |
| Docker Dev Environment | ✅ Working | Flask + PostgreSQL + Redis + Vite |
| Documentation | ✅ Extensive | API reference, architecture docs, roadmap, changelog, contributing guide |

### ⚠️ What's Partially Built

- Optimization Engine — ✅ stat sensitivity analysis fully exposed via API with explanations
- Craft Engine — ✅ consolidated to structured `{success, reason}` responses, rule enforcement hardened
- Stat Engine — ✅ passive stats now correctly mapped (integer→string ID fix), affix stat_keys expanded (238 mapped vs. 47 before), composite stats handled (`_all_attributes`, `_all_res`, `_elemental_res`, `_attack_and_cast_speed`); 🔄 conditional stats still needed
- Combat Engine — ✅ spec tree modifiers applied (`more_damage_pct`, `crit_chance_pct`, `crit_multiplier_pct`, `added_hits_per_cast`, `hits_per_cast`); 🔄 enemy-specific modeling still needed
- Defense Engine — 🔄 EHP + resistance capping works, burst vulnerability panel added, needs DoT modeling

### 🔓 Open Issues

Issue board was audited and cleaned up 2026-03-27. Phase 1 issues closed where implementations exist.

---

## 2. The Competitive Landscape & Your Edge

### Current Competitors

| Tool | Strengths | Weaknesses |
|------|-----------|------------|
| Last Epoch Tools | Largest database, fast updates, massive user base | No backend simulation engine, no Monte Carlo, no crafting strategy optimization, no EHP modeling |
| Maxroll.gg | Best guides, editorial quality, integrated planner | Guide-focused not sim-focused, no crafting predictor, no stat sensitivity analysis |
| Pro Game Guides | Simple talent calculator | No simulation, no crafting, no analysis |

### Your Unfair Advantages

1. **Backend-driven simulation** — No existing tool runs Monte Carlo simulations on crafting outcomes, DPS variance, or stat sensitivity. They're all static calculators.
2. **Multi-engine architecture** — 9 specialized engines vs. monolithic calculators. This scales.
3. **Optimization intelligence** — No competitor answers "what's my best upgrade?" or "should I keep crafting?" with probabilistic analysis.
4. **Desktop-first** — Electron packaging means The Forge can run locally with zero latency, no server costs, offline support.
5. **Explanation-driven results** — Not just numbers, but why something is better. This builds trust that competitors don't have.

### The Gap to Exploit

No existing Last Epoch tool combines build analysis + crafting simulation + statistical optimization + explanation-driven recommendations in a single platform.

That's the gap. That's what makes The Forge #1.

---

## 3. Immediate Priorities (Next 30 Days) — ✅ SECTION COMPLETE

These are the highest-impact, lowest-risk actions that will accelerate everything else.

### 3.1 Close the Open Phase 1 Issues — ✅ Done
Issue board audited and cleaned up 2026-03-27.

### 3.2 Finish Optimization Engine API Exposure — ✅ Done
- ✅ `POST /api/builds/<slug>/optimize` — ranked stat upgrades with DPS/EHP gain %
- ✅ `POST /api/simulate/sensitivity` — stat sensitivity analysis with Marshmallow validation + caching
- ✅ `explanation` field on every recommendation (why this stat, what it affects)
- ✅ `stat_sensitivity()` in optimization_engine.py for per-unit marginal analysis

### 3.3 Harden Craft Engine Rule Enforcement — ✅ Done
- ✅ Add affix: prefix/suffix limit enforcement
- ✅ Upgrade affix: max tier validation + safe failure
- ✅ Remove affix: empty case handling
- ✅ Seal affix: 1 sealed max enforcement
- ✅ All actions: structured `{ success, reason }` responses
- ✅ All backend tests updated and passing

### 3.4 Add Structured Logging (Issue #14) — ✅ Done
- ✅ `ForgeLogger` added to all 9 engines
- ✅ `JsonFormatter` for machine-readable JSON output
- ✅ `LOG_FORMAT_JSON=true` config toggle
- ✅ Structured key=value logging throughout

### 3.5 Clean Up and Triage Issue Board — ✅ Done
Issue board triaged 2026-03-27. Phase labels applied.

---

## 4. Short-Term Roadmap (30–90 Days) — 🔄 IN PROGRESS

### 4.1 Mastery Gate Behavior (Passive Tree) — ✅ Complete

Per docs/passive_tree_missing_features.md:

- ✅ Mastery gate enforcement implemented — correct Last Epoch rules applied
- ✅ State flag for chosen mastery per class
- ✅ Deeper nodes blocked until gate requirements met
- ✅ Specialization selection workflow
- ✅ Mastery-specific sub-trees visually distinct in UI

### 4.2 Skill Tree UI Component — ✅ Complete

- ✅ Per-skill node graph with layout (SkillTreeGraph.tsx)
- ✅ Node tooltips with stat values, scaling info, and structured stat parsing (`|` separator)
- ✅ Downside detection with red highlighting and "penalty" badge
- ✅ Multi-point nodes show per-point values with max points
- ✅ Point allocation tracking — spec_tree stored per skill, persisted to DB
- ✅ Skill tree viewable in both edit and read-only (view) mode
- ✅ Mastery gate integration

### 4.3 Build Import System — ✅ ~95%

- ✅ LE Tools URL import — parse Last Epoch Tools build planner export URLs with correct class/mastery mapping (0-indexed, fixed)
- ✅ JSON import — paste structured JSON to auto-populate all fields
- ✅ Auto-populate: character class, mastery, level, passives, skills, gear
- ✅ Import presets — load template builds
- 📋 Game save file import (future/long-term)
- 📋 Patch version mismatch warnings on import (nice-to-have)

### 4.4 Defense Analysis Panel — ✅ Complete

- ✅ Health pool + effective health visualization (SimulationDashboard)
- ✅ Resistance bar chart (color-coded)
- ✅ Mitigation layer breakdown (armor, dodge, block, ward)
- ✅ Burst vulnerability warnings — `BurstVulnerabilityPanel` tests 5 endgame burst scenarios with element-specific mitigation
- ✅ Sustain gap analysis — Total HP/s from leech (DPS × leech%), health regen, ward net shown in AvoidancePanel

### 4.5 Stat Efficiency Scoring UI — ✅ Complete

- ✅ Top DPS gains ranked with percentage bars (UpgradeChart)
- ✅ Top EHP gains ranked
- ✅ Diminishing return warnings (badge in UpgradeChart)
- ✅ "Dead stats" flagged (<1% → "low impact" muted/strikethrough)
- ✅ Color-coded upgrade priority matrix — 2D scatter (DPS gain% vs EHP gain%) with Balanced/Offensive/Defensive/Low Impact quadrants

### 4.6 Full Simulation Pipeline (Passives + Spec Tree + Gear) — ✅ ~80% Complete

The core "analyze a build and get real numbers" pipeline now works end-to-end:

**Passive Tree Integration — ✅ Fixed**
- ✅ Integer→string ID mismatch resolved: `build.passive_tree` stores raw integer node IDs; `raw_id_to_str` map built from DB to translate before stat aggregation
- ✅ Double-counting prevention: when real DB passive data exists, skip fallback modulo formula for non-keystone nodes
- ✅ Keystone bonuses always applied via `KEYSTONE_BONUSES` dict regardless of tier

**Affix Stat Pipeline — ✅ Fixed**
- ✅ `_apply_stat_key()` helper handles direct and composite stat keys (`_all_attributes`, `_all_res`, `_elemental_res`, `_attack_and_cast_speed`)
- ✅ Affix stat_key coverage expanded: 238 affixes mapped (was 47); includes idol affixes, all resistance types, ward regen, leech, block chance
- ✅ Unique item stat parsing: 60+ regex patterns extract midpoint values from free-text descriptions ("+20–80% increased Fire Damage" → 50)

**Spec Tree Integration — ✅ Complete**
- ✅ `skill_tree_resolver.py`: parses `|` separator in node descriptions, routes `build_stat_bonuses` to BuildStats and `skill_modifiers` to DPS engine
- ✅ `skill_tree_nodes.json`: 132 skill trees, 2190 nodes, all description text preserved
- ✅ `combat_engine.py` updated: `more_damage_pct` (multiplicative stacking), `crit_chance_pct`, `crit_multiplier_pct`, `added_hits_per_cast`, `hits_per_cast` all applied in both `calculate_dps` and `monte_carlo_dps`
- ✅ `build_analysis_service.py`: extracts `primary_spec_tree` from first sorted skill, converts flat node-ID list to `{node_id, points}` via `Counter`, applies resolver output to stats and DPS call

**Remaining:**
- 📋 Multi-skill DPS — calculate DPS for each of 5 skill slots, return combined total + per-skill breakdown
- 📋 Hits-per-cast metadata — add `hits_per_cast`, `base_minion_count`, `is_channelled` to SKILL_STATS definitions
- 📋 Conditional stats — stats that only apply under certain conditions (on-hit, on-crit, vs. specific enemy types)

### 4.7 Gear Editor — Full Item Coverage — ✅ Complete

- ✅ 110 named base items across 19 slot categories (Rusted Coif → Imperial Helm, Corroded Sword → Dragonlance, etc.) with real LE-style implicit stats and FP ranges
- ✅ `base_engine.py` updated for list-based structure; named item lookup by name or slot key; backward compatible
- ✅ `GET /api/ref/base-items?slot=helmet` returns flat list for slot
- ✅ `ItemPicker.tsx` — unified modal with **Unique Items** and **Crafted Items** tabs
- ✅ Crafted tab: base item list filtered by slot, rarity selector (Normal/Magic/Rare/Exalted), preview pane showing implicit + FP range + base armor
- ✅ `AffixEditorModal` — opens when clicking an equipped crafted item; slot-filtered affix dropdown (234 affixes for body slot), tier slider (1–maxTier), sealed toggle, add/remove, save → feeds directly into simulation
- ✅ `SLOT_TO_AFFIX_SLOT` mapping — translates gear slot names ("body", "helmet") to affix `applicable_to` values ("chest", "helm") so dropdown populates correctly
- ✅ Crafted items displayed in emerald green with rarity + affix count; uniques remain amber

---

## 5. Medium-Term Roadmap (90–180 Days) — 📋 PLANNED

### 5.1 Explanation-Driven Recommendation Engine — 📋 Planned

This is the killer feature. No competitor does this. Foundation laid with `explanation` field on StatUpgrade.

Every recommendation should include:

- **What**: "+15% Necrotic Damage"
- **Why**: "Your build scales heavily on necrotic damage through Bone Curse..."
- **Tradeoff**: "This replaces +Health on your helmet, reducing EHP by 4.9%..."
- **Confidence**: "Based on 10,000 Monte Carlo simulations with σ = 2841 DPS"
- **Risk**: "Low — safe upgrade with no defensive threshold violations"

### 5.2 Crafting Strategy Planner — 📋 Planned

- 📋 Decision mode: "Should I keep crafting?" → Expected value analysis
- 📋 Path visualization: Decision tree with probabilities
- 📋 Risk dial: Visual "safe" to "gambling" indicator
- 📋 Budget mode: "I have 28 FP. What's realistically achievable?"
- 📋 Outcome distribution chart: Histogram of 10K simulated items

### 5.3 Boss Encounter Simulation — 📋 Planned

data/enemy_profiles.json exists. Build on it:

- 📋 Select specific bosses (Lagon, Julra, Shade of Orobyss, etc.)
- 📋 "Can my build survive a hit from Lagon's Lunar Beam?"
- 📋 Time-to-kill with confidence intervals
- 📋 Corruption scaling: "At what corruption does my build fail?"
- 📋 Per-boss gear optimization

### 5.4 Gear Upgrade Ranker — 📋 Planned

- 📋 Paste item stats → compare against equipped
- 📋 DPS delta, EHP delta, efficiency score
- 📋 Rank all 11 gear slots by upgrade opportunity
- 📋 Upgrade history tracking

### 5.5 Build Comparison Enhancements — 📋 Planned

Comparison page exists. Enhancements:

- 📋 Radar chart: DPS / EHP / Speed / Resistances / Crit / Sustain
- 📋 Delta breakdown
- 📋 "Clone and modify" workflow
- 📋 Multi-build comparison (3+)

### 5.6 Multi-Skill DPS Breakdown — 📋 Next Up

- 📋 Calculate DPS for each of the 5 skill slots independently
- 📋 Return per-skill breakdown + combined total in simulation response
- 📋 Each skill uses its own spec_tree from the build's skill array
- 📋 Display per-skill contribution bars in SimulationDashboard

---

## 6. Long-Term Vision (180+ Days) — 📋 PLANNED

### 6.1 Meta Analytics Dashboard — 📋 Planned

GET /api/builds/meta/snapshot exists. Expand:

- 📋 Class meta trends over time
- 📋 Win rate estimation
- 📋 Stat meta — popular affix combos per class
- 📋 Crafting meta — success rates
- 📋 Economy insight

### 6.2 Leveling Path Optimizer — 📋 Planned

Using the passive tree leveling path tracker (already built):

- 📋 Optimal point allocation order
- 📋 Leveling milestone analysis
- 📋 Respec cost calculator

### 6.3 Character Progression Simulator — 📋 Planned

- 📋 Simulate character growth level 1 to 100
- 📋 Track DPS/EHP evolution with gear upgrades
- 📋 "What if" analysis
- 📋 Progression timeline visualization

### 6.4 Community Intelligence Layer — 📋 Planned

- 📋 Aggregate anonymous build data for meta trends
- 📋 Crowdsourced gear reviews
- 📋 Build diff tool

### 6.5 Localization — 📋 Planned

extracted_localization/ and extracted_text_assets/ directories exist.

- 📋 Multi-language UI support
- 📋 Localized skill/affix names
- 📋 Community translation contributions

---

## 7. Backend Architecture Hardening — 🔄 PARTIAL

### 7.1 Schema Validation Everywhere — 🔄 ~60%

- ✅ Marshmallow schemas exist for builds, crafting, simulation endpoints
- ✅ `SimulateSensitivitySchema` added for sensitivity endpoint
- 📋 Validate all engine inputs (stat inputs, gear, affix data, skill modifiers)
- 📋 Structured validation errors: `{ "errors": [{ "field": "level", "message": "must be 1-100" }] }`

### 7.2 Engine Purity Contract — 🔄 ~70%

The golden rule from CONTRIBUTING.md: Engines have no DB/HTTP imports.

- ✅ All engines follow purity contract (verified in audit)
- ✅ `BuildStats` dataclass is pure — no DB imports
- 📋 CI check scanning engines/ for forbidden imports
- 📋 Document engine contracts: input → output for every function
- 📋 Full type hints on every engine function signature

### 7.3 Game Data Versioning — 📋 Planned

- 📋 data/version.json tracking game patch, data export date, engine version
- 📋 Simulation results include data version
- 📋 Multiple data versions for patch comparison

### 7.4 Deterministic Replay — 🔄 ~50%

- ✅ test_simulation_determinism.py exists and passes
- ✅ Simulation accepts optional seed parameter (in API)
- ✅ Results include seed used
- 📋 "Replay this simulation" button in UI
- 📋 Regression testing with snapshot expected outputs

### 7.5 Error Budget & Assumption Documentation — 📋 Planned

- 📋 docs/simulation_assumptions.md (crit formula, damage conversion, resistance caps, FP RNG model, ward calc, armor formula)

---

## 8. Frontend & UX Transformation — 🔄 PARTIAL

### 8.1 Results Dashboard Overhaul — 🔄 ~65%

- ✅ SimulationDashboard with DPS, EHP, Score display
- ✅ Top upgrades ranked with explanation text
- ✅ Weakness/strength display from defense engine
- ✅ BurstVulnerabilityPanel with 5 endgame scenarios
- ✅ Upgrade Priority Matrix — 2D scatter chart with Balanced/Offensive/Defensive/Low Impact quadrants
- ✅ Sustain panel — Total HP/s from leech (DPS × leech%), health regen, ward net
- 📋 Full "command center" layout as designed
- 📋 Recommended craft action with success rate

### 8.2 Simulation Presets — 📋 Planned

- 📋 Quick DPS Check
- 📋 Boss Fight presets (Lagon, Julra, etc.)
- 📋 Corruption 300
- 📋 Survivability Stress Test
- 📋 Budget Build Analysis
- 📋 SSF Mode

### 8.3 Visual Polish — 🔄 ~40%

- ✅ Dark theme with forge-bg, forge-amber Tailwind tokens
- ✅ Hexagonal node styling on passive/skill trees
- 📋 Animated transitions on simulation results
- 📋 Particle effects on crafting success/failure
- 📋 Sound effects (desktop mode)
- 📋 Loading skeletons during API calls

### 8.4 Gear Editor — ✅ Complete (Full Item Coverage)

- ✅ Paper-doll equipment layout matching Last Epoch's in-game UI (CSS grid-template-areas)
- ✅ Equipment tab — Helmet, Body, Weapon (meta-slot: all 9 weapon types), Off-hand (Shield/Quiver/Catalyst), Amulet, Ring×2, Belt, Gloves, Boots, Relic
- ✅ Idols tab — 1×1, 1×3, 1×4, 2×2 idol grid with correct slot counts
- ✅ **ItemPicker modal** — Unique Items tab (403 uniques, search by name/base/tag, full preview) + **Crafted Items tab** (110 named base items, rarity selector, FP/armor preview)
- ✅ **AffixEditorModal** — slot-filtered affix dropdown (234+ affixes per slot), tier slider (1→max tier), sealed checkbox, add/remove up to 4 affixes; feeds directly into simulation via `{name, tier}` affix objects
- ✅ Hover tooltips — fixed-position portal overlay on every equipped unique showing all stats (implicit, affixes, unique effects, lore, tags)
- ✅ Crafted items display in emerald green with rarity + affix count badge; uniques remain amber
- ✅ Read-only mode — view mode shows gear without interaction
- ✅ Backend API — `/api/ref/uniques?slot=` with meta-slot expansion; `/api/ref/base-items?slot=` with named base list; 24h cache

### 8.5 Mobile Responsiveness — 📋 Planned

- 📋 Responsive grid layouts
- 📋 Touch-friendly passive tree
- 📋 Collapsible panels

---

## 9. Data Pipeline & Game Accuracy — 🔄 PARTIAL

### 9.1 Expand Game Data Coverage

| File | Status | Notes |
|------|--------|-------|
| affixes.json (1.1MB) | ✅ Complete | 1230 affixes; **238 stat_keys mapped** (was 47); composite stats handled |
| base_items.json | ✅ **Rebuilt** | **110 named base items** across 19 slots with level req, FP range, armor, implicit text |
| crafting_rules.json | ✅ Exists | Validate against live game |
| damage_types.json | ✅ Exists | Complete |
| enemy_profiles.json | ✅ Exists | Add all bosses + corruption scaling |
| forging_potential_ranges.json | ✅ Exists | Validate against live data |
| implicit_stats.json | ✅ Exists | 19 slot entries — expand to all item bases |
| item_types.json | ✅ Exists | Complete |
| rarities.json | ✅ Exists | Complete |
| skills_metadata.json (40KB) | ✅ Exists | Complete with skill tree node data |
| tags.json | ✅ Exists | Complete |
| uniques.json | ✅ Complete | 403 unique items — name, slot, base, affixes, unique_effects, lore, tags, level_req |
| set_items.json | ✅ Complete | Extracted — set bonuses not yet surfaced in UI |
| idols.json | 🔴 Missing | Add idol types, affix pools |
| blessings.json | 🔴 Missing | Timeline blessings per boss |
| passive_nodes_full.json | ✅ Complete | Extracted with full stat values per node |
| **skill_tree_nodes.json** | ✅ **New** | **132 skill trees, 2190 nodes** generated from frontend skill tree index; pipe-separated description format |

### 9.2 Automated Data Sync Pipeline — 🔄 ~30%

- ✅ scripts/sync_game_data.py exists
- 📋 CI job for scheduled sync
- 📋 Diff report on changes
- 📋 Automated data integrity tests
- 📋 Version tagging

### 9.3 Community Data Validation — 📋 Planned

- 📋 Export simulation results as JSON
- 📋 "Report incorrect calculation" button
- 📋 Cross-reference against Last Epoch Tools

---

## 10. Simulation Engine Upgrades — 🔄 IN PROGRESS

### 10.1 Full Damage Pipeline — 🔄 ~75%

combat_engine.py models the core pipeline:

- ✅ Base → Flat Added → Increased% → More multipliers → Crit → Resistance → Final
- ✅ Ailment damage (bleed, poison, ignite)
- ✅ **Spec tree modifiers applied**: `more_damage_pct` (multiplicative), `crit_chance_pct`, `crit_multiplier_pct`, `hits_per_cast` from `added_hits_per_cast`
- ✅ **Passive stats correctly aggregated**: integer→string ID fix means passive tree bonuses now actually affect simulation
- ✅ **Affix stats correctly applied**: 238 mapped stat_keys feed into BuildStats (was silently ignored before)
- ✅ **Unique item stats parsed**: regex extraction of midpoint values from description strings
- 📋 Damage conversion (physical → void, etc.)
- 📋 DoT calculations
- 📋 Channeled skill modeling
- 📋 Minion damage (summon builds)
- 📋 Multi-skill DPS (per-skill breakdown + combined total)

### 10.2 Ward Simulation — 🔄 ~40%

- ✅ Ward buffer, ward regen/decay in defense_engine
- 📋 Full ward generation per second model
- 📋 Ward retention rate
- 📋 "Ward threshold" — functional immortality point

### 10.3 Proc & Trigger Modeling — 📋 Planned

- 📋 On-hit procs, on-crit triggers, on-kill effects
- 📋 Cooldown-based triggers
- 📋 Companion/minion triggers

### 10.4 Time-Series Simulation — 📋 Planned

- 📋 DPS over 10-second fight window
- 📋 Mana sustainability
- 📋 Cooldown rotation modeling
- 📋 Burst vs. sustained comparison

---

## 11. Community & Social Features — 📋 PLANNED

### 11.1 Build Sharing & Discovery — 🔄 ~40%

- ✅ Community builds with browse, vote, filter, search
- 📋 Shareable build URLs for Discord
- 📋 Build embed cards (OG meta tags)
- 📋 Build templates and forks
- 📋 Patch notes integration

### 11.2 Voting & Tier System Enhancement — 🔄 ~30%

- ✅ Basic voting exists
- 📋 Weighted votes by engagement
- 📋 Auto-tier from composite score
- 📋 "Verified" badge
- 📋 Season-specific tier lists

### 11.3 Discord Bot — 📋 Planned

- 📋 /forge build, /forge craft, /forge compare, /forge upgrade commands

---

## 12. Developer Experience & Infrastructure — 🔄 PARTIAL

### 12.1 CI/CD Pipeline — 📋 Planned

- 📋 PR: pytest + lint + type check
- 📋 Merge: full suite + build frontend + build Electron
- 📋 Release: publish Electron binaries
- 📋 Scheduled: weekly data sync

### 12.2 Test Coverage Expansion — 🔄 ~65%

Current: **325 tests passing**. Target: 400+

- ✅ Engine tests with edge cases (stat, combat, defense, craft, optimization)
- ✅ Simulation determinism regression tests
- ✅ **Base engine tests expanded to 8** (named item lookup, all 110 bases validated)
- ✅ **Affix engine tests updated** for idol type and real tier values
- ✅ **Stat engine tests updated** for correct T1 health midpoint (1000, not 10)
- 📋 API endpoint integration tests
- 📋 Frontend component tests
- 📋 Data integrity tests

### 12.3 Development Documentation — 🔄 ~50%

- ✅ CONTRIBUTING.md with engine purity rules
- ✅ API reference docs
- 📋 Architecture decision records (ADRs)
- 📋 "How to add a new engine" tutorial
- 📋 Troubleshooting FAQ

### 12.4 Code Quality — 🔄 ~30%

- ✅ ForgeLogger structured logging
- 📋 mypy type checking
- 📋 Strict ESLint + Prettier
- 📋 Pre-commit hooks
- 📋 Dependabot

---

## 13. Performance & Scalability — 📋 PLANNED

### 13.1 Simulation Performance Targets

| Operation | Current | Target |
|-----------|---------|--------|
| Craft Monte Carlo (10K runs) | ~500ms | <100ms |
| Build simulation (full analysis) | ~1s | <200ms |
| Stat sensitivity (10 stats) | ~2s | <500ms |
| Boss encounter sim (1K runs) | ~3s | <500ms |

### 13.2 Optimization Strategies — 📋 Planned

1. 📋 NumPy vectorization
2. 📋 Redis result caching (Redis already available)
3. 📋 Lazy data loading
4. 📋 Multiprocessing for batch simulations
5. ✅ React Query frontend caching (24h stale time on all ref data)
6. 📋 Database query optimization (indexes)

### 13.3 Benchmarking — 📋 Planned

- 📋 scripts/benchmark.py
- 📋 Standard workloads with timing + memory
- 📋 Performance tracking over time

---

## 14. Packaging & Distribution — 🔄 SCAFFOLDED

### 14.1 Electron Desktop App — 🔄 ~30%

- ✅ electron/ directory with macOS/Windows/Linux targets
- 📋 Auto-start backend (Electron spawns Flask)
- 📋 Bundled Python (PyInstaller)
- 📋 Auto-update
- 📋 Splash screen
- 📋 Tray icon

### 14.2 Release Strategy

| Version | Scope | Status |
|---------|-------|--------|
| v0.2.0 | Optimization engine + craft hardening | ✅ Done |
| v0.3.0 | Skill trees, mastery gates, build import, unique items + gear editor | ✅ Done |
| **v0.3.5** | **Spec tree → DPS pipeline, crafted gear with affix editor, base items, passive fix** | ✅ **Done** |
| v0.4.0 | Boss simulation, crafting strategy planner, multi-skill DPS, defense panel completion | 📋 Planned |
| v0.5.0 | Recommendation engine with explanations | 📋 Planned |
| v1.0.0 | Feature-complete desktop release | 📋 Planned |

### 14.3 Distribution Channels — 📋 Planned

- 📋 GitHub Releases (primary)
- 📋 itch.io
- 📋 Last Epoch community Discord
- 📋 Reddit r/LastEpoch

---

## 15. Marketing & Community Growth — 📋 PLANNED

### 15.1 README as Marketing — 📋 Planned

- 📋 Hero screenshot at top
- 📋 "Try it now" badge
- 📋 Feature comparison table vs. competitors
- 📋 Video demo GIF

### 15.2 Content Strategy — 📋 Planned

- 📋 Reddit simulation findings
- 📋 Build analysis posts
- 📋 Patch analysis on patch day
- 📋 Content creator partnerships

### 15.3 Open Source Community — 🔄 ~20%

- ✅ CONTRIBUTING.md exists
- 📋 Good first issue labels
- 📋 Discord server for contributors
- 📋 Philosophy doc

---

## 16. What Will Make This #1

### The Five Pillars

**1. 🧠 Intelligence, Not Just Information**
- Every other tool shows numbers. The Forge tells you what the numbers mean.
- ✅ Foundation: `explanation` field on recommendations, `stat_sensitivity()`, dead stat flagging
- ✅ Upgrade Priority Matrix — visual quadrant system (Balanced / Offensive / Defensive / Low Impact)

**2. 🎯 Answer the Questions Players Actually Ask**
- "Is this item an upgrade?" → Item comparison with DPS/EHP delta
- "Should I keep crafting?" → Expected value analysis
- "Where is my build weakest?" → ✅ Ranked weakness list with burst vulnerability panel
- "What stat should I prioritize?" → ✅ Sensitivity analysis with diminishing return warnings
- "Can I do this boss?" → Boss-specific simulation
- "What gear should I be crafting?" → ✅ Crafted item picker with full base library + affix editor

**3. ⚡ Speed to Insight**
- 📋 Presets, one-click import, instant results, no manual entry

**4. 🔬 Simulation Depth That Others Can't Match**
- ✅ Monte Carlo on DPS and crafting
- ✅ Deterministic replay with seed
- ✅ **Spec tree modifiers applied to DPS** — no competitor does this
- ✅ **All three data layers flow into simulation**: passives + spec tree + gear affixes
- 📋 Confidence intervals on every number
- 📋 10K-run simulations

**5. 🏠 Desktop-First Experience**
- ✅ Electron scaffolded
- 📋 Zero latency, offline, no ads, local data

### The Moat

Once The Forge has all five pillars, no competitor can catch up quickly because:
- Last Epoch Tools would need to build an entire backend simulation engine
- Maxroll would need to pivot from guides to analysis software
- Both would need to replicate 9 specialized engines and 325 tests

The Forge's moat is its engine architecture. Everything else is presentation. The engines are the hard part, and you've already built them.

---

## Summary: Execution Order

| Priority | Action | Timeframe | Status |
|----------|--------|-----------|--------|
| 🔴 Critical | Close open Phase 1 issues | Now | ✅ Done |
| 🔴 Critical | Expose optimization engine via API | Week 1-2 | ✅ Done |
| 🔴 Critical | Harden craft engine rules | Week 2-3 | ✅ Done |
| 🟡 High | Mastery gate behavior | Week 3-4 | ✅ Done |
| 🟡 High | Build import system | Month 2 | ✅ ~95% |
| 🟡 High | Unique items + gear editor | Month 2 | ✅ Done |
| 🟡 High | Defense analysis panel UI | Month 2 | ✅ Done |
| 🟡 High | Stat efficiency scoring UI | Month 2-3 | ✅ Done |
| 🟢 Medium | Skill tree UI component | Month 3 | ✅ Done |
| 🟢 Medium | **Spec tree → DPS pipeline** | **Month 3** | ✅ **Done** |
| 🟢 Medium | **Passive tree ID fix + full stat aggregation** | **Month 3** | ✅ **Done** |
| 🟢 Medium | **Crafted items + base library + affix editor** | **Month 3** | ✅ **Done** |
| 🟢 Medium | Multi-skill DPS breakdown | Month 3-4 | 📋 Next |
| 🟢 Medium | Boss encounter simulation | Month 3-4 | 📋 Planned |
| 🟢 Medium | Recommendation engine with explanations | Month 4-5 | 📋 Planned |
| 🟢 Medium | Crafting strategy planner | Month 5-6 | 📋 Planned |
| 🔵 Long-term | Meta analytics | Month 6+ | 📋 Planned |
| 🔵 Long-term | v1.0 desktop release | Month 6+ | 📋 Planned |

---

The foundation is built. The engines exist. The architecture is sound. The simulation pipeline — passives, spec trees, and gear — now flows end-to-end. Now it's about surfacing the intelligence that already lives in the backend, making it effortless to use, and explaining why — not just what.

That's how The Forge becomes the best Last Epoch tool the game has ever seen. 🔥
