# v2.5 Report / Debug Navigation Cleanup

## Scope

This checkpoint improves discoverability for v2 and v2.5 trusted-data debug surfaces. It is frontend navigation and UX only. It does not change backend runtime behavior, planner calculations, production planner output, value normalization, or skill identity bridging.

## Navigation Surface Added

Added a dedicated development debug index:

`/debug/v2`

The page lists the main trusted-data inspection surfaces with short safety labels:

- Trusted Data Explanation: `/trusted-data`
- Stats / Modifiers: `/debug/v2-stats-modifiers`
- Forge-Safe Affixes: `/debug/forge-safe-affixes`
- Items: `/debug/v2-items`
- Uniques / Sets: `/debug/v2-unique-sets`
- Idols: `/debug/v2-idols`
- Classes / Masteries: `/debug/v2-classes`
- Passives: `/debug/v2-passives`
- Skills: `/debug/v2-skills`

## Route Alias Added

Added a development-only alias:

`/debug/v2-affixes -> /debug/forge-safe-affixes`

This prevents confusion from the expected v2 route name while preserving the existing canonical Forge-Safe affix debug page.

## Discoverability Improvements

The trusted-data explanation page now links to the v2 debug index, alongside the existing stats/modifiers and affix debug links. The debug index links back to `/trusted-data`, so users can move between plain-language explanations and detailed debug surfaces.

## Safety Copy

The debug index explicitly states that these pages are read-only inspection surfaces and do not power production planner calculations. It uses existing v2.5 limitation copy for:

- experimental-only surfaces
- display-only data
- not planner-calculable data
- production planner unchanged

## Tests

Added:

`frontend/src/__tests__/pages/v2-debug-navigation-page.test.tsx`

The test covers:

- debug index rendering
- `/trusted-data` discoverability
- `/debug/v2-stats-modifiers` discoverability
- canonical affix route linking
- `/debug/v2-affixes` alias registration
- safety copy that does not imply production planner support

## Remaining Navigation Gaps

- Global app navigation still does not expose every debug page, which is intentional for development-only surfaces.
- A future support matrix page can provide a non-debug user-facing route for trust status by domain.
- Report links could eventually be generated from backend report metadata rather than maintained as a static frontend list.
