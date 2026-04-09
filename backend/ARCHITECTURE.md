# The Forge — Architecture & Pipeline Reference

> Version 0.3.0 | Last Epoch Build Optimization Toolkit

---

## Project Overview

The Forge is a full-stack build optimization and combat simulation tool for Last Epoch. It consists of a **Python Flask backend** (stat engines, combat simulation, crafting) and a **React TypeScript frontend** (build planner, passive tree, gear editor, encounter simulator).

```
le-the-forge/
├── backend/          Python Flask API + simulation engines
├── frontend/         React TypeScript UI
├── data/             Game data (JSON — classes, items, enemies, skills)
├── electron/         Desktop app packaging
├── docs/             Documentation
├── scripts/          Build/deploy scripts
└── docker-compose.yml
```

---

## Backend Architecture

### Directory Map

```
backend/
├── app/                    Flask application
│   ├── combat/             Combat simulation loop (NEW)
│   ├── constants/          Game constants (crit caps, defense values, slots)
│   ├── domain/             Pure domain models (no DB, no HTTP)
│   │   ├── calculators/    Pure math functions (damage, crit, speed, etc.)
│   │   └── registries/     O(1) lookup registries (affix, skill, enemy)
│   ├── enemies/            Enemy defense engine (NEW)
│   ├── engines/            Core computation engines
│   ├── game_data/          JSON data files + loaders
│   ├── models/             SQLAlchemy ORM models
│   ├── routes/             Flask API endpoints
│   ├── schemas/            Marshmallow request/response schemas
│   ├── services/           Service layer (DB → engine orchestration)
│   ├── skills/             Skill execution engine (NEW)
│   ├── stats/              Derived + conditional stat layers (NEW)
│   └── utils/              Logging, auth, caching
├── builds/                 Build definition + subsystems
├── buffs/                  Buff lifecycle engine
├── combat/                 Hit resolution + spatial combat
├── conditions/             Condition model + evaluator
├── data/                   Data pipeline (loaders, mappers, schemas)
├── debug/                  Debug loggers
├── encounter/              Multi-enemy encounter system
├── modifiers/              Conditional modifier engine
├── services/               Integration services
├── state/                  Simulation state engine
└── tests/                  Test suite (9900+ tests)
```

---

## Pipeline 1: Stat Resolution (8 Layers)

The core character stat pipeline transforms build inputs into final resolved stats.

```
AffixDefinition → Affix → Item → EquipmentSet → StatPool
                                                    ↑
                                     PassiveSystem ──┘
                                                    ↑
                                       BuffSystem ──┘
                                                    ↓
                              stat_resolution_pipeline
                                        ↓
                    Layer 1: Base Stats (class + mastery)
                    Layer 2: Flat Additions (gear affixes)
                    Layer 3: Increased % (additive percent pool)
                    Layer 4: More Multipliers (multiplicative)
                    Layer 5: Conversions (damage type redirects)
                    Layer 6: Derived Stats (attribute → secondary)
                    Layer 7: Registry Derived (EHP, armor mit, dodge)
                    Layer 8: Conditional Stats (context-driven bonuses)
                                        ↓
                                   BuildStats
```

### Key Files

| File | Purpose |
|------|---------|
| `app/engines/stat_engine.py` | BuildStats dataclass (200+ fields), StatPool (flat/increased/more/multiplier buckets), aggregate_stats() — Layer 1-4 aggregation |
| `app/engines/stat_resolution_pipeline.py` | resolve_final_stats() — orchestrates all 8 layers, ResolutionResult with layer snapshots |
| `app/domain/item.py` | AffixDefinition (template), AffixTier, Affix (instance), Item with apply_to_stat_pool() |
| `app/domain/equipment_set.py` | EquipmentSet — slot-managed item container, apply_to_stat_pool() aggregates all items |
| `app/domain/build_state.py` | BuildState — mutable build container, recompute() orchestrates full pipeline |
| `builds/passive_system.py` | PassiveSystem — node allocation + apply_to_stat_pool() via CORE_STAT_CYCLE/KEYSTONE_BONUSES |
| `builds/buff_system.py` | Buff, BuffSystem — buff lifecycle + apply_to_stat_pool() |
| `builds/build_definition.py` | BuildDefinition — immutable build config (class, mastery, gear, passives, buffs) |
| `builds/build_stats_engine.py` | BuildStatsEngine — compiles BuildDefinition → BuildStats |
| `builds/stat_modifiers.py` | StatModifier, FinalModifierStack, StatModifierEngine |
| `builds/gear_system.py` | GearItem, GearAffix — gear slot system with validation |
| `app/stats/derived_stats.py` | DerivedStatRegistry — Layer 7: armor mitigation, EHP, dodge chance, health regen, mana regen |
| `app/stats/conditional_stats.py` | Layer 8: apply_conditional_stats() — context-driven bonuses (moving, ward, frozen, boss) |
| `app/stats/runtime_context.py` | RuntimeContext — bridges build-planning flags to SimulationState |

### Pipeline Contract

**Inputs:**
- `build: dict` — character_class (str), mastery (str), passive_tree (list[int] | list[dict]), gear (list[dict]), gear_affixes (list[dict]), passive_stats (dict | None)
- `conversions: list[dict] | None` — damage type redirections `{"from": str, "to": str, "pct": float}`
- `conditional_modifiers: list[ConditionalModifier] | None` — Layer 8 context-gated modifiers
- `runtime_context: RuntimeContext | None` — assumed conditions for Layer 8

**Outputs:**
- `ResolutionResult.stats: BuildStats` — fully resolved character stats (200+ fields)
- `ResolutionResult.layer_snapshots: dict[str, dict]` — per-layer BuildStats snapshots (when capture_snapshots=True)
- `ResolutionResult.resolution_order: list[str]` — ordered layer labels (8 entries)
- `ResolutionResult.warnings: list[str]` — resistance cap warnings, validation notes

