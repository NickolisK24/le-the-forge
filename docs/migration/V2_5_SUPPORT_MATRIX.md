# v2.5 User-Facing Support Matrix

## Scope

This checkpoint adds a user-facing support matrix for v2.5 Trust & UX. It is frontend UX and documentation only. It does not add backend routes, enable production planner consumption, normalize values, bridge skill identities, or begin v3 mechanical intelligence work.

## Page Added

Route:

`/trusted-data/support`

File:

`frontend/src/pages/TrustedDataSupportMatrixPage.tsx`

## Domains Covered

The matrix covers:

- Items / item bases
- Affixes
- Unique/set items
- Idols
- Classes/masteries
- Passive trees
- Skills / skill trees
- Stats
- Modifiers
- Planner adapter

Each row explains what is safe to show today, what remains display-only, the primary blockers, and the expected next track.

## Statuses Shown

The page uses existing v2.5 badges and limitation copy for:

- validated/provenance-backed data
- display-only data
- audit-only data
- not planner-calculable data
- production planner unchanged
- unresolved skill identity gaps

The global safety copy keeps these truths visible:

- production planner consumption is false
- planner-calculable count is `0`
- stable-calculable count is `0`
- value normalization is `audit_only`
- skill identity bridge status is `unbridged`

## Integration Links

Added links:

- `/trusted-data` links to `/trusted-data/support`
- `/debug/v2` links to `/trusted-data/support`
- `/trusted-data/support` links back to `/trusted-data`, `/debug/v2`, and `/debug/v2-stats-modifiers`

## Safety Rules

The page avoids wording that implies:

- planner DPS is powered by v2 data
- unsupported mechanics are calculated
- value normalization is complete
- skill identity gaps are resolved
- v3 mechanical intelligence already exists

## Remaining UX Gaps

- The matrix is static and intentionally conservative. A later support matrix could be generated from backend report metadata.
- Domain rows can gain richer drill-down links as user-facing report pages become available.
- Global navigation still does not expose every trusted-data page, which remains a separate navigation design task.
