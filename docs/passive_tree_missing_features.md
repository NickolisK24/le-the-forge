# Passive Tree System — Status & Remaining Work

## Completed Systems ✅

- **Node rendering** — hexagonal SVG nodes, color-coded by type
- **Node types** — Core / Notable / Keystone / Mastery-Gate visually distinct
- **Class mastery tabs** — region selector working
- **Real game coordinates** — x/y positions loaded from exported layout JSON (no procedural layout)
- **Static auto-fit layout** — tree scales to fill panel; pan/zoom removed
- **Connection rendering** — SVG lines drawn between connected node pairs
- **Path validation (BFS)** — only nodes reachable from root can be allocated
- **Passive point tracking** — points spent per node, total displayed
- **Leveling path tracker** — `PassiveProgressBar` records allocation order with timestamps, hover tooltips, rewind support, and level ruler
- **Stone texture background** — themed dark panel background

---

## Remaining Work

### Mastery Gate Behavior

Gate nodes render but clicking one does not trigger specialization selection or unlock the deeper branch. Needs:

- Modal or inline prompt to choose specialization
- State flag that records chosen mastery per character class
- Deeper nodes locked behind gate become unlocked when mastery is chosen

### Node Icons

The `iconId` values (`a-r-*`) are custom IDs from the export script with no mapping to Unity sprite names in the actual game files. Resolution options:

- Use a community-maintained icon pack if one becomes available
- Render node type glyphs as SVG symbols (no external images required)
- Leave as color+shape only (current state — acceptable)

### Skill Tree UI

Data is loaded (`frontend/src/data/skillTrees/index.ts`) but no visual component exists yet. The skill tree is a separate graph per skill with its own node layout.

### Mastery-Specific Sub-Trees

Some classes have mastery-specific passive regions that should only become visible/interactable after the mastery gate is passed.

---

## Progress Snapshot

```
Data extraction              ✅ Complete
Layout rendering             ✅ Complete
Node drawing                 ✅ Complete
Real game positions          ✅ Complete
Connection rendering         ✅ Complete
Path validation              ✅ Complete
Passive point tracking       ✅ Complete
Leveling path tracker        ✅ Complete
Static auto-fit layout       ✅ Complete
Mastery gate behavior        ⬅️ Next Target
Node icons                   Deferred (blocked by data)
Skill tree UI                Upcoming
```
