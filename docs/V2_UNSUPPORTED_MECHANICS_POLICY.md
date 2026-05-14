# EpochForge v2 Unsupported Mechanics Policy

## Purpose

Unsupported and partially supported mechanics must be explicit. The planner should show what is known, avoid fake precision, and prevent text-only or unvalidated data from becoming calculated behavior.

## Policy

- Unsupported mechanics may be displayed with clear status, but must not affect calculations.
- Text-only effects remain `text_only` until structured source data proves calculation semantics.
- Unknown mechanics remain `unknown` until reviewed.
- Partial mechanics may be included only where the supported subset is clear and the unsupported portion is visible.
- Experimental mechanics must remain isolated from stable planner, crafting, stat aggregation, simulation, and reference routes.
- Tooltip text can support user-facing explanation, but it is not sufficient evidence for formulas, scaling, triggering, stacking, or conditional behavior.

## Required Metadata

Every reviewed mechanic or data source should carry:

- source path
- support status
- trust level
- provenance note
- validation state
- stable or experimental scope
- known unsupported behavior

## Handling Incomplete Mechanics

Incomplete mechanics should prefer one of these outcomes:

- `text_only` for display-only effects.
- `partial` for a reviewed subset with visible limitations.
- `unsupported` for known blocked mechanics.
- `experimental` for isolated diagnostics or prototypes.
- `unknown` when evidence is insufficient.

## Runtime Safety

Stable runtime paths must not silently consume unsupported, text-only, placeholder, fallback, debug/demo, or unknown data as trusted calculations. If a current implementation is useful but not fully trusted, keep it behind the existing behavior path until a reviewed v2 replacement is ready.
