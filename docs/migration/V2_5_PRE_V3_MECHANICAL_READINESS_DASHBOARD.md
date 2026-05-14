# v2.5 Pre-v3 Mechanical Readiness Dashboard

## Scope

This checkpoint adds a frontend-only readiness dashboard for explaining what must be solved before trusted v2 data can become mechanical planner input. It does not begin v3 mechanical intelligence work, add backend routes, change planner output, normalize values, bridge skill identities, or consume v2 data in production planner calculations.

## Dashboard Added

Route:

`/trusted-data/pre-v3-readiness`

File:

`frontend/src/pages/PreV3MechanicalReadinessPage.tsx`

## Sections Included

The dashboard includes:

- current readiness decision
- completed v2/v2.5 trust and visibility work
- remaining blocker categories
- value normalization blockers
- operation semantics blockers
- stat identity blockers
- skill identity blockers
- unsupported/scripted/text-only mechanic blockers
- golden baseline requirements
- what v3 must prove before production planner remap

## Readiness Cards

Cards show:

- v2 Infrastructure: Ready
- Production Planner: Not Ready
- Mechanical Remap: Not Ready
- Planner-Calculable Records: `0`
- Stable-Calculable Records: `0`
- Value Normalization: Audit Only
- Skill Identity Bridge: Unbridged
- Golden Baselines: Planned / Partial Scaffold
- Experimental Adapter Mode: Disabled by Default

## Navigation Links Added

Added links to `/trusted-data/pre-v3-readiness` from:

- `/trusted-data`
- `/trusted-data/support`
- `/debug/v2`

The dashboard links back to:

- `/trusted-data`
- `/trusted-data/support`
- `/debug/v2`

## Safety Copy

The page states that EpochForge can inspect trusted data today, but it will not use that data to change build output yet. It keeps these blockers visible:

- value normalization remains audit-only
- operation semantics are not proven safe
- stat identities must resolve consistently
- skill identity bridge remains unbridged
- unsupported/scripted/text-only mechanics are not inferred
- golden mechanical baselines are required before remap

## Remaining v3 Blockers

v3 must prove:

- explicit value scale contracts
- deterministic operation semantics
- stat identity coverage and blocked fallbacks
- skill identity bridge policy based on source evidence
- golden planner/crafting/passive/skill/item/modifier baselines
- dry-run comparison snapshots before production remap

## Remaining UX Gaps

- The dashboard is static and conservative. A future report-backed dashboard could read generated readiness reports directly.
- Drill-down pages for each blocker category can be added after the trust UX layer stabilizes.
- Global navigation exposure remains intentionally minimal.
