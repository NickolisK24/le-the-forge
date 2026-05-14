# Sidecar-Backed Item Diagnostic Consumer Design

This document designs the first non-production diagnostic consumer after the bundle item migration diagnostic milestone.

The initial CLI-only consumer has been implemented as developer-only diagnostic tooling. It does not change production loaders, change importer output, expose new API/frontend behavior, alter simulation behavior, or mark any result `production_safe=true`.

## 1. Purpose

The proposed consumer reads saved LET import context sidecar diagnostics and reports canonical bundle item type resolver results in a developer-only workflow.

The consumer must:

- Consume saved sidecar diagnostics only.
- Use `backend/tests/fixtures/le_tools_import_context_sidecar_current.json` as the first input artifact.
- Validate the sidecar before reporting.
- Avoid live importer output.
- Avoid production loaders.
- Avoid public API and frontend behavior.
- Preserve `production_safe=false` globally and per record.

This is the first proposed non-production consumer because the diagnostic milestone has already proven the bundle item mapping chain, sidecar builder, sidecar validator, and saved sidecar artifact validation. The consumer should prove that a downstream tool can safely consume validated diagnostics without becoming production behavior.

## 2. Why This Consumer Comes First

The saved sidecar artifact is the safest available input because it separates diagnostics from production importer behavior.

Reasons this consumer should come before any live importer or production loader migration:

- The saved sidecar fixture already validates with warning status and no errors.
- The fixture is explicit, offline, and developer-only.
- The sidecar preserves raw, mapped, resolver, and context sections together.
- The consumer can exercise resolver output without calling the importer.
- The consumer can prove report behavior before any production or live data dependency exists.
- The consumer can keep all warning labels visible instead of silently falling back.
- The consumer can fail closed when sidecar validation errors are present.

This step is about proving diagnostic consumption, not proving production readiness.

## 3. Input Contract

Initial input:

```text
backend/tests/fixtures/le_tools_import_context_sidecar_current.json
```

Expected top-level fields:

| Field | Requirement |
| --- | --- |
| `production_safe` | Must be `false`. |
| `source` | Identifies the sidecar source, currently synthetic/offline diagnostics. |
| `importer` | Expected to identify the LET importer context. |
| `build_id` | May be `null`. |
| `generated_at` | Timestamp from sidecar generation. |
| `items` | Required list of per-item diagnostics. |
| `summary` | Required status and context count summary. |

Expected per-item fields:

| Section | Required Fields / Meaning |
| --- | --- |
| `raw` | Raw/source context such as `item_type`, `base_type_id`, `subtype_id`, `name`, and `source_item_id`. |
| `mapped` | Mapped importer-output context such as `slot`, `base_type_id`, `subtype_id`, `has_item_type`, `mapped_item_id`, and `mapped_name`. |
| `resolver` | Dry-run resolver result: `status`, `bundle_item_type_id`, `match_source`, `production_safe`, `warnings`, and `notes`. |
| `context` | Context flags such as `has_base_type_id`, `has_subtype_id`, `subtype_only`, `has_raw_item_type_signal`, and `requires_test_pairing`. |

Validation requirement:

- The consumer must run the existing sidecar validator before consuming records.
- Validation errors must block consumption.
- Warning-only validation may continue, but the report must clearly label the warning state.

The first implementation should not accept live importer output as input.

## 4. Output Contract

The consumer should produce a developer-only report, likely through a CLI.

Default human-readable output should include:

- Sidecar path.
- Validation status.
- Validation warnings and errors.
- `production_safe=false` confirmation.
- Total records.
- Resolved count.
- `needs_context` count.
- `needs_review` count.
- Deferred count.
- Unresolved count.
- Blocked records.
- Resolved `bundle_item_type_id` values.
- Records requiring `base_type_id`.
- Records that cannot resolve.
- Records requiring manual review, including `spear`.
- Records with subtype-only or name-only context that remain unresolved.

Optional JSON output should include the same information in a serializable shape, for example:

```json
{
  "production_safe": false,
  "sidecar_path": "tests/fixtures/le_tools_import_context_sidecar_current.json",
  "validation_status": "warning",
  "errors": [],
  "warnings": [],
  "summary": {
    "total_items": 12,
    "resolved": 8,
    "needs_context": 2,
    "needs_review": 1,
    "deferred": 0,
    "unresolved": 1
  },
  "records": [
    {
      "index": 0,
      "slot": "helm",
      "resolver_status": "resolved",
      "bundle_item_type_id": "helmet",
      "match_source": "adapter_translation",
      "production_safe": false,
      "warnings": [],
      "notes": []
    }
  ],
  "blocked_records": [],
  "recommendations": []
}
```

The output is diagnostic-only. It must not be used as production data or API response data.

## 5. Consumer Behavior

Required behavior:

