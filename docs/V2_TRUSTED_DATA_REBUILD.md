# EpochForge v2 Trusted Data Rebuild

## Purpose

EpochForge v2 rebuilds the project data foundation around provenance, validation, support status, and debug transparency. The goal is to make every planner-visible mechanic traceable to an accepted source or explicitly marked as partial, text-only, unsupported, experimental, or unknown.

This document covers Phase 0 ground rules only. It does not approve new data contracts, adapters, stat routing, planner changes, crafting changes, or simulation behavior.

## Ground Rules

- Do not introduce new hardcoded gameplay data.
- Do not infer unsupported mechanics from tooltip text.
- Do not treat text-only effects as calculated effects.
- Do not remove working planner behavior without a safe fallback.
- Do not mix stable and experimental mechanics.
- Do not create fake precision.
- Keep stable behavior backward-compatible unless a reviewed phase explicitly changes it.
- Prefer correctness, provenance, validation, and debug transparency over visual polish.
- Preserve current useful behavior when it can be refined safely.

## Support Statuses

| Status | Meaning |
| --- | --- |
| trusted | Fully sourced, validated, and allowed for stable runtime consumption. |
| partial | Some structured evidence exists, but coverage or semantics are incomplete. |
| text_only | Display text exists, but calculated behavior is not supported. |
| unsupported | Known mechanic or source that must not drive calculations. |
| experimental | Isolated research or diagnostic path, not stable planner behavior. |
| unknown | Source or mechanic has not been reviewed enough to classify. |

## Trust Levels

| Trust level | Meaning |
| --- | --- |
| game_extracted | Directly extracted from accepted game data. |
| generated_from_game_data | Derived deterministically from accepted extracted data. |
| manual_bridge | Human-maintained bridge needed for compatibility or translation. |
| inferred | Derived from incomplete evidence and not safe for stable use. |
| placeholder | Temporary scaffold or sample data. |
| deprecated | Known obsolete source retained only for compatibility or audit history. |

## Stable and Experimental Boundaries

Stable planner, crafting, stat aggregation, simulation, and reference routes must continue using their current safe sources until a later reviewed phase approves a replacement. Experimental diagnostics may compare, audit, and report, but they must not mutate production registries or become silent runtime consumers.

## Phase 0 Scope

Phase 0 establishes policy and checkpoint expectations. Phase 1 inventories existing sources. Phase 2 and later contract work must wait for human review of the Phase 1 inventory.
