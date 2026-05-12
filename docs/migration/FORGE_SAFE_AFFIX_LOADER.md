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

## Forge-Safe Affix Bundle

The preferred controlled consumption artifact is now:

`last-epoch-data/docs/generated/forge_safe_affix_bundle.json`

The bundle pairs Forge-safe affix records with Forge-safe modifier records and includes cross-reference validation. The current finalized bundle reports:

- `export_policy=deterministic_affix_bundle`
- 1098 Forge-safe affixes
- 1624 Forge-safe modifiers
- `cross_reference_validation.status=pass`
- zero unmatched affixes/modifiers
- zero duplicate affix/modifier IDs
- `production_safe=false`

`backend/data/loaders/forge_safe_affix_bundle_loader.py` validates this bundle without using JSON Schema. It requires the bundle export policy, cross-reference pass state, `summary.production_safe=false`, `summary.forge_safe_records_only=true`, `safety.forge_safe=true` on every affix and modifier, and rejects `production_safe=true` anywhere meaningful.

`backend/data/repositories/forge_safe_affix_bundle_repository.py` is the read-only repository over that validated bundle. It supports affix lookup, source identity lookup, modifier lookup by affix, search/filter operations, and summary metadata. It is not registered globally and does not power planner, crafting, simulation, or existing affix behavior.

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

The page calls `GET /experimental/forge-safe-affixes` so it can display the preferred bundle data source, total affix/modifier counts, warning state, modifier counts per affix, and optional modifier detail through `include_modifiers=true`. It also supports a `limit` control and an optional affix ID lookup. The backend endpoint still requires explicit experimental configuration and remains read-only.

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

## Experimental Catalog Endpoint

`GET /experimental/forge-safe-affixes` exposes the repository as a controlled read-only backend data-consumption endpoint.

Required configuration:

- `FORGE_SAFE_AFFIX_CATALOG_ENABLED=true`
- Canonical fallback mode: `FORGE_SAFE_AFFIX_EXPORT_PATH=D:\Forge\last-epoch-data\docs\generated\forge_safe_canonical_affixes.json`
- Preferred bundle mode:
  - `FORGE_SAFE_AFFIX_BUNDLE_ENABLED=true`
  - `FORGE_SAFE_AFFIX_BUNDLE_PATH=D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json`

Example request:

```powershell
Invoke-RestMethod "http://localhost:5050/experimental/forge-safe-affixes?limit=25&q=void"
```

Supported query parameters:

- `limit`
- `offset`
- `q` or `search`
- `affix_id`
- `source_type`
- `item_type`
- `include_modifiers=true` when bundle mode is enabled

When bundle mode is enabled, the endpoint constructs a `ForgeSafeAffixBundleRepository` on request, which loads through `ForgeSafeAffixBundleLoader`. The response includes `data_source=forge_safe_affix_bundle`, `total_affixes`, `total_modifiers`, `bundle_summary`, and `modifier_count` for each affix. With `include_modifiers=true`, each returned affix includes its validated modifier records.

`GET /experimental/forge-safe-affixes/<affix_id>` returns one affix record. In bundle mode it can include the affix modifiers with `include_modifiers=true`.

Example bundle response shape:

```json
{
  "success": true,
  "experimental": true,
  "read_only": true,
  "production_consumer": false,
  "data_source": "forge_safe_affix_bundle",
  "total_affixes": 1098,
  "total_modifiers": 1624,
  "records": [
    {
      "affix_id": 0,
      "affix_name": "Void Penetration",
      "modifier_count": 1
    }
  ]
}
```

If bundle mode is disabled, the endpoint preserves the earlier canonical affix export fallback using `ForgeSafeAffixRepository`.

This endpoint is the controlled Forge-side consumption surface for the finalized Forge-safe affix bundle. It still does not power planner logic, crafting, simulation, gameplay calculations, or existing affix APIs.

## Legacy Comparison Diagnostic

`GET /experimental/forge-safe-affixes/compare-legacy` compares legacy Forge affix data from the same JSON fallback used by `/api/ref/affixes` against the configured Forge-safe affix bundle.

Required configuration:

- `FORGE_SAFE_AFFIX_CATALOG_ENABLED=true`
- `FORGE_SAFE_AFFIX_BUNDLE_ENABLED=true`
- `FORGE_SAFE_AFFIX_BUNDLE_PATH=D:\Forge\last-epoch-data\docs\generated\forge_safe_affix_bundle.json`

Supported query parameters:

- `limit`: maximum records returned in each detail list
- `include_details=true`: reserved in the response metadata for future expanded diagnostics

The diagnostic reports exact `affix_id` matches only. It does not fuzzy-match names, infer stat semantics, normalize gameplay behavior, write files, mutate registries, or authorize migration. Reported differences are migration-planning evidence, not automatic bugs.

The comparison categories are:

- identity and source/category
- slot and item applicability
- tier/value structure and malformed tier signals
- legacy `stat_key` versus bundle modifier/property references
- Forge-safe safety and provenance flags

This endpoint must remain experimental/read-only. It must not be used by production planner, crafting, stat resolution, simulation, or `/api/ref/affixes`; migration requires a separate explicit implementation and test gate.
