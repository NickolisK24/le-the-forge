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
