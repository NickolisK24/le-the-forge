# v2.5 Planner Adapter Status Panel

## Scope

This checkpoint adds a reusable frontend status panel for the v2 planner-safe adapter boundary. It is a Trust & UX surface only. It does not enable planner remap, production v2 consumption, stat/modifier calculations, value normalization promotion, or skill identity bridging.

## Component Added

`frontend/src/components/v2/V2PlannerAdapterStatusPanel.tsx`

The panel displays:

- adapter mode enabled/disabled state
- production consumption status
- adapter-visible record count
- blocked record count
- planner-calculable count
- stable-calculable count
- top blocked reasons
- baseline readiness counts
- value normalization status
- skill identity bridge status
- limitation copy explaining why the data is still not production planner math

## Data Source

The first integration uses the existing stats/modifiers debug endpoint consumed by `/debug/v2-stats-modifiers`:

`/api/experimental/v2/modifiers/debug`

No backend route was added. The page already exposes the modifier registry count, stable-calculable count, blocked reason summary, value scale distribution, and production consumption status needed for the panel. The v2.5 baseline fixture counts remain the current planned values:

- safe-now baseline fixtures: `7`
- blocked baseline fixtures: `6`

## Integration Point

The panel is integrated into:

`frontend/src/pages/debug/V2StatsModifiersDebugPage.tsx`

This is intentionally colocated with the stat/modifier dry-run debug page because that page already explains the adapter-visible but non-calculating status of v2 modifier rows.

## Safety Messaging

The panel explicitly states:

- the adapter is read-only diagnostics
- it is not production planner math
- production planner calculations are not consuming v2 data
- planner-calculable count remains `0`
- stable-calculable count remains `0`
- value normalization remains `audit_only`
- skill identity bridge remains `unbridged`
- v3 mechanical intelligence is required before adapter-visible records can become production calculation inputs

## Tests

Added:

`frontend/src/__tests__/components/v2-planner-adapter-status-panel.test.tsx`

Updated:

`frontend/src/__tests__/pages/v2-stats-modifiers-debug-page.test.tsx`

## Remaining UX Gaps

- A future status dashboard could aggregate adapter status beyond the stats/modifiers page.
- Baseline readiness can move from fixed frontend status values to a dedicated read-only status endpoint if broader status pages need live report aggregation.
- Debug navigation still needs a later cleanup pass so users can discover v2.5 trust surfaces consistently.
