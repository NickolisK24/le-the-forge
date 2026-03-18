# The Forge – Engine Architecture

## Overview

This document defines the backend architecture for the analytical engines used by **The Forge**.

The system is designed to power:

* Build Simulation Engine
* Crafting Outcome Predictor
* Build Optimization Engine
* Gear Impact Analyzer

The architecture prioritizes:

* modularity
* testability
* scalability
* deterministic simulation

---

# Core Engine Philosophy

All calculations should follow this rule:

> Input game state → run deterministic simulation → return analytical result

No UI logic should exist inside engine modules.

---

# Engine Layer Structure

```
engine/
│
├── core/
│   ├── character_engine.py
│   ├── stat_engine.py
│   ├── damage_engine.py
│   └── defense_engine.py
│
├── simulation/
│   ├── combat_simulator.py
│   ├── survival_simulator.py
│   └── stat_tester.py
│
├── crafting/
│   ├── craft_simulator.py
│   ├── craft_tree_builder.py
│   └── craft_optimizer.py
│
├── analysis/
│   ├── build_analyzer.py
│   ├── weakness_detector.py
│   └── recommendation_engine.py
│
└── utils/
    ├── probability.py
    └── stat_scaling.py
```

---

# Engine Responsibilities

## Character Engine

Responsible for constructing the **final character stat state**.

Inputs:

* base character stats
* gear stats
* skill modifiers
* passive tree modifiers

Outputs:

* unified stat block

Example output:

```
final_stats = {
  "base_damage": 140,
  "crit_chance": 0.42,
  "crit_multiplier": 3.2,
  "attack_speed": 1.8,
  "health": 2400,
  "armor": 1500
}
```

---

# Stat Engine

Handles stat interactions such as:

* additive scaling
* multiplicative scaling
* diminishing returns

Example responsibilities:

```
increase_damage
more_damage
crit_scaling
attack_speed_scaling
```

---

# Damage Engine

Calculates real combat damage.

Metrics produced:

* average hit damage
* crit distribution
* sustained DPS
* burst DPS

Example formula:

```
AverageHit =
(1 - CritChance) * HitDamage
+
CritChance * HitDamage * CritMultiplier
```

---

# Defense Engine

Calculates survivability metrics.

Metrics produced:

* effective health pool
* mitigation layers
* armor scaling
* resist effectiveness

---

# Combat Simulator

Simulates thousands of combat events.

Purpose:

* measure real DPS
* calculate damage variance
* evaluate RNG effects

Example simulation:

```
simulate 10,000 attacks
apply crit RNG
apply damage modifiers
average result
```

---

# Survival Simulator

Simulates incoming damage scenarios.

Used for:

* corruption scaling
* boss damage simulation
* survival time estimates

Outputs:

```
time_to_death
damage_taken_distribution
survivability_score
```

---

# Stat Tester

Tests stat improvements.

Used by the optimizer to determine:

```
which stat improves performance the most
```

Example loop:

```
+5% crit chance
+10% attack speed
+50% increased damage
+200 health
```

Each change triggers a full simulation.

---

# Craft Tree Builder

Creates a tree of possible crafting states.

Example:

```
Initial Item
 ├ Add Affix
 │   ├ Success
 │   └ Fracture
 ├ Upgrade Affix
 │   ├ Success
 │   └ Fracture
 └ Rune of Removal
```

---

# Craft Optimizer

Evaluates crafting paths and returns the highest expected value.

Metrics:

```
success_probability
expected_item_score
brick_probability
```

---

# Build Analyzer

Combines simulation results to produce insights.

Outputs:

```
build strengths
build weaknesses
stat inefficiencies
```

---

# Weakness Detector

Detects problems such as:

```
overcapped resistances
low armor scaling
inefficient crit investment
```

---

# Recommendation Engine

Produces player-facing guidance.

Example output:

```
Best Offensive Upgrade
+Crit Multiplier (+14% DPS)

Best Defensive Upgrade
+Armor (+9% survivability)
```

---

# Design Principles

The engine should follow these rules:

1. Each module performs one responsibility
2. Calculations must be deterministic
3. Simulation results must be reproducible
4. Engines should remain independent of UI

---

# Testing Strategy

Every module must have unit tests.

Example test targets:

```
damage formulas
armor mitigation
crit calculations
crafting probabilities
```

This ensures analytical accuracy.
