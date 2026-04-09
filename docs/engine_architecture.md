# Engine Architecture

All engines live in `backend/app/engines/`. They are pure calculation modules -- no database access, no HTTP requests, no side effects. They communicate via typed dataclasses and dicts.

---

## Core Pipeline

```
Player Input
  |
  v
Stat Engine (8-layer pipeline)
  |
  +--> Combat Engine (DPS, Monte Carlo, ailments)
  |
  +--> Defense Engine (EHP, resistances, survivability)
  |
  +--> Optimization Engine (upgrade ranking, Pareto front)
  |
  +--> Boss Encounter (multi-phase simulation)
  |
  +--> Comparison Engine (two-build comparison)
```

---

## Engine Modules

### stat_engine.py -- Master Stats Aggregation

**Input:** character_class, mastery, allocated_node_ids, nodes, gear_affixes, passive_stats
**Output:** `BuildStats` dataclass (200+ fields)

The stat engine aggregates all stat sources into a single `BuildStats` object via an 8-layer pipeline:

1. **Base Stats** -- class and mastery base values from `CLASS_BASE_STATS` and `MASTERY_BONUSES`
2. **Flat Additions** -- gear implicits and affix flat values
3. **Increased (%)** -- additive percentage pool
4. **More Multipliers** -- multiplicative product pool
5. **Conversions** -- damage type conversions
6. **Derived Stats** -- attribute-to-secondary expansion (Strength +1 health/pt, Intelligence +0.1% ward retention/pt, Attunement +0.2 mana regen/pt)
7. **Registry Derived** -- EHP, armor mitigation, dodge chance
8. **Conditional Stats** -- context-dependent bonuses (while moving, against bosses, etc.)

Uses `StatPool` bucket system: `add_flat()`, `add_increased()`, `add_more()`, `add_multiplier()`, `resolve_to()`.

### combat_engine.py -- DPS Calculation & Combat Simulation

**Input:** `BuildStats`, skill_name, skill_level, skill_modifiers, conversions
**Output:** `DPSResult`, `MonteCarloDPS`, `EnemyAwareDPS`

- `calculate_dps()` -- deterministic DPS: flat added damage + scaled base, increased/more multipliers, crit-weighted average
- `monte_carlo_dps()` -- variance simulation with configurable sample size and deterministic seeding; parallelizable via ProcessPoolExecutor
- `calculate_dps_vs_enemy()` -- applies enemy armor/resist minus character penetration

165+ hardcoded skill definitions in `SKILL_STATS` with fallback to SkillRegistry lookup.

Ailment DPS (bleed, ignite, poison) computed separately from proc chance and scaling stats.

### defense_engine.py -- Survivability & EHP Calculation

**Input:** `BuildStats`
**Output:** `DefenseResult`

- Health metrics: max_health, effective_hp, health_regen, total_ehp
- Mitigation: armor_reduction_pct, avg_resistance (7 elements capped at 75%)
- Avoidance: dodge_chance_pct, block_chance_pct, block_mitigation_pct, glancing_blow_pct
- Endurance: endurance_pct, endurance_threshold_pct, endurance_damage_reduction
- Ward: ward_buffer, ward_regen_per_second, net_ward_per_second
- Composite: survivability_score (0-100), sustain_score (0-100)
- Lists: weaknesses[], strengths[]

Layered reduction model: `(1 - armor_reduction) * (1 - avg_res_reduction)`. Block/dodge as avoidance multipliers. Endurance as conditional damage reduction below threshold.

### craft_engine.py -- Crafting Action Application

**Input:** item state, craft action, affix_name, target_tier
**Output:** modified item state, outcome, FP cost

Actions: `add_affix`, `upgrade_affix`, `seal_affix`, `unseal_affix`, `remove_affix`.

Enforces prefix/suffix limits, tier validation, FP consumption, and failure handling.

### craft_simulator.py -- Monte Carlo Craft Simulation

**Input:** item config, target tiers, run count, seed
**Output:** success_rate, expected_fp_used, percentiles, strategy comparison

Simulates thousands of craft attempts. Compares aggressive/balanced/conservative strategies and finds optimal path.

### optimization_engine.py -- Multi-Objective Stat Upgrade Optimization

**Input:** build (dict or BuildStats), goals, iterations, primary_skill
**Output:** `OptimizationResult` with best_upgrade, all_upgrades, Pareto front

Tests 86 candidate stat bumps. Composite scoring: `dps_gain * dps_weight + ehp_gain * ehp_weight`. Default weights: DPS 1.0, EHP 0.5.

`pareto_front()` returns candidates where no other candidate dominates in both DPS and EHP.

### build_optimizer.py -- Single-Value Upgrade Ranking

