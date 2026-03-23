# The Forge – Development Roadmap

This document outlines the development stages for The Forge.

---

# ✅ Phase 1 – Core Foundation *(Complete)*

- Character data model
- Stat calculation engine (base stats, mastery, passive nodes, gear affixes, attribute scaling)
- Base damage simulation (DPS, crit scaling, attack/cast speed)
- Defensive stat modeling (EHP, resistance capping, survivability score)
- Basic build analysis output (upgrade advisor, weakness detection)

---

# ✅ Phase 2 – Crafting Simulation *(Complete)*

- Affix tier system with full seed data (34 affixes)
- Forging potential tracking and RNG cost model
- Crafting probability modeling and outcome simulation
- Monte Carlo simulation across thousands of craft attempts
- Strategy comparison and optimal path search

> **Note:** Fracture mechanics were removed in alignment with modern Last Epoch (1.0+) game design.

---

# ✅ Phase 3 – Passive Tree *(Complete)*

- Real game node coordinates loaded from exported layout JSON
- SVG connection rendering between nodes
- BFS path validation — only reachable nodes can be allocated
- Hexagonal nodes with stone texture background, color-coded by type
- Static auto-fit layout (pan/zoom removed)
- Leveling path tracker — scrollable timeline recording allocation order per level

---

# 🔧 Phase 4 – Optimization Engine *(In Progress)*

- Stat sensitivity analysis
- Offensive stat ranking
- Defensive improvement analysis
- Upgrade efficiency scoring

Partially implemented in `optimization_engine.py`. Needs expansion and full API exposure.

---

# 🔜 Phase 5 – Skill Tree UI

- Visual skill tree component (data already loaded in `skillTrees/index.ts`)
- Mastery gate behavior — specialization selection unlocking deeper branches
- Skill node tooltips with stat values and scaling

---

# 🔜 Phase 6 – Full Build Import System

- Gear import
- Passive tree import from external format
- Skill modifier import
- Automated character state generation

---

# 🔜 Phase 7 – Advanced Analysis Tools

- Boss encounter simulations
- Corruption scaling analysis
- Gear upgrade ranking against current build
- Build weakness detection UI

---

# 🔜 Phase 8 – Community Tools

- Build comparison tools
- Meta build analytics
- Shared build reports
- Theorycrafting tools

---

# Long-Term Vision

The Forge aims to become the most powerful analytical tool available for Last Epoch players.

Future expansion may include:

* advanced crafting prediction models
* community build databases
* statistical meta analysis
* encounter-specific build optimization
* native desktop packaging (Electron/Tauri)
