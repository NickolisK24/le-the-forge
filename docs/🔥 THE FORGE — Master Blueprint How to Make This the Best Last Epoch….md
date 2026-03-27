🔥 THE FORGE — Master Blueprint: How to Make This the Best Last Epoch Tool the Game Has Ever Seen  
  
Repository: NickolisK24/le-the-forgeDate: 2026-03-27Status: Active Development — Phases 1–3 Complete, Phase 4 In Progress  
  
  
Table of Contents  
  
1. Where You Stand Right Now  
  
2. The Competitive Landscape & Your Edge  
  
3. Immediate Priorities (Next 30 Days)  
  
4. Short-Term Roadmap (30–90 Days)  
  
5. Medium-Term Roadmap (90–180 Days)  
  
6. Long-Term Vision (180+ Days)  
  
7. Backend Architecture Hardening  
  
8. Frontend & UX Transformation  
  
9. Data Pipeline & Game Accuracy  
  
10. Simulation Engine Upgrades  
  
11. Community & Social Features  
  
12. Developer Experience & Infrastructure  
  
13. Performance & Scalability  
  
14. Packaging & Distribution  
  
15. Marketing & Community Growth  
  
16. What Will Make This #1  
  
  
1. Where You Stand Right Now  
  
✅ What’s Already Built  
  
The Forge is not a concept — it’s a working multi-engine simulation platform. Here’s the verified inventory:  
  
SystemStatusKey FilesBackend Architecture✅ Matureroutes/ → services/ → engines/ → models/9 Specialized Engines✅/⚠️ Activestat_engine, combat_engine, defense_engine, craft_engine, optimization_engine, affix_engine, base_engine, item_engine, fp_engine40+ Backend Tests✅ Passingtest_stat_engine, test_combat_engine, test_defense_engine, test_craft_engine, test_optimization_engine, test_simulation_determinism, etc.Full REST API✅ Documented30+ endpoints across auth, builds, craft sessions, simulation, reference dataGame Data Layer✅ Rich11 JSON data files including 1.1MB affixes.json, skills_metadata.json, enemy_profiles.json, damage_types.jsonCrafting Simulator✅ FunctionalMonte Carlo simulation, strategy comparison, optimal path search, FP trackingBuild Planner✅ FunctionalPassive tree (real game coords, BFS validation, leveling path), skill selection, gear slotsPassive Tree✅ AdvancedHexagonal SVG nodes, real game positions, connection rendering, BFS path validation, leveling path trackerBuild Comparison✅ ExistsSide-by-side comparison pageCommunity Builds✅ ExistsBrowse, vote, filter, search, tier systemMeta Tracker✅ ExistsClass distribution, tier breakdownLoot Filter Builder✅ ExistsCondition editor, preview, .filter exportDiscord OAuth✅ WorkingJWT authentication, user profilesElectron Desktop✅ ScaffoldedmacOS/Windows/Linux targets, auto-launch backend+frontendDocker Dev Environment✅ WorkingFlask + PostgreSQL + Redis + ViteDocumentation✅ ExtensiveAPI reference, architecture docs, roadmap, changelog, contributing guide⚠️ What’s Partially Built (from ROADMAP & Review)  
  
• Optimization Engine — stat sensitivity analysis exists but needs full API exposure and defensive analysis  
  
• Craft Engine — core actions work but needs rule enforcement hardening  
  
• Stat Engine — aggregation works but needs expansion for all conditional stats  
  
• Combat Engine — DPS + Monte Carlo works but needs enemy-specific modeling  
  
• Defense Engine — EHP + resistance capping works but needs DoT modeling and burst analysis  
  
🔓 10 Open Issues (All Phase 1)  
  
#TitleLabel#3Create base API routeapi#4Create Character data modelmodels#7Create Item data modelmodels#9Create Skill data modelmodels#10Create sample character JSONtesting#11Create /simulate endpointapi#12Add input validationapi#13Parse API into modelsbackend#14Add loggingbackend#15Test full API flowtesting  
  
2. The Competitive Landscape & Your Edge  
  
Current Competitors  
  
ToolStrengthsWeaknessesLast Epoch ToolsLargest database, fast updates, massive user baseNo backend simulation engine, no Monte Carlo, no crafting strategy optimization, no EHP modelingMaxroll.ggBest guides, editorial quality, integrated plannerGuide-focused not sim-focused, no crafting predictor, no stat sensitivity analysisPro Game GuidesSimple talent calculatorNo simulation, no crafting, no analysisYour Unfair Advantages  
  
