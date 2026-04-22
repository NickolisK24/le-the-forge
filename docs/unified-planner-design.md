# Unified Build Workspace — Phase 1 Design Note

Phase 1 of 5: shell + state architecture. No user-visible behavior change.

## 1. Current Architecture (as found)

### 1.1 Pages

Two pages exist today whose names suggest overlap but whose responsibilities do not:

- **`BuildPlannerPage`** — `frontend/src/components/features/build/BuildPlannerPage.tsx` (≈1,452 lines).
  Mounted at `/build` (create mode), `/build/:slug` (view/edit mode), and `/planner` (alias redirect to `/build`,
  declared in `frontend/src/App.tsx` lines 210–211 and 240). This is the canonical build editor: it handles
  create, view, and edit flows, persists to the `Build` model via `/api/builds`, and triggers full-build
  analysis via `/api/builds/<slug>/simulate`.

- **`BuildEditorPage`** — `frontend/src/components/features/encounter/BuildEditorPage.tsx` (≈233 lines).
  Mounted at `/build-editor` (`App.tsx` line 220). Despite the name, this is **not** an editor for
  persisted builds. It is a stateless **encounter simulator** that drives `/api/simulate/encounter-build`
  with an in-memory `BuildDefinition` (single skill, not 5-slot; no blessings; encounter knobs). It does
  not load, save, or mutate any `Build` row.

The task description refers to a `/edit/:buildId` route. **No such route exists** in `App.tsx` and no
component renders at that path. The "edit page" in the user's mental model is `BuildPlannerPage` in
edit mode at `/build/:slug`. This discovery is material to the route plan in §3.

### 1.2 State flow in `BuildPlannerPage`

Build state is held in ~13 `useState` hooks at the top of the component (lines 874–886):
`name`, `description`, `level`, `characterClass`, `mastery`, `isSsf`, `isHc`, `isLadder`,
`isBudget`, `draftSkills`, `passiveTree`, `draftGear`, `draftBlessings`. There is no unifying
object — each surface owns one or more slices of local state and mutates via its own setter.

- Load: `useBuild(slug)` (`frontend/src/hooks/index.ts` lines 78–84) issues `GET /api/builds/<slug>`
  via React Query and seeds the local state via effects when `data` resolves.
- Draft persistence: without a slug, the page auto-saves the form under the `forge_draft_build`
  localStorage key on a 1.5s debounce (lines 946–1005) and restores on mount.
- Save: `useCreateBuild` / `useUpdateBuild` (`hooks/index.ts` lines 86–110) map to
  `POST /api/builds` and `PATCH /api/builds/<slug>`.
- Analyze: `simulateApi.build(slug)` (`lib/api.ts` lines 425–427) → `POST /api/builds/<slug>/simulate`
  (backend route `backend/app/routes/builds.py` lines 252–264). Returns `BuildSimulationResult`
  (`lib/api.ts` lines 412–423). Triggered only by an explicit "Analyze Build" button.

### 1.3 Editor surfaces currently rendered on `BuildPlannerPage`

All live under `frontend/src/components/features/build/` except blessings:

| Surface       | Component             | How it reads state | How it writes state |
|---------------|-----------------------|---------------------|---------------------|
| Gear (view/edit) | `GearEditor`           | `gear` prop        | `onChange(gear[])` callback |
| Gear (quick-create) | `QuickGearGrid` (inline, lines 171–236) | `gear` prop | `onChange(gear[])` callback |
| Idols         | `GearEditor` "idols" tab | same as gear      | same as gear |
| Skills        | `SkillSelector`       | `skills` prop       | `onAddSkill` / `onRemoveSkill` / `onPointsChange` / `onTreeAlloc` callbacks |
| Passive tree  | `BuildPassiveTree`    | `allocated` map prop | `onAllocate(nodeId, points)` callback |
| Passive history | `PassiveProgressBar` | `history` array prop | `onRewindTo(step)` callback |
| Blessings     | `BlessingsPanel` (`frontend/src/components/blessings/BlessingsPanel.tsx`) | `selectedBlessings` prop | `onChange(blessings[])` callback |

