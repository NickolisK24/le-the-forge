# Unified Planner — Phase 2 Notes (real-time analysis wiring)

Companion note to `docs/unified-planner-design.md`. Phase 2 of 5 wires the
existing analyze-build endpoint into the `AnalysisPanel` so that the panel
updates in real time as the user edits any surface of the build.

This document is the baseline record of what the analysis endpoint looks
like today, for reference during phase 4 (performance optimization).

## 1. Existing analyze endpoints on the backend

Two endpoints return the same full simulation pipeline result:

| Endpoint                               | Input                                                                                                    | Shape of payload                                                                                 |
|----------------------------------------|----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `POST /api/builds/<slug>/simulate`     | slug of a persisted `Build` row                                                                           | none (reads the row)                                                                             |
| `POST /api/simulate/build` (stateless) | Raw build fields: `character_class`, `mastery`, `skill_name`, `allocated_node_ids`, `gear_affixes`, …     | see `SimulateBuildSchema` in `backend/app/schemas/simulate.py`                                   |

The slug-based endpoint is served by `build_service.simulate_build(build)` →
`build_analysis_service.analyze_build(build)`
(`backend/app/services/build_analysis_service.py:132`). It is the more
feature-complete path: returns `dps_per_skill`, `combined_dps`, and resolves
passive-node stats from the DB. It has two drawbacks for real-time analysis:

1. It only reads the **persisted** build row, so edits made on the client but
   not yet saved are invisible to it. Real-time analysis requires that the
   user's working-copy state — which is held in the Zustand store and has
   not been written to the server — drive the result.
2. It requires a slug. `/workspace/new` has no slug until the build is saved,
   which is explicitly deferred to a later phase (see
   `docs/unified-planner-design.md` §6.2).

For phase 2 we use `POST /api/simulate/build` — the stateless endpoint. It
accepts the working-copy fields directly, which is exactly what the
unified-page store holds. It covers `/workspace/new` and `/workspace/:slug`
with the same code path.

### 1.1 Request shape (phase 2 client payload)

```ts
{
  character_class: CharacterClass;
  mastery: string;
  skill_name: string;             // primary skill — first slot with a skill_name
  skill_level: number;            // from the primary skill's points_allocated (min 1)
  allocated_node_ids: number[];   // from build.passive_tree (ints)
  gear_affixes: { name: string; tier: number }[];  // flattened across gear slots
  n_simulations: number;          // default 5_000 (schema default)
}
```

Fields not sent in phase 2:

- `passive_tree` (string IDs, optional). The frontend's working copy holds
  ints, not the DB's namespaced string IDs, so we cannot provide this without
  a lookup. The backend still resolves passive contributions via
  `allocated_node_ids`, which is what the schema exercises.
- `seed`. Left unset so each run is a fresh Monte Carlo draw.
- `spec_tree` / per-skill trees. Only the **primary** skill's tree feeds DPS
  at this endpoint today. Full per-skill DPS breakdown lives in the slug
  endpoint (`dps_per_skill`) and is out of scope for phase 2.

### 1.2 Response shape

`/api/simulate/build` returns (see `simulate_full_build` in
`backend/app/services/simulation_service.py:213`):

```
{
  primary_skill:      string | null,
  skill_level:        number,
  skill_classifications: Record<string, string>,
  stats:              Record<string, number>,
  dps:                DPSResult,
  monte_carlo:        MonteCarloDPS,
  defense:            DefenseResult,
  stat_upgrades:      StatUpgrade[],
  seed:               number | null,
  // plus conversion-data-gap diagnostics
}
```

This is a strict subset of the slug endpoint's response: `dps_per_skill` and
`combined_dps` are **absent**. The existing `SimulationDashboard` component
(`frontend/src/components/features/build/SimulationDashboard.tsx:669`)
destructures `dps_per_skill` and `combined_dps` and guards its per-skill
sections with `hasMultipleSkills`, so it degrades gracefully when those
fields are missing — the per-skill DPS panel is simply not rendered. This
parity gap is acceptable for phase 2; closing it is either a matter of
switching to the slug endpoint for persisted builds (phase 4+ consideration)
or extending the stateless endpoint to accept the full `skills[]` array.

## 2. Baseline response times

Measured in-process via `flask.test_client()` on this sandbox host (no
network hop). 5 samples per configuration after a single warm-up call.
Running with `n_simulations=5_000` unless noted.

