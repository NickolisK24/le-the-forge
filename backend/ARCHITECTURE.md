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
└── tests/                  Test suite (800+ tests)
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
| `app/domain/enemy.py` | EnemyStats, EnemyArchetype (TRAINING_DUMMY/NORMAL/ELITE/BOSS), EnemyProfile, EnemyInstance |
| `app/domain/resistance.py` | apply_resistance(), RES_CAP (75%), RES_MIN (-100%) |
| `app/domain/armor.py` | armor_mitigation_pct(), apply_armor(), ARMOR_K=10, ARMOR_MITIGATION_CAP=0.75 |
| `app/domain/dodge.py` | dodge_chance(), DODGE_CAP=0.75 |
| `app/domain/penetration.py` | effective_resistance() with penetration + shred |
| `app/domain/registries/enemy_registry.py` | EnemyRegistry — O(1) enemy profile lookup |

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
| `app/combat/combat_simulator.py` | CombatSimulator.simulate() — tick loop, SimulationResult, TimelineEvent |
| `app/combat/combat_scenario.py` | CombatScenario (duration, enemy, rotation, mana config), SkillRotationEntry |
| `app/domain/mana.py` | ManaPool — can_afford(), spend(), regenerate(), InsufficientManaError |

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

---

## Data Layer

### Game Data Files

| File | Contents |
|------|----------|
| `app/game_data/skills.json` | 80+ skill definitions (damage, speed, scaling, type) |
| `app/game_data/affixes.json` | 34+ affix definitions with tiers and slot applicability |
| `app/game_data/items.json` | Base items per slot with FP ranges |
| `app/game_data/constants.json` | Crafting limits, defense caps, passive limits |
| `app/game_data/enemies.json` | Enemy profile data |
| `app/game_data/classes.json` | Class/mastery definitions |
| `data/entities/enemy_profiles.json` | 8 enemy profiles (training dummy → pinnacle boss) |
| `data/classes/skill_tree_nodes.json` | Skill tree node definitions |
| `data/items/base_items.json` | 100+ base items |
| `data/items/affixes.json` | Full affix dataset |

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
| `app/routes/simulate.py` | POST /api/simulate/stats, /build, /encounter |
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

---

## Test Coverage

800+ tests across all systems. Key test files:

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