1. Backend-driven simulation — No existing tool runs Monte Carlo simulations on crafting outcomes, DPS variance, or stat sensitivity. They’re all static calculators.  
  
2. Multi-engine architecture — 9 specialized engines vs. monolithic calculators. This scales.  
  
3. Optimization intelligence — No competitor answers “what’s my best upgrade?” or “should I keep crafting?” with probabilistic analysis.  
  
4. Desktop-first — Electron packaging means The Forge can run locally with zero latency, no server costs, offline support.  
  
5. Explanation-driven results — Not just numbers, but why something is better. This builds trust that competitors don’t have.  
  
The Gap to Exploit  
  
No existing Last Epoch tool combines build analysis + crafting simulation + statistical optimization + explanation-driven recommendations in a single platform.  
  
That’s the gap. That’s what makes The Forge #1.  
  
  
3. Immediate Priorities (Next 30 Days)  
  
These are the highest-impact, lowest-risk actions that will accelerate everything else.  
  
3.1 Close the Open Phase 1 Issues  
  
The 10 open issues are foundational. Many appear to already have working implementations (the API, models, and simulate endpoints exist). Audit each issue against the actual codebase and close what’s done. This cleans up your project board and shows progress.  
  
3.2 Finish Optimization Engine API Exposure  
  
The optimization_engine.py exists with stat sensitivity analysis but isn’t fully exposed via the API. This is the single highest-value backend task.  
  
Must deliver:  
  
• POST /api/builds/<slug>/optimize → returns ranked stat upgrades with DPS and EHP gain percentages  
  
• POST /api/simulate/sensitivity → stat sensitivity analysis for arbitrary build configs  
  
• Response includes explanations for each recommendation (why this stat, what it affects, what tradeoff exists)  
  
3.3 Harden Craft Engine Rule Enforcement  
  
Per the development roadmap, craft_engine.py needs:  
  
• Add affix: prefix/suffix limit enforcement  
  
• Upgrade affix: max tier validation + safe failure  
  
• Remove affix: empty case handling  
  
• Seal affix: 1 sealed max enforcement  
  
• All actions: structured { success, reason } responses instead of bare booleans  
  