- Read a sidecar JSON file from a supplied `--sidecar` path.
- Default to no implicit live importer calls.
- Validate the sidecar before building a report.
- Refuse to continue if validation errors exist.
- Continue with warning status when the validator returns warning without errors.
- Never mutate the sidecar input.
- Never call the production importer.
- Never call frontend or backend API routes.
- Never write unless `--output` is explicitly provided.
- Refuse output paths inside production data directories such as `data/items`.
- Preserve `production_safe=false`.
- Clearly label synthetic/offline fixture warnings.

The consumer should treat the saved sidecar as immutable diagnostic input. If a future implementation needs fresh sidecar output, that should remain a separate builder step.

## 6. Safety Rules

The consumer must enforce or preserve these rules:

- No production loader imports.
- No public API exposure.
- No frontend exposure.
- No production item resolution.
- No fallback guessing.
- No `subtype_id`-only resolution.
- No name-only resolution.
- No `base_items` migration by name.
- `spear` remains blocked as `needs_review` or unresolved.
- Collapsed groups without `base_type_id` remain `needs_context`.
- `production_safe` remains `false` globally and per record.
- Warning-only diagnostics remain visibly warning-only.

If any input attempts to mark `production_safe=true`, the validator should fail before the consumer reports results.

## 7. Proposed CLI

Implemented script:

```text
backend/scripts/consume_le_tools_sidecar_diagnostic.py
```

Human-readable command:

```powershell
cd D:\Forge\le-the-forge\backend
.\.venv\Scripts\python.exe scripts\consume_le_tools_sidecar_diagnostic.py --sidecar tests\fixtures\le_tools_import_context_sidecar_current.json
```

JSON output:

```powershell
.\.venv\Scripts\python.exe scripts\consume_le_tools_sidecar_diagnostic.py --sidecar tests\fixtures\le_tools_import_context_sidecar_current.json --json
```

Explicit output file:

```powershell
.\.venv\Scripts\python.exe scripts\consume_le_tools_sidecar_diagnostic.py --sidecar tests\fixtures\le_tools_import_context_sidecar_current.json --output ..\docs\generated\le_tools_sidecar_diagnostic_consumer_report.md
```

Exit behavior:

- Exit `0` when the sidecar is valid or warning-only and the report is produced.
- Exit `1` when the sidecar is missing, malformed, fails validation, or an output path is unsafe.

The CLI is developer-only and must not be imported by production loaders or routes.

## 8. Tests Required

The implementation includes focused tests before the consumer is considered usable.

Required tests:

- Valid saved sidecar produces a report.
- Warning-only sidecar is allowed but labeled.
- Sidecar validation errors block the consumer.
- `production_safe=true` fails.
- Missing sidecar path fails.
- Output includes `resolved`, `needs_context`, `needs_review`, `deferred`, and `unresolved` counts.
- Output includes blocked records and warning details.
- No production importer is called.
- No production route or frontend code is imported.
- Sidecar input is not mutated.
- Output path guard refuses production data directories.
- JSON output has stable top-level keys.

The tests use `backend/tests/fixtures/le_tools_import_context_sidecar_current.json` and mutated local copies for failure cases. They do not require network access or live LET URLs.

Current test file:

```text
backend/tests/test_le_tools_sidecar_diagnostic_consumer.py
```

Current generated report:

```text
docs/generated/le_tools_sidecar_diagnostic_consumer_report.md
```

## 9. What This Does Not Prove

This consumer does not prove:

- Live LET payload shape.
- Production importer migration.
- Production bundle consumption.
- Production-safe item type resolution.
- Production-safe adapter behavior.
- Base item migration.
- Item legality authority.
- Simulation correctness.
- Public API readiness.

It proves only that a validated saved sidecar artifact can be consumed by developer-only diagnostics without changing production behavior.

## 10. Recommended Implementation Step

The CLI-only developer diagnostic consumer has been implemented using the saved sidecar fixture and the existing sidecar validator.

Implemented behavior:

- `backend/app/game_data/le_tools_sidecar_diagnostic_consumer.py` consumes saved sidecar diagnostics.
- `backend/scripts/consume_le_tools_sidecar_diagnostic.py` exposes human-readable, JSON, and explicit-output modes.
- The consumer reads `backend/tests/fixtures/le_tools_import_context_sidecar_current.json`.
- The consumer validates with `le_tools_import_context_sidecar_validator` before consumption.
- Validation errors block reporting.
- Warning-only validation is allowed and visibly labeled.
- Output writes only with explicit `--output`.
- Production data output paths are refused.
- Tests prove validation gating, no mutation, no importer calls, stable output shape, and warning labeling.

Next recommendation:

- Keep this consumer limited to saved sidecar diagnostics.
- Review whether the next diagnostic step should consume freshly built sidecars, still behind the same validator and still outside production behavior.
- Do not plan production migration until a separate non-production expansion plan exists and passes the same no-false-confidence checks.
