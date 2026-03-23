
# Passive Tree System — Missing Components & Next Steps

## Current Working Systems ✅

Your passive tree currently has:

- Node rendering working
- Node types displaying (Core / Notable / Keystone / Gate)
- Class mastery tabs working
- Zoom and pan functionality
- Layout positioning functioning
- Data successfully loaded from exported JSON files

This confirms:

```
Layout pipeline = Working
Rendering engine = Working
Data extraction = Successful
```

---

# Missing Core Systems (Priority Order)

## 1 — Node Connections (Highest Priority)

**Current State:**  
Nodes are floating independently.

**Expected State:**  
Nodes should be connected by visual lines.

Without connections:

- Pathing cannot function
- Progression validation fails
- Tree visuals feel incomplete

**What Must Be Implemented:**

- Render connection lines between linked nodes
- Use node relationship data from metadata
- Draw lines using SVG or Canvas

This is the **most important missing system.**

---

## 2 — Mastery Gate Behavior

**Current State:**  
Mastery gate renders visually only.

**Missing Behavior:**

- Selecting mastery
- Unlocking specialization tree
- Enabling deeper nodes

**Required System:**

```
Reach mastery gate
→ Select specialization
→ Unlock new node branch
```

---

## 3 — Path Unlock Logic

**Current State:**  
Nodes likely clickable without path validation.

**Expected Behavior:**

Nodes should only be selectable if:

```
Connected to unlocked nodes
```

**Required Implementation:**

- Graph traversal logic
- Breadth-first search (BFS)
- Connectivity validation

---

## 4 — Node Tooltips

**Current State:**  
Nodes are visual only.

**Missing UX Elements:**

- Node description
- Stat bonuses
- Scaling values
- Requirements
- Point limits

**Data Source:**

```
char-tree-metadata.json
skill-tree-metadata.json
```

This transforms the tree from visual → functional.

---

## 5 — Background Artwork

**Current State:**

Black background.

**Expected:**

Themed passive tree background image.

Adds:

- Visual clarity
- Professional polish
- UI immersion

---

## 6 — Node Icons

**Current State:**

Generic node visuals.

**Missing:**

- Ability icons
- Stat icons
- Mastery visuals

These improve:

- Readability
- Recognition speed
- Visual depth

---

## 7 — Passive Point Tracking

**Current State:**

Node count displayed.

**Missing:**

- Points spent
- Points remaining
- Refund logic
- Allocation validation

Expected logic:

```
Total Points - Spent Points = Remaining
```

---

## 8 — Tree Centering & Scaling

**Current State:**

Tree visible but not perfectly normalized.

**Needed:**

- Auto-centering logic
- Viewport scaling
- Bounding normalization

Ensures consistent display across screen sizes.

---

# The Single Most Important Next Task

## Implement Connection Rendering

Without connections:

```
Tree = Visual Only
```

With connections:

```
Tree = Functional System
```

This unlocks:

- Valid node progression
- Path checking
- Full gameplay simulation

---

# Recommended Next Build Order

Follow this exact sequence:

1. Render node connections
2. Add path validation logic
3. Implement node tooltips
4. Add mastery unlock behavior
5. Add passive point tracking
6. Add UI polish (icons/background)

---

# Current Project Progress Snapshot

```
Data extraction        ✅ Complete
Layout rendering       ✅ Complete
Node drawing           ✅ Complete
Connection rendering   ⬅️ Next Target
Path validation        Upcoming
Tooltip system         Upcoming
Mastery unlocking      Upcoming
```

---

# Immediate Development Goal

**Next system to build:**

```
Connection Graph Renderer
```

Once this exists:

- Tree becomes logically functional
- Progression rules become enforceable
- Path validation becomes possible
