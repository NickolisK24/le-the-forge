# LE Tools Import Context Sidecar Design

## 1. Purpose

This document defines a future developer-only sidecar shape for LE Tools import diagnostics.

The sidecar is not production importer output, does not activate bundle IDs, and does not change user-facing import behavior. It exists to preserve raw/source item type context through importer stages so diagnostics can explain whether canonical bundle `item_type` IDs could be resolved safely.

## 2. Problem Statement

Current raw-stage versus mapped-output diagnostics show:

| Metric | Count |
| --- | ---: |
| total_items | 12 |
| raw_with_base_type_id | 9 |
| mapped_with_base_type_id | 9 |
| raw_missing_base_type_id | 3 |
| mapped_missing_item_type | 12 |
| needs_test_only_pairing | 11 |
| raw_with_subtype_only | 1 |
| resolved | 8 |
| needs_context | 2 |
| needs_review | 1 |
| unresolved | 1 |

The current importer path can preserve `base_type_id` from raw/source stage into mapped gear output for ID-backed records. However, mapped output does not expose enough item type context for resolver diagnostics. Current tests therefore need index-based pairing between raw fixture records and mapped gear records.

That matters because collapsed Forge item type slugs such as `axe`, `mace`, `sword`, and `idol_1x1` require `base_type_id` context. `subtype_id` alone is unsafe because subtype IDs are scoped under base type IDs. Name-only matching is also unsafe. Canonical bundle `item_type` IDs should not be consumed without explicit context.

Future diagnostics need an explicit sidecar instead of implicit test-only pairing.

## 3. Non-Goals

- Do not change production import output.
- Do not expose the sidecar in public API responses.
- Do not feed the sidecar into simulation.
- Do not use the sidecar for production item resolution.
- Do not mark the sidecar `production_safe=true`.
- Do not resolve `base_items` by name.
- Do not use `subtype_id` alone.
- Do not infer missing context from prose or item names.

## 4. Proposed Sidecar Shape

Proposed diagnostic shape:

```json
{
  "production_safe": false,
  "source": "le_tools_import_diagnostic",
  "importer": "lastepochtools",
  "build_id": "string or null",
  "generated_at": "ISO-8601 timestamp",
  "items": [
    {
      "index": 0,
      "slot": "helm",
      "raw": {
        "item_type": "helm",
        "base_type_id": 0,
        "subtype_id": 0,
        "name": "string or null",
        "source_item_id": "string or number or null"
      },
      "mapped": {
        "slot": "helmet",
        "base_type_id": 0,
        "subtype_id": 0,
        "has_item_type": false,
        "mapped_item_id": "string or null",
        "mapped_name": "string or null"
      },
      "resolver": {
        "status": "resolved | needs_context | needs_review | deferred | unresolved",
        "bundle_item_type_id": "helmet or null",
        "match_source": "accepted_direct | adapter_translation | none",
        "production_safe": false,
        "warnings": [],
        "notes": []
      },
      "context": {
        "has_base_type_id": true,
        "has_subtype_id": true,
        "subtype_only": false,
        "has_raw_item_type_signal": true,
        "requires_test_pairing": false
      }
    }
  ],
  "summary": {
    "total_items": 0,
    "resolved": 0,
    "needs_context": 0,
    "needs_review": 0,
    "deferred": 0,
    "unresolved": 0,
    "raw_with_base_type_id": 0,
    "mapped_with_base_type_id": 0,
    "mapped_missing_item_type": 0
  }
}
```

This is a proposed diagnostic object, not an implemented API or production payload.

## 5. Field Definitions