There is **no Weaver Tree surface in the frontend** today. Weaver tree data is loaded by the
backend (`backend/app/game_data/pipeline.py` lines 57, 321–360) but no editor component exists.

### 1.4 Data model

`Build` (`frontend/src/types/index.ts` lines 61–87) is the canonical persisted shape:
`{ id, slug, name, description?, character_class, mastery, level, passive_tree[], gear[], skills[],
blessings[], is_ssf, is_hc, is_ladder_viable, is_budget, patch_version, cycle, tier?, ... }`.
The backend `Build` model (`backend/app/models/__init__.py` lines 75–141) mirrors this with
`passive_tree`, `gear`, `blessings` as JSON columns and `skills` as a related `BuildSkill` table.

`BuildDefinition` (`frontend/src/services/buildApi.ts` lines 40–48) is the encounter-simulator's
incompatible sibling and is **out of scope** for this consolidation.

### 1.5 State management layer

The project uses **Zustand** (`frontend/src/store/index.ts`) for two scoped stores: `useAuthStore`
and `useCraftStore`. Neither is a build store. React Query (`@tanstack/react-query`) handles server
data (`useBuild`, `useCreateBuild`, `useUpdateBuild`). There is **no shared, immutable build state
object** — every editor surface reads and writes through ad-hoc callbacks on `BuildPlannerPage`.

### 1.6 Divergence / duplication observed

- `BuildPlannerPage` contains inline gear helpers (`QuickGearGrid`, lines 93–236) that duplicate logic
  already in `GearEditor`. These will stay untouched this phase — noted for future consolidation.
- `BuildEditorPage` ships its own `SkillSelector`, `GearPanel`, `PassivePanel` under
  `frontend/src/components/features/encounter/`. These are an entirely different component family
  from the planner's editors. **Out of scope** for this phase.
- The orphan stub `frontend/src/pages/build/BuildWorkspace.tsx` was removed from the router
  (`App.tsx` line 36 notes "Removed: BuildWorkspace (stub)") but the file and its test
  (`frontend/src/__tests__/pages/workspaces.test.tsx`) still exist. We leave both in place —
  touching them is out of scope for phase 1.

## 2. Target Architecture

A single page component — `UnifiedBuildPage` — renders all editor surfaces against a single
Zustand store, `useBuildWorkspaceStore`. The store owns the working copy of a `Build` object.
Every editor surface reads from the store (via selector hooks) and writes through a small,
documented action API. Analysis is a separate concern, triggered by a side-panel that reads
the same store but lives in its own component — in this phase that side-panel is a placeholder.

**Three rules that govern the target architecture**:

1. **One source of truth.** The store holds a `BuildWorkspaceState` object whose `build` field is
   the full working-copy `Build`. Editor components never maintain their own copy of any field
   that also lives on `build`. They may hold local UI state (which slot modal is open, which tab
   is active), but they do not hold build data.

2. **All updates go through the action API.** The store exposes intent-named actions
   (`setSkills`, `setGear`, `setPassiveTree`, `setBlessings`, `setMeta`, `initialize`, `reset`).
   Every action returns a new `build` object — never an in-place mutation. Zustand's default
   `set()` already produces a new state object at the top level; the store's reducers ensure
   nested fields (`gear`, `skills`, etc.) are replaced rather than mutated. This invariant is
   required for the reveal-animation diffing in phase 2 and the undo/redo stack in a later
   phase.

3. **Analysis is decoupled from editing.** The shell does not trigger analysis as a side effect
   of edits in phase 1. A placeholder `AnalysisPanel` reads from the store but renders a
   "wired up in next phase" message. In phase 2 the real-time analysis hook will replace this
   placeholder; no shell code should need to change.

### 2.1 Coexistence with the old pages

Phase 1 is **additive**. `BuildPlannerPage` at `/build` and `/build/:slug` is unchanged. Nothing
imports the old planner into the new shell and the new shell does not import anything from the
old planner beyond the leaf editor components (`GearEditor`, `SkillSelector`, `BuildPassiveTree`,
`PassiveProgressBar`, `BlessingsPanel`). Those leaf components take `value` + `onChange` style
callbacks today and therefore bind to the store trivially via thin section wrappers.