**Input:** `BuildStats`, primary_skill, skill_level, top_n
**Output:** `list[StatUpgrade]` with stat, label, dps_gain_pct, ehp_gain_pct, explanation

Same 86 stat increments, sorted by dps_gain_pct. Generates contextual explanations (diminishing return warnings, capped resistance notes).

### sensitivity_analyzer.py -- Stat Marginal Value Analysis

**Input:** `BuildStats`, primary_skill, offense/defense weights
**Output:** `SensitivityResult` with entries sorted by impact_score

Tests 50+ stats with +10% delta (or flat 10 for zero-value stats). Reports DPS gain, EHP gain, and weighted impact score.

### efficiency_scorer.py -- Affix Upgrade Scoring

**Input:** `BuildStats`, candidate_affixes, primary_skill, offense/defense weights
**Output:** `EfficiencyResult` with ranked `AffixCandidate` list

Efficiency = `(dps_gain * offense_weight + ehp_gain * defense_weight) / fp_cost`. FP cost scales by tier.

### upgrade_ranker.py -- Ranked Upgrade Lists

**Input:** `SensitivityResult`, mode (balanced/offense/defense)
**Output:** `RankingResult` with re-weighted stat rankings

Wraps sensitivity analysis with mode-based weight presets: balanced (60/40), offense (100/0), defense (0/100).

### boss_encounter.py -- Multi-Phase Boss Simulation

**Input:** `BuildStats`, boss profile, primary_skill, corruption, health/damage multipliers
**Output:** `BossEncounterResult` with per-phase results and summary

Per-phase: DPS adjusted for boss armor, resistances, and damage reduction. Health split by phase thresholds. Enrage detection. Immunity phases (0 DPS, fixed duration).

### corruption_scaler.py -- Corruption Scaling Curve

**Input:** `BuildStats`, boss profile, primary_skill, breakpoints, survival_threshold
**Output:** `CorruptionScalingResult` with curve data points and recommended_max_corruption

Health multiplier: linear 0-200 (up to 3x), accelerating curve 200+ via `(corruption - 200)^1.5`. Damage multiplier: linear `1.0 + corruption * 0.005`.

Recommended max = highest corruption where survival >= threshold.

### gear_upgrade_ranker.py -- Per-Slot Gear Item Evaluation

**Input:** `BuildStats`, build, primary_skill, slot_filter, top_n
**Output:** `GearUpgradeResult` with per-slot candidates and cross-slot top-10

Generates candidates from affix registry (filtered by slot). Evaluates DPS/EHP delta and FP cost. Efficiency = weighted_impact / fp_cost.

### comparison_engine.py -- Two-Build Comparison

**Input:** two builds with stats, primary skills, gear
**Output:** `ComparisonResult` with DPS/EHP comparison, stat deltas, skill comparison, overall winner

DPS winner by total_dps, EHP winner by effective_hp. Overall winner: 60% DPS + 40% EHP normalized scoring. Stat deltas for all BuildStats fields with >0.001 difference.

### combat_simulator.py -- Time-Based Combat Loop

Tick-based combat loop with skill rotation, cooldown tracking, mana gating, and priority ordering.

### stat_resolution_pipeline.py -- 8-Layer Stat Resolution

Convenience wrapper implementing the full 8-layer pipeline. `quick_resolve(build)` resolves a build dict into final `BuildStats`. `apply_derived_stats(stats)` handles layer 6 (attribute-to-secondary expansion).

### affix_engine.py -- Affix Data & Filtering

Loads and filters affix data. Functions: `get_prefixes()`, `get_suffixes()`, `get_affix_pool()`, `get_affix_by_name()`. Integrates with AffixRegistry at app startup.

### base_engine.py -- Base Item Data & FP Management

Base item definitions, FP ranges, random/manual/fixed FP modes. Functions: `get_base()`, `get_bases_for_slot()`, `generate_fp()`, `validate_fp()`.

### item_engine.py -- Item Creation

Creates items with base properties and affix containers.

### fp_engine.py -- Forging Potential Cost Engine

Rolls FP costs per tier with RNG-based outcomes.

### build_serializer.py -- Build Serialization

Serializes build data for engine consumption.

### validators.py -- Input Validation

Validates engine input parameters.

---

## Key Design Patterns

**Stat Modification Pattern:**
Clone BuildStats, modify target field, re-derive dependent stats (e.g., crit_chance from crit_chance_pct), recalculate DPS/EHP, compare against baseline.

**Result Serialization:**
All engines return dataclasses with `.to_dict()` methods for JSON serialization.

**Deterministic with Seeding:**
Monte Carlo DPS supports seed parameter for reproducible runs. All optimization uses sorted iteration order.

**Pure Functions:**
No side effects, no global state mutations. Engines accept typed inputs and return new outputs.
