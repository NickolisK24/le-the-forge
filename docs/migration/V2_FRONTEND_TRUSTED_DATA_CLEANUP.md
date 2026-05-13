# V2 Frontend Trusted Data Cleanup

## Purpose

This cleanup standardizes how frontend debug pages consume the experimental v2 trusted-data API envelope finalized in Phase 12.

The work is limited to debug and inspection surfaces. It does not route v2 data into planner calculations, crafting, simulation, or production stat aggregation.

## Pages Reviewed

- `/debug/forge-safe-affixes`
- `/debug/v2-items`
- `/debug/v2-unique-sets`
- `/debug/v2-idols`
- `/debug/v2-classes`
- `/debug/v2-passives`
- `/debug/v2-skills`

No production planner pages were changed.

## Envelope Helpers Added

Frontend debug pages now share helpers for reading the standardized v2 API envelope:

- `data`
- `meta`
- `support_summary`
- `warnings`
- `provenance`
- `debug`

The helpers also preserve compatibility with existing legacy debug fields:

- `records`
- `sample_records`
- `summary`
- `debug_summary`
- `source_path`
- string-based `error` responses

## UI Behavior

Debug pages continue to render their existing tables and summaries. They now also expose shared panels for:

- support status summary
- provenance/source metadata
- debug contract metadata

Unsupported, partial, unknown, audit-only, and non-stable-calculable states remain visible. The UI does not imply planner readiness unless the backend response reports stable-calculable support.

## Compatibility Behavior

The frontend accepts both Phase 12 envelopes and earlier route-specific payloads. Record extraction prefers legacy top-level fields first when present, then falls back to envelope `data` fields.

Error rendering accepts both legacy string errors and standardized structured errors.

## Backend Changes

No backend files were changed in this cleanup. The Phase 12 response contract remains the source of truth.

## Tests

Focused frontend tests cover:

- envelope record extraction
- legacy top-level compatibility
- support summary extraction
- source/provenance fallback behavior
- string and structured error handling
- debug page rendering with the shared envelope panels

## Remaining Frontend Gaps

- The debug panels intentionally show compact key/value summaries rather than a full expandable JSON inspector.
- Stats and modifiers do not yet have a dedicated frontend debug page in this cleanup.
- Stable planner consumption remains intentionally blocked until later planner remap phases.

## Runtime Behavior

Production behavior was not changed.

Planner, crafting, stat aggregation, simulation, and production routes do not consume v2 trusted-data APIs as part of this cleanup.