| Field | Definition |
| --- | --- |
| `production_safe` | Always `false`. The sidecar is diagnostic-only. |
| `source` | Diagnostic source identifier, for example `le_tools_import_diagnostic`. |
| `importer` | Importer name, expected to be `lastepochtools` for this sidecar. |
| `build_id` | Optional local import/build identifier if available. Use `null` when unavailable. |
| `generated_at` | ISO-8601 timestamp for the diagnostic sidecar. |
| `items` | Ordered list of per-item diagnostic records. |
| `items[].index` | Stable item index in the inspected import payload. |
| `items[].slot` | Raw or mapped slot label used for display and diagnostics. |
| `items[].raw.item_type` | Optional raw/source item type signal. May come from source parser stage only. |
| `items[].raw.base_type_id` | Raw/source base type ID where present. Required context for collapsed item type resolution. |
| `items[].raw.subtype_id` | Raw/source subtype ID where present. Preserved for diagnostics but never sufficient by itself. |
| `items[].raw.name` | Optional raw/source item name. Must not be used for authoritative resolution. |
| `items[].raw.source_item_id` | Optional raw source item ID or encoded item ID. |
| `items[].mapped.slot` | Slot after current importer mapping. |
| `items[].mapped.base_type_id` | `base_type_id` preserved by current mapped gear output where available. |
| `items[].mapped.subtype_id` | Mapped subtype ID if a future diagnostic path exposes it. |
| `items[].mapped.has_item_type` | Whether mapped output exposes item type context. Currently expected to be `false`. |
| `items[].mapped.mapped_item_id` | Optional mapped item identifier if exposed in a future diagnostic path. |
| `items[].mapped.mapped_name` | Optional mapped item/base name. Diagnostic only. |
| `items[].resolver.status` | Result from the developer-only dry-run resolver. |
| `items[].resolver.bundle_item_type_id` | Resolved bundle item type ID, or `null`. |
| `items[].resolver.match_source` | Dry-run match source, such as `accepted_direct`, `adapter_translation`, or `none`. |
| `items[].resolver.production_safe` | Always `false`. |
| `items[].resolver.warnings` | Warnings explaining missing or ambiguous context. |
| `items[].resolver.notes` | Notes explaining match source or blocked status. |
| `items[].context.has_base_type_id` | Whether either raw or mapped stage has base type ID context. |
| `items[].context.has_subtype_id` | Whether subtype ID is present. |
| `items[].context.subtype_only` | `true` only when subtype exists without base type ID. Such records must not resolve. |
| `items[].context.has_raw_item_type_signal` | Whether raw/source stage has a usable item type signal. |
| `items[].context.requires_test_pairing` | Whether raw and mapped records had to be paired externally for diagnostics. |
| `summary` | Counts derived from `items`, resolver statuses, and stage context. |

## 6. Creation Point Options

### A. Developer-Only Wrapper Around The Importer

Pros:

- Keeps production importer output unchanged.
- Can call existing importer behavior and inspect copied output.
- Easy to make CLI/test-only.
- Can explicitly pair raw and mapped records without leaking sidecar data to users.

Cons:

- Requires careful handling to avoid relying on fragile index pairing.
- May need fixture-specific adapters until real LET payload shape is confirmed.

Risk: Low, if isolated under developer-only modules/scripts.

### B. Test-Only Diagnostic Helpers

Pros:

- Lowest production risk.
- Good for locking assumptions before implementation.
- No CLI or route exposure.

Cons:

- Less useful for ad hoc developer diagnostics.
- Does not produce reusable reports unless paired with a script later.

Risk: Very low.

### C. Backend Script Calling Importer Internals

Pros:

- Useful for repeatable local diagnostics.
- Can generate reports under `docs/generated`.
- Can remain outside production imports and routes.

Cons:

- Calls importer internals, so it must avoid accidental assumptions about production behavior.
- Needs explicit no-network/offline fixture handling.

Risk: Low to medium, depending on script scope.

### D. Importer Diagnostic Flag

Pros:

- Could capture raw/mapped context at the exact parse point.
- Avoids index pairing if implemented carefully.

Cons:

- Higher risk because it touches production importer code.
- Requires strict guarantees that default output and behavior are unchanged.
- More likely to be mistaken for a production feature.

Risk: Medium.

Recommendation: start with option A or C: a developer-only wrapper or script that calls existing importer behavior, copies mapped output, and builds the sidecar externally. Do not add an importer diagnostic flag until wrapper limitations are proven.

## 7. Safety Rules

