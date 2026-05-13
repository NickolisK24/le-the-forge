# v2.5 Trusted-Data Explanation Page

v2.5 Checkpoint 6 adds a user-facing trusted-data explanation page.

This is frontend UX and documentation work only. It does not change backend runtime behavior, production planner output, crafting, simulation, stat aggregation, value normalization, or skill identity handling.

## Page Added

- `frontend/src/pages/TrustedDataExplanationPage.tsx`
- Route: `/trusted-data`
- Focused test: `frontend/src/__tests__/pages/trusted-data-explanation-page.test.tsx`

## Major Sections

The page explains:

- what trusted data means
- what generated data means
- what validation and provenance mean
- what display-only means
- what not planner-calculable means
- what audit-only value normalization means
- why unsupported mechanics are shown honestly
- why unresolved skill identity gaps are not guessed
- what users can safely rely on today
- what is waiting for v3 mechanical intelligence

## Components Reused

The page reuses existing v2.5 trust UX components:

- `V2TrustBadge`
- `V2SupportBadge`
- `V2LimitationNotice`

## User-Facing Copy Goals

The copy distinguishes trusted identity and provenance from mechanical planner readiness:

- trusted data can be sourced and validated without being planner-calculable
- display-only data is inspectable but not used for stat math
- audit-only value normalization means values are not converted into planner math
- unsupported mechanics are visible instead of guessed
- unresolved skill identity gaps remain visible and unbridged
- production planner calculations do not consume v2 trusted data yet

## Safety Rules

The page must not imply:

- DPS or EHP is accurate because data is trusted
- planner calculations are supported by v2 data
- unsupported mechanics are solved
- value normalization is complete
- skill identity gaps are resolved
- v3 mechanical intelligence already exists

## Navigation Status

The `/trusted-data` route is registered as a normal app route. Global navigation was not redesigned in this checkpoint. The page links to existing debug surfaces for deeper inspection.

## Remaining UX Gaps

- Add a visible navigation entry once the broader trust/report navigation is cleaned up.
- Add a user-facing support matrix.
- Add a planner-safe adapter status panel.
- Add a pre-v3 mechanical readiness dashboard.
- Add clearer route/report discovery for non-developer users.