**Invariants:**
- Layer execution order is strict: 1→2→3→4→5→6→7→8, never reordered
- All "increased" modifiers are summed additively before application
- All "more" modifiers are compounded multiplicatively after "increased"
- Derived stats (Layer 7) resolve after conversions (Layer 5) and attribute expansion (Layer 6)
- Conditional stats (Layer 8) apply after all base math is final
- Resistances are capped at RES_CAP (75) after all layers complete
- Identical inputs always produce identical outputs (deterministic)
- Input dicts are never mutated

**Failure Conditions:**
- Unknown stat_key in affix → silently skipped (no crash, value lost)
- Circular derived stat dependency → detected by `_validate_no_circular_deps()` at registration time
- Missing character_class → defaults to "Sentinel"
- Empty gear_affixes → valid (zero gear contribution)

### Observability Hooks

- **Layer snapshots:** `capture_snapshots=True` records `dataclasses.asdict(stats)` after each layer (keys: `1_base_stats` through `8_conditional_stats`)
- **Derived entry trace:** Layer 7 snapshot includes `_derived_entries` list with per-function `{name, inputs, outputs}`
- **Conditional trace:** Layer 8 snapshot includes `_conditional` dict with `{context, evaluated, active_ids, stat_deltas}`
- **Resolution warnings:** Resistance cap events logged as structured warnings in `ResolutionResult.warnings`
- **Structured logging:** `ForgeLogger` emits `resolve_final_stats.start` and `.done` events with class, mastery, affix count, node count

### Performance Characteristics

- **Complexity:** O(A + N + D + C) where A=affixes, N=passive nodes, D=derived stat entries, C=conditional modifiers
- **StatPool bucketing:** O(1) per modifier insertion, O(F) for resolve_to where F=unique stat fields
- **Memory:** One BuildStats instance (~200 floats) per resolution + optional snapshot copies (8× when capturing)
- **Scaling risk:** Large passive_stats dicts with 100+ keys increase Layer 5 merge time linearly

---

## Pipeline 2: Skill Damage Execution

Computes per-hit damage, average hit, and DPS for a skill using resolved BuildStats.

```
SkillStatDef + BuildStats + SkillModifiers
                    ↓
     1. scale_skill_damage() — base × level scaling
     2. sum_flat_damage() — added gear damage
     3. DamageContext.from_build() — increased% + more sources
     4. calculate_final_damage() — Base → Increased → More
     5. effective_crit_chance() + calculate_average_hit()
     6. effective_attack_speed()
     7. DPS = avg_hit × hits_per_cast × casts/sec
     8. calc_ailment_dps() — Bleed/Ignite/Poison steady-state DPS
     9. total_dps = hit_dps + ailment_dps
                    ↓
          SkillExecutionResult
```

### Key Files

| File | Purpose |
|------|---------|
| `app/skills/skill_execution.py` | SkillExecutionEngine.execute() — single entry point, SkillExecutionResult |
| `app/domain/skill.py` | SkillStatDef (template: damage, speed, scaling, mana_cost), SkillSpec (instance: name, level, spec tree) |
| `app/domain/skill_modifiers.py` | SkillModifiers — per-skill spec-tree bonuses (more damage, extra hits, speed, crit) |
| `app/domain/calculators/skill_calculator.py` | scale_skill_damage(), sum_flat_damage(), hits_per_cast() |
| `app/domain/calculators/final_damage_calculator.py` | DamageContext, DamageResult, calculate_final_damage() pipeline |
| `app/domain/calculators/damage_type_router.py` | DamageType enum, stat field routing per damage/skill type |
| `app/domain/calculators/increased_damage_calculator.py` | sum_increased_damage() — additive % pools |
| `app/domain/calculators/more_multiplier_calculator.py` | apply_more_multiplier() — multiplicative stacking |
| `app/domain/calculators/crit_calculator.py` | effective_crit_chance(), effective_crit_multiplier(), calculate_average_hit() |
| `app/domain/calculators/speed_calculator.py` | effective_attack_speed() — spell cast speed vs melee attack speed routing |
| `app/domain/calculators/ailment_calculator.py` | calc_ailment_dps() — Bleed/Ignite/Poison steady-state DPS from proc chance + scaling |

### Pipeline Contract

**Inputs:**
- `skill_def: SkillStatDef` — base_damage, level_scaling, attack_speed, scaling_stats, damage_types, mana_cost, hit_count, is_spell/melee/throwing/bow
- `stats: BuildStats` — fully resolved character stats (read-only, never mutated)
- `level: int` — skill level (1–20)
- `skill_mods: SkillModifiers | None` — more_damage_pct, added_hits_per_cast, attack_speed_pct, cast_speed_pct, crit_chance_pct, crit_multiplier_pct

**Outputs:**
- `SkillExecutionResult.hit_damage: float` — raw per-hit damage before crit
- `SkillExecutionResult.average_hit: float` — crit-weighted per-hit damage
- `SkillExecutionResult.dps: float` — sustained damage per second
- `SkillExecutionResult.crit_chance: float` — effective crit (0.0–0.95)
- `SkillExecutionResult.crit_multiplier: float` — effective multiplier
- `SkillExecutionResult.casts_per_second: float` — effective attack/cast speed
- `SkillExecutionResult.hits_per_cast: int` — total hits per activation
- `SkillExecutionResult.damage_by_type: dict[str, float]` — per-DamageType breakdown

**Invariants:**
- BuildStats is never modified (read-only consumption)
- Level scaling: `base × (1 + level_scaling × (level - 1))`
- Increased % sources are summed additively, then applied as single multiplier
- More multipliers applied sequentially after increased
- Crit chance capped at CRIT_CHANCE_CAP (0.95)
- DPS = average_hit × hits_per_cast × casts_per_second (exact formula)
- Deterministic: no randomness in any stage

**Failure Conditions:**
- Unknown scaling_stat → silently produces 0 increased% for that stat
- Zero attack_speed → defaults to 1.0 in SkillStatDef.from_dict()
- Empty damage_types → untyped total (no per-type breakdown)

