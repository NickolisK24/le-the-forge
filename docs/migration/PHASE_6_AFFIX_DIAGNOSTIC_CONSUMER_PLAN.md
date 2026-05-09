# Phase 6 Affix Diagnostic Consumer Plan

## 1. Purpose

This document designs the minimum safe Phase 6 affix diagnostic consumer. It is planning only. It does not implement a consumer, change Forge production behavior, generate bundle families, or make affix data production-safe.

Phase 6 is allowed only because the current readiness sweep permits planning for a read-only, non-production diagnostic consumer. The consumer must inspect approved diagnostic artifacts and preserve their warning state. It must not power build math, item generation, crafting, runtime gameplay output, production APIs, or production loaders.

Current boundary:

- `production_safe=false` remains required.
- Phase 1 affix source/tier shape is `warning`.
- Phase 2 affix identity/provenance is `warning`.
- Phase 3 affix eligibility is `warning` after accepted exact duplicate policy application.
- Phase 4 affix tag/category evidence is `warning`.
- Phase 5 saved-vs-fresh comparison is `warning`.
- Affix `910` duplicate `canRollOn` evidence remains visible and is not deduplicated.

## 2. Allowed Scope

The Phase 6 consumer may:

- Read approved generated diagnostic artifacts only.
- Produce a developer-only CLI/report output.
- Summarize affix records and embedded tier diagnostic state for inspection.
- Summarize identity/provenance diagnostic state for inspection.
- Summarize eligibility warning state for inspection.
- Summarize tag/category warning state for inspection.
- Surface blocked, ambiguous, unsupported, warning, and unresolved records.
- Preserve raw warning/error metadata from source diagnostics.
- Preserve affix `910` raw duplicate count, duplicate positions, and diagnostic-only unique-target label.
- Compare or restate Phase 5 saved-vs-fresh agreement.
- Keep all output explicitly diagnostic-only and `production_safe=false`.

The first implementation should be CLI-only and read-only. It should not be exposed through Flask routes, frontend screens, importers, loaders, simulation code, or crafting/optimizer systems.

## 3. Forbidden Scope

The Phase 6 consumer must not:

- Read live production importer output.
- Read live Forge runtime state.
- Replace current Forge affix behavior.
- Replace current Forge item, crafting, optimizer, or simulation logic.
- Generate or modify bundle family files.
- Modify `exports_json`, `data_bundle`, `data/items`, or source extraction outputs.
- Deduplicate source or generated affix data.
- Hide warning/error evidence.
- Treat diagnostic unique-target views as source mutation.
- Infer eligibility from display names, prose, tooltips, or item names.
- Use `subtype_id` alone as identity.
- Use name-only matching.
- Return sidecar or affix diagnostic data from production API endpoints.
- Mark any output `production_safe=true`.
- Claim production readiness.

## 4. Required Inputs

The minimum consumer should read these approved generated diagnostic artifacts from `D:\Forge\last-epoch-data\docs\generated`:

| Phase | Required artifact | Required use |
| --- | --- | --- |
| Phase 1 | `affix_source_shape_diagnostic_report.json` | Source/tier shape summary, embedded tier warnings, malformed ranges, missing modifier/stat references, unsupported fields. |
| Phase 2 | `affix_identity_provenance_diagnostic_report.json` | Stable identity/provenance summary, name-only/subtype-only identity checks, duplicate identity checks, display-name collision warnings. |
| Phase 3 | `affix_eligibility_diagnostic_report.json` | Eligibility coverage, unsafe matching counts, unresolved item references, affix `910` duplicate warning evidence. |
| Phase 4 | `affix_tag_category_diagnostic_report.json` | Tag/category coverage, unknown values, ambiguous mappings, unsafe name/subtype matching checks. |
| Phase 5 | `affix_saved_vs_fresh_diagnostic_comparison_report.json` | Gate status, saved/fresh status agreement, count/warning/error deltas. |

The consumer should not read `exports_json/affixes.json` directly in the minimum implementation. If later inspection needs full source records, that should be a separate diagnostic artifact and review gate, not an implicit bypass around Phase 1-5 reports.

## 5. Required Output Shape

The consumer should return a serializable report shaped like:

```json
{
  "diagnostic": "phase_6_affix_diagnostic_consumer",
  "production_safe": false,
  "consumer_scope": "non_production_read_only",
  "input_artifacts": [
    {
      "phase": "phase_1_source_shape",
      "path": "D:\\Forge\\last-epoch-data\\docs\\generated\\affix_source_shape_diagnostic_report.json",
      "validation_status": "warning",
      "production_safe": false,
      "errors": 0,
      "warnings": 0
    }
  ],
  "migration_gate_status": "warning",
  "summary": {
    "total_affixes": 1227,
    "equipment_affixes": 1112,
    "idol_affixes": 115,
    "total_embedded_tiers": 6959,
    "phases_compared": 4,
    "count_deltas": 0,
    "warning_deltas": 0,
    "error_deltas": 0
  },
  "inspection_views": {
    "source_shape": {},
    "embedded_tiers": {},
    "identity_provenance": {},
    "eligibility": {},
    "tag_category": {}
  },
  "warning_records": [
    {
      "source_affix_id": 910,
      "source_section": "equipment",
      "warning_type": "exact_duplicate_eligibility_target",
      "raw_duplicate_count": 2,
      "duplicate_positions": [0, 1],
      "diagnostic_unique_targets_label": "diagnostic_only_not_source_mutation",
      "production_safe": false
    }
  ],
  "blocked_records": [],
  "recommendations": []
}
```

The exact record details may be limited by what the approved artifacts expose. The consumer should not reach around the artifacts to fill gaps from raw source files.

## 6. Required Safety Checks

The consumer must fail or block reporting when:

- Any required input artifact is missing.
- Any required input artifact is invalid JSON.
- Any input artifact reports `production_safe=true`.
- Phase 5 `migration_gate_status` is `blocked`.
- Any Phase 1-4 artifact reports `validation_status=error`.
- Saved/fresh count, warning, or error deltas are nonzero unless explicitly allowed by a later diagnostic policy.
- Phase 3 no longer exposes affix `910` raw duplicate evidence while still reporting warning-only classification.
- Phase 3 reports name-only eligibility matching.
- Phase 3 reports subtype-only eligibility identity.
- Phase 4 reports name-only tag/category matching.
- Phase 4 reports subtype-only tag/category identity.

The consumer may continue with a warning label when:

- All required artifacts are present.
- All artifacts keep `production_safe=false`.
- Phase 1-4 statuses are `warning`.
- Phase 5 gate is `warning`.
- Count/warning/error deltas are zero.
- Warning metadata remains visible.

## 7. Failure Modes

Failure modes should be explicit and conservative:

| Failure | Required result |
| --- | --- |
| Missing artifact | Exit nonzero; report blocked. |
| Invalid JSON | Exit nonzero; report blocked. |
| `production_safe=true` anywhere | Exit nonzero; report blocked. |
| Phase status `error` | Exit nonzero; report blocked. |
| Phase 5 gate `blocked` | Exit nonzero; report blocked. |
| Nonzero count/warning/error deltas | Exit nonzero or warning depending on later policy; initial implementation should block. |
| Missing affix `910` duplicate evidence | Exit nonzero; report blocked because accepted policy evidence is no longer visible. |
| Output path inside production data directories | Exit nonzero; refuse write. |

Blocked reporting must not mutate inputs or try to repair data.

## 8. CLI and Reporting Behavior

Recommended CLI-only implementation:

```powershell
cd D:\Forge\le-the-forge\backend
.\.venv\Scripts\python.exe scripts\report_affix_diagnostic_consumer.py --diagnostics-dir D:\Forge\last-epoch-data\docs\generated
```

Recommended JSON output:

```powershell
.\.venv\Scripts\python.exe scripts\report_affix_diagnostic_consumer.py --diagnostics-dir D:\Forge\last-epoch-data\docs\generated --json
```

Recommended generated report:

```powershell
.\.venv\Scripts\python.exe scripts\report_affix_diagnostic_consumer.py --diagnostics-dir D:\Forge\last-epoch-data\docs\generated --output ..\docs\generated\affix_diagnostic_consumer_report.md
```

Required CLI behavior:

- Default stdout only.
- `--json` prints the serializable result.
- `--output` writes only when explicitly provided.
- Output guard refuses production data paths such as `data/items`, `exports_json`, `data_bundle`, and `last-epoch-data/data_bundle`.
- Exit `0` only for valid warning-only or diagnostic-pass reports.
- Exit `1` for missing inputs, invalid JSON, blocked gates, unsafe production flags, output guard failures, or internal errors.

## 9. Tests Required Before Implementation

Implementation must include tests for:

- Valid warning-only Phase 1-5 artifacts produce a diagnostic report.
- Report output always includes `production_safe=false`.
- Phase 1-4 warning states are preserved.
- Phase 5 `migration_gate_status=warning` is preserved.
- Missing artifact blocks the consumer.
- Invalid JSON blocks the consumer.
- `production_safe=true` in any phase blocks the consumer.
- Phase 3 `validation_status=error` blocks the consumer.
- Phase 5 `migration_gate_status=blocked` blocks the consumer.
- Nonzero count delta blocks the initial consumer.
- Nonzero warning/error delta blocks the initial consumer.
- Affix `910` warning record preserves raw duplicate count and duplicate positions.
- The diagnostic-only unique-target label is preserved.
- Name-only eligibility matching blocks or surfaces unsafe status.
- Subtype-only eligibility identity blocks or surfaces unsafe status.
- Name-only tag/category matching blocks or surfaces unsafe status.
- Subtype-only tag/category identity blocks or surfaces unsafe status.
- Output path guard refuses production data directories.
- Consumer does not import production loaders, importers, routes, frontend code, crafting, optimizer, or simulation modules.

## 10. How Phase 6 Differs From Production Consumption

Phase 6 is a consumer of diagnostic reports, not a consumer of canonical affix data.

Phase 6 may inspect:

- Counts.
- Validation statuses.
- Warning/error metadata.
- Diagnostic identity/provenance summaries.
- Diagnostic eligibility summaries.
- Diagnostic tag/category summaries.
- Embedded tier shape warnings.
- Saved-vs-fresh comparison agreement.

Phase 6 must not use this data to:

- Drive build math.
- Generate items.
- Validate crafting legality.
- Filter production item affixes.
- Replace Forge static affix behavior.
- Feed optimizer/BIS logic.
- Expose public API data.
- Update frontend state.
- Write bundle families.

Passing Phase 6 means the project can safely inspect the diagnostic state through a read-only report. It does not mean affixes, tiers, eligibility, or tags are production-ready.

## 11. Requirements After Phase 6 Before Production Migration Planning

Before any production migration planning, the program still needs:

- A validated Phase 6 CLI/report implementation.
- A generated Phase 6 report with `production_safe=false`.
- Stable saved-vs-fresh agreement over regenerated diagnostics.
- A separate affix bundle family design.
- A separate `affix_tiers` normalization design.
- A separate `affix_eligibility` bundle design.
- A separate `affix_tags` bundle design.
- Explicit Forge-side non-production consumer tests.
- Fallback and rollback strategy.
- Source ID preservation strategy.
- Production safety criteria.
- Explicit review that warnings are acceptable for a specific production use case, or resolution of those warnings.

Production migration remains forbidden until those later gates are satisfied.

## 12. Recommended Next Implementation Prompt

Recommended next task:

```text
Implement Phase 6 as a CLI-only, read-only affix diagnostic consumer.

Inputs:
- D:\Forge\last-epoch-data\docs\generated\affix_source_shape_diagnostic_report.json
- D:\Forge\last-epoch-data\docs\generated\affix_identity_provenance_diagnostic_report.json
- D:\Forge\last-epoch-data\docs\generated\affix_eligibility_diagnostic_report.json
- D:\Forge\last-epoch-data\docs\generated\affix_tag_category_diagnostic_report.json
- D:\Forge\last-epoch-data\docs\generated\affix_saved_vs_fresh_diagnostic_comparison_report.json

Constraints:
- Read generated diagnostics only.
- Preserve production_safe=false.
- Preserve warning metadata.
- Preserve affix 910 raw duplicate count and duplicate positions.
- Do not read production loaders/importers/routes/frontend/simulation.
- Do not read raw affix source files in the minimum consumer.
- Do not generate bundle families.
- Do not deduplicate.
- Do not claim production readiness.
```
