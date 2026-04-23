# Unified Planner — Phase 3 Notes (presentation layer)

Companion to `docs/unified-planner-design.md` and
`docs/unified-planner-phase2-notes.md`. Phase 3 of 5 replaces the phase-2
`SimulationDashboard` render inside `AnalysisPanel` with a purpose-built
presentation stack — score card, split cards, primary-skill breakdown, skills
summary, improvement recommendations, and an advanced-analysis accordion.

This document is the baseline record of the analysis payload shape and the
design-token vocabulary available, written up-front as the single source of
truth for the rest of the phase.

## 1. Analysis response field inventory

`BuildSimulationResult` (`frontend/src/lib/api.ts:412`) is the full shape of
the success body returned by `POST /api/simulate/build` (phase 2 endpoint)
and `POST /api/builds/<slug>/simulate`. Every field the presentation layer
binds to is enumerated below so downstream work can refer to this table
instead of re-reading the TypeScript.

### 1.1 Top-level fields

| Field              | Type                          | Source                                              |
|--------------------|-------------------------------|-----------------------------------------------------|
| `primary_skill`    | `string`                       | Primary-skill detector in `simulate_full_build`.    |
| `skill_level`      | `number`                       | Primary skill's level as sent on the request.       |
| `stats`            | `Record<string, number>`       | Aggregated `BuildStats.to_dict()`.                  |
| `dps`              | `DPSResult`                    | `combat_engine.calculate_dps()` result.             |
| `monte_carlo`      | `MonteCarloDPS`                | `combat_engine.monte_carlo_dps()` result.           |
| `defense`          | `DefenseResult`                | `defense_engine.calculate_defense()` result.        |
| `stat_upgrades`    | `StatUpgrade[]`                | `optimization_engine.get_stat_upgrades()` (top 5).  |
| `seed`             | `number \| null`               | Echo of the request seed (optional).                |
| `dps_per_skill`    | `SkillDpsEntry[]`              | Slug endpoint only today — missing on stateless.    |
| `combined_dps`     | `number`                       | Slug endpoint only today — missing on stateless.    |

Phase 2 already documented that `dps_per_skill` and `combined_dps` are not
returned by the stateless endpoint. The phase-3 components must therefore
render reasonable fallbacks when those fields are missing — single-row
primary-skill card on an unsaved build is a known limitation the presentation
layer absorbs without fabricating data.

### 1.2 `DPSResult`

| Field                    | Type     | Notes                                                        |
|--------------------------|----------|--------------------------------------------------------------|
| `hit_damage`             | `number` | Per-hit pre-crit damage.                                     |
| `average_hit`            | `number` | Crit-weighted average hit.                                   |
| `dps`                    | `number` | Hit DPS (no ailment contribution).                           |
| `effective_attack_speed` | `number` | Attacks / casts per second.                                  |
| `crit_contribution_pct`  | `number` | % of DPS attributable to crits.                              |
| `flat_damage_added`      | `number` | Flat added damage from gear + build bonuses.                 |
| `bleed_dps`              | `number` | Bleed DoT DPS.                                               |
| `ignite_dps`             | `number` | Ignite DoT DPS.                                              |
| `poison_dps`             | `number` | Poison DoT DPS.                                              |
| `ailment_dps`            | `number` | Sum of the three ailment DPS streams.                        |
| `total_dps`              | `number` | Hit DPS + ailment DPS.                                       |

The "contribution split" on the primary skill card reads
`crit_contribution_pct` + heuristic base/modifier split. There is no
per-source DPS decomposition in the payload today; the card labels the split
as a presentational breakdown and does not claim to reflect engine internals.

### 1.3 `DefenseResult`