### Observability Hooks

- **Debug trace:** `capture_debug=True` populates `SkillExecutionResult.debug` dict with: scaled_total, flat_added, effective_base, increased_damage_pct, more_damage_sources, hit_damage, crit_chance, crit_multiplier, average_hit, casts_per_second, hits_per_cast, dps
- **Structured logging:** `skill_execution.start` and `.done` events with skill name, level, base_damage, hit_damage, dps

### Performance Characteristics

- **Complexity:** O(S + T) where S=scaling_stats count, T=damage_types count
- **Memory:** One SkillExecutionResult per call (~12 scalars + small dict)
- **Hot path:** Pre-computable — combat simulator caches results since same skill+stats=same output

---

## Pipeline 3: Enemy Defense Application

Applies enemy resistances, armor, and dodge to skill damage output.

```
SkillExecutionResult + EnemyInstance
                    ↓
     1. Per-type damage split
     2. Resistance reduction per type
     3. Armor mitigation (physical only)
     4. Dodge as expected-value multiplier
     5. Effective DPS = raw DPS × defense multiplier
                    ↓
          DefensedDamageResult
```

### Key Files

| File | Purpose |
|------|---------|
| `app/enemies/enemy_defense.py` | EnemyDefenseEngine.apply_defenses(), DefensedDamageResult |
| `app/engines/defense_engine.py` | calculate_defense() → DefenseResult with endurance_damage_reduction, EHP, survivability score |
| `app/domain/enemy.py` | EnemyStats, EnemyArchetype (TRAINING_DUMMY/NORMAL/ELITE/BOSS), EnemyProfile, EnemyInstance |
| `app/domain/resistance.py` | apply_resistance(), RES_CAP (75%), RES_MIN (-100%) |
| `app/domain/armor.py` | armor_mitigation_pct(), apply_armor(), ARMOR_K=10, ARMOR_MITIGATION_CAP=0.75 |
| `app/domain/dodge.py` | dodge_chance(), DODGE_CAP=0.75 |
| `app/domain/penetration.py` | effective_resistance() with penetration + shred |
| `app/domain/registries/enemy_registry.py` | EnemyRegistry — O(1) enemy profile lookup |

### Pipeline Contract

**Inputs:**
- `skill_result: SkillExecutionResult` — pre-computed skill damage output (read-only)
- `enemy: EnemyInstance` — mutable combat instance with resistances, armor, shred state
- `penetration: dict[str, float] | None` — per-type penetration from BuildStats

**Outputs:**
- `DefensedDamageResult.damage_dealt: float` — final damage after all defenses
- `DefensedDamageResult.damage_mitigated: float` — total absorbed by defenses
- `DefensedDamageResult.mitigation_pct: float` — overall % mitigated
- `DefensedDamageResult.effective_dps: float` — DPS after defenses
- `DefensedDamageResult.per_type_damage: dict[str, float]` — post-defense per-type breakdown
- `DefensedDamageResult.resistance_reduction: float` — damage lost to resistances
- `DefensedDamageResult.armor_reduction: float` — damage lost to armor (physical only)
- `DefensedDamageResult.dodge_reduction: float` — damage lost to dodge (expected value)

**Invariants:**
- damage_dealt + damage_mitigated = damage_before (conservation law)
- Armor applies only to "physical" damage type — all others bypass
- Resistance clamped to [RES_MIN (-100%), RES_CAP (75%)] after penetration/shred
- Penetration reduces effective resistance: `eff = clamp(base - shred - pen)`
- Dodge is expected-value: `final = post_armor × (1 - dodge_chance)`
- Training dummy (zero defenses) produces damage_dealt == damage_before

**Failure Conditions:**
- Negative armor → raises ValueError in armor_mitigation_pct()
- Unknown damage_type key → 0% resistance applied (no crash)
- SkillExecutionResult with empty damage_by_type → treated as untyped

### Observability Hooks

- **Debug trace:** `capture_debug=True` populates `DefensedDamageResult.debug` with: damage_by_type_before, resistance_detail (per-type effective_res/before/after), armor_mitigation (enemy_armor/physical_before/physical_after), dodge (dodge_chance/dodge_reduction)
- **Structured logging:** `enemy_defense.start`, `.resistance_done`, `.armor_done`, `.done` events

### Performance Characteristics

- **Complexity:** O(T) where T=damage types in the skill (typically 1–3)
- **Memory:** One DefensedDamageResult per call (~10 scalars + small dict)
- **Hot path:** Pre-computable per (skill, enemy) pair — combat simulator caches this

---

## Pipeline 4: Combat Simulation Loop

Time-based execution loop that repeatedly casts skills against an enemy.

```
CombatScenario + BuildStats
        ↓
  ┌─────────────────────────────────────┐
  │  for tick in 0 → duration:          │
  │    for skill in rotation (priority):│
  │      if cooldown ready:             │
  │        if mana available:           │
  │          spend mana                 │
  │          SkillExecutionEngine       │
  │          EnemyDefenseEngine         │
  │          accumulate damage          │
  │        else: skip (OOM)             │
  │    advance cooldowns                │
  │    mana_pool.regenerate(tick)       │
  └─────────────────────────────────────┘
        ↓
  SimulationResult
```

### Key Files

| File | Purpose |
|------|---------|
| `app/combat/combat_simulator.py` | CombatSimulator.simulate() — tick loop, SimulationResult (includes ailment_dps, mana tracking), TimelineEvent |
| `app/combat/combat_scenario.py` | CombatScenario (duration, enemy, rotation, mana config), SkillRotationEntry |
| `app/domain/mana.py` | ManaPool — can_afford(), spend(), regenerate(), InsufficientManaError |

### Pipeline Contract

