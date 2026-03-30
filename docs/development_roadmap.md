# THE FORGE — MASTER DEVELOPMENT ROADMAP

This is the single source of truth for project progress, current objectives, and planned features.

---

# PROJECT VISION

Create:

```text
A full-featured crafting simulator and optimizer
for Last Epoch that runs as a desktop application
on Windows and MacOS.
```

Final Product Must:

```text
✔ Load full game affix database
✔ Simulate crafting with real FP rules
✔ Optimize crafting outcomes
✔ Calculate full stat output
✔ Evaluate survivability
✔ Run large-scale simulations
✔ Provide smooth UI interaction
✔ Package into a native desktop app
```

This is a **multi-engine architecture project**.

---

# CURRENT PROJECT STATE (REAL STATUS)

Based on your engine tree:

```text
backend/app/engines

affix_engine.py        ✅ EXISTS
base_engine.py         ✅ EXISTS
combat_engine.py       ⚠ PARTIAL
craft_engine.py        ⚠ PARTIAL
defense_engine.py      ⚠ PARTIAL
fp_engine.py           ✅ EXISTS
item_engine.py         ✅ EXISTS
optimization_engine.py ⚠ PARTIAL
stat_engine.py         ⚠ PARTIAL
```

You are **NOT early-stage anymore**.

You are entering:

```text
Core Simulation Implementation Phase
```

This is where projects either:

```text
Become real
OR
Collapse
```

---

# COMPLETED SYSTEMS (LOCKED IN)

These are working foundations.

Do not rewrite unless broken.

---

# ✅ Phase A — Core Engine Architecture

Completed:

```text
✔ Modular engine folder structure
✔ Dedicated engine separation
✔ Engine-level responsibility isolation
✔ Import structure stabilized
```

Result:

```text
Clean architecture foundation established
```

---

# ✅ Phase B — Item Engine

File:

```text
item_engine.py
```

Responsible For:

```text
Item creation
Item structure
Item base properties
Affix storage container
Forge Potential storage
```

Item Format:

```python
item = {

    "item_type": "...",

    "forging_potential": int,

    "prefixes": [],
    "suffixes": [],

    "sealed_affix": None

}
```

Status:

```text
STABLE
```

---

# ✅ Phase C — Forge Potential Engine

File:

```text
fp_engine.py
```

Responsible For:

```text
Rolling FP cost
Handling FP consumption
Validating FP availability
```

Core Reality:

```text
FP must be RNG-based
Never static
Never deterministic
```

Status:

```text
FUNCTIONAL
```

---

# ✅ Phase D — Affix Data Integration

File:

```text
affix_engine.py
```

Responsible For:

```text
Loading affixes.json
Filtering affixes
Validating slot compatibility
Managing affix metadata
```

Data Source:

```text
/data/affixes.json
```

Status:

```text
ACTIVE AND WORKING
```

You confirmed:

```text
Affixes are displaying
```

That is a **major milestone**.

---

# IN-PROGRESS SYSTEMS (CRITICAL ZONE)

These exist but are incomplete.

They define the **success of this project**.

---

# 🔧 Phase E — Craft Engine (PRIMARY FOCUS)

File:

```text
craft_engine.py
```

Current Status:

```text
Partial functionality exists
Needs rule enforcement expansion
```

Must Fully Implement:

```text
Add affix
Upgrade affix
Remove affix
Seal affix
FP consumption
Slot enforcement
Tier validation
Failure handling
```

---

# REQUIRED FEATURES

## Add Affix Logic

Must:

```text
Check prefix/suffix limits
Validate FP
Add affix object
Consume FP
Return success state
```

---

## Upgrade Affix Logic

Must:

```text
Increase tier
Check max tier
Consume FP
Fail safely
```

---

## Remove Affix Logic

Must:

```text
Remove affix
Consume FP
Handle empty cases
```

---

## Seal Affix Logic

Must:

```text
Move affix into sealed slot
Enforce 1 sealed max
Consume FP
```

---

## Failure Handling

Must return:

```python
{
    "success": False,
    "reason": "Not enough FP"
}
```

Not:

```python
False
```

---

# 🔧 Phase F — Stat Engine

File:

```text
stat_engine.py
```

Status:

```text
Needs full implementation
```

Purpose:

```text
Calculate total stats
Aggregate affix values
Apply tier scaling
Return final stat object
```

---

# REQUIRED STAT FEATURES

Must Calculate:

```text
Health
Resistances
Armor
Damage modifiers
Attribute scaling
Conditional stats
```

---

# Expected Output:

```python
{
    "health": 1425,
    "fire_res": 75,
    "armor": 320,
    "damage": 118
}
```

---

# 🔧 Phase G — Defense Engine

File:

```text
defense_engine.py
```

Purpose:

```text
Calculate survivability
Apply damage models
Evaluate effective health
```

Must Include:

```text
Armor mitigation
Resistance caps
Hit damage modeling
DoT modeling
```

---

# 🔧 Phase H — Combat Engine

