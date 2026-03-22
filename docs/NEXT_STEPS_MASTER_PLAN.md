
# The Forge — Master Development Plan (Current Phase)

This document defines:

1. What is already complete
2. What must be fixed immediately
3. What must be built next
4. What features unlock major value
5. Long-term architectural goals

This is the **single source of truth** for current development priorities.

---

# CURRENT PROJECT STATE

The project is no longer in early development.

Core systems already exist:

✔ Affix database loaded (~1100+ affixes)  
✔ Prefix / suffix slot validation  
✔ Forge Potential (FP) cost engine  
✔ Instability modeling  
✔ Fracture probability math  
✔ Monte Carlo simulation engine  
✔ Strategy comparison system  
✔ Path planning logic  
✔ Rarity-based FP generation  
✔ Craft action functions  
✔ UI build planner + craft simulator  

The project is currently in:

```
PHASE: Simulation Integration
```

Not UI building.  
Not data loading.  

**System integration.**

---

# CRITICAL ARCHITECTURAL FIXES (DO FIRST)

These are required corrections to prevent long-term instability.

---

# 1 — Create Unified Craft Pipeline

Current problem:

Craft actions exist independently:

- add_affix()
- upgrade_affix()
- remove_affix()
- seal_affix()

But they:

- Roll FP separately
- Do not consistently log
- Do not consistently apply fracture
- Do not consistently apply instability

This must be unified.

## Build:

```python
def apply_craft_action(
    item,
    action_type,
    affix_name=None
):
```

## Pipeline Order (MANDATORY)

Every craft must execute:

```
1 Validate action
2 Consume FP
3 Apply craft effect
4 Apply instability gain
5 Roll fracture
6 Log result
7 Return result
```

---

# 2 — Attach Instability To Item State

Instability must exist directly on the item.

Required structure:

```python
item = {

    "forge_potential": 28,
    "instability": 0,
    "is_fractured": False,

    "prefixes": [],
    "suffixes": [],
    "sealed_affix": None

}
```

---

# 3 — Integrate Fracture Into Real Crafting

Simulation includes fractures.

Manual crafting must also include fractures.

After Instability Gain:

```python
risk = fracture_risk(
    item["instability"],
    sealed_count
)

if random.random() < risk:

    fracture_item(item)
```

Must occur:

```
AFTER EVERY CRAFT ACTION
```

---

# 4 — Replace Direct FP Rolls With apply_fp()

All FP consumption must use:

```python
apply_fp(item, action_type)
```

Never call roll_fp_cost directly.

---

# CORE SYSTEMS TO BUILD NEXT

---

# 5 — Craft Session Engine

## Build:

```python
class CraftSession:
```

Responsibilities:

```
Maintain item state
Apply craft actions
Track instability
Track FP
Track fractures
Store history
Allow undo
```

Example:

```python
session.apply("upgrade_affix", "health")

session.undo()

session.get_state()
```

---

# 6 — Undo Last Action System

## Build:

```python
def undo_last_action(item):
```

Required Behavior:

```
Restore previous FP
Restore previous instability
Restore previous affix state
Remove last history entry
```

---

# 7 — Full Craft History Tracking

Every craft must log:

```python
{
    "action": "upgrade_affix",
    "affix": "health",
    "tier_before": 2,
    "tier_after": 3,
    "fp_used": 5,
    "instability_before": 14,
    "instability_after": 20,
    "fractured": False
}
```

---

# 8 — Real-Time Craft Feedback API

Backend endpoint:

```python
POST /craft/action
```

Response:

```json
{
    "success": true,
    "fp_remaining": 18,
    "instability": 27,
    "fractured": false,
    "history": [...]
}
```

---

# SIMULATION EXPANSION

---

# 9 — Live Simulation Preview

Run:

```
10,000 simulations
```

Return:

```
Brick Chance
Perfect Chance
FP Distribution
Instability Distribution
Step Failure Risk
```

---

# 10 — Strategy Comparison UI

Display:

```
Aggressive
Balanced
Conservative
```

With:

```
Expected FP Cost
Brick Chance
Perfect Chance
```

---

# ITEM ENGINE IMPROVEMENTS

---

# 11 — Enforce Slot Limits Everywhere

Always enforce:

```
Max Prefixes = 2
Max Suffixes = 2
Max Sealed = 1
```

---

# 12 — Tier Cap Validation

Ensure:

```python
is_max_tier()
```

Is checked everywhere.

---

# 13 — Add Fracture Severity Effects

Example:

```python
if destructive:

    remove_random_affix()

elif major:

    reduce_tier()

elif minor:

    mark item fractured
```

---

# UI FEATURES TO BUILD NEXT

---

# 14 — Craft Timeline Viewer

Display:

```
Step-by-step crafting history
```

---

# 15 — Risk Indicator Display

Show:

```
Current Fracture Risk: 14%
```

---

# 16 — FP Distribution Graph

Plot:

```
min
max
mean
p50
p75
```

---

# DATA SYSTEM EXPANSION

---

# 17 — Item Base Database

Add:

```
Base Items
Implicit stats
Level requirements
Tags
```

---

# 18 — Affix Weighting

Add:

```json
"weight": 75
```

---

# 19 — Tier Weight Scaling

Higher tiers:

```
Lower success chance
Higher instability
```

---

# TESTING REQUIREMENTS

---

# 20 — Unit Tests

Test:

```
FP consumption
Instability gain
Fracture risk math
Affix limits
Tier limits
```

Use:

```
pytest
```

---

# 21 — Monte Carlo Validation Tests

Verify:

```
Simulated fracture rate matches expected math
```

---

# PERFORMANCE IMPROVEMENTS

---

# 22 — Cache FP Rules

---

# 23 — Vectorize More Systems

---

# LONG-TERM FEATURES

---

# 24 — Craft Optimizer Engine

Goal:

```
Find best crafting path automatically.
```

---

# 25 — Build Export System

Allow:

```
Export crafting session
Import later
Share with others
```

---

# 26 — Community Build Sharing

---

# 27 — Craft Replay System

Replay full crafting session.

---

# DEVELOPMENT PRIORITY ORDER

---

# IMMEDIATE PRIORITY

```
Unified Craft Pipeline
Instability on Item
Fracture Integration
FP Logging Standardization
```

---

# SHORT-TERM PRIORITY

```
Craft Session Engine
Undo System
History Expansion
Live Craft API
```

---

# MID-TERM PRIORITY

```
Simulation UI Integration
Strategy Comparison UI
Timeline Viewer
Risk Indicators
```

---

# LONG-TERM PRIORITY

```
Optimizer Engine
Replay System
Community Sharing
Advanced Analytics
```

---

# FINAL PROJECT DIRECTION

Build:

```
apply_craft_action()
```

Everything depends on it.