**Inputs:**
- `scenario: CombatScenario` — duration_seconds, enemy (EnemyInstance), rotation (tuple[SkillRotationEntry]), tick_size, max_mana, mana_regen_rate, penetration
- `stats: BuildStats` — fully resolved character stats (read-only)
- `capture_timeline: bool` — whether to record per-cast TimelineEvents

**Outputs:**
- `SimulationResult.total_damage: float` — sum of all post-defense damage
- `SimulationResult.effective_dps: float` — total_damage / fight_duration
- `SimulationResult.raw_dps: float` — DPS before enemy defenses
- `SimulationResult.total_casts: int` — total skill activations
- `SimulationResult.skill_usage: dict[str, int]` — per-skill cast counts
- `SimulationResult.skill_damage: dict[str, float]` — per-skill total damage
- `SimulationResult.total_mana_spent: float` — total mana consumed
- `SimulationResult.total_mana_regenerated: float` — total mana restored
- `SimulationResult.casts_skipped_oom: int` — casts skipped due to insufficient mana
- `SimulationResult.timeline: list[TimelineEvent]` — per-cast event log (if captured)

**Invariants:**
- Fully deterministic: same inputs → same outputs, zero randomness
- Skill execution results pre-computed once (same skill + stats = same damage every cast)
- Cooldown only starts on successful cast (OOM skip does NOT trigger cooldown)
- Mana regeneration occurs after all casting in each tick
- Skills evaluated in priority order (lower priority number = higher priority)
- ManaPool created fresh per simulate() call (no cross-run state leakage)
- max_mana=0 disables mana system entirely (backward compatible)
- sum(skill_damage.values()) == total_damage
- sum(skill_usage.values()) == total_casts

**Failure Conditions:**
- duration_seconds <= 0 → raises ValueError
- Empty rotation → raises ValueError
- tick_size <= 0 → raises ValueError
- Negative mana_cost on skill → skipped by ManaPool validation

### Observability Hooks

- **Timeline events:** Each cast recorded as `TimelineEvent(time, skill_name, damage_before_defense, damage_after_defense, mitigation_pct)` when `capture_timeline=True`
- **Mana telemetry:** `total_mana_spent`, `total_mana_regenerated`, `casts_skipped_oom` always tracked in SimulationResult
- **Structured logging:** `combat_sim.start` (duration, tick, n_skills, mana_enabled, max_mana) and `combat_sim.done` (total_damage, effective_dps, total_casts, ticks, mana_spent, mana_regenerated, casts_skipped_oom)
- **Serialization:** `SimulationResult.to_dict()` omits mana fields when mana was not used

### Performance Characteristics

- **Complexity:** O((D/T) × S) where D=duration, T=tick_size, S=skills in rotation — linear in fight length
- **Pre-computation:** Skill execution and defense results computed once upfront (O(S) setup), then O(1) lookup per cast
- **Memory:** O(D/T) for timeline events if captured; O(S) for cooldown/mana tracking
- **Scaling risk:** Very small tick_size (e.g. 0.01) with long duration (e.g. 300s) → 30,000 ticks; timeline capture at that scale produces large event lists

### Ailment Integration

The combat simulator aggregates steady-state ailment DPS from all skills in the rotation.
Ailment DPS is computed per-skill by `SkillExecutionEngine` (via `calc_ailment_dps()`) and
summed across the rotation into `SimulationResult.ailment_dps` and `total_dps_with_ailments`.

| Ailment | Application Stat | Stack Limit | Base Ratio | Duration | Damage Scaling |
|---------|-----------------|-------------|------------|----------|----------------|
| Ignite  | `ignite_chance_pct` | 1 (strongest) | 20% DPS/stack | 3s | `fire_damage_pct + dot_damage_pct + ailment_damage_pct + ignite_damage_pct` |
| Bleed   | `bleed_chance_pct`  | 8 | 70% total/duration | 4s | `physical_damage_pct + dot_damage_pct + ailment_damage_pct + bleed_damage_pct` |
| Poison  | `poison_chance_pct` | 8 | 30% DPS/stack | 3s | `poison_damage_pct + dot_damage_pct + ailment_damage_pct + poison_dot_damage_pct` |
| Shock   | `shock_chance_pct`  | 1 | — (utility) | — | +20% damage taken by target |
| Chill   | `chill_chance_pct`  | 1 | — (utility) | — | +25% cold damage taken by target |

### Key Ailment Files

| File | Purpose |
|------|---------|
| `app/domain/ailments.py` | AilmentType enum, AilmentInstance, apply_ailment(), tick_ailments() |
| `app/domain/ailment_scaling.py` | scale_ailment_damage() — routes ailment types to stat pools |
| `app/domain/ailment_stacking.py` | STACK_LIMITS, enforce_stack_limit(), apply_ailment_with_limit() |
| `app/domain/ailment_duration_scaling.py` | scale_ailment_duration() — duration modifier application |
| `app/domain/calculators/ailment_calculator.py` | calc_ailment_dps() — steady-state Bleed/Ignite/Poison DPS |
| `app/domain/status_interactions.py` | Shock/Frostbite damage-taken multipliers, ailment synergies |

---

## Pipeline 5: Crafting Simulation

Models the item crafting system with forging potential and RNG.

```
Base Item + Crafting Action
        ↓
  FP Engine (cost roll)
  Affix Engine (valid affixes for slot)
  Craft Engine (apply action)
  Craft Simulator (Monte Carlo outcomes)
        ↓
  Crafted Item + FP History
```

### Key Files

| File | Purpose |
|------|---------|
| `app/engines/craft_engine.py` | Crafting action execution |
| `app/engines/craft_simulator.py` | Monte Carlo crafting simulation |
| `app/engines/fp_engine.py` | Forging potential cost/generation |
| `app/engines/affix_engine.py` | Affix pool queries, validation, slot limits |
| `app/engines/base_engine.py` | Base item data, FP ranges |
| `app/engines/item_engine.py` | Item creation with FP resolution |
| `app/domain/registries/affix_registry.py` | AffixRegistry — O(1) affix lookup by name/id/slot |

