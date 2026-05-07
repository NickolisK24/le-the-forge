# LE Tools Import Context Dry Run

## Purpose

This developer-only diagnostic checks whether LE Tools import-like gear records carry enough `base_type_id` context to resolve canonical bundle `item_type` IDs through the existing dry-run resolver.

It does not change LE Tools importer output, production import behavior, bundle files, frontend behavior, API behavior, or simulation behavior. It reports context availability only.

## Commands

From `D:\Forge\le-the-forge\backend`:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py
```

JSON output:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py --json
```

Fixture input:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py --fixture path\to\sample_import_payload.json
```

`--sample-json` is accepted as an alias for `--fixture`.

Output file:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py --output ..\docs\generated\le_tools_import_context_report.md
```

The command writes only when `--output` is provided and refuses production data directories such as `data/items`.

## Representative Fixture

A representative developer-only parsed gear fixture lives at:

```text
backend/tests/fixtures/le_tools_parsed_gear_context_sample.json
```

Run it with:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py --fixture tests\fixtures\le_tools_parsed_gear_context_sample.json
```

JSON:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py --fixture tests\fixtures\le_tools_parsed_gear_context_sample.json --json
```

Generated report:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_context.py --fixture tests\fixtures\le_tools_parsed_gear_context_sample.json --output ..\docs\generated\le_tools_import_context_fixture_report.md
```

Expected fixture summary:

- `resolved`: 10
- `needs_context`: 3
- `needs_review`: 1
- `deferred`: 0
- `unresolved`: 2

The fixture proves that base-type-backed parsed gear records can resolve through the existing developer-only dry-run resolver, including collapsed weapon and idol groups when `baseTypeID` is present. It also proves that missing `baseTypeID`, subtype-only records, name-only records, `spear`, and unknown item types do not silently resolve.

It does not prove production importer compatibility, change importer output, or make any mapping production-safe.

## Offline BuildInfo Fixture

A synthetic offline LET `buildInfo`-style fixture lives at:

```text
backend/tests/fixtures/le_tools_offline_buildinfo_equipment_sample.json
```

It is used by:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_le_tools_importer_fixture_context.py -q
```

The test maps the fixture through the existing importer path, copies the mapped gear into a diagnostic-only context shape, and then runs the context report. The copy is needed because production importer output preserves `base_type_id` but does not expose raw `item_type`; the test reads `_raw.item_type` only for diagnostics and asserts importer output is unchanged.

Generated report:

```text
docs/generated/le_tools_offline_buildinfo_context_report.md
```

Expected summary:

- `resolved`: 10
- `needs_context`: 2
- `needs_review`: 1
- `deferred`: 0
- `unresolved`: 1
- `production_safe`: false

## Stage Context Comparison

The raw-stage versus mapped-output comparison uses:

```text
backend/tests/fixtures/le_tools_offline_buildinfo_stage_context_sample.json
```

Command:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_stage_context.py
```

JSON:

```powershell
.\.venv\Scripts\python.exe scripts\report_le_tools_import_stage_context.py --json
```

Generated report:

```text
docs/generated/le_tools_import_stage_context_report.md
```

This report compares raw fixture equipment records to the current mapped importer output. It shows that mapped output preserves `base_type_id`, but does not expose item type context, so any future non-production diagnostic consumer would need explicit context threading rather than relying on production mapped gear alone.

## Sidecar Builder

The sidecar builder creates a single developer-only diagnostic object with raw, mapped, resolver, and context sections:

```powershell
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py
```

JSON:

```powershell
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py --json
```

Output:

```powershell
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py --output D:\Forge\le-the-forge\docs\generated\le_tools_import_context_sidecar_report.md
```

The sidecar remains developer-only, does not change importer output, and keeps `production_safe=false` globally and per item.

Validate the current sidecar:

```powershell
.\.venv\Scripts\python.exe scripts\validate_le_tools_import_context_sidecar.py --build-current
```

Validation report:

```text
docs/generated/le_tools_import_context_sidecar_validation_report.md
```

`warning` is the expected current status. `failed` blocks any future non-production consumer work.

## Built-In Sample

When no fixture is provided, the command runs a small built-in sample:

- `helm` with `baseTypeID=0`, expected to resolve to bundle `helmet`
- `axe` without `base_type_id`, expected to return `needs_context`
- `idol_1x1` without `base_type_id`, expected to return `needs_context`
- `spear` with `baseTypeID=14`, expected to return `needs_review`
- `unknown_type`, expected to return `unresolved`

## Statuses

- `resolved`: reviewed mapping resolved with required context
- `needs_context`: item type is known or collapsed, but `base_type_id` is missing or mismatched
- `needs_review`: item type is intentionally blocked from resolution pending review
- `deferred`: item type is outside the current migration scope
- `unresolved`: no reviewed mapping exists

## Safety Rules

`base_type_id` is required because Forge slugs such as `axe`, `mace`, `sword`, and `idol_1x1` collapse multiple bundle item types. `subtype_id` alone is forbidden because subtype IDs are scoped under base type IDs and are not globally unique.

The report never uses name-only matching, never treats `subtype_id` alone as sufficient, and keeps `production_safe=false` globally and per item.

Before any production importer migration, a separate migration step must define payload shape, fallback behavior, tests, and a production-safe adapter strategy. This dry run is only a context measurement tool.