| Configuration                                  | Avg      | Min      | Max      |
|------------------------------------------------|----------|----------|----------|
| Minimal (no passives, no gear, MC = 500)       | 4.3 ms   | 4.0 ms   | 4.5 ms   |
| Default (20 passives, 10 affixes, MC = 5_000)  | 5.6 ms   | 5.3 ms   | 5.9 ms   |
| High (40 passives, 15 affixes, MC = 10_000)    | 6.8 ms   | 6.6 ms   | 7.0 ms   |

Reproduction script committed inline with this PR:

```bash
python - <<'PY'
import time
from app import create_app
app = create_app("testing")
client = app.test_client()
with app.app_context():
    from app import db; db.create_all()
# ... see commit for full script
PY
```

These numbers are **server-side in-process**. Real clients incur, on top:

- Flask routing + JSON (de)serialisation overhead (~1–3 ms typical).
- Gunicorn worker dispatch (~1–2 ms when warm, higher when cold).
- Network round-trip (< 5 ms LAN, 20–80 ms typical WAN).
- React Query / fetch overhead on the browser side.

End-to-end p50 is therefore expected to sit in the **30–100 ms** range on a
typical deployment, well under our 400 ms debounce budget. This baseline is
the reference point for phase 4's performance work — if the endpoint grows
past ~300 ms p50 with realistic builds, we'll need to re-evaluate debounce
or add caching / pipeline shortcuts. Phase 4 is where those optimisations
land; phase 2 does **not** introduce any caching.

## 3. Error modes

The stateless endpoint can return:

- **400** — `ValueError` / `KeyError` from the service layer (e.g. unknown
  skill name). Body: `{ errors: [{ message: "<text>" }] }`.
- **422** — schema validation failure (missing `skill_name`, mismatched
  class/mastery). Body: `{ errors: { <field>: [<messages>] } }`.
- **429** — rate-limit exceeded. Default `30 per minute` per IP; configurable
  via the `RATE_LIMIT_SIMULATE_BUILD` env var.
- **5xx** — service/engine exception. Body: `{ errors: [{ message: "<text>" }] }`.
- **Network error** — the shared `request<T>()` helper in
  `frontend/src/lib/api.ts:70` returns `{ errors: [{ message: "Network error — check your connection" }] }`
  instead of throwing, so the hook sees a normal error response.

Phase 2's hook must treat any non-`data` response as an error and surface a
message to the panel.

## 4. Pre-phase-1 presentation (what phase 2 matches)

The canonical "analyse build" flow lives on `BuildPlannerPage` at
`frontend/src/components/features/build/BuildPlannerPage.tsx:266`. On click
of the `Analyze Build` button it calls `simulateApi.build(slug)` and renders
the result through **`SimulationDashboard`**
(`frontend/src/components/features/build/SimulationDashboard.tsx`). That
component is self-contained: it consumes `BuildSimulationResult` and paints
seven sections (summary strip, DPS breakdown, Monte Carlo, EHP, resistances,
avoidance, stat upgrades, insights).

Phase 2 reuses `SimulationDashboard` verbatim from the right-rail
`AnalysisPanel`. The newer `BuildScoreCard`, plain-English labels, and
contextual benchmarks from the masterplan are explicitly **phase 3** scope.

## 5. Deviations from the phase 2 prompt

Documenting for the same reason phase 1 documented its route deviation.

1. **Stateless endpoint used for all builds, including persisted ones.** The
   prompt says "the existing analyze build endpoint," singular. There are
   two (§1). Using the slug endpoint on saved builds would mean the panel
   reflects the persisted build, not the working-copy edits the user has
   made since load — i.e., not real-time. Phase 2's contract is real-time
   analysis of the working copy, so the stateless endpoint is the only
   option today. The slug endpoint stays reserved for a future phase that
   may trade freshness for per-skill DPS detail.
2. **`passive_tree` (string IDs) omitted from the payload.** See §1.1. Passive
   contributions still resolve through `allocated_node_ids`; only the
   DB-backed stat resolver is skipped. This is identical to how the existing
   `TestSimulateBuild.test_full_pipeline` integration test exercises the
   endpoint.
3. **Primary-skill-only.** As noted in §1.1, only the first specialised
   skill drives DPS. Per-skill DPS breakdown is a future follow-up.

