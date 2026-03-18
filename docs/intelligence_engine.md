# The Forge – Intelligence Engine

## Overview

The **Intelligence Engine** is the analytical core of The Forge.

It combines multiple simulation systems to evaluate builds, analyze items, and recommend optimal crafting strategies.

Instead of simply displaying stats, the Intelligence Engine answers high-value questions such as:

* Is this item an upgrade for my build?
* What stat improves my damage the most?
* What is the safest way to craft this item?
* What weakness currently limits my build?

The engine works by simulating character performance and measuring the impact of changes.

---

# Core Philosophy

The Intelligence Engine follows a simple model:

```id="g0c3ji"
Game State → Simulation → Analysis → Recommendation
```

Every recommendation is derived from measurable performance differences.

---

# Engine Components

The Intelligence Engine is composed of several subsystems.

```id="aah6uh"
Character Engine
      ↓
Stat Engine
      ↓
Combat Simulation
      ↓
Analysis Layer
      ↓
Recommendation Engine
```

Each layer contributes to generating build insights.

---

# Character Engine

The Character Engine constructs the full character model from imported data.

Inputs may include:

* base character stats
* equipped gear
* passive tree bonuses
* skill modifiers

Output:

```id="yq94p8"
Character State
{
  damage stats
  defensive stats
  attack speed
  resistances
  gear modifiers
}
```

This unified model becomes the foundation for simulations.

---

# Stat Engine

The Stat Engine handles all stat scaling and interactions.

Responsibilities include:

* additive damage scaling
* multiplicative damage scaling
* crit scaling
* attack speed scaling
* defensive layer interactions

Example stat scaling model:

```id="4zy12q"
Total Damage =
Base Damage
× (1 + Increased Damage)
× More Multipliers
```

---

# Combat Simulation

The Combat Simulation system estimates real combat performance.

Simulations typically run thousands of iterations to account for randomness.

Example simulation process:

```id="14b9aj"
for 10,000 simulated attacks:
    determine crit outcome
    apply damage modifiers
    record final hit damage
```

Outputs include:

* sustained DPS
* burst DPS
* damage variance

---

# Defensive Simulation

The engine also simulates survivability.

Key metrics include:

* Effective Health Pool
* mitigation layers
* estimated time to death

Example model:

```id="j98qea"
Armor Reduction =
Armor / (Armor + 1000)

Total Damage Reduction =
Armor Reduction + Resistance Reduction
```

These values help identify defensive weaknesses.

---

# Stat Optimization System

One of the most important parts of the Intelligence Engine is the **stat optimizer**.

The optimizer tests how small stat increases affect build performance.

Example process:

```id="fntv67"
baseline_dps = simulate(character)

test_stat_changes = [
  +5% crit chance
  +10% attack speed
  +40% increased damage
  +200 health
]

for each stat change:
    simulate new character
    measure performance difference
```

This produces a ranking of the most valuable upgrades.

Example output:

```id="dcmv35"
Best Offensive Upgrades

1. Crit Multiplier (+14% DPS)
2. Attack Speed (+9% DPS)
3. Increased Damage (+4% DPS)
```

---

# Crafting Outcome Integration

The Intelligence Engine also powers the **Crafting Outcome Predictor**.

Instead of evaluating items by raw stats, items are evaluated based on **how much they improve the build**.

Example workflow:

```id="o3kptj"
Item Craft Simulation
       ↓
New Item Stats
       ↓
Build Simulation
       ↓
Measure DPS/EHP difference
```

This allows the engine to calculate:

* expected value of crafting outcomes
* optimal crafting paths
* crafting risk vs reward

---

# Weakness Detection

The engine analyzes build data to detect common inefficiencies.

Examples include:

```id="97k0rg"
overcapped resistances
insufficient armor
low crit scaling
low base damage scaling
```

This allows the system to produce targeted recommendations.

---

# Recommendation Engine

The final layer converts simulation results into player-friendly advice.

Example recommendations:

```id="53wfnv"
Best Offensive Upgrade
+Crit Multiplier (+14% DPS)

Best Defensive Upgrade
+Armor (+9% survivability)

Crafting Recommendation
Upgrade Crit Multiplier before sealing prefixes
```

This makes the system useful even for players unfamiliar with the underlying math.

---

# Design Principles

The Intelligence Engine should follow several key principles.

### Deterministic Results

Simulations must produce consistent results for identical inputs.

### Modular Architecture

Each engine component should operate independently.

### Data-Driven Recommendations

All recommendations must be based on measurable performance differences.

### Extensibility

The system should allow future expansion such as:

* skill-specific scaling
* corruption scaling
* boss encounter simulations

---

# Long-Term Vision

The Intelligence Engine will eventually power all major systems in The Forge.

```id="xv4izq"
Build Analyzer
Crafting Predictor
Loot Filter Generator
Gear Optimization
Meta Build Analytics
```

By combining simulation with analysis, The Forge aims to become a powerful tool for build optimization and theorycrafting in Last Epoch.

---

# Summary

The Intelligence Engine transforms The Forge from a simple toolset into a **decision-support system** for ARPG players.

Instead of guessing, players can use simulation-driven insights to:

* improve builds
* craft smarter
* identify weaknesses
* optimize gear progression