- The sidecar must never be returned by production import endpoints.
- The sidecar must never be used by production loaders.
- The sidecar must never set `production_safe=true`.
- The sidecar must never infer missing `base_type_id`.
- The sidecar must never use `subtype_id` alone.
- The sidecar must never resolve name-only items.
- The sidecar must preserve warnings for collapsed slugs missing `base_type_id`.
- The sidecar must not mutate importer output.
- The sidecar must not require network access.
- The sidecar must not write bundle files or production data.

## 8. Validation Rules

Future sidecar validation should check:

- Top-level `production_safe=false`.
- Every item has `resolver.production_safe=false`.
- Every item has `index` and `slot`.
- `base_type_id` values are numbers or `null`.
- `subtype_id` values are numbers or `null`.
- `subtype_only=true` records never resolve.
- Name-only records never resolve.
- `spear` remains `needs_review` or `unresolved`.
- Collapsed slugs missing `base_type_id` return `needs_context`.
- Summary counts match item statuses.
- No production output shape changes.

## 9. Test Requirements Before Implementation

Implementation tests should prove:

- Sidecar builder preserves production importer output unchanged.
- Sidecar builder detects raw `baseTypeID`.
- Sidecar builder detects mapped `base_type_id`.
- Sidecar builder flags `mapped_missing_item_type`.
- Sidecar builder calls the existing dry-run resolver.
- Sidecar builder marks `production_safe=false`.
- Sidecar builder reports missing context.
- Sidecar builder does not use `subtype_id` alone.
- Sidecar builder does not resolve name-only records.
- Sidecar builder handles `spear` and unknown item types safely.
- No network calls are made.

## 10. Relationship To Existing Diagnostics

The sidecar would consolidate context currently spread across:

- Dry-run resolver: produces `resolved`, `needs_context`, `needs_review`, `deferred`, or `unresolved`.
- Adapter translation fixture: defines reviewed slug/base type translations.
- Context coverage report: shows how many current Forge item type inputs have `base_type_id`.
- LE Tools import context dry-run report: checks fixture-like item records.
- Stage context report: compares raw fixture records to mapped importer output using test-only pairing.

The sidecar should become the single diagnostic object that carries raw context, mapped context, resolver output, warnings, and summary counts.

## 11. Recommended Implementation Order Later

1. Implement sidecar builder as a developer-only module.
2. Add tests proving importer output remains unchanged.
3. Add CLI report for sidecar generation from the offline fixture.
4. Generate sidecar report under `docs/generated`.
5. Run resolver diagnostics through the sidecar.
6. Only after that, consider a non-production consumer.

## 12. Open Questions

- Should the sidecar live only in diagnostics/tests, or behind an explicit debug flag?
- Should the sidecar include raw source item ID?
- Should the sidecar include mapped Forge item ID?
- Should the sidecar include build/import ID?
- How should old imports without `base_type_id` be represented?
- What is the first non-production consumer that would use the sidecar?
- How should a future live LET capture be stored safely?
- Should the sidecar eventually become an internal debug API, or stay CLI-only?

## 13. Initial Developer Implementation

The initial developer-only sidecar builder now lives at:

```text
backend/app/game_data/le_tools_import_context_sidecar.py
```

CLI:

```powershell
cd D:\Forge\le-the-forge\backend
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py
```

JSON:

```powershell
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py --json
```

Generated report:

```powershell
.\.venv\Scripts\python.exe scripts\build_le_tools_import_context_sidecar.py --output D:\Forge\le-the-forge\docs\generated\le_tools_import_context_sidecar_report.md
```

The implementation remains developer-only. It builds from the offline stage fixture, copies mapped importer output, pairs raw and mapped records for diagnostics, runs the existing dry-run resolver, validates sidecar safety rules, and keeps `production_safe=false`.

Current summary:

| Metric | Count |
| --- | ---: |
| total_items | 12 |
| resolved | 8 |
| needs_context | 2 |
| needs_review | 1 |
| deferred | 0 |
| unresolved | 1 |
| raw_with_base_type_id | 9 |
| mapped_with_base_type_id | 9 |
| mapped_missing_item_type | 12 |
| requires_test_pairing | 11 |
| raw_with_subtype_only | 1 |
