# Bundle Item Diff Diagnostic

This diagnostic compares the `last-epoch-data` bundle families `item_types` and `base_items` against current Forge item/static data sources.

It is read-only. It does not replace production loaders, change simulation math, mutate game data, update the database, start services, or write to the bundle. Its purpose is to measure drift and migration risk before any Forge-side item loader migration.

## Run

From the backend directory:

```powershell
cd D:\Forge\le-the-forge\backend
.\.venv\Scripts\python.exe scripts\diff_bundle_items.py --bundle-dir D:\Forge\last-epoch-data\data_bundle
```

JSON output:

```powershell
.\.venv\Scripts\python.exe scripts\diff_bundle_items.py --bundle-dir D:\Forge\last-epoch-data\data_bundle --json
```

You can also set the bundle path with:

```powershell
$env:FORGE_DATA_BUNDLE_DIR = "D:\Forge\last-epoch-data\data_bundle"
.\.venv\Scripts\python.exe scripts\diff_bundle_items.py
```

If neither `--bundle-dir` nor `FORGE_DATA_BUNDLE_DIR` is set, the command uses:

```text
D:\Forge\last-epoch-data\data_bundle
```

## Status

`PASS` means the diagnostic found no structural problems or drift warnings in comparable fields.

`WARN` means the bundle can be inspected, but there is migration risk: missing comparable Forge source data, approximate name-only matching, static fallback data, count drift, or fields that need an adapter.

`FAIL` means the diagnostic found a structural issue that would make migration unsafe, such as a missing bundle family file, invalid JSON, duplicate bundle IDs, or duplicate bundle `base_type_id`/`subtype_id` composite keys.

## Comparison Limits

Current Forge data is not shaped like the new bundle families.

- Bundle `item_types` has game/base type IDs and generated slugs.
- Current Forge item type data has curated static slugs and slots.
- Bundle `base_items` uses composite identity from `base_type_id` and `subtype_id`.
- Current Forge `data/items/base_items.json` does not expose `base_type_id` or `subtype_id`.

Because of that, name-only matching is reported as approximate and must not be treated as authoritative proof of compatibility.

## Subtype Identity

`subtype_id` is scoped by `base_type_id`. It must not be used alone as a canonical base item key.

The diagnostic checks for subtype-only Forge mappings and reports them as migration risk when present. A safe future consumer should carry both `base_type_id` and `subtype_id`, or use a bundle canonical ID derived from both.

## Expected Current Outcome

The current bundle is expected to produce `WARN`, not `PASS`.

That is expected because:

- `item_types` and `base_items` are newly generated bundle families.
- Current Forge item data uses older static/curated shapes.
- Current Forge base item data is much smaller and lacks composite game IDs.
- Forge production loaders are not migrated yet.
- Implicit refs in the bundle are references only, not resolved mechanics.

## How This Informs Migration

Use this diagnostic before any loader migration to decide:

- what adapter map is needed between Forge static slugs and bundle item type IDs
- whether base item consumers can accept composite IDs
- which current Forge base items are missing from the bundle by normalized name
- which bundle records current Forge does not represent
- whether any production path still risks treating `subtype_id` as globally unique

The next safe step is a developer-only adapter/diff layer that maps current Forge item type slugs to bundle `base_type_id` records without changing production loader behavior.
