# Engine Architecture

The backend is composed of modular, independent engines.

---

## Structure

```
engine/
  core/
  simulation/
  crafting/
  analysis/
```

---

## Core Engines

### Character Engine

Builds the final character state.

### Stat Engine

Handles stat scaling and aggregation.

### Damage Engine

Calculates damage output.

### Defense Engine

Calculates survivability.

---

## Simulation Engines

### Combat Simulator

* simulates attacks
* produces DPS and variance

### Survival Simulator

* simulates incoming damage
* calculates time-to-death

---

## Crafting Engines

### Craft Simulator

Simulates crafting attempts.

### Craft Optimizer

Finds best crafting paths.

---

## Analysis Engines

### Build Analyzer

Identifies strengths and weaknesses.

### Recommendation Engine

Produces actionable insights.

---

## Design Principles

* single responsibility
* deterministic results
* no UI logic
