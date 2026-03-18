# The Forge -- Simulation Design Document

This document defines the **core mathematical and simulation
architecture** behind The Forge's analytical engines.

The goal is to create a **reliable theorycrafting engine** capable of
evaluating Last Epoch builds using realistic combat modeling and
probabilistic crafting simulations.

------------------------------------------------------------------------

# Core Philosophy

The Forge should not be a simple calculator.

Instead it should function as a **simulation engine** that can:

• Evaluate build damage output\
• Measure survivability under different conditions\
• Predict crafting outcomes\
• Recommend optimal stat upgrades

To achieve this, the system should rely on **deterministic calculations
combined with Monte Carlo simulations**.

------------------------------------------------------------------------

# Engine Architecture Overview

The system is composed of five major engines.

    Stat Engine
    Combat Engine
    Defense Engine
    Craft Engine
    Optimization Engine

Each engine has a specific responsibility.

    Stat Engine → aggregates character stats
    Combat Engine → simulates offensive performance
    Defense Engine → evaluates survivability
    Craft Engine → predicts crafting outcomes
    Optimization Engine → recommends upgrades

------------------------------------------------------------------------

# 1. Stat Engine Design

Location:

    backend/app/engines/stat_engine.py

The stat engine aggregates all stat modifiers into final usable values.

### Inputs

    character base stats
    gear affixes
    passive tree bonuses
    skill modifiers
    temporary buffs

### Outputs

    total_damage_multiplier
    crit_chance
    crit_multiplier
    attack_speed
    armor
    resistances
    ward
    health

### Modifier Stacking

Last Epoch uses two major modifier types:

    increased
    more

Example:

    100 base damage
    +100% increased damage
    +50% more damage

Calculation:

    100 * (1 + 1.00) * 1.50 = 300

The stat engine should maintain separate buckets for these values.

Example structure:

    damage = base_damage * (1 + total_increased) * total_more

------------------------------------------------------------------------

# 2. Combat Simulation Engine

Location:

    backend/app/engines/combat_engine.py

The combat engine estimates real damage output.

Instead of a single formula, it should use **Monte Carlo simulation**.

### Simulation Process

    repeat N times (e.g. 10,000)

    roll base damage
    roll crit chance
    apply crit multiplier
    apply damage multipliers
    record result

### Output Metrics

    average_hit_damage
    crit_hit_damage
    burst_dps
    sustained_dps
    damage_variance

Example pseudocode:

    for attack in range(10000):
        damage = random_between(min_damage, max_damage)

        if random() < crit_chance:
            damage *= crit_multiplier

        damage *= total_damage_multiplier

        record(damage)

Then compute:

    average(damage)
    standard_deviation(damage)

This provides **realistic DPS modeling**.

------------------------------------------------------------------------

# 3. Defense Engine

Location:

    backend/app/engines/defense_engine.py

This engine evaluates **how survivable a build is**.

### Defensive Layers

    health
    armor
    resistances
    block
    dodge
    ward
    endurance

### Effective Health Pool

One of the key outputs should be **Effective Health Pool (EHP)**.

Example simplified formula:

    EHP = health / (1 - damage_reduction)

Damage reduction may come from:

    armor mitigation
    resistances
    damage reduction modifiers

### Survivability Simulation

Later versions could simulate incoming damage events.

Example:

    simulate enemy attacks
    apply dodge
    apply block
    apply mitigation
    track time to death

This allows measuring **real survivability instead of static EHP**.

------------------------------------------------------------------------

# 4. Crafting Simulation Engine

Location:

    backend/app/engines/craft_engine.py

Crafting outcomes involve randomness and instability.

The best way to model this is **Monte Carlo crafting simulations**.

### Crafting Simulation Process

    repeat N times (e.g. 5000)

    apply crafting action
    increase instability
    roll fracture result
    record outcome

Possible outcomes:

    success
    minor fracture
    major fracture
    destructive fracture

### Metrics to Compute

    success_probability
    minor_fracture_probability
    major_fracture_probability
    destructive_fracture_probability
    expected_final_stats

Example output:

    Success Chance: 61%
    Minor Fracture: 18%
    Major Fracture: 11%
    Destructive Fracture: 10%

------------------------------------------------------------------------

# 5. Optimization Engine

Location:

    backend/app/engines/optimization_engine.py

This engine determines **which upgrades produce the largest
improvements**.

### Algorithm

1.  Run baseline simulation
2.  Generate stat mutations
3.  Re-run simulations
4.  Compare results
5.  Rank improvements

### Example Stat Mutations

    +20% crit multiplier
    +10% attack speed
    +40% increased damage
    +150 armor
    +200 health

### Example Output

    Top DPS Improvements

    +20% Crit Multiplier → +14% DPS
    +10% Attack Speed → +9% DPS
    +40% Increased Damage → +4% DPS

For defense:

    Top Survivability Improvements

    +150 Armor → +11% EHP
    +200 Health → +9% EHP
    +20% Dodge → +6% survivability

This feature will be one of the **most valuable parts of the platform**.

------------------------------------------------------------------------

# Engine Integration Pipeline

Once all engines are stable, they should operate in sequence.

    Build Input
        ↓
    Stat Engine
        ↓
    Combat Engine
        ↓
    Defense Engine
        ↓
    Optimization Engine
        ↓
    Final Build Analysis

Example final output:

    Build Performance

    DPS: 1.25M
    Effective Health: 5200
    Damage Variance: 17%

    Detected Weaknesses:
    Low armor
    Overcapped lightning resist
    Inefficient crit scaling

------------------------------------------------------------------------

# Future Simulation Features

Later improvements could include:

    enemy simulation
    boss encounter modeling
    damage uptime modeling
    cooldown rotations
    skill interaction modeling

This would elevate The Forge into a **full theorycrafting simulation
platform**.

------------------------------------------------------------------------

# Long-Term Vision

If fully implemented, The Forge could become the **primary analytical
tool for the Last Epoch community**, offering:

    build performance simulation
    crafting outcome prediction
    upgrade recommendations
    defensive weakness detection
    meta build analysis

This document serves as the **blueprint for the intelligence layer of
the platform**.
