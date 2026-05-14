# EpochForge v2 Ship Criteria

## Purpose

This document defines the minimum acceptance criteria for shipping trusted data infrastructure changes. It is a policy checklist, not a migration approval.

## Required Before Stable Consumption

- Every stable data source has source path, provenance, support status, trust level, schema version, and validation result.
- Every calculated mechanic is backed by structured source data or is explicitly blocked.
- Text-only mechanics remain display-only unless later reviewed evidence supports calculation.
- Stable runtime paths preserve backward-compatible behavior or provide a reviewed fallback.
- Experimental diagnostics are isolated from stable planner, crafting, stat aggregation, simulation, and reference routes.
- Generated artifacts include enough metadata to identify source reports, read-only status, and production safety.
- Validation failures are visible in reports or debug output, not silently swallowed.

## Required Before Replacing Existing Runtime Data

- A source inventory entry exists for the old source and the proposed replacement.
- Contract fields and support statuses are reviewed.
- Fixture, fallback, debug/demo, and sample data are excluded from stable consumption.
- Tests cover the compatibility path and the new trusted path.
- Rollback behavior is documented.

## Required Before Planner or Simulation Changes

- Stat routing changes are isolated behind a reviewed gate.
- Value scale and polarity handling are validated by structured evidence.
- Slot, item type, class, and category applicability are normalized by policy.
- Unsupported and text-only mechanics are visible to users without affecting calculations.
- Existing useful planner behavior remains available unless a reviewed replacement is complete.

## Non-Shipping Conditions

- A mechanic depends on tooltip interpretation only.
- A value uses guessed scale or guessed precision.
- A manual mapping lacks provenance or migration rationale.
- A fallback source is consumed as trusted data.
- Experimental data affects stable output.
- Tests pass only because fixtures encode unreviewed runtime assumptions.
