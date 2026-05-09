# Forge-Safe Affix Loader

## Purpose

`backend/data/loaders/forge_safe_affixes_loader.py` is a controlled loader for the `last-epoch-data` Forge-safe canonical affix export.

This is an ingestion boundary only. It does not replace existing Forge affix systems, planner behavior, crafting behavior, simulation behavior, API responses, or frontend behavior.

## Input

The expected external artifact is:

`last-epoch-data/docs/generated/forge_safe_canonical_affixes.json`

The loader accepts an explicit JSON path. The artifact is not wired into production data loading by default.

## Safety Rules

The loader:

- accepts only records with `safety.forge_safe=true`
- rejects records with `production_safe=true`
- rejects top-level or summary `production_safe=true`
- requires `affix_id`, `source_type`, and `safety` metadata
- rejects duplicate `affix_id` values
- reports summary count drift as a warning

The loader does not infer missing modifier mappings, gameplay behavior, or special behavior from text. It only validates and returns the exported records that already passed the `last-epoch-data` export gates.

## Current Boundary

This loader is experimental and controlled. It is safe for tests and explicit developer tooling, but it is not a production consumer. Existing Forge data, planner behavior, build math, crafting, and simulation remain unchanged.
