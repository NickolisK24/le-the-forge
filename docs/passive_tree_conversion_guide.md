
# Converting Your Passive Tree System to a Real Last Epoch Layout

## Problem Summary

Your current passive tree is generated procedurally. That means nodes are created dynamically with random offsets and layer counts. This results in a generic-looking skill tree rather than matching the real layout used in **Last Epoch** or on **Maxroll**.

Procedural generation approach:

- Nodes are created with `genNodes()`
- X positions are randomized with an RNG
- Layers determine how many nodes appear

Because of this, the structure will **never match the actual passive tree**.

---

# Correct Approach

Instead of generating nodes dynamically, you need to load **predefined node data** with fixed coordinates and explicit connections.

Real build planners use a **graph system**:

```
nodes = [
  { id: 1, x: 340, y: 820, parentId: null },
  { id: 2, x: 290, y: 760, parentId: 1 },
  { id: 3, x: 390, y: 760, parentId: 1 }
]
```

```
edges = [
  [1,2],
  [1,3]
]
```

Rendering then becomes:

```
SVG lines → connections
SVG circles → nodes
```

---

# Step 1 — Remove Procedural Generation

Delete the following components:

- `genNodes()`
- `CHOSEN_LAYERS`
- `UNCHOSEN_LAYERS`
- `lcg()`

These functions generate fake layouts and prevent the tree from matching the real game structure.

---

# Step 2 — Create Passive Tree Data Files

Create a directory for your passive tree datasets.

```
/data/passiveTrees/

acolyteTree.ts
mageTree.ts
rogueTree.ts
sentinelTree.ts
primalistTree.ts
```

Example dataset:

```ts
export const ACOLYTE_TREE = [
  {
    id: 1,
    x: 400,
    y: 900,
    type: "core",
    name: "Vitality",
    regionId: "base"
  },
  {
    id: 2,
    x: 350,
    y: 820,
    type: "core",
    name: "Intelligence",
    parentId: 1,
    regionId: "base"
  },
  {
    id: 3,
    x: 450,
    y: 820,
    type: "core",
    name: "Health",
    parentId: 1,
    regionId: "base"
  }
]
```

Each node has:

- `id`
- `x`
- `y`
- `type`
- `name`
- `regionId`
- optional `parentId`

---

# Step 3 — Load Tree Data Instead of Generating

Replace this:

```ts
const [nodes, setNodes] = useState(() =>
  genNodes("Acolyte", "Necromancer")
);
```

With:

```ts
import { ACOLYTE_TREE } from "@/data/passiveTrees/acolyteTree"

const [nodes, setNodes] = useState(ACOLYTE_TREE);
```

Now your tree loads fixed positions.

---

# Step 4 — Draw Connections Using Parent Relationships

Instead of detecting connections using distance math like:

```
Math.hypot(nodeA.x - nodeB.x)
```

Use explicit parent relationships:

```ts
nodes.forEach(node => {
  if (node.parentId) {
    const parent = nodeMap[node.parentId]

    drawLine(parent.x, parent.y, node.x, node.y)
  }
})
```

This ensures the correct nodes are always connected.

---

# How Maxroll Gets Their Layout

Maxroll does **not manually place nodes**.

They extract node coordinates directly from **game asset data**.

However, a simple approach for your project is:

### Screenshot Method

1. Screenshot the passive tree in-game
2. Import the screenshot into Figma
3. Place markers on each node
4. Read the X/Y coordinates
5. Export those into your dataset

This usually takes about **10 minutes per class tree**.

---

# Recommended Project Structure

```
/src
  /data
    /passiveTrees
      acolyte.ts
      mage.ts
      rogue.ts
      sentinel.ts
      primalist.ts

  /components
    PassiveTreeCanvas.tsx
    PassiveNode.tsx
    PassiveEdge.tsx
```

Each tree exports:

```
nodes
edges
```

Your UI simply renders that graph.

---

# Important Improvement

Your current prerequisite logic checks node proximity.

Example:

```
Math.hypot(...)
```

This is unreliable.

Instead rely on **explicit graph edges** defined in your dataset.

---

# Final Architecture

```
PassiveTree Data
      ↓
Nodes + Edges
      ↓
Canvas / SVG Renderer
      ↓
Node Interaction
      ↓
Stat Simulation
```

This architecture matches how real build planners work.

---

# Good News

Your existing system already supports:

- Node IDs
- Parent relationships
- Region grouping
- Point allocation

That means converting your system to this model should only take **1–2 hours**.

Once complete, your planner will be able to visually match the **real Last Epoch passive tree layout**.
