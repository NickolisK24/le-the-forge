# The Forge -- Improvement & Development Roadmap

This document outlines **specific improvements and architectural
changes** needed to evolve **The Forge** from a strong prototype into a
**serious simulation platform for Last Epoch theorycrafting**.

The goal is to transform the project into:

• a true simulation engine\
• a reliable build analysis tool\
• a standout portfolio project\
• potentially the best build‑analysis tool in the Last Epoch community

This roadmap is organized into **clear implementation phases** so
progress can be tracked step‑by‑step.

------------------------------------------------------------------------

# Phase 1 --- Establish Backend as the Source of Truth

## Current Issue

Some simulation logic exists in both the frontend and backend. Comments
indicate that backend engines mirror logic in frontend files like:

frontend/src/lib/simulation.ts

This introduces **duplicate logic and long‑term maintenance problems**.

If formulas change, both systems must be updated.

------------------------------------------------------------------------

## Correct Architecture

The backend must become the **authoritative simulation engine**.

Frontend (UI)\
↓\
API request\
↓\
Backend Engines\
↓\
Simulation Results\
↓\
Frontend Visualization

The frontend should **never compute gameplay results**.

------------------------------------------------------------------------

## Required Changes

### 1. Remove simulation math from the frontend

Locate logic in:

frontend/src/lib/simulation.ts\
frontend/src/lib/crafting.ts

These should only prepare data for API calls.

------------------------------------------------------------------------

### 2. Create simulation API endpoints

Example endpoints:

POST /simulate/build\
POST /simulate/combat\
POST /simulate/defense\
POST /simulate/craft\
POST /simulate/optimize

Each endpoint should call the appropriate engine.

Example:

``` python
@router.post("/simulate/build")
def simulate_build(build_data):
    stats = stat_engine.calculate_stats(build_data)
    combat = combat_engine.simulate_combat(stats)
    defense = defense_engine.evaluate_survivability(stats)

    return {
        "stats": stats,
        "combat": combat,
        "defense": defense
    }
```