| Field                     | Type       |
|---------------------------|------------|
| `max_health`              | `number`   |
| `effective_hp`            | `number`   |
| `armor_reduction_pct`     | `number`   |
| `avg_resistance`          | `number`   |
| `fire_res` .. `poison_res` (7 resists) | `number` |
| `dodge_chance_pct`        | `number`   |
| `block_chance_pct`        | `number`   |
| `block_mitigation_pct`    | `number`   |
| `endurance_pct`           | `number`   |
| `endurance_threshold_pct` | `number`   |
| `crit_avoidance_pct`      | `number`   |
| `glancing_blow_pct`       | `number`   |
| `stun_avoidance_pct`      | `number`   |
| `ward_buffer`             | `number`   |
| `total_ehp`               | `number`   |
| `ward_regen_per_second`   | `number`   |
| `ward_decay_per_second`   | `number`   |
| `net_ward_per_second`     | `number`   |
| `leech_pct`               | `number`   |
| `health_on_kill` / `mana_on_kill` / `ward_on_kill` | `number` |
| `health_regen` / `mana_regen` | `number` |
| `survivability_score`     | `number`   | 0 to 100 rating. |
| `sustain_score`           | `number`   | 0 to 100 rating. |
| `weaknesses`              | `string[]` | Pre-formatted short strings, e.g. "Low Fire Resistance (12%)". |
| `strengths`               | `string[]` | Pre-formatted short strings. |

### 1.4 `StatUpgrade`

| Field             | Type                |
|-------------------|---------------------|
| `stat`            | `string`            |
| `label`           | `string`            |
| `dps_gain_pct`    | `number`            |
| `ehp_gain_pct`    | `number`            |
| `explanation`     | `string` (optional) |

The stateless endpoint returns the top 5. The phase-3 "What to improve next"
section reuses the existing `StatUpgradePanel` / `UpgradeCandidatesPanel`
components, which today are driven by the separate `/api/builds/<slug>/optimize`
endpoint and therefore only render on saved builds. On `/workspace/new` the
panel is omitted; this is acceptable because `stat_upgrades[0]?.label` is
already surfaced in the BuildScoreCard's summary sentence.

### 1.5 `MonteCarloDPS` and `SkillDpsEntry`

`MonteCarloDPS` (`mean_dps`, `min_dps`, `max_dps`, `std_dev`, `percentile_25`,
`percentile_75`, `n_simulations`) is consumed by the legacy
`SimulationDashboard` charts. Phase 3 does not surface Monte Carlo variance
in the new presentation stack — the compact-panel design drops it intentionally;
the legacy planner still carries the charts for users who want them.

`SkillDpsEntry` (`skill_name`, `skill_level`, `slot`, `dps`, `total_dps`,
`is_primary`) powers the per-skill DPS rows on `SkillsSummaryTable`. The
stateless endpoint returns an empty array today; the table falls back to a
role/classification-only render (no per-row DPS numbers) when the array is
empty.

## 2. Design-token vocabulary

Source: `frontend/tailwind.config.js` and `frontend/src/styles/design-tokens.ts`.

### 2.1 Colors in active use

| Token            | Hex                          | Intended use                         |
|------------------|------------------------------|--------------------------------------|
| `forge-bg`       | `#06080f`                    | Page backdrop.                       |
| `forge-surface`  | `#0c0f1c`                    | Panel background.                    |
| `forge-surface2` | `#10152a`                    | Card inner background.               |
| `forge-surface3` | `#161c34`                    | Elevated inner chrome.               |
| `forge-border`   | `rgba(80,100,210,0.22)`      | Hairline panel borders.              |
| `forge-border-hot` | `rgba(130,160,255,0.50)`   | Focus / hover border.                |
| `forge-amber`    | `#f0a020`                    | Primary accent, equipment, rating S. |
| `forge-amber-hot`| `#ffb83f`                    | Primary accent hover.                |
| `forge-gold`     | `#f5d060`                    | Gold highlight (rating S alt).       |
| `forge-ember`    | `#e06030`                    | Warning/heat accent.                 |
| `forge-cyan`     | `#00d4f5`                    | Simulation accent, rating B.         |
| `forge-cyan-hot` | `#40ddf5`                    | Cyan hover.                          |
| `forge-text`     | `#eceef8`                    | Default body text.                   |
| `forge-muted`    | `#8890b8`                    | Secondary text.                      |
| `forge-dim`      | `#4a5480`                    | Tertiary text / labels.              |
| `forge-green`    | `#3dca74`                    | Positive status / rating A.          |
| `forge-red`      | `#ff5050`                    | Negative status / rating D.          |
| `forge-blue`     | `#5ab0ff`                    | Info status.                         |
| `forge-purple`   | `#b870ff`                    | Class chip, rating decoration.       |