The encounter simulator at `/build-editor` is untouched and remains out of scope.

### 2.2 Separation between the store and the server

The store is a pure client-side working copy. Loading (`useBuild`) and saving
(`useCreateBuild` / `useUpdateBuild`) remain the responsibility of React Query. The shell calls
`useBuild(slug)` on mount, waits for the server object, and hands it to `store.initialize(build)`.
The store never fetches, and React Query never owns editable state.

## 3. Route Structure

### 3.1 Requested vs. available URL space

The phase brief specifies the new unified page should live at `/build/:buildId` and `/build/new`.
The existing `BuildPlannerPage` already owns `/build` and `/build/:slug`. Any plan that puts the
new shell at `/build/:buildId` for existing builds would either (a) shadow the existing planner at
its canonical URL, breaking the "old routes must remain functional" constraint, or (b) require
retargeting `/build/:slug` to the new shell, which is a cutover — explicitly reserved for phase 5.

The brief also refers to `/edit/:buildId` as an "old route that must continue to work." As noted
in §1.1, no such route exists. Nothing needs to be preserved for it.

### 3.2 Routes registered in phase 1

To satisfy both constraints (new shell is reachable and independently testable; old planner keeps
working at its canonical URL), the new shell is registered under a distinct namespace:

| Route                | Component           | Behavior                                                    |
|----------------------|---------------------|-------------------------------------------------------------|
| `/workspace/new`     | `UnifiedBuildPage`  | Initializes the store with a default empty build.           |
| `/workspace/:slug`   | `UnifiedBuildPage`  | Fetches `Build` by slug, initializes the store with result. |

These routes are declared in `App.tsx` alongside the existing planner routes. Static segments
(e.g. `new`) take precedence over dynamic segments in React Router v6, so ordering is not a
concern, but the `new` route is declared first by convention for readability.

### 3.3 Routes left untouched

| Route                | Component           | Status                                                      |
|----------------------|---------------------|-------------------------------------------------------------|
| `/build`             | `BuildPlannerPage`  | Unchanged.                                                  |
| `/build/:slug`       | `BuildPlannerPage`  | Unchanged.                                                  |
| `/planner`           | `AliasRedirect→/build` | Unchanged.                                               |
| `/build-editor`      | `BuildEditorPage`   | Unchanged (encounter simulator; not part of this consolidation). |

### 3.4 Cutover plan (phase 5, not this phase)

In the migration cutover phase, `/build` and `/build/:slug` will be retargeted to
`UnifiedBuildPage`, and `/workspace/*` will be kept as a stable internal alias or retired entirely.
`BuildPlannerPage` will then be deleted. None of that happens in phase 1. The `/workspace/*`
namespace is a phase-1 staging area, explicitly called out as a temporary deviation from the brief's
requested URL shape, chosen to preserve the "old routes must remain functional" constraint.

## 4. Component Tree

All new files live under `frontend/src/components/features/build-workspace/`, matching the
existing feature-folder convention (`features/build/`, `features/encounter/`, `features/craft/`,
`features/builds/`, etc.). No files are moved, renamed, or modified outside this folder and a
single-line addition to the router in `App.tsx` plus a single-line re-export in `store/index.ts`.

```
<UnifiedBuildPage>                     // frontend/src/components/features/build-workspace/UnifiedBuildPage.tsx
├── <BuildWorkspaceLayout>             // two-column layout: editor area + analysis rail
│   ├── <SectionNav>                   // tabs: Meta / Gear / Skills / Passives / Blessings
│   └── <section content>
│       ├── <MetaSection>              // name, description, class, mastery, level, flags
│       │     (reads/writes: meta fields via setMeta action)
│       ├── <GearSection>              // wraps <GearEditor> (includes idol tab)
│       │     (reads: build.gear; writes: setGear)
│       ├── <SkillsSection>            // wraps <SkillSelector>
│       │     (reads: build.skills + build.character_class + build.mastery;
│       │      writes: setSkills, via add/remove/points/tree-alloc adapters)
│       ├── <PassivesSection>          // wraps <BuildPassiveTree> + <PassiveProgressBar>
│       │     (reads: build.passive_tree + class/mastery;
│       │      writes: setPassiveTree)
│       └── <BlessingsSection>         // wraps <BlessingsPanel>
│             (reads: build.blessings; writes: setBlessings)
└── <AnalysisPanel>                    // placeholder — renders "wired up in phase 2"
```