### Pipeline Contract

**Inputs:**
- `base_type: str` — base item slot/type
- `rarity: str` — Normal/Magic/Rare/Exalted
- `action_type: str` — crafting action (e.g. "add_affix", "upgrade_tier")
- `item: dict` — item state with prefixes, suffixes, sealed_affix, forging_potential
- `n_simulations: int` — Monte Carlo iteration count (for craft_simulator)

**Outputs:**
- Crafted item dict with updated affixes, FP, history
- `craft_simulator` → probability distributions, success rates, expected costs

**Invariants:**
- FP cost is always non-negative
- FP cannot go below 0 (craft fails if cost > remaining FP)
- Prefix count <= MAX_PREFIXES (2), suffix count <= MAX_SUFFIXES (2)
- Sealed affixes do not count toward prefix/suffix limits
- Affix tier range: [1, MAX_AFFIX_TIER (7)]
- FP cost rolls use seeded RNG for reproducibility when seed is provided

**Failure Conditions:**
- Insufficient FP for action → craft fails, item unchanged
- Invalid affix for item slot → rejected by is_affix_valid_for_item()
- Affix slot overflow → rejected by validate_affix_slots()

### Observability Hooks

- **FP history:** Each craft action appends `{action, fp_cost, remaining_fp}` to item["history"]
- **Monte Carlo logging:** craft_simulator records attempt distributions
- **Structured logging:** FP events logged via `log_fp_event()`

### Performance Characteristics

- **Single craft:** O(1) per action
- **Monte Carlo:** O(N) where N=n_simulations — linear in iteration count
- **Memory:** O(N) for result distributions; O(H) for per-item FP history where H=craft attempts

---

## Pipeline 6: Validation Layer

Validates build configurations, items, and affixes before processing.

### Key Files

| File | Purpose |
|------|---------|
| `app/engines/validators.py` | validate_item(), validate_build(), validate_affix_combination(), validate_stat_ranges() |
| `app/schemas/api_contracts.py` | Marshmallow schemas for API request/response validation |

---

## Conditional & Buff Systems

### Condition System

```
Condition (model) → ConditionEvaluator → ConditionalModifier → ConditionalModifierEngine
                          ↑
                   SimulationState
```

| File | Purpose |
|------|---------|
| `conditions/models/condition.py` | Condition — immutable predicate (health_pct, buff_active, status_present, time_elapsed) |
| `conditions/condition_evaluator.py` | ConditionEvaluator — evaluates Condition vs SimulationState |
| `conditions/time_window.py` | TimeWindow, TimeWindowTracker — time-based condition windows |
| `modifiers/models/conditional_modifier.py` | ConditionalModifier — stat delta gated by Condition |
| `modifiers/conditional_modifier_engine.py` | ConditionalModifierEngine — evaluates + aggregates active modifiers |
| `state/state_engine.py` | SimulationState — mutable runtime state (health, buffs, statuses, time) |

### Buff System

| File | Purpose |
|------|---------|
| `buffs/buff_definition.py` | BuffDefinition — immutable template with stacking behavior |
| `buffs/buff_instance.py` | BuffInstance — active buff with remaining duration |
| `buffs/buff_engine.py` | BuffEngine — lifecycle management |
| `buffs/stack_resolver.py` | Stack behavior resolution (ADD_STACK, REFRESH, REPLACE, IGNORE) |
| `buffs/tick_buffs.py` | Per-tick buff advancement |
| `app/domain/timeline.py` | TimelineEngine — tick-based buff tracking for combat |
| `app/domain/buff_snapshot.py` | SnapshotBuff vs DynamicBuff resolution modes |

### Buff & Condition Pipeline Contract

**Condition Inputs:**
- `condition: Condition` — condition_id, condition_type (target_health_pct | player_health_pct | buff_active | status_present | time_elapsed), threshold_value, comparison_operator
- `state: SimulationState` — player_health, target_health, elapsed_time, active_buffs (set[str]), active_status_effects (dict[str, int])

**Condition Outputs:**
- `bool` — True when condition is satisfied

**Buff Engine Inputs:**
- `definition: BuffDefinition` — buff_id, stat_modifiers, duration_seconds, max_stacks, stack_behavior, activation_condition
- `timestamp: float` — application time
- `delta_time: float` — tick advancement

**Buff Engine Outputs:**
- `BuffFrameResult` — aggregated stat deltas, active buff list, debug snapshot

**Invariants:**
- Condition evaluation is stateless and pure (no side effects)
- Numeric conditions (health_pct, time_elapsed) use explicit comparison operators (lt, le, eq, ge, gt)
- Buff stacking obeys StackBehavior: ADD_STACK increments, REFRESH_DURATION resets timer, IGNORE is no-op, REPLACE overwrites
- BuffEngine execution order is strict: apply → tick → resolve
- Duration=None buffs are permanent (never expire)
- Deterministic: `BuffEngine.run_determinism_check()` validates this

**Failure Conditions:**
- Invalid condition_type → raises ValueError on construction
- Numeric condition without threshold_value → raises ValueError
- Negative duration → raises ValueError
- Invalid modifier_type → raises ValueError (must be additive | multiplicative | override)

### Observability Hooks

- **Buff debug export:** `export_active_buffs()` produces per-buff debug entries (id, stacks, remaining_duration, modifiers)
- **Condition evaluation logging:** ConditionalModifierEngine logs per-modifier active/inactive status
- **ConditionalLogger:** `debug/conditional_logger.py` records tick-level evaluation history with state snapshots

---

## Encounter System

Multi-enemy encounter simulation with phases, spawning, and downtime.

