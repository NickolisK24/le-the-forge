# Architecture

The Forge is a backend-driven simulation platform that evaluates character builds and provides actionable insights.

---

## Core Pipeline

```
Player Input
↓
Stat Engine
↓
Combat Simulation
↓
Defense Simulation
↓
Analysis Layer
↓
Optimization Engine
↓
Recommendations
↓
Frontend Visualization
```

---

## Core Systems

### Build Simulation
Calculates DPS, damage variance, survivability, and effective health pool.

### Crafting Predictor
Simulates crafting success rates, fracture probabilities, and expected outcomes.

### Optimization Engine
Determines best stat upgrades, most impactful changes, and defensive improvements.

---

## Engine Structure

```
backend/app/engines/
  core/         — character state, stat aggregation
  simulation/   — combat and survival simulators
  crafting/     — craft simulator and optimizer
  analysis/     — build analyzer and recommendation engine
```

### Core Engines
- **Stat Engine** — handles stat scaling and aggregation
- **Character Engine** — builds final character state
- **Damage Engine** — calculates damage output
- **Defense Engine** — calculates survivability

### Simulation Engines
- **Combat Simulator** — simulates attacks, produces DPS and variance
- **Survival Simulator** — simulates incoming damage, calculates time-to-death

### Crafting Engines
- **Craft Simulator** — simulates crafting attempts and tracks outcomes
- **Craft Optimizer** — finds best crafting paths

### Analysis Engines
- **Build Analyzer** — identifies strengths and weaknesses
- **Recommendation Engine** — produces actionable insights

---

## Simulation Math

**Damage formula:**
```
damage = base_damage × (1 + increased_damage) × more_damage
```

**Defense (EHP):**
```
EHP = health / (1 - damage_reduction)
```

**Combat simulation:** Monte Carlo — simulate thousands of attacks, apply crit chance and modifiers, record average DPS and variance.

**Crafting simulation:** Monte Carlo — simulate crafting attempts, track outcomes, compute probabilities.

**Optimization:** Simulate baseline → apply stat changes → compare → rank improvements.

---

## Design Principles

- All calculations occur in the backend — frontend is input + visualization only
- Single responsibility per engine
- Deterministic, reproducible results
- No UI logic in engine layer