### 4.1 Section wrappers

Each `*Section` is a thin adapter: ~20–50 lines, no business logic, no local build state.
It subscribes to the store via a narrow selector (e.g. `useBuildWorkspaceStore(s => s.build.gear)`),
passes that value to the underlying editor as a prop, and wires the editor's `onChange` (or
per-callback variants) to the store's action. Section wrappers exist so that the existing editor
components remain **unmodified** in this phase — the brief is explicit that this phase is
structural consolidation, not component rewrites.

### 4.2 Navigation pattern

The existing `BuildPlannerPage` does not use tabs — it stacks sections vertically and uses
`AccordionSection` (`components/features/build/simulation/AccordionSection.tsx`) for the analysis
output only. The brief says to match the existing convention "unless that convention is clearly
worse than an alternative."

**Choice: tabs, not vertical stacking.** Rationale:

- A vertical stack of six full editor surfaces (Meta, Gear, Skills, Passives, Blessings, plus idols
  inside Gear) combined with a persistent analysis rail produces an unusable amount of scroll.
  The existing planner dodges this by only rendering a subset at a time (view vs. create vs. edit)
  and by omitting several surfaces in the create-mode quick path.
- Last Epoch Tools and Maxroll — both referenced in the brief as the target pattern — use tab/
  section navigation, not infinite scroll.
- Tabs also give the phase 2 reveal-animation layer a natural surface boundary to animate around.

The tab strip is implemented inline in `UnifiedBuildPage`; no new UI-kit component is introduced.

### 4.3 Analysis rail

`AnalysisPanel` is a pure-presentational component in this phase. It reads nothing from the
server and triggers nothing. It renders a single card containing the working build's class/mastery
summary plus the string "Analysis panel — wired up in next phase." It exists primarily to lock in
the two-column layout so phase 2 has a stable DOM target.

## 5. Build State Shape

### 5.1 Why a new store (minimum-necessary refactor)

The current state layer is **not** adequate for the unified page. `BuildPlannerPage` holds build
data in ~13 separate `useState` hooks with no shared object, which means:

- There is no way for a sibling component (e.g. the analysis rail in phase 2) to observe the
  working build without being a child of the page.
- There is no stable identity for "the working build" that future undo/redo can snapshot.
- Immutability is not enforced — callbacks like `onChange(gear)` hand back an array whose
  provenance (new array vs. mutated array) is not guaranteed.

The brief says: "If the current state management does not support [the unified pattern] — for
example, if planner and edit each maintain their own local state — introduce the minimum necessary
state layer to make the unified page work. Prefer extending the existing state management over
introducing a new library."

The project already uses Zustand (`useAuthStore`, `useCraftStore`). Adding a third Zustand slice
is the minimum-necessary refactor. No new dependency, no new pattern.

### 5.2 Store file and API

`frontend/src/store/buildWorkspace.ts` exports `useBuildWorkspaceStore`. Re-exported from
`frontend/src/store/index.ts` alongside the existing `useAuthStore` / `useCraftStore`.

Shape (TypeScript):

```ts
export type BuildWorkspaceBuild = Omit<
  Build,
  | "id" | "slug" | "vote_count" | "view_count"
  | "created_at" | "updated_at" | "author" | "user_vote" | "tier"
>;
// The "working copy" excludes server-only fields that the editor cannot mutate.
// Server identity (id, slug) and audit metadata are held as a sibling field:

export interface BuildWorkspaceState {
  build: BuildWorkspaceBuild;
  identity: { id: string | null; slug: string | null };
  status: "empty" | "loading" | "ready";

  // Actions — each produces a new `build` object via Zustand `set`.
  initializeFromServer: (b: Build) => void;
  initializeEmpty: () => void;
  reset: () => void;

  setMeta: (patch: Partial<Pick<BuildWorkspaceBuild,
    | "name" | "description" | "character_class" | "mastery" | "level"
    | "is_ssf" | "is_hc" | "is_ladder_viable" | "is_budget"
    | "patch_version" | "cycle" | "is_public"
  >>) => void;
  setSkills: (skills: BuildSkill[]) => void;
  setGear: (gear: GearSlot[]) => void;
  setPassiveTree: (nodeIds: number[]) => void;
  setBlessings: (blessings: SelectedBlessing[]) => void;
}
```