| File | Purpose |
|------|---------|
| `encounter/state_machine.py` | EncounterMachine — full encounter runner |
| `encounter/enemy.py` | EncounterEnemy — mutable combat entity with shields |
| `encounter/target_manager.py` | TargetManager — multi-target selection |
| `encounter/spawn_controller.py` | Wave-based enemy spawning |
| `encounter/phases.py` | PhaseController — boss phase transitions |
| `encounter/downtime.py` | DowntimeTracker — movement/dodge windows |
| `encounter/result_aggregator.py` | AggregatedResult — multi-run statistics |
| `encounter/boss_templates.py` | Pre-built boss encounter configs |

### Encounter Pipeline Contract

**Inputs:**
- `EncounterConfig` — enemies (list[EncounterEnemy]), fight_duration, tick_size, base_damage, hit_config (MultiHitConfig), phases, spawn_waves, downtime_windows, timeline_events, stop_on_all_dead

**Outputs:**
- `EncounterRunResult` — total_damage, elapsed_time, ticks_simulated, all_enemies_dead, enemies_killed, total_casts, downtime_ticks, active_phase_id, damage_per_tick (list[float])
- `AggregatedResult` (from result_aggregator) — multi-run statistics (avg/min/max/std for damage, dps, kills)

**Invariants:**
- Tick loop advances in fixed tick_size increments
- Downtime windows suppress all casting during their active period
- Phase transitions trigger at health thresholds
- Spawn waves introduce enemies at scheduled times
- stop_on_all_dead=True terminates early when all enemies die
- Dead enemies cannot take further damage

**Failure Conditions:**
- Empty enemy list → no targets (zero damage)
- fight_duration <= 0 → invalid config
- Enemy health <= 0 → immediately dead on spawn

### Observability Hooks

- **damage_per_tick:** Full tick-level damage history in EncounterRunResult
- **Phase tracking:** active_phase_id in result shows final phase state
- **Result aggregation:** aggregate_results() computes statistical summaries across multiple runs

### Performance Characteristics

- **Complexity:** O((D/T) × E) where D=duration, T=tick_size, E=alive enemies per tick
- **Memory:** O(D/T) for damage_per_tick list; O(E) for target tracking
- **Scaling risk:** Large enemy counts (50+ via MAX_ENEMIES) with small tick_size

---

## Rotation System

### Key Files

| File | Purpose |
|------|---------|
| `app/domain/rotation.py` | SkillEntry, RotationEngine, select_next() — priority-based skill selection |
| `app/domain/cooldown.py` | CooldownManager — per-skill cooldown tracking |
| `app/domain/full_combat_loop.py` | FullCombatLoop — integrates rotation + cooldowns + mana + ailments + buffs + triggers |

### Rotation Pipeline Contract

**Inputs:**
- `entries: list[SkillEntry]` — skills with name, mana_cost, cooldown, priority
- `current_mana: float` — available mana
- `cooldown_remaining: dict[str, float]` — per-skill cooldown timers

**Outputs:**
- `SkillEntry | None` — highest-priority ready skill, or None if all on cooldown/OOM

**Invariants:**
- Skills evaluated in priority order (lower number = higher priority)
- A skill is "ready" when: cooldown_remaining <= 0 AND current_mana >= mana_cost
- select_next() is a pure function — no side effects
- Cooldown only starts after successful cast

---

## Data Layer

> **Note:** `data/` is the single source of truth for game data. The `app/game_data/` directory
> retains only files unique to the backend (skills.json, constants.json, classes.json).
> Affixes, enemies, base items, and crafting rules are loaded from `data/` via the GameDataPipeline.

### Game Data Files

| File | Contents |
|------|----------|
| `app/game_data/skills.json` | 80+ skill definitions (damage, speed, scaling, mana_cost, type) |
| `app/game_data/constants.json` | Crafting limits, defense caps, passive limits |
| `app/game_data/classes.json` | Class/mastery definitions (curated backend config) |
| `data/entities/enemy_profiles.json` | 8 enemy profiles (training dummy → pinnacle boss) |
| `data/classes/skill_tree_nodes.json` | Skill tree node definitions |
| `data/items/base_items.json` | 100+ base items |
| `data/items/affixes.json` | 1000+ affix definitions with tiers and slot applicability |

### Data Pipeline

| File | Purpose |
|------|---------|
| `app/game_data/game_data_loader.py` | Loads JSON data, provides affix tier midpoints, stat keys |
| `data/loaders/raw_data_loader.py` | Raw data file loading |
| `data/mappers/data_mapper.py` | Transforms raw data to domain models |
| `data/versioning/versioned_loader.py` | Version-aware data loading |

---

## API Routes

| Route File | Endpoints |
|------------|-----------|
| `app/routes/simulate.py` | POST /api/simulate/stats (60/min), /build (30/min), /encounter (15/min) — rate limits configurable via env vars |
| `app/routes/builds.py` | CRUD for builds |
| `app/routes/craft.py` | POST /api/craft, /predict, /action |
| `app/routes/passives.py` | Passive tree data |
| `app/routes/optimize.py` | Build optimization |
| `app/routes/conditional.py` | POST /api/simulate/conditional |
| `app/routes/rotation.py` | Skill rotation simulation |
| `app/routes/multi_target.py` | Multi-target encounter API |
| `app/routes/auth.py` | Discord OAuth |
| `app/routes/import_route.py` | Build import |
| `app/routes/bis_search.py` | Best-in-slot search |

---

## Frontend Structure

```
frontend/src/
├── App.tsx                 Root component
├── main.tsx                Entry point
├── lib/
│   ├── api.ts              Backend API client
│   ├── simulation.ts       Frontend stat aggregation (mirrors stat_engine)
│   ├── gameData.ts         Skill/class constants
│   └── crafting.ts         Crafting logic
├── components/
│   ├── features/           Feature pages
│   │   ├── build/          Build editor (GearEditor, PassiveTree, etc.)
│   │   ├── encounter/      Encounter simulator UI
│   │   ├── optimizer/      Optimization UI
│   │   └── craft/          Crafting simulator UI
│   ├── PassiveTree/        Passive tree SVG renderer
│   ├── skills/             Skill tree UI
│   ├── ui/                 Shared UI components
│   ├── visualization/      Replay/heatmap viewers
│   └── bis/                Best-in-slot UI
├── types/
│   ├── build.ts            Build type definitions
│   ├── skillTree.ts        Skill tree types
│   ├── buff.ts             Buff types
│   ├── conditionalStats.ts Conditional stat types
│   └── runtimeContext.ts   Runtime context types
├── store/                  State management
├── hooks/                  React hooks
├── pages/                  Route pages
└── styles/                 CSS
```

