# Data Models

Defines the core data structures used across The Forge.

---

## Design Rules

* Models must be serializable
* Models are immutable during simulation
* Engines operate on copies
* Updates create new instances

---

## Character

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

## Stats

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

## Defenses

```python
class Defenses:
    health: float
    armor: float
    dodge: float
    endurance: float
    ward: float
```

---

## Item

```python
class Item:
    item_type: str
    rarity: str
    prefixes: list[Affix]
    suffixes: list[Affix]
    forging_potential: int
```

---

## Affix

```python
class Affix:
    stat: str
    tier: int
    value: float
```

---

## Skill

```python
class Skill:
    name: str
    level: int
    nodes: list[str]
```

---

## Crafting

```python
class CraftState:
    item: Item
    forging_potential: int
```

```python
class CraftResult:
    success: bool
    fracture: bool
    new_item: Item
```

---

## Simulation Output

```python
class SimulationResult:
    average_dps: float
    damage_variance: float
    ehp: float
```

---

## Analysis Output

```python
class BuildAnalysis:
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
```