### 5.3 Immutability guarantee

Every action assigns a new top-level object via `set(...)` and, for collection fields, returns a
new array from the caller's input. Section wrappers that expose fine-grained callbacks (e.g.
`onAddSkill`) compute the new collection with a pure helper and call `setSkills(next)`. The
underlying leaf editor components already pass full replacement arrays through their `onChange`
callbacks, so no defensive copying is required at the store boundary.

### 5.4 What the store is NOT

- **Not a React Query replacement.** Server fetch and save stay in `hooks/index.ts`.
- **Not a persistence layer.** No localStorage. The legacy `forge_draft_build` localStorage key
  used by `BuildPlannerPage` is intentionally not touched — the old planner still owns it.
- **Not an undo/redo stack.** That arrives in a later phase. The immutability guarantee is
  scaffolding for it, nothing more.
- **Not a global singleton beyond this feature.** Only the unified page and its section wrappers
  import the store. The old planner keeps its `useState` hooks.

## 6. Intentional Deviations from Parity

The brief requires feature parity: every editable surface on the old pages present on the unified
page, every edit persists correctly, every build that loads on the old pages loads on the unified
page. Parity is met with the following documented deviations.

### 6.1 Routes

- **New routes use `/workspace/*`, not `/build/:buildId`** — see §3 for rationale. Preserving the
  old planner at its canonical URL was the overriding constraint.

### 6.2 Save/analyze UI

- **No "Save" button in phase 1.** The store holds a working copy; it does not call
  `useUpdateBuild` or `useCreateBuild` on its own. Persistence wiring is a phase-2+ concern
  because the reveal-animation phase needs to decide how edits commit (on blur, on explicit
  save, on navigation). For phase 1, edits update the store and are lost on refresh. This is
  called out explicitly so reviewers do not assume the shell is production-ready: it is a shell.

- **No "Analyze Build" button in phase 1.** The analysis panel is a placeholder. The old planner
  retains its analyze button and its full analysis flow.

### 6.3 Surfaces

- **No Weaver Tree section.** No Weaver Tree editor component exists in the frontend today
  (backend data pipeline exists but no UI). There is nothing to consolidate. The tab strip is
  designed so a `<WeaverTreeSection>` can be added later without shell changes.

- **Idols remain inside Gear.** `GearEditor` already has an "idols" internal tab. The unified
  shell reuses that and does not promote Idols to its own top-level section. This matches the
  existing component boundary and keeps this phase zero-touch on leaf editors.

- **No BuildEditorPage ("encounter simulator") integration.** Out of scope — see §1.1.

### 6.4 Create-mode UX

- The old planner's create mode uses an inline `QuickGearGrid` instead of the full `GearEditor`.
  The unified shell uses `GearEditor` uniformly for both create (`/workspace/new`) and edit
  (`/workspace/:slug`). This is structurally simpler and eliminates one source of the duplication
  called out in §1.6. Functionally `GearEditor` is a superset of `QuickGearGrid`.

### 6.5 Draft persistence

- The old planner's `forge_draft_build` localStorage autosave is **not** reimplemented on the
  unified page. Phase 2's real-time analysis and phase 3's animation layer will redefine when
  and how edits commit; autosaving to localStorage before those decisions are made would create
  throwaway code. Users on `/workspace/new` will lose their work on refresh in phase 1. The old
  planner's draft autosave continues to work at its existing URLs.

### 6.6 Visual parity

- Pixel-perfect visual match is not claimed and not required by the brief. The shell uses the
  project's existing Tailwind/forge design tokens and reuses the leaf editors unmodified, so
  each surface looks identical in isolation. The containing chrome (tab strip, analysis rail)
  is new.

---

_End of phase 1 design note. Phase 2 (real-time analysis wiring) and later phases will update
this document in place rather than forking a new one._
