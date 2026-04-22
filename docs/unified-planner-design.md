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

_To be filled in._

## 4. Component Tree

_To be filled in._

## 5. Build State Shape

_To be filled in._

## 6. Intentional Deviations from Parity

_To be filled in._