---

## Constants Reference

| Constant | Value | File |
|----------|-------|------|
| CRIT_CHANCE_CAP | 0.95 | `app/constants/combat.py` |
| BASE_CRIT_CHANCE | 0.05 | `app/constants/combat.py` |
| BASE_CRIT_MULTIPLIER | 1.5 | `app/constants/combat.py` |
| RES_CAP | 75 | `app/constants/defense.py` |
| ARMOR_K | 10.0 | `app/domain/armor.py` |
| ARMOR_MITIGATION_CAP | 0.75 | `app/domain/armor.py` |
| DODGE_CAP | 0.75 | `app/domain/dodge.py` |
| MAX_PREFIXES | 2 | `app/constants/crafting.py` |
| MAX_SUFFIXES | 2 | `app/constants/crafting.py` |
| MAX_AFFIX_TIER | 7 | `app/game_data/constants.json` |
| ENDURANCE_CAP | 60 | `app/constants/defense.py` |
| BLEED_BASE_RATIO | 0.70 | `app/constants/combat.py` |
| BLEED_DURATION | 4.0s | `app/constants/combat.py` |
| IGNITE_DPS_RATIO | 0.20 | `app/constants/combat.py` |
| IGNITE_DURATION | 3.0s | `app/constants/combat.py` |
| POISON_DPS_RATIO | 0.30 | `app/constants/combat.py` |
| POISON_DURATION | 3.0s | `app/constants/combat.py` |

---

## Test Coverage

9900+ tests across all systems. Key test files:

| Test File | Tests | System |
|-----------|-------|--------|
| `test_equipment_pipeline.py` | 34 | Item → EquipmentSet → BuildState → BuildStats |
| `test_derived_stats.py` | 28 | DerivedStatRegistry, Layer 7 pipeline |
| `test_conditional_stats.py` | 37 | RuntimeContext, Layer 8 pipeline |
| `test_skill_execution.py` | 28 | SkillExecutionEngine damage pipeline |
| `test_enemy_defense.py` | 23 | EnemyDefenseEngine resistance/armor/dodge |
| `test_combat_sim_loop.py` | 24 | CombatSimulator time-based loop |
| `test_mana_integration.py` | 18 | Mana resource gating in combat |
| `test_stat_engine.py` | 100+ | BuildStats, StatPool, aggregate_stats |
| `test_stat_resolution_pipeline.py` | 40+ | 8-layer pipeline |
| `test_validators.py` | 70+ | Input validation |
| `test_ailment_integration.py` | 13 | Ailment DPS in skill execution + combat sim |
| `test_rate_limiting.py` | 4 | Rate limit enforcement on simulation endpoints |

---

## System Boundaries & Responsibilities

Strict ownership rules govern what each layer is allowed to do.

### `app/domain/` — Pure Domain Models

- **MUST:** Be pure Python dataclasses/classes with no side effects
- **MUST:** Accept typed domain objects or primitives as inputs
- **MUST:** Return computed values without mutating inputs
- **MUST NOT:** Import Flask, SQLAlchemy, or any HTTP/DB modules
- **MUST NOT:** Perform I/O (file reads, network calls, database queries)
- **MUST NOT:** Access `current_app`, `request`, or any Flask globals
- **Side effects:** None permitted. All functions are referentially transparent.

### `app/domain/calculators/` — Pure Math Functions

- **MUST:** Be stateless functions (no class state, no globals)
- **MUST:** Accept primitives or domain objects, return primitives
- **MUST NOT:** Import anything outside `app/domain/` and `app/constants/`
- **Side effects:** None. These are the innermost pure core.

### `app/engines/` — Computation Engines

- **MUST:** Orchestrate domain calculators into higher-level computations
- **MAY:** Load game data from JSON files (via `game_data_loader`)
- **MAY:** Use `@lru_cache` for data file memoization
- **MUST NOT:** Import Flask, SQLAlchemy, or HTTP modules
- **MUST NOT:** Write to disk or make network calls
- **Side effects:** File reads for game data loading (cached). No writes.

### `app/services/` — Service Layer

- **MUST:** Orchestrate engines + DB access for API consumption
- **MAY:** Import Flask extensions (current_app, db)
- **MAY:** Perform database reads and writes
- **MAY:** Call multiple engines in sequence
- **MUST NOT:** Contain game logic or damage math
- **Side effects:** Database mutations, cache updates.

### `app/routes/` — API Endpoints

- **MUST:** Handle HTTP request/response only
- **MUST:** Validate input via Marshmallow schemas
- **MUST:** Delegate all logic to services or engines
- **MUST NOT:** Contain business logic, math, or data transformation
- **MUST NOT:** Directly instantiate domain objects
- **Side effects:** HTTP responses, request logging.

### `builds/` — Build Subsystems

- **MUST:** Be pure Python (no Flask, no DB)
- **MAY:** Import from `app/domain/` and `app/engines/`
- **Purpose:** Build-level abstractions (definition, gear, passives, buffs, stat compilation)
- **Side effects:** None.

### `buffs/`, `conditions/`, `modifiers/`, `state/` — Runtime Systems

- **MUST:** Be pure Python with mutable state containers
- **MUST:** Provide deterministic behavior (verifiable via determinism checks)
- **MAY:** Import from `app/domain/` for type references
- **MUST NOT:** Import Flask, DB, or HTTP modules
- **Side effects:** Internal state mutation only (buff stacks, cooldowns, health).