## 6. Layout stability verification

Phase-2 step-6 static verification. Browser-based confirmation is deferred
to the project owner (see §7).

### 6.1 What the panel does to guarantee stability

- **Fixed minimum height.** `AnalysisPanel` applies
  `min-h-[520px]` on its outermost `<aside>`. This reserves vertical space
  on initial paint, before any analysis has resolved, so the panel occupies
  the same footprint in idle, pending-skeleton, error, and freshly
  successful states.
- **Panel width is set by the parent column**
  (`frontend/src/components/features/build-workspace/UnifiedBuildPage.tsx`:
  `<div className="w-full lg:w-80 lg:flex-none">`). Internal panel content
  does not influence the column width, so no state transition can push or
  pull adjacent editors horizontally.
- **Previous result is preserved during pending.** When a new request is in
  flight and a previous result exists, the panel keeps rendering that
  result and overlays a small "Updating…" badge in the panel header. The
  visible DOM does not swap to a spinner or skeleton — the dashboard stays
  mounted. This eliminates the common "dashboard → spinner → dashboard"
  flicker loop under rapid edits.
- **Skeleton mirrors the dashboard's rough block layout.** On the rare
  transition from no-prior-result pending to a successful result, the
  skeleton's stacked blocks sit in roughly the same vertical positions the
  dashboard's summary strip / 2-up grids occupy. Some settling is
  unavoidable because the dashboard's exact height depends on how many
  recharts bars the result produces, but the skeleton gets within ~1-2
  card-heights of the final layout.
- **Error state renders in the same container geometry.** The
  `ErrorPanel` is centred in a `min-h-[440px]` flex column inside the
  panel, meaning the retry button sits in the vertical centre of the
  reserved 520px outer frame. This keeps it well away from the editor
  controls on the left side of the main column in desktop layout, and
  below them in the stacked mobile layout.

### 6.2 Assessment against the three transitions called out in the brief

| Transition                        | Panel width | Panel contents vertical jump | Editor reflow risk |
|----------------------------------|-------------|-------------------------------|--------------------|
| success → pending (with result)  | Unchanged — width is fixed by column | None — result stays, only header badge toggles | None — the editor column is a separate flex item |
| pending → success                | Unchanged   | Small settling possible only on the very first success of the session (skeleton → dashboard); subsequent success transitions are result-on-top-of-result no-ops | None |
| idle/pending → error             | Unchanged   | Error block is centred in the reserved 520 px frame, so moves toward the middle when the panel was previously taller | None; retry button stays within the panel column |
| error → success (retry path)    | Unchanged   | Error block swaps for dashboard within the same min-height frame | None |

### 6.3 Known limitations

- **Dashboard height is content-dependent.** On a build with fewer skill
  upgrades or a very sparse resistance profile, `SimulationDashboard`'s
  own charts shrink. A dramatic drop in dashboard height between two
  sequential successful results could cause the panel's footprint to
  shrink. This does not reflow editor surfaces (they are in the sibling
  flex column), but the page's overall height will change. Phase 3 owns
  presentation redesign; reserving a hard maximum is that phase's call.
- **Stacked (mobile) layout.** On narrow viewports the panel stacks below
  the editor column. State transitions on the panel can push content
  below it (e.g. page footer) further down. This is acceptable — nothing
  the user is editing is displaced — but is worth noting for phase 3
  UX review.

### 6.4 No new styling library introduced

All styles are Tailwind utility classes, consistent with the rest of the
project. No new dependency, no CSS-in-JS, no global CSS edits.

## 7. Manual verification checklist for the reviewer

This sandbox has no display; the project owner performs the following
checks in a browser before merge:

- Open `/workspace/new`, make an edit, confirm the analysis request fires
  after ~400 ms (network tab, `POST /api/simulate/build`).
- Open `/workspace/:slug` for an existing build and confirm analysis fires
  immediately on mount.
- Make rapid successive edits and confirm only one request fires (the last
  one wins).
- Force an error (stop the backend, or block the endpoint in DevTools) and
  confirm the error state renders with a retry button that bypasses the
  debounce.
- Confirm no layout shifts occur during state transitions (success → pending
  → success), especially that adjacent editor surfaces do not reflow and
  the retry button does not overlap editor controls.