3.4 Add Structured Logging (Issue #14)  
  
Backend logging is critical for debugging simulation results and engine behavior. Use Python’s logging module with structured JSON output. Log every engine call with inputs, outputs, and timing.  
  
3.5 Clean Up and Triage Issue Board  
  
Create new issues for Phase 4+ work. Label them by phase, area (backend/frontend/data/infra), and priority. This creates a visible public roadmap.  
  
  
4. Short-Term Roadmap (30–90 Days)  
  
4.1 Mastery Gate Behavior (Passive Tree)  
  
Per docs/passive_tree_missing_features.md, the next target is mastery gate behavior:  
  
• Modal/inline prompt for specialization selection  
  
• State flag for chosen mastery per class  
  
• Deeper nodes unlock after gate is passed  
  
• Mastery-specific sub-trees become visible  
  
4.2 Skill Tree UI Component  
  
Data is already loaded in frontend/src/data/skillTrees/index.ts. Build the visual component:  
  
• Per-skill node graph with its own layout  
  
• Node tooltips with stat values and scaling info  
  
• Point allocation tracking  
  
• Mastery gate integration (specialization unlocks deeper skill branches)  
  
4.3 Build Import System (Phase 6)  
  
This is what turns The Forge from “interesting” into “practical.” Users need to bring their characters in without manual setup.  
  
Implementation plan:  
  
1. Paste-to-import — Parse Last Epoch Tools build planner export URLs  
  
2. JSON import — Accept structured JSON character data  
  
3. Future: Game save file import — If community tooling enables it  
  
4. Imported data auto-populates: gear, passives, skills, modifiers, character state  
  
4.4 Defense Analysis Panel  
  
The defense_engine.py calculates EHP, resistance capping, survivability score, and weakness detection. Surface this prominently in the UI:  
  
• Health pool + effective health visualization  
  
• Resistance bar chart (color-coded: capped = green, low = red)  
  
• Mitigation layer breakdown (armor, dodge, block, ward)  
  
• Burst vulnerability warnings  
  
• Sustain gap analysis (leech, regen, ward retention)  
  
4.5 Stat Efficiency Scoring UI  
  
The optimization engine already ranks stats. Build a visual dashboard:  
  
• Top 5 DPS gains ranked with percentage bars  
  
• Top 5 EHP gains ranked  
  
• Diminishing return warnings (stat near cap)  
  
• “Dead stats” flagged (stats that provide <1% improvement)  
  
• Color-coded upgrade priority matrix  
  
  
5. Medium-Term Roadmap (90–180 Days)  
  
5.1 Explanation-Driven Recommendation Engine  
  
This is the killer feature. No competitor does this.  
  
Every recommendation should include:  
  
• What: “+15% Necrotic Damage”  
  
• Why: “Your build scales heavily on necrotic damage through Bone Curse. This affix has the highest marginal DPS gain at 8.4% because your current necrotic scaling is only at 120%, well below the diminishing return threshold of 300%.”  
  
• Tradeoff: “This replaces +Health on your helmet, which reduces your EHP by 4.9%. Your survivability score drops from 71 to 67.”  
  
• Confidence: “Based on 10,000 Monte Carlo simulations with σ = 2841 DPS”  
  
• Risk: “Low — this is a safe upgrade with no defensive threshold violations”  
  
5.2 Crafting Strategy Planner  
  
Elevate the crafting simulator from “what happened” to “what should I do”:  
  
• Decision mode: “Should I keep crafting?” → Expected value analysis of continuing vs. stopping  
  
• Path visualization: Decision tree showing branching outcomes with probabilities at each node  
  
• Risk dial: Visual indicator from “safe” to “gambling”  
  
• Budget mode: “I have 28 FP. What’s the best I can realistically achieve?”  
  
• High-roll mode: “What’s the dream outcome and what’s the probability?”  
  
• Outcome distribution chart: Histogram of 10,000 simulated final items  
  
5.3 Boss Encounter Simulation  
  
You already have data/enemy_profiles.json. Build on it:  
  
• Select specific bosses (Lagon, Julra, Shade of Orobyss, etc.)  
  
• Simulate: “Can my build survive a hit from Lagon’s Lunar Beam?”  
  
• Time-to-kill estimates with confidence intervals  
  
• Corruption scaling: “At what corruption level does my build start failing?”  
  
• Per-boss gear optimization recommendations  
  
5.4 Gear Upgrade Ranker  
  
When a player finds a new item:  
  
• Paste item stats → instantly compare against equipped item  
  
• Show: DPS delta, EHP delta, efficiency score, trade-off analysis  
  
• Rank all 11 gear slots by “biggest upgrade opportunity”  
  
• Track upgrade history over time  
  
5.5 Build Comparison Enhancements  
  
The comparison page exists but should become a full analysis tool:  
  
• Radar chart: DPS / EHP / Speed / Resistances / Crit / Sustain  
  
• Delta breakdown: what exactly changed and by how much  
  
• “Clone and modify” workflow: duplicate a build, tweak one thing, compare  
  
• Multi-build comparison (3+ builds side-by-side)  
  
  
6. Long-Term Vision (180+ Days)  
  
6.1 Meta Analytics Dashboard  
  
You already have GET /api/builds/meta/snapshot. Expand it:  
  
• Class meta trends — popularity over time, patch-to-patch shifts  
  
• Win rate estimation — which builds clear highest corruption  
  
• Stat meta — most popular affix combinations per class  
  
• Crafting meta — most attempted crafts, success rates  
  
• Economy insight — which items are most valuable to craft  
  
6.2 Leveling Path Optimizer  
  
Using the passive tree leveling path tracker (already built):  
  
• Optimal point allocation order — “What passive nodes should I take at level 30 vs. level 60?”  
  
• Leveling milestone analysis — “At what level does your build ‘come online’?”  
  
• Respec cost calculator — “How much gold to switch from this tree to that tree?”  
  
6.3 Character Progression Simulator  
  
Go beyond single-snapshot analysis:  
  
• Simulate character growth from level 1 to 100  
  
• Track how DPS and EHP evolve with gear upgrades  
  
• “What if” analysis: “If I find this unique at level 70, how much does my build change?”  
  
• Progression timeline visualization  
  
6.4 Community Intelligence Layer  
  
Turn user data into collective wisdom:  
  
• Aggregate anonymous build data to identify real meta trends  
  
• Crowdsourced gear reviews — “Players who used this build found Exalted Helmets with +Health most impactful”  
  
• Build diff tool — “Your build is most similar to these community builds. Here’s what they do differently.”  
  
6.5 Localization  
  
You already have extracted_localization/ and extracted_text_assets/ directories. Plan for:  
  
• Multi-language support in the UI  
  
• Localized skill/affix names from game data  
  
• Community translation contributions  
  
  
7. Backend Architecture Hardening  
  
7.1 Schema Validation Everywhere  
  
You have backend/app/schemas/. Enforce validation on every engine input:  
  
• Use Marshmallow or Pydantic schemas for all request payloads  
  
• Validate stat inputs, gear inputs, affix data, skill modifiers before they reach engines  
  
• Return structured validation errors: { "errors": [{ "field": "level", "message": "must be 1-100" }] }  
  
7.2 Engine Purity Contract  
  
The golden rule from CONTRIBUTING.md: Engines have no DB/HTTP imports.  
  
Enforce this programmatically:  
  
• Add a CI check that scans backend/app/engines/ for forbidden imports (flask, sqlalchemy, requests)  
  
• Document engine contracts: input type → output type for every engine function  
  
• Add type hints (dataclasses or TypedDict) to every engine function signature  
  
7.3 Game Data Versioning  
  
Last Epoch patches change stats, affixes, and mechanics. You need:  
  
• data/version.json — tracks game patch version, data export date, engine assumption version  
  
• Every simulation result includes the data version it was computed against  
  
• Support loading multiple data versions for patch comparison (“How did my build change between 1.1 and 1.2?”)  
  
7.4 Deterministic Replay  
  
You already have test_simulation_determinism.py. Expand this:  
  
• Every simulation accepts an optional seed parameter (already in API)  
  
• Simulation results include the seed used  
  
• “Replay this simulation” button in the UI  
  
• Regression testing: snapshot expected outputs for known seeds  
  
7.5 Error Budget & Assumption Documentation  
  
Create docs/simulation_assumptions.md:  
  
• Crit formula used and source  
  
• Damage conversion rules  
  
• Resistance cap behavior  
  
• Forging potential RNG model  
  
• Ward calculation methodology  
  
• Armor mitigation formula  
  
• What’s approximated vs. exact  
  
  
8. Frontend & UX Transformation  
  
8.1 Results Dashboard Overhaul  
  
The results view should feel like a command center:  
  
**┌─────────────────────────────────────────────────────┐**  
│  BUILD SUMMARY: Bone Curse Lich (Lv 90)             │  
**├──────────────┬──────────────┬───────────────────────┤**  
│  DPS: 11,480 │  EHP: 6,120  │  Score: 71/100        │  
**├──────────────┴──────────────┴───────────────────────┤**  
│  ⚡ TOP UPGRADES                                     │  
│  1. +15% Necrotic Damage  → +8.4% DPS               │  
│  2. +30% Crit Multiplier  → +6.1% DPS               │  
│  3. +200 Health           → +4.9% EHP                │  
**├─────────────────────────────────────────────────────┤**  
│  ⚠️ WEAKNESSES                                       │  
│  • Low physical resistance (23% — cap is 75%)       │  
│  • No leech source — sustain gap in long fights     │  
**├─────────────────────────────────────────────────────┤**  
│  🎯 RECOMMENDED CRAFT                               │  
│  Upgrade % Increased Health T2→T4 on helmet         │  
│  81% success rate • 4 FP cost • +4.9% EHP           │  
**└─────────────────────────────────────────────────────┘**  
  
8.2 Simulation Presets  
  
Reduce setup friction with one-click presets:  
  
• Quick DPS Check — standard enemy, no specific encounter  
  
• Boss Fight: Lagon — Lagon’s stat profile, beam damage, phases  
  
• Corruption 300 — scaled enemy stats for high corruption  
  
• Survivability Stress Test — worst-case burst damage scenarios  
  
• Budget Build Analysis — focus on attainable gear only  
  
• SSF Mode — exclude trade-only items  
  
8.3 Visual Polish  
  
Match the game’s aesthetic:  
  
• Dark theme with gold/amber accents (already using forge-bg, forge-amber Tailwind tokens)  
  
• Animated transitions on simulation results  
  
• Particle effects on crafting success/failure  
  
• Sound effects for craft actions (optional, desktop mode)  
  
• Loading skeletons during API calls  
  
8.4 Mobile Responsiveness  
  
While desktop-first, the web version should work on mobile:  
  
• Responsive grid layouts  
  
• Touch-friendly passive tree (pinch-to-zoom consideration)  
  
• Collapsible panels for smaller screens  
  
  
9. Data Pipeline & Game Accuracy  
  
9.1 Expand Game Data Coverage  
  
Current /data/ has 11 files. Target complete coverage:  
  
FileStatusActionaffixes.json (1.1MB)✅ CompleteMaintain on patchbase_items.json✅ ExistsExpand to all base typescrafting_rules.json✅ ExistsValidate against live gamedamage_types.json✅ ExistsCompleteenemy_profiles.json✅ ExistsAdd all bosses + corruption scalingforging_potential_ranges.json✅ ExistsValidate against live dataimplicit_stats.json✅ ExistsExpand to all item basesitem_types.json✅ ExistsCompleterarities.json✅ ExistsCompleteskills_metadata.json (40KB)✅ ExistsAdd skill tree node datatags.json✅ ExistsCompleteuniques.json🔴 MissingAdd all unique items with special affixesidols.json🔴 MissingAdd idol types, affix poolsblessings.json🔴 MissingTimeline blessings per bosspassive_nodes_full.json🔴 MissingFull stat values per node per pointskill_tree_nodes.json🔴 MissingSkill specialization tree dataset_items.json🔴 MissingSet bonuses9.2 Automated Data Sync Pipeline  
  
You already have scripts/sync_game_data.py pulling from last-epoch-data. Enhance:  
  
• CI job that runs sync on schedule or manual trigger  
  
• Diff report: “These affixes changed, these are new”  
  
• Automated test that verifies data integrity after sync  
  
• Version tagging on each data update  
  
9.3 Community Data Validation  
  
• Export simulation results as JSON for community verification  
  
• “Report incorrect calculation” button → creates GitHub issue with build + expected vs. actual  
  
• Cross-reference results against Last Epoch Tools calculator for known builds  
  
  
10. Simulation Engine Upgrades  
  
10.1 Full Damage Pipeline  
  
Expand combat_engine.py to model the complete damage pipeline:  
  
Base Damage  
→ + Flat Added Damage  
→ × (1 + Increased Damage%)  
→ × (1 + More Damage multipliers)  
→ × Crit Multiplier (if crit)  
→ × (1 - Enemy Resistance%)  
→ × (1 - Enemy Armor Mitigation%)  
→ = Final Damage  
  
Include:  
  
• Damage conversion (physical → void, etc.)  
  
• Ailment damage (bleed, poison, ignite)  
  
• DoT calculations  
  
• Channeled skill modeling  
  
• Minion damage (summon builds)  
  
10.2 Ward Simulation  
  
Ward is a critical defensive layer for many builds:  
  
• Ward generation per second  
  
• Ward retention rate  
  
• Ward decay modeling  
  
• Ward-based EHP calculation  
  
• “Ward threshold” — at what point does ward make you functionally immortal?  
  
10.3 Proc & Trigger Modeling  
  
Many builds depend on triggered effects:  
  
• On-hit procs with probability  
  
• On-crit triggers  
  
• On-kill effects  
  
• Cooldown-based triggers  
  
• Companion/minion triggers  
  
10.4 Time-Series Simulation  
  
Move beyond snapshot DPS to time-series:  
  
• DPS over a 10-second fight window  
  
• Mana sustainability analysis  
  
• Cooldown rotation modeling  
  
• Burst vs. sustained damage comparison  
  
  
11. Community & Social Features  
  
11.1 Build Sharing & Discovery  
  
The community builds system exists. Enhance it:  
  
• Shareable build URLs — copy link, paste in Discord  
  
• Build embed cards — OG meta tags for rich Discord/Reddit previews  
  
• Build templates — “Start from this meta build, customize it”  
  
• Build forks — “I took Ghostblade’s Wraithlord build and changed these 3 things”  
  
• Patch notes integration — “These builds were affected by patch 1.3 changes”  
  
11.2 Voting & Tier System Enhancement  
  
You have voting. Make it smarter:  
  
• Weight votes by voter engagement (active users > drive-by votes)  
  
• Auto-tier based on composite score (votes + views + simulation results)  
  
• “Verified” badge for builds that have been tested in-game  
  
• Season-specific tier lists  
  
11.3 Discord Bot  
  
Build a companion Discord bot:  
  
• /forge build <name> → returns build summary card  
  
• /forge craft <item> → quick craft simulation  
  
• /forge compare <build1> <build2> → side-by-side  
  
• /forge upgrade <build> → top 3 recommended upgrades  
  
  
12. Developer Experience & Infrastructure  
  
12.1 CI/CD Pipeline  
  
Set up GitHub Actions:  
  
• On PR: Run pytest tests/ -v, lint, type check  
  
• On merge to main: Run full test suite, build frontend, build Electron  
  
• On release tag: Build and publish Electron binaries for macOS/Windows/Linux  
  
• Scheduled: Run data sync check weekly  
  
12.2 Test Coverage Expansion  
  
Current: 40+ tests. Target: 100+ tests covering:  
  
• Every engine function with edge cases  
  
• API endpoint integration tests  
  
• Frontend component tests (React Testing Library)  
  
• Simulation determinism regression tests  
  
• Data integrity tests (affix JSON schema validation)  
  
12.3 Development Documentation  
  
Enhance CONTRIBUTING.md:  
  
• Architecture decision records (ADRs) for major design choices  
  
• “How to add a new engine” tutorial  
  
• “How to add a new API endpoint” tutorial  
  
• “How to add game data for a new patch” tutorial  
  
• Local development troubleshooting FAQ  
  
12.4 Code Quality  
  
• Add mypy type checking for backend  
  
• Add strict ESLint + Prettier for frontend  
  
• Pre-commit hooks for formatting  
  
• Dependabot for dependency updates  
  
  
13. Performance & Scalability  
  
13.1 Simulation Performance Targets  
  
OperationCurrentTargetCraft Monte Carlo (10K runs)~500ms<100msBuild simulation (full analysis)~1s<200msStat sensitivity (10 stats)~2s<500msBoss encounter sim (1K runs)~3s<500ms13.2 Optimization Strategies  
  
1. NumPy vectorization — Replace Python loops in Monte Carlo with numpy array operations  
  
2. Result caching — Redis cache for identical simulation inputs (already have Redis)  
  
3. Lazy data loading — Load game data on first access, not on app startup  
  
4. Multiprocessing — For batch simulations, use Python multiprocessing pool  
  
5. Frontend caching — React Query already handles this; tune stale times  
  
6. Database query optimization — Add indexes on builds.slug, builds.character_class, builds.vote_count  
  
13.3 Benchmarking  
  
Add a scripts/benchmark.py:  
  
• Runs standard simulation workloads  
  
• Reports timing, memory usage, result counts  
  
• Tracks performance over time (store results in repo)  
  
  
14. Packaging & Distribution  
  
14.1 Electron Desktop App (Exists — Polish It)  
  
You already have the electron/ directory with macOS/Windows/Linux targets. Focus on:  
  
• Auto-start backend — Electron main process spawns Flask  
  
• Bundled Python — Use PyInstaller or similar to embed Python runtime  
  
• Auto-update — Electron Builder auto-update for new versions  
  
• Splash screen — Show loading while backend initializes  
  
• Tray icon — Minimize to system tray  
  
14.2 Release Strategy  
  
1. v0.2.0 — Optimization engine fully exposed, craft engine hardened  
  
2. v0.3.0 — Skill tree UI, mastery gates, build import  
  
3. v0.4.0 — Boss simulation, crafting strategy planner, defense panel  
  
4. v0.5.0 — Recommendation engine with explanations  
  
5. v1.0.0 — Feature-complete desktop release  
  
14.3 Distribution Channels  
  
• GitHub Releases (primary)  
  
• itch.io (gaming community visibility)  
  
• Last Epoch community Discord (announce each release)  
  
• Reddit r/LastEpoch  
  
  
15. Marketing & Community Growth  
  
15.1 README as Marketing  
  
Your README is already good. Make it great:  
  
• Hero screenshot at the very top (your screenshots exist — feature the best one)  
  
• “Try it now” badge linking to a hosted demo or desktop download  
  
• Feature comparison table vs. Last Epoch Tools and Maxroll  
  
• Video demo GIF (you already have a script for this: docs/screenshots/README.md)  
  
15.2 Content Strategy  
  
• Reddit posts: Share interesting simulation findings (“Did you know +Crit Multiplier beats +Damage at 400% increased?”)  
  
• Build analysis posts: “I simulated every Lich build — here’s what the numbers say”  
  
• Patch analysis: When patches drop, immediately publish stat change impact analysis  
  
• YouTube/Twitch: Partner with Last Epoch content creators for tool showcases  
  
15.3 Open Source Community  
  
• Add good first issue labels for newcomers  
  
• Create a Discord server for contributors  
  
• Write a “Philosophy” doc explaining why The Forge exists and how it’s different  
  
• Respond to every issue and PR promptly  
  
  
16. What Will Make This #1  
  
Here’s the honest truth about what separates “good tool” from “the best tool the game has ever seen”:  
  
The Five Pillars  
  
1. 🧠 Intelligence, Not Just Information  
  
• Every other tool shows you numbers. The Forge should tell you what the numbers mean.  
  
• “Your DPS is 11,480” → ❌ Not enough  
  
• “Your DPS is 11,480. Adding +15% Necrotic Damage would push it to 12,445 (+8.4%). This is your highest-value upgrade because your build has low necrotic scaling (120% total) and Bone Curse scales directly with necrotic damage.” → ✅ This is what wins  
  
2. 🎯 Answer the Questions Players Actually Ask  
  
• “Is this item an upgrade?” → Item comparison with real DPS/EHP delta  
  
• “Should I keep crafting?” → Expected value analysis with risk assessment  
  
• “Where is my build weakest?” → Ranked weakness list with fix recommendations  
  
• “What stat should I prioritize?” → Sensitivity analysis with diminishing return warnings  
  
• “Can I do this boss?” → Boss-specific simulation with survival probability  
  
3. ⚡ Speed to Insight  
  
• Presets for common scenarios  
  
• One-click build import  
  
• Instant simulation results  
  
• No manual data entry required for standard builds  
  
4. 🔬 Simulation Depth That Others Can’t Match  
  
• Monte Carlo on everything: DPS variance, craft outcomes, survival probability  
  
• 10,000-run simulations that reveal the truth about RNG-dependent builds  
  
• Confidence intervals on every number  
  
• Deterministic replay for reproducibility  
  
5. 🏠 Desktop-First Experience  
  
• Zero latency (local computation)  
  
• Works offline  
  
• No server costs  
  
• No ads  
  
• Your data stays on your machine  
  
The Moat  
  
Once The Forge has all five pillars, no competitor can catch up quickly because:  
  
• Last Epoch Tools would need to build an entire backend simulation engine  
  
• Maxroll would need to pivot from guides to analysis software  
  
• Both would need to replicate 9 specialized engines and 40+ tests  
  
The Forge’s moat is its engine architecture. Everything else is presentation. The engines are the hard part, and you’ve already built them.  
  
  
Summary: Execution Order  
  
PriorityActionTimeframeImpact🔴 CriticalClose open Phase 1 issuesNowClean project board🔴 CriticalExpose optimization engine via APIWeek 1-2Unlocks the #1 differentiating feature🔴 CriticalHarden craft engine rulesWeek 2-3Trustworthy crafting simulation🟡 HighMastery gate behaviorWeek 3-4Complete passive tree system🟡 HighBuild import systemMonth 2Practical usability leap🟡 HighDefense analysis panel UIMonth 2Surface existing backend power🟡 HighStat efficiency scoring UIMonth 2-3Users see intelligence, not just data🟢 MediumSkill tree UI componentMonth 3Full build planner🟢 MediumBoss encounter simulationMonth 3-4Unique feature no competitor has🟢 MediumRecommendation engine with explanationsMonth 4-5The killer feature🟢 MediumCrafting strategy plannerMonth 5-6Decision support, not just simulation🔵 Long-termMeta analyticsMonth 6+Community intelligence🔵 Long-termv1.0 desktop releaseMonth 6+Distribution milestone  
  
The foundation is built. The engines exist. The architecture is sound. Now it’s about surfacing the intelligence that already lives in the backend, making it effortless to use, and explaining why — not just what.  
  
That’s how The Forge becomes the best Last Epoch tool the game has ever seen. 🔥  
