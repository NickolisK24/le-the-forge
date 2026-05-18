# v4.5C.3 Frontend Trust Navigation Entry Points

## Architectural Purpose

v4.5C.3 makes the existing `/trusted-data/frontend-trust` surface discoverable
from the app through controlled read-only navigation and local trusted-data
entry points.

This phase does not rename the route, remove deterministic fallback behavior,
or change the v4.5C.2 report integration model. It adds discoverability only.

## Navigation Philosophy

Frontend trust navigation remains:

- deterministic
- read-only
- governance-safe
- fail-visible
- descriptive-only
- publicly transparent
- non-authoritative

Navigation copy is intentionally short and plain. It avoids launch, approval,
recommendation, ranking, scoring, correctness, execution, and production claims.

## Stable Trust Surface Route

The trust surface remains available at:

```text
/trusted-data/frontend-trust
```

This route is linked from the trusted data explanation page and the app sidebar.

## Trusted Data Explanation Entry Point

The trusted data explanation page now includes a local read-only trust surface
callout. The callout explains that the surface shows support status, evidence,
provenance, lineage, report-backed metadata, fallback visibility, and
fail-visible diagnostics.

The callout explicitly says it does not enable planner authority or operational
behavior.

## App Navigation Entry Point

The sidebar now includes a non-intrusive `Trust Visibility` link to the existing
trust surface route. This link is discoverability only. It is not an action
control, planner control, launch control, approval control, or production
enablement control.

## Report-Aware Messaging

The entry point and existing trust surface preserve report-aware messaging for:

- deterministic report-backed visibility
- fallback data visibility
- report hash and certification visibility
- fail-visible diagnostics

Fallback limitations remain visible and are not silently hidden.

## Prohibited Navigation Language

The new navigation surfaces avoid:

- Approved
- Safe to use
- Recommended
- Best build
- Fully trusted
- Production ready
- Guaranteed correct

## Inherited Prohibitions Preserved

v4.5C.3 preserves the inherited prohibitions against:

- planner execution
- planner recommendations
- planner ranking
- trust scoring
- evidence scoring
- confidence scoring
- recommendation systems
- ranking systems
- authorization semantics
- approval semantics
- orchestration execution
- orchestration routing
- orchestration traversal
- production enablement
- runtime mutation
- operational mutation
- hidden automation behavior
- live mutable trust state
- report-driven planner behavior
- frontend launch authorization language

## Intentionally Preserved Limitations

- Navigation entry points are read-only links to the existing trust surface.
- Trust navigation does not fetch, mutate, repair, or backfill report data.
- Sidebar discoverability remains a link, not a planner or production enablement control.
- Report-aware messaging keeps fallback and diagnostic limitations visible.

Frontend trust navigation does NOT imply frontend launch authorization, planner
authority, execution safety, correctness guarantees, operational readiness,
production enablement, recommendation quality, ranking quality, authorization,
or approval.
