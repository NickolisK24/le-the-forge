# The Forge --- Core Architecture Implementation Plan

This document defines the foundational architecture to implement next.

Goal:

Create a deterministic, data-driven simulation core capable of powering:

- Build Simulation Engine
- Crafting Outcome Predictor
- Optimization Engine

All other systems depend on these.

---

# Core Philosophy

All systems must be:

- Deterministic first
- Data-driven
- Modular
- Testable
- Expandable

Random simulation comes later.

---

# System Overview

Core Flow:

Game Data → Stat Engine → Combat Engine\
                       → Defense Engine\
                       → Craft Engine\
                       → Optimization Engine

---

# 1. Data Layer (Highest Priority)

Create structured game data files.

Required:

data/ ├ affixes.json\
├ items.json\
├ skills.json\
├ enemies.json\
├ constants.json

---

## Affix Schema (Required)

    {
      "id": "crit_chance",
      "name": "Increased Critical Strike Chance",
      "stat": "crit_chance",
      "type": "increased",
      "tags": ["crit", "offensive"],
      "tiers": [
        { "tier": 1, "value": 10 },
        { "tier": 2, "value": 20 },
        { "tier": 3, "value": 30 }
      ]
    }

---

# 2. Stat Engine

Foundation system.

Everything depends on this.

---

## Required Stat Buckets

    stats = {
        "flat": {},
        "increased": {},
        "more": {},
        "multipliers": {}
    }

---

## Required Functions

create_empty_stat_pool()

apply_affix()

aggregate_stats()

---

Example:

    def apply_affix(stats, affix, tier):
        value = affix["tiers"][tier]["value"]
        stat = affix["stat"]
        type_ = affix["type"]

        if type_ == "flat":
            stats["flat"][stat] += value

        elif type_ == "increased":
            stats["increased"][stat] += value

        elif type_ == "more":
            stats["more"][stat] *= (1 + value / 100)

---

# 3. Combat Engine

Deterministic damage output.

Required function:

calculate_dps(build, stats)

Must calculate:

- Base damage
- Attack speed
- Critical chance
- Critical multiplier
- Increased damage
- More damage

---

# 4. Defense Engine

Survivability math.

Required function:

calculate_ehp(build, stats)

Must calculate:

- Health
- Armor
- Resistances
- Mitigation
- Effective Health Pool

---

# 5. Craft Engine

Probability foundation.

Required:

calculate_success_probability()

calculate_fracture_probability()

simulate_craft_attempt()

---

# 6. Optimization Engine

Upgrade discovery.

Required:

find_best_affix_upgrade(build)

Must:

- Modify stats
- Recalculate DPS/EHP
- Rank improvement value

---

# Required Tests

Each engine must include unit tests.

Required:

tests/ ├ test_stat_engine.py\
├ test_combat_engine.py\
├ test_defense_engine.py\
├ test_craft_engine.py\
├ test_optimization_engine.py

---

# Deterministic Validation Phase

Before randomness:

Every calculation must produce known outputs.

Example:

Input:

100 base damage\
50% increased damage

Expected:

150 damage

---

# File Structure Target

backend/ ├ app/ │ ├ engines/ │ │ ├ stat_engine.py\
│ │ ├ combat_engine.py\
│ │ ├ defense_engine.py\
│ │ ├ craft_engine.py\
│ │ ├ optimization_engine.py\
│ │ ├ data/ │ │ ├ affixes.json\
│ │ ├ items.json\
│ │ ├ skills.json\
│ │ ├ enemies.json\
│ │ ├ tests/

frontend/

docs/ ├ architecture_implementation_plan.md

---

# Implementation Order (Strict)

Follow exactly:

1.  Build Stat Engine\
2.  Validate Stat Output\
3.  Build Combat Engine\
4.  Build Defense Engine\
5.  Build Craft Engine\
6.  Build Optimization Engine\
7.  Add Monte Carlo Simulation\
8.  Expand UI

---

# Final Objective

After completion:

The Forge becomes a:

- Deterministic build analyzer
- Crafting simulator
- Optimization platform

This becomes the permanent foundation for all future features.
