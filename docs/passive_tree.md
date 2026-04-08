# Passive Tree System

---

## Overview

The passive tree renders each class's full node graph using real in-game coordinates exported from Last Epoch's character tree layout data. The system supports both passive trees (class-wide) and skill specialization trees (per-skill).

---

## Data Sources

| File | Purpose |
|------|---------|
| `data/classes/passives.json` | Passive node definitions per class (backend, seeded to DB) |
| `frontend/src/data/passiveTrees/index.ts` | Node definitions per class and region (frontend rendering) |
| `data/classes/skill_tree_nodes.json` | Skill specialization tree definitions |
| `char-tree-layout.json` | Original exported layout with real x/y positions |

---

## Node Structure

```ts
interface PassiveNode {
  id: number;
  name: string;
  type: "core" | "notable" | "keystone" | "mastery-gate";
  description?: string;
  connections: number[];   // IDs of directly connected nodes
  x: number;              // real game x coordinate
  y: number;              // real game y coordinate
  maxPoints?: number;
  iconId?: string;        // a-r-* identifier
}
```

---

## Layout System

Nodes use **real game x/y coordinates** -- no radial or procedural layout.

The tree is rendered as an SVG that **auto-fits** to the available panel space:

```
scale = min((width - pad*2) / treeWidth, (height - pad*2) / treeHeight)
offsetX = (width - treeWidth * scale) / 2 - minX * scale
offsetY = (height - treeHeight * scale) / 2 - minY * scale
```

Pan and zoom are intentionally removed. The tree is always static and fully visible.

---

## Connection Rendering

SVG `<line>` elements are drawn for each node pair listed in `node.connections`. Connections are rendered behind nodes on the `<svg>` layer.

---

## Path Validation (BFS)

Only nodes connected (directly or transitively) to the class root node can be allocated. The `isUnlocked(nodeId)` function runs a BFS from root across currently allocated nodes.

```
isUnlocked(id):
  if id === rootId -> true
  BFS from rootId across allocated nodes
  return whether id is a neighbor of any visited node
```

Deallocation also uses BFS to check for orphaned nodes -- a node cannot be deallocated if removing it would disconnect other allocated nodes from the root.

---

## Allocation State

`passiveTree: number[]` -- ordered array of node IDs representing the player's allocation history.

- **Allocate**: append nodeId to array
- **Dealloc**: remove the **last occurrence** of nodeId (preserves history order)
- **Point count per node**: count occurrences in array

This preserves leveling order for the progress bar.

---

## Leveling Path Tracker

`PassiveProgressBar` reads the ordered `passiveTree` array and renders a scrollable timeline of each allocation step:

- Color-coded chips by node type (core / notable / keystone / mastery-gate)
- Hover tooltip with node name, type, estimated level, and description
- Level ruler showing pts/113 with milestone markers at 28 / 56 / 85 pts
- Click to rewind (edit mode only) -- slices array to that step index
- Collapsible via header toggle

---

## Node Types

| Type | Visual | Description |
|------|--------|-------------|
| `core` | Small amber hexagon | Standard stat nodes |
| `notable` | Medium blue hexagon | Named nodes with stronger effects |
| `keystone` | Large green hexagon | Major build-defining passives |
| `mastery-gate` | Orange hexagon | Unlocks specialization branch |

---

## Skill Specialization Trees

Skill trees share the same BFS path validation and node allocation patterns as passive trees. Each skill has a specialization tree with nodes that provide:

- **Build stat bonuses** -- flat additions to BuildStats fields (damage, speed, defense, etc.)
- **Skill modifiers** -- multiplicative effects specific to the skill (more damage, added hits per cast, cast/attack speed, crit)
- **Special effects** -- mechanics that cannot be summed numerically ("Converts to channelled", "Pierces enemies")

The `skill_tree_resolver` service parses node descriptions (format: `Flavor text. | Stat Label +value; Another Stat +value`) and routes them to the appropriate output bucket.

---

## Backend Stat Resolution

When a build is simulated, passive and skill tree stats are resolved through dedicated services:

1. `passive_stat_resolver.resolve_passive_stats()` -- batch-loads PassiveNode rows from DB, maps human-readable stat keys to BuildStats fields via `STAT_KEY_MAP` (150+ mappings), handles composite stats (e.g., "All Attributes" maps to all 5 attribute fields)
2. `skill_tree_resolver.resolve_skill_tree_stats()` -- parses spec tree node descriptions, scales per-point values by allocated points, outputs build stat bonuses and skill modifiers
3. Both outputs feed into `stat_engine.aggregate_stats()` as part of the 8-layer pipeline
