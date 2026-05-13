# v2.5 Stats / Modifiers Debug Page

v2.5 Checkpoint 5 adds a dedicated frontend debug page for v2 stat and modifier registry status.

This is frontend debug and UX work only. It does not change backend runtime behavior, production planner output, crafting, simulation, stat aggregation, value normalization, or skill identity handling.

## Page Added

- `frontend/src/pages/debug/V2StatsModifiersDebugPage.tsx`
- Dev route: `/debug/v2-stats-modifiers`
- Focused test: `frontend/src/__tests__/pages/v2-stats-modifiers-debug-page.test.tsx`

## Data Source

The page uses the existing read-only experimental endpoint:

- `GET /experimental/v2/modifiers/debug`

No backend route was added.

The endpoint exposes debug summaries for:

- `docs/generated/v2_stat_registry.json`
- `docs/generated/v2_modifier_registry.json`

## Fields Shown

The page displays:

- stat registry count
- modifier row count
- planner-calculable count
- stable-calculable count
- value normalization status
- `source_units` value scale count
- `unknown` value scale count
- production consumer status
- top blocked reasons
- operation distribution
- value scale distribution
- stat and modifier registry source paths

## Safety Messaging

The page uses existing v2.5 trust UX components:

- `V2EnvelopePanels`
- `V2LimitationNotice`

It explicitly states:

- stat and modifier data is visible for inspection
- modifier values are not planner-calculable yet
- value normalization remains audit-only
- unknown and source-unit values remain blocked
- production planner calculations do not consume v2 stat/modifier data
- v3 mechanical intelligence is required before calculation use

## Backend Route Changes

None.

## Remaining UX Gaps

- Add debug navigation cleanup so all v2 debug pages are discoverable from one place.
- Add drill-down views for individual stat and modifier records.
- Add clearer filtering for blocked reason, operation, source type, and value scale.
- Add a non-developer trusted-data explanation page.

## Safety Status

- Production planner remap: not performed
- Production v2 stat/modifier consumption: false
- Planner output changes: none
- Value normalization promotion: none
- Skill identity bridge changes: none
- v3 mechanical implementation: none
