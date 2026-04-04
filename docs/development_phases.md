# Development Phases & GitHub Workflow

This document defines the **5-phase development system** for The Forge and how each phase integrates with GitHub Projects for structured progress tracking.

---

## 🧠 Philosophy

Each phase represents a **major system milestone**, not just tasks.

* Phases = big picture progress
* Issues = individual tasks
* Projects = workflow management

---

# ✅ Phase 1 — Backend Foundation (Complete)

## Goal

Establish the backend as the **single source of truth**.

## Tasks

* Remove all frontend calculations
* Set up Flask/FastAPI server
* Create base API structure
* Define core data models

## GitHub Setup

### Create Project Column:

* `Phase 1 – Backend Foundation`

### Create Issues:

* "Setup backend server"
* "Create Character model"
* "Create Stats model"
* "Create API base route"

### Label Suggestions:

* `phase:1`
* `backend`
* `core`

---

# ✅ Phase 2 — Stat Engine (Complete)

## Goal

Accurately calculate all character stats.

## Tasks

* Implement stat aggregation
* Handle "increased" vs "more"
* Add crit calculations
* Add attack speed scaling

## GitHub Setup

### Project Column:

* `Phase 2 – Stat Engine`

### Issues:

* "Implement stat aggregation logic"
* "Add crit calculation system"
* "Test stat scaling accuracy"

### Labels:

* `phase:2`
* `engine`
* `stats`

---

# ✅ Phase 3 — Simulation Engine (Complete)

## Goal

Simulate combat and survivability.

## Tasks

* Build combat simulator
* Implement Monte Carlo logic
* Calculate DPS + variance
* Build defense/EHP system

## GitHub Setup

### Project Column:

* `Phase 3 – Simulation`

### Issues:

* "Build combat simulation loop"
* "Implement RNG for crits"
* "Calculate average DPS"
* "Implement EHP formula"

### Labels:

* `phase:3`
* `simulation`

---

# ✅ Phase 4 — Crafting Engine (Complete)

## Goal

Simulate crafting outcomes and probabilities.

## Tasks

* Build crafting simulator
* Implement fracture logic
* Track forging potential
* Run probability simulations

## GitHub Setup

### Project Column:

* `Phase 4 – Crafting`

### Issues:

* "Create crafting state model"
* "Simulate affix upgrades"
* "Implement fracture chance"
* "Run 1000x craft simulations"

### Labels:

* `phase:4`
* `crafting`

---

# 🔧 Phase 5 — Optimization & Analysis (In Progress)

## Goal

Turn raw data into actionable insights.

## Tasks

* Compare stat changes
* Rank upgrades
* Identify weaknesses
* Generate recommendations

## GitHub Setup

### Project Column:

* `Phase 5 – Optimization`

### Issues:

* "Compare stat deltas"
* "Rank DPS improvements"
* "Generate build recommendations"
* "Create analysis output model"

### Labels:

* `phase:5`
* `analysis`
* `optimization`

---

# 📊 Recommended GitHub Project Structure

## Columns

* Backlog
* Phase 1 – Backend Foundation
* Phase 2 – Stat Engine
* Phase 3 – Simulation
* Phase 4 – Crafting
* Phase 5 – Optimization
* In Progress
* Completed

---

# 🔁 Workflow (How You Use This Daily)

1. Pick a phase
2. Move issue → "In Progress"
3. Complete task
4. Commit with reference

Example:

```bash
git commit -m "feat(stat-engine): implement crit calculation (#12)"
```

5. Move issue → Completed

---

# 🏷 Commit Message Standard

Use structured commits:

* feat: new feature
* fix: bug fix
* refactor: code cleanup
* docs: documentation updates

Example:

```bash
feat(simulation): add monte carlo combat loop
```

---

# 🎯 End Result

By following this system, you will have:

* A clearly structured project
* Traceable progress
* Professional GitHub workflow
* Portfolio-level engineering practices

---

# 🔥 Key Rule

Never work outside a phase.

If a task doesn’t belong to a phase →
👉 create a new issue and assign it properly.

---

# ✅ Summary

Phases give you direction.
GitHub Projects give you structure.
Issues give you execution.

Together, they turn this into a **real engineering project**, not just code.