File:

```text
combat_engine.py
```

Purpose:

```text
Run Monte Carlo simulations
Evaluate combat outcomes
```

Must Simulate:

```text
Hit distribution
Damage outcomes
Enemy patterns
Survival probability
```

---

# 🔧 Phase I — Optimization Engine

File:

```text
optimization_engine.py
```

Purpose:

```text
Find best crafting paths
Evaluate probability trees
Recommend upgrade sequences
```

This becomes:

```text
The core intelligence system
```

---

# 🔜 UPCOMING SYSTEMS (NEXT BUILD ORDER)

Follow this order exactly.

---

# PHASE 1 — Finalize Craft Engine

Priority:

```text
CRITICAL
```

Must Complete:

```text
All craft actions
All FP rules
All slot rules
All tier logic
```

Estimated Difficulty:

```text
HIGH
```

---

# PHASE 2 — Build Stat Aggregation

Priority:

```text
CRITICAL
```

Must:

```text
Sum affix stats
Apply tier scaling
Return full stat object
```

---

# PHASE 3 — Build Defense Modeling

Priority:

```text
HIGH
```

Must:

```text
Simulate survivability
Calculate effective health
```

---

# PHASE 4 — Build Optimization Core

Priority:

```text
VERY HIGH
```

Must:

```text
Simulate crafting trees
Evaluate success probability
Rank outcomes
```

---

# PHASE 5 — Add Complete Game Data

Priority:

```text
CRITICAL
```

Must Include:

```text
All affixes
All item types
All tiers
All stat scaling
All item bases
```

Your affix JSON work directly feeds this.

---

# DATA SYSTEM EXPANSION (MAJOR MILESTONE)

You will eventually maintain:

```text
/data

affixes.json
item_bases.json
rarities.json
implicit_stats.json
damage_types.json
enemy_profiles.json
crafting_costs.json
```

This transforms your system into:

```text
A full Last Epoch data model
```

---

# FRONTEND DEVELOPMENT PHASE

Only after backend stabilizes.

---

# UI GOALS

Must Provide:

```text
Item builder
Affix selection
Craft simulation viewer
Stat results display
Optimization results
```

Technology Path:

```text
React
Tailwind
API backend
```

---

# DESKTOP APPLICATION TARGET

Final product must run as:

```text
Native Desktop Application
```

For:

```text
Windows
MacOS
```

Recommended Tool:

```text
Electron
OR
Tauri
```

Must:

```text
Start backend automatically
Load frontend automatically
Run locally
```

---

# TESTING INFRASTRUCTURE (MANDATORY)

You must maintain:

```text
backend/tests/
```

Test Categories:

```text
Affix tests
Craft tests
FP tests
Stat tests
Simulation tests
```

Goal:

```text
100% logic reliability
```

---

# PERFORMANCE TARGETS

Long-term simulation goals:

```text
10,000+ craft simulations/sec
Large optimization trees
Minimal latency UI
```

Optimization Tools Later:

```text
NumPy
Multiprocessing
Cython (optional)
```

---

# FUTURE ADVANCED FEATURES

These separate this tool from competitors.

---

# FEATURE — Craft Path Prediction

Predict:

```text
Best crafting path
Success probability
Risk level
```

---

# FEATURE — Affix Priority Optimization

Allow:

```text
Weighted stat targeting
Build optimization
```

---

# FEATURE — Multi-Item Build Simulation

Simulate:

```text
Entire character gear set
Not just one item
```

---

# FEATURE — Enemy Simulation Library

Add:

```text
Boss profiles
Damage models
Combat scenarios
```

---

# FEATURE — Build Templates

Allow:

```text
Preset builds
Reusable crafting plans
```

---

# FUTURE DATA SOURCES

You will eventually import from:

```text
Maxroll
In-game data
Manual structured extraction
Community resources
```

Manual input remains required for accuracy.

---

# PACKAGING PHASE (FINAL)

Convert into:

```text
Installable application
```

Must Include:

```text
Bundled Python backend
Frontend UI
Local database
Executable launcher
```

Tools:

```text
PyInstaller
Electron
Tauri
```

---

# MASTER DEVELOPMENT ORDER

Follow this exactly.

```text
1 — Finalize craft_engine.py
2 — Build stat_engine.py
3 — Expand affix datasets
4 — Implement defense_engine.py
5 — Build combat simulation
6 — Implement optimization engine
7 — Expand datasets
8 — Build frontend UI
9 — Package desktop app
10 — Performance optimization
```

This is your:

```text
Execution Backbone
```

---

# CURRENT PRIMARY OBJECTIVE

Right now:

```text
Finish crafting system logic.
```

Not:

```text
UI
Optimization
Packaging
```

Just:

```text
Craft correctness
```

---

# FINAL PROJECT DESTINATION

If completed fully:

You will have:

```text
The most accurate crafting simulator
for Last Epoch available.
```

Not a helper.

Not a calculator.

A **full simulation engine**.