### `data/` — Data Pipeline

- **MUST:** Load, validate, and transform raw game data files
- **MAY:** Perform file I/O (read-only)
- **MUST NOT:** Import Flask or depend on application context
- **Side effects:** File reads only.

---

## Known Failure Modes & Safeguards

### Invalid Stat Reference

- **Detection:** `hasattr(stats, stat_key)` check before `setattr` in StatPool.resolve_to() and aggregate_stats
- **Recovery:** Unknown stat keys are silently skipped. Value is lost but no crash occurs.
- **Risk:** Typo in affix stat_key → silently ineffective gear. Mitigated by affix registry validation.

### Missing Skill Scaling Stats

- **Detection:** `AFFIX_STAT_KEYS.get(affix_name)` returns None for unknown affixes
- **Recovery:** apply_affix() returns early with no effect
- **Risk:** New affixes added to JSON but not to stat_key mappings → zero contribution

### Cooldown Desync

- **Detection:** Cooldown tracking uses `max(0.0, cd - tick)` clamping every tick
- **Recovery:** Floating-point drift cannot produce negative cooldowns
- **Risk:** Very small tick_size with many skills → accumulated float error. Mitigated by 1e-9 epsilon in ready check.

### Negative Resource Drift

- **Detection:** ManaPool.spend() raises InsufficientManaError if cost > current
- **Recovery:** Combat loop checks can_afford() before spend() — exception should never fire
- **Risk:** ManaPool.regenerate() clamps to max_mana — overshoot impossible

### Infinite Rotation Loop

- **Detection:** Combat simulator outer loop bounds: `while elapsed < duration`
- **Recovery:** Loop always terminates — elapsed advances by tick_size every iteration regardless of casting outcome
- **Risk:** Zero tick_size → infinite loop. Prevented by CombatScenario.__post_init__() validation.

### Circular Buff Dependencies

- **Detection:** BuffEngine.run_determinism_check() verifies identical outputs for identical inputs
- **Recovery:** Buff conditions evaluate against SimulationState, not against other buffs' stat outputs
- **Risk:** A buff that modifies health_pct could theoretically affect another buff's health_pct condition. Mitigated by strict apply→tick→resolve ordering (resolve reads state from before this frame's apply).

### Circular Derived Stat Dependencies

- **Detection:** `_validate_no_circular_deps()` in derived_stats.py checks at registration time
- **Recovery:** Warnings logged. Registry execution order is explicit (by `order` field).
- **Risk:** An entry that writes a field read by an earlier entry → stale data. Detected and warned.

### Resistance Over-Penetration

- **Detection:** `_clamp_resistance()` enforces [RES_MIN, RES_CAP] bounds
- **Recovery:** Penetration beyond enemy resistance produces negative effective resistance (more damage taken), clamped at RES_MIN (-100%)
- **Risk:** None — intentional game mechanic.

---

## Extension Safety Rules

Guidelines for adding new mechanics without architectural erosion.

### Adding a New Stat

1. Add the field to `BuildStats` in `app/engines/stat_engine.py` with a default value
2. If the stat comes from gear affixes: ensure the stat_key exists in `AFFIX_STAT_KEYS` (game_data_loader) and follows naming convention (`_pct` for increased, `more_` for multiplicative)
3. If the stat is derived: add a `DerivedStatEntry` to `DERIVED_STAT_REGISTRY` in `app/stats/derived_stats.py` with explicit reads/writes/order
4. Never modify existing stat field names — downstream consumers depend on them
5. Add test coverage for the new stat's pipeline path

### Adding a New Modifier Type

1. Extend `StatPool` buckets only if the new type has genuinely different math (not just a new stat key)
2. New modifier routing must go through `_route_to_pool()` or `apply_affix()` — never bypass StatPool
3. If the modifier is conditional: use the existing `ConditionalModifier` + `Condition` system
4. Add the modifier to `builds/stat_modifiers.py` ModifierType enum if it's a new category

### Adding a New Buff

1. Create a `BuffDefinition` with appropriate `StackBehavior`
2. Use existing `StatModifier` for stat effects — do not create parallel modifier systems
3. If the buff has activation conditions: use existing `Condition` model
4. Register via `BuffEngine.apply()` — do not directly mutate BuildStats
5. Test stacking behavior and duration decay independently

### Adding a New Enemy Type

1. Add profile to `data/entities/enemy_profiles.json` with all 7 resistance types
2. Register in `EnemyRegistry` at app startup
3. Use existing `EnemyArchetype` for preset tiers, or `EnemyProfile` for custom
4. Create `EnemyInstance` for mutable combat state — never modify EnemyProfile
5. EnemyDefenseEngine already handles arbitrary resistance/armor values — no engine changes needed

### Adding a New Resource System

1. Follow the `ManaPool` pattern: mutable dataclass with `can_afford()`, `spend()`, `regenerate()`
2. Add resource config to `CombatScenario` as immutable fields
3. Create fresh resource instance per `simulate()` call — never share across runs
4. Gate skill casting in the combat loop with the same `if can_afford → spend → cast` pattern
5. Track resource telemetry in `SimulationResult`

### Adding a New Pipeline Layer

1. Assign an explicit layer number (e.g. Layer 9)
2. Insert in `resolve_final_stats()` between the appropriate existing layers
3. Update `resolution_order` list
4. Add snapshot capture under `capture_snapshots` flag
5. Update all tests that assert layer count
6. Document the layer in this file with inputs, outputs, and invariants

### General Rules

- **Never bypass the pipeline.** All stat modifications must flow through StatPool or a designated pipeline layer.
- **Never add global mutable state.** All simulation state must be scoped to a single run.
- **Never import upward.** domain/ must not import from engines/. engines/ must not import from services/. services/ must not import from routes/.
- **Always default to backward-compatible.** New fields must have defaults. New parameters must be optional.
- **Always add tests.** No pipeline change ships without test coverage for the new path AND regression tests for the existing path.
