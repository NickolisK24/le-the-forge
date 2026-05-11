# Forge-safe Affix Loader and Controlled Consumption

The Forge-safe canonical affix export is now available as a controlled internal catalog data source. It is intentionally read-only and does **not** replace planner, crafting, or simulation behavior by default.

## Export contract

* Export path: `FORGE_SAFE_AFFIX_EXPORT_PATH`.
* Accepted records must include `safety.forge_safe=true`.
* Records with `production_safe=true` are rejected with a clean loader error.
* Missing mappings are not inferred.
* Gameplay behavior is not inferred from tooltip text.
* Endpoint payloads always expose `production_consumer=false`.

## Backend components

* Loader: `backend/data/loaders/forge_safe_affixes_loader.py`
* Repository: `backend/data/repositories/forge_safe_affix_repository.py`
* Service: `backend/app/services/affix_catalog_service.py`
* Routes: `backend/app/routes/affixes.py`
* Comparison tool: `backend/scripts/compare_forge_safe_affixes.py`

`AffixCatalogService` chooses between the legacy registry and the Forge-safe repository. It does not mutate `app.extensions["affix_registry"]` or any global affix registry.

## Environment variables and modes

```env
FORGE_SAFE_AFFIX_CATALOG_ENABLED=false
FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=false
FORGE_SAFE_AFFIX_EXPORT_PATH=D:\Forge\last-epoch-data\docs\generated\forge_safe_canonical_affixes.json
FORGE_SAFE_AFFIX_CONSUMPTION_MODE=shadow
```

Modes:

* `shadow`: load/compare only; stable catalog endpoints remain unavailable to users.
* `read_only`: stable catalog endpoints and the development UI can browse the Forge-safe export. No planner/crafting/simulation usage.
* `active`: allowed as the source for affix catalog browsing only. Planner/crafting/simulation still require a separate dedicated migration flag before they can consume Forge-safe affixes.

Default is disabled + `shadow`.

## Stable catalog endpoints

All stable endpoints are feature-gated by `FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=true` and require mode `read_only` or `active`.

* `GET /api/affixes/catalog`
  * Query params: `limit`, `offset`, `q`/`query`, `source_type`, `item_type`.
  * Returns paginated catalog records and metadata including `data_source`.
* `GET /api/affixes/catalog/{affix_id}`
  * Returns one catalog record or a clean 404.
* `GET /api/affixes/catalog/summary`
  * Returns active source, mode, legacy count, Forge-safe count, and safe metadata.

The existing experimental endpoint is preserved under the affix route namespace:

* `GET /api/affixes/experimental/forge-safe-affixes`

## Frontend route

* Route/page: `/affix-catalog`
* Page component: `frontend/src/components/features/affixCatalog/AffixCatalogPage.tsx`
* Frontend gate: `VITE_FORGE_SAFE_AFFIX_CATALOG_ENABLED=true` or Vite development mode.

The page shows the Forge-safe count, data source label, search, `source_type` filtering, `item_type` filtering, and selected affix detail. It does not feed planner/crafting selections.

## Shadow comparison tooling

Run:

```bash
cd backend
python scripts/compare_forge_safe_affixes.py --export-path "D:\Forge\last-epoch-data\docs\generated\forge_safe_canonical_affixes.json"
```

The report includes:

* Forge-safe affixes not in legacy.
* Legacy affixes not in Forge-safe.
* Matching IDs.
* Name mismatches.
* Source/type mismatches.
* Item-type mismatches.
* Total counts.

## Rollback plan

1. Set `FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=false`.
2. Set `FORGE_SAFE_AFFIX_CATALOG_ENABLED=false` if the experimental endpoint should also be hidden.
3. Leave `FORGE_SAFE_AFFIX_EXPORT_PATH` unset or remove the file mount.
4. Restart backend and frontend processes.

Because the implementation does not mutate legacy registries and does not wire into planner/crafting/simulation, rollback is configuration-only.

## Not yet migrated

Planner, crafting, simulation, BIS generation, and stat aggregation continue to use the existing legacy systems. Migrating any of those consumers must be done separately behind a dedicated feature flag with focused tests.
