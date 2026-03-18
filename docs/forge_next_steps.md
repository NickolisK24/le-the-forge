# The Forge -- Next Development Phase Guide

This document outlines the **next major development steps** for The
Forge. The goal is to transition the project from a **well-structured
platform with engines** into a **fully functional analytical tool for
Last Epoch builds**.

The steps are ordered intentionally. Following this order will prevent
major rewrites later.

------------------------------------------------------------------------

# Development Phase 1: Stabilize the Stat Engine

Your **stat engine** is the most important system in the entire project.
Every other engine relies on the values produced here.

backend/app/engines/stat_engine.py

## Goal

Create a **single source of truth for all stat aggregation**.

The stat engine should take inputs like:

-   character base stats
-   item affixes
-   passive tree bonuses
-   skill modifiers
-   temporary buffs

and convert them into **final usable stats**.

## Required Functions

Add or expand functions like:

calculate_total_stats() calculate_damage_multiplier()
calculate_crit_chance() calculate_crit_multiplier()
calculate_attack_speed() calculate_resistances()
calculate_armor_mitigation() calculate_ward()

## Key Concepts to Implement

### Increased vs More Modifiers

Example:

100 base damage +100% increased damage +50% more damage

Calculation:

100 \* (1 + 1.00) \* 1.50 = 300

Handling this correctly is critical.

------------------------------------------------------------------------

# Development Phase 2: Expand the Combat Engine

Location:

backend/app/engines/combat_engine.py

## Goal

Simulate **real combat damage output**.

Right now the engine likely performs direct calculations. The next step
is implementing **probabilistic simulations**.

### Recommended Approach

Use **Monte Carlo simulations**.

Example:

simulate 10,000 attacks roll crit chance roll damage ranges record
results

## Metrics to Calculate

average_hit_damage critical_hit_damage burst_dps sustained_dps
damage_variance

This allows the tool to show players **realistic performance metrics**.

------------------------------------------------------------------------

# Development Phase 3: Expand the Defense Engine

Location:

backend/app/engines/defense_engine.py

## Goal

Evaluate **build survivability**.

Players need to understand:

-   how tanky their build is
-   what defensive weaknesses exist

## Metrics to Implement

effective_health_pool armor_damage_reduction dodge_effectiveness
block_effectiveness ward_sustainability resistance_mitigation

Example EHP formula:

effective_health = health / (1 - damage_reduction)

Eventually this engine should detect:

low armor overcapped resistances low ward sustain

------------------------------------------------------------------------

# Development Phase 4: Improve the Crafting Engine

Location:

backend/app/engines/craft_engine.py

## Goal

Predict crafting outcomes and probabilities.

Currently this engine likely calculates **single-step outcomes**.

Next step: simulate **entire crafting paths**.

## Example Craft Path

1.  Seal suffix
2.  Upgrade crit chance
3.  Add crit multiplier

## Simulation Method

simulate 5000 crafting attempts apply instability growth roll fracture
results record final item

## Output Example

Craft Success Chance: 58% Minor Fracture Chance: 19% Major Fracture
Chance: 13% Destructive Fracture Chance: 10%

Later this can evolve into:

best crafting path detection

------------------------------------------------------------------------

# Development Phase 5: Upgrade the Optimization Engine

Location:

backend/app/engines/optimization_engine.py

## Goal

Identify the **most impactful upgrades** for a build.

The engine should:

run baseline simulation apply stat mutations simulate results rank
improvements

## Example Upgrade Simulation

Test stat changes like:

+20% crit multiplier +10% attack speed +40% increased damage

Then compare results.

Example output:

Top DPS Upgrades

1.  Crit Multiplier +20% → +14% DPS
2.  Attack Speed +10% → +9% DPS
3.  Increased Damage +40% → +4% DPS

This feature alone can make The Forge extremely valuable.

------------------------------------------------------------------------

# Development Phase 6: Introduce Game Data

Simulation engines require **accurate game data**.

Create a new directory:

backend/app/game_data/

Add structured files such as:

affixes.json item_bases.json skills.json passives.json damage_types.json

These files will serve as the **source of truth** for the engines.

Example affix entry:

{ "name": "Critical Strike Chance", "tiers": \[ {"tier": 1, "value": 5},
{"tier": 2, "value": 10}, {"tier": 3, "value": 15} \] }

Engines should load this data during simulation.

------------------------------------------------------------------------

# Development Phase 7: Build Analysis Layer

Create a new service:

build_analysis_service.py

This service will orchestrate all engines.

Pipeline:

build input → stat engine → combat engine → defense engine →
optimization engine → output analysis

Example response:

Build Performance

DPS: 1.2M Effective Health: 4800 Damage Variance: 16%

Detected Weaknesses: Low armor Overcapped lightning resist Low crit
scaling

------------------------------------------------------------------------

# Development Phase 8: Frontend Visualization

Your frontend already has a solid structure.

Next step is visualizing engine outputs.

## Build Dashboard

Display:

DPS graphs damage breakdown defense layers stat scaling

## Crafting Simulator UI

Show:

success chance fracture risk expected stat outcome

------------------------------------------------------------------------

# Long-Term Vision

Once these systems mature, The Forge could support:

build optimization crafting strategy analysis meta build analysis
upgrade recommendations stat scaling graphs

At that stage the project becomes a **true theorycrafting platform**.

------------------------------------------------------------------------

# Final Advice

Do not try to build everything at once.

Follow this order:

1.  Strengthen the stat engine
2.  Expand combat simulations
3.  Improve defensive modeling
4.  Upgrade crafting simulations
5.  Build optimization analysis
6.  Add structured game data
7.  Connect engines into build analysis
8.  Visualize results in the frontend

Following this roadmap will allow The Forge to grow into a **powerful
analytical tool for the Last Epoch community**.