### 2.2 Benchmark indicator colors

`BENCHMARK_COLORS` in `frontend/src/constants/statBenchmarks.ts`:

- `strong` → `#4ade80` (Tailwind-green-400; brighter than `forge-green` by
  design — it reads as "target met" on dark surface).
- `average` → `#f0a020` (`forge-amber`).
- `weak` → `#f87171` (Tailwind-red-400; softer than `forge-red` so the
  panel doesn't scream on an unfinished build).

The benchmark-color palette is intentionally distinct from `forge-green` /
`forge-red` so the "status tier" visuals don't collide with system-level
status states (success toasts, error alerts). Documented here so later phases
do not try to unify them.

### 2.3 Letter-grade color mapping

Existing `computeBuildRating` in
`frontend/src/components/features/build/simulation/BuildScoreCard.tsx`:

| Grade | Color     | Notes                                         |
|-------|-----------|-----------------------------------------------|
| `S`   | `#f0a020` | `forge-amber` (gold equivalent on this theme).|
| `A`   | `#4ade80` | Benchmark-strong green.                       |
| `B`   | `#22d3ee` | Tailwind-cyan-400, close to `forge-cyan`.      |
| `C`   | `#f0a020` | `forge-amber` — same as S. Intentional: C is  |
|       |           | still a usable build, not a failure.           |
| `D`   | `#f87171` | Benchmark-weak red.                           |

The S and C sharing `#f0a020` was inherited from the existing card on the
legacy planner. Phase 3 changes C to the warning-yellow `#facc15` (Tailwind-
yellow-400) to distinguish the two tiers visually per the prompt (`C uses
yellow`).

### 2.4 Typography

`Cinzel` for display headers, `Exo 2` for body, `JetBrains Mono` for numeric /
label text. The existing simulation panels follow a consistent pattern:

- Panel titles: display font, `text-xl`, tracking-wider.
- Stat labels: mono font, `text-[10px]`, uppercase, `tracking-widest`, muted.
- Stat values: display font for large numbers; mono font + tabular-nums for
  table rows.

Phase 3 components must follow that pattern rather than introducing a new
typographic register.

### 2.5 Spacing

Panel content uses `gap-3` / `gap-4` (`12px` / `16px`) internally. Between
top-level sections, the existing planner uses `gap-6` (`24px`) for its
dashboard column. Phase 3's reassembled `AnalysisPanel` uses `gap-4` between
sections because the right-rail column is narrower than the full-width
planner column; `gap-6` would leave too much whitespace.

## 3. Reuse map

Phase 3 is explicitly "do not rewrite existing components." The reuse map:

| Phase-3 component                                                        | Sources                                                                          |
|--------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `build-workspace/analysis/BuildScoreCard`                                | Thin wrapper around `features/build/simulation/BuildScoreCard` (legacy card).    |
| `build-workspace/analysis/OffenseCard` + `DefenseCard`                  | Split out of `features/build/simulation/OffenseDefenseSplit` (same rows, layout).|
| `build-workspace/analysis/PrimarySkillBreakdown`                         | Thin wrapper around `features/build/simulation/PrimarySkillBreakdown`.           |
| `build-workspace/analysis/SkillsSummaryTable`                            | Thin wrapper around `features/build/simulation/AllSkillsSummary`.                |
| `build-workspace/analysis/AdvancedAnalysisAccordion`                     | Thin wrapper around `features/build/simulation/AccordionSection` + existing boss/corruption/gear panels. |

Where a phase-3 file adds no behaviour beyond prop-shaping, it still exists
so the unified-page composition references `build-workspace/analysis/*`
everywhere and the legacy planner keeps importing from
`features/build/simulation/*`. This lets phase 5 retire the legacy planner
without touching the unified-page imports.

## 4. Store wiring deltas

Phase 3 does not modify `useBuildWorkspaceStore`. The presentation layer is
pure-read: selectors bind to `analysisResult`, `analysisStatus`,
`analysisError`, `identity.slug`, and `build.skills`. All write actions
remain phase-1/phase-2 surface area.

## 5. Open questions (deferred to phase 4+)

- Per-section skeletons during pending-with-no-prior-result. Phase 2 rendered
  a single panel-wide skeleton. Phase 3 upgrades this slightly: the score
  card renders a structurally-correct skeleton and the offense / defense /
  primary-skill / skills-summary sections each render placeholder rectangles
  of the right rough height. Further refinement is a phase-4 perf concern.
- Override-primary-skill wiring. The phase-3 `BuildScoreCard` and
  `PrimarySkillBreakdown` have a "Change" button but the workspace store
  has no action to pin a primary-skill override — the button currently
  routes through `onOpenSkills` so the user can switch which skills are
  slotted. Real override wiring requires a new store action and backend
  support; deferred to phase 5.

## 6. Phase-3 step-9 verification — empty state and reveal

### 6.1 Empty-state copy change

Before phase 3 the idle message read "Edit your build to see analysis."
That instruction is technically correct but meaningless to a user who
just landed on `/workspace/new` and hasn't yet understood that the panel
is waiting for a simulatable build. Phase 3 splits the idle copy into two:

| Workspace state                                   | Copy                                                    |
|---------------------------------------------------|---------------------------------------------------------|
| Not simulatable (no class + mastery or no skills) | "Select a class and specialize a skill to see analysis."|
| Simulatable but no request has fired yet          | "Edit your build to see analysis."                      |

The second branch only fires when the hook has not yet produced any
response — e.g. between the first keystroke that makes the build
simulatable and the debounce landing. In practice this flicker-window
is ~0..400 ms, which is why keeping the old copy for this branch is fine.

A subtle SVG "sun / focus" icon renders above the message using the
`forge-dim` stroke colour. Source is inline in `AnalysisPanel.tsx` — no
new asset file, no new icon library. The icon picks up no additional
characters the message didn't already carry, so the aria-live region
continues to announce the message alone.

### 6.2 Reveal behaviour on /workspace/new

The phase-2 hook has an `isInitialLoadRef` 0-ms fast path that was designed
for `/workspace/:slug` — an already-populated build that is simulatable
at mount time. `/workspace/new` begins non-simulatable. The reveal path
for a fresh `/workspace/new` is:

1. Mount → `initializeEmpty()` sets `status = "ready"`.
2. `useDebouncedAnalysis` sees the ready transition and schedules a 0 ms
   fire. `runAnalysis` runs, checks `buildIsSimulatable`, returns early
   because there are no skills yet.
3. `isInitialLoadRef` flipped to `false` (phase-2 semantics: the flag
   discharges on the first scheduled fire, whether or not the run
   actually posts a request).
4. User sets class → `Mage`, mastery → `Sorcerer`, opens the Skills tab,
   adds `Fireball`. Each edit re-schedules the debounced fire. Now-
   standard 400 ms debounce applies.
5. 400 ms after the last edit, `runAnalysis` fires. `buildIsSimulatable`
   is true, the request posts, the panel transitions to `pending` (with
   skeletons) and then `success`.

The prompt explicitly calls out that "If the first fire after becoming
simulatable uses the 400 ms debounce, that is acceptable". It is — the
user is mid-edit, and a real-time analysis panel that reacts within
half a second is indistinguishable from "instant" to a human user.

### 6.3 Edge cases observed during step-9 implementation

- **Class change after full build**: switching `Mage → Rogue` on a
  fully-specialized build makes the cached `primary_skill` (e.g.
  `Fireball`) a mismatch for the new class. The next analysis request
  returns an engine error because the mastery / skill combo is invalid.
  The existing error-state retry covers this — phase 3 does not special-
  case class changes.
- **Rapid skill swap**: the phase-2 stale-response protection (monotonic
  `analysisRequestId`) already handles two requests in flight; phase 3
  inherits that without change.
- **Analysis returning a non-primary skill for the slotted skill set**:
  the primary-skill detector on the backend can pick a different skill
  than the user expects. The `BuildScoreCard` "Change" button + the
  SkillsSummaryTable's "Primary" badge give the user visibility into
  which skill drove the render.
