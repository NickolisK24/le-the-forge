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

## Inspection CLI

The backend includes a developer-only inspection command that loads an explicit export path through the same loader:

```powershell
D:\Forge\le-the-forge\backend\.venv\Scripts\python.exe backend\scripts\inspect_forge_safe_affixes.py --input D:\Forge\last-epoch-data\docs\generated\forge_safe_canonical_affixes.json
```

Machine-readable output:

```powershell
D:\Forge\le-the-forge\backend\.venv\Scripts\python.exe backend\scripts\inspect_forge_safe_affixes.py --input D:\Forge\last-epoch-data\docs\generated\forge_safe_canonical_affixes.json --json
```

The command prints the source path, loaded record count, loader warnings, export policy, export summary metadata, and a small sample of affix IDs/names. It does not modify the export, register data globally, or wire the export into production behavior.

## Debug API

The backend also exposes a disabled-by-default debug endpoint for inspecting the configured export from a running Flask app:

`GET /debug/forge-safe-affixes`

Required configuration:

- `FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED=true`
- `FORGE_SAFE_AFFIX_EXPORT_PATH=D:\Forge\last-epoch-data\docs\generated\forge_safe_canonical_affixes.json`

Example request:

```powershell
Invoke-RestMethod "http://localhost:5050/debug/forge-safe-affixes?limit=5"
```

Optional query parameters:

- `limit`: maximum sample records to return, capped by the backend
- `affix_id`: return a sample for a specific affix ID

The endpoint loads the configured file on demand through `ForgeSafeAffixLoader`; it does not duplicate validation logic and does not auto-load the export at app startup. When the flag is disabled, the endpoint returns a disabled debug response.

This endpoint does NOT power production planner logic, APIs, UI, crafting, simulation, or gameplay behavior. It is read-only and debug-only.

## Frontend Debug Page

Development builds register a matching frontend inspection page:

`/debug/forge-safe-affixes`

The page calls `GET /debug/forge-safe-affixes`, displays the loader summary, warning state, debug/read-only flags, and a limited sample of records. It also supports a `limit` control and an optional affix ID lookup.

This page is available only through the frontend debug route block. It does not fetch from production-facing pages, does not mutate planner state, and does not replace existing affix UI/data.

## Internal Consumption Repository

`backend/data/repositories/forge_safe_affix_repository.py` is the first controlled internal Forge consumption layer for the validated export.

The repository:

- loads through `ForgeSafeAffixLoader`
- keeps loader validation as the single safety gate
- preserves source path, loader warnings, export policy, export status, total seen, excluded count, and loaded count
- supports read-only lookup by affix ID
- supports listing, name/ID search, source-type filtering, and item-type filtering
- returns defensive copies so callers cannot mutate repository state

This repository is not registered globally and is not wired into planner, crafting, simulation, frontend, or production affix behavior. Future consumers must opt into it explicitly behind an experimental/config-controlled boundary.
