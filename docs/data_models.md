# The Forge – Data Models

## Overview

This document defines the core data models used throughout The Forge.

These models represent the structure of:

* characters
* gear
* affixes
* items
* crafting states
* simulations

The goal is to create a consistent data structure across the entire system.

---

# Character Model

Represents the player's build.

Example:

```
Character
├ class
├ level
├ stats
├ gear
├ skills
└ defenses
```

Example schema:

```python
class Character:
    class_name: str
    level: int
    stats: Stats
    gear: list[Item]
    skills: list[Skill]
    defenses: Defenses
```

---

# Stats Model

Represents offensive attributes.

Example structure:

```python
class Stats:
    base_damage: float
    increased_damage: float
    more_damage: float
    crit_chance: float
    crit_multiplier: float
    attack_speed: float
```

---

# Defense Model

Represents defensive layers.

Example:

```python
class Defenses:
    health: float
    armor: float
    dodge: float
    endurance: float
    endurance_threshold: float
    ward: float
```

---

# Resistance Model

Represents elemental resistances.

Example:

```python
class Resistances:
    fire: float
    cold: float
    lightning: float
    poison: float
    void: float
    necrotic: float
    physical: float
```

---

# Item Model

Represents a piece of gear.

Example structure:

```
Item
├ item_type
├ rarity
├ prefixes
├ suffixes
└ forging_potential
```

Example schema:

```python
class Item:
    item_type: str
    rarity: str
    prefixes: list[Affix]
    suffixes: list[Affix]
    forging_potential: int
```

---

# Affix Model

Represents an affix on an item.

Example:

```python
class Affix:
    stat: str
    tier: int
    value: float
```

Example affixes:

```
melee_damage
crit_multiplier
attack_speed
health
armor
```

---

# Skill Model

Represents a player skill.

Example:

```python
class Skill:
    name: str
    level: int
    nodes: list[str]
```

---

# Crafting State Model

Represents an item during crafting simulation.

Example:

```python
class CraftState:
    item: Item
    forging_potential: int
    fracture_chance: float
```

---

# Craft Action Model

Represents a crafting action.

Example:

```python
class CraftAction:
    action_type: str
    target_affix: str
    tier_change: int
    fp_cost: int
```

Possible actions:

```
upgrade_affix
add_affix
remove_affix
seal_affix
chaos_reroll
```

---

# Craft Result Model

Represents the result of a crafting step.

Example:

```python
class CraftResult:
    success: bool
    fracture: bool
    new_item: Item
    fp_remaining: int
```

---

# Simulation Result Model

Represents results from combat simulations.

Example:

```python
class SimulationResult:
    average_dps: float
    damage_variance: float
    ehp: float
    time_to_death: float
```

---

# Optimization Result Model

Represents stat optimization results.

Example:

```python
class OptimizationResult:
    stat_name: str
    improvement_percent: float
```

---

# Build Analysis Model

Represents insights returned to the player.

Example:

```python
class BuildAnalysis:
    strengths: list[str]
    weaknesses: list[str]
    recommended_stats: list[str]
```

---

# Data Model Guidelines

The system should follow these principles:

1. All models must be serializable
2. Models should remain immutable during simulation
3. Simulation engines should operate on model copies
4. All model updates should produce new instances

---

# Future Extensions

The data model should be flexible enough to support:

* idols
* legendary items
* skill scaling
* corruption modifiers
* boss mechanics
* multiplayer buffs

This ensures the system can grow with the game.
