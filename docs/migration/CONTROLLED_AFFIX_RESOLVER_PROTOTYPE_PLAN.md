# Controlled Affix Resolver Prototype Plan

## 1. Purpose

This document designs the first controlled affix resolver prototype after the Phase 6 read-only diagnostic consumer.

The prototype is non-production, read-only, and diagnostic-only. Its purpose is to prove that validated/generated affix diagnostic artifacts can be transformed into deterministic, inspection-safe normalized affix objects while preserving provenance, warnings, and raw source evidence.

The prototype has now been implemented as CLI-only read-only diagnostic tooling in:

- `backend/app/game_data/controlled_affix_resolver_prototype.py`
- `backend/scripts/report_controlled_affix_resolver_prototype.py`
- `backend/tests/test_controlled_affix_resolver_prototype.py`
- `docs/generated/controlled_affix_resolver_prototype_report.md`
- `docs/generated/controlled_affix_resolver_prototype_report.json`

The saved-vs-fresh comparison for the prototype has also been implemented as CLI-only read-only diagnostic tooling in:

- `backend/app/game_data/controlled_affix_resolver_comparison.py`
- `backend/scripts/compare_controlled_affix_resolver_prototype.py`
- `backend/tests/test_controlled_affix_resolver_comparison.py`
- `docs/generated/controlled_affix_resolver_comparison_report.md`
- `docs/generated/controlled_affix_resolver_comparison_report.json`

The richer per-affix diagnostic record artifact has also been implemented as CLI-only read-only diagnostic tooling in:

- `backend/app/game_data/controlled_affix_per_affix_diagnostic.py`
- `backend/scripts/report_controlled_affix_per_affix_diagnostic.py`
- `backend/tests/test_controlled_affix_per_affix_diagnostic.py`
- `docs/generated/controlled_affix_per_affix_diagnostic_records.md`
- `docs/generated/controlled_affix_per_affix_diagnostic_records.json`

This implementation does not generate bundle families, replace Forge affix loaders, change runtime behavior, power crafting or build math, expose APIs, or mark any output `production_safe=true`.

Current commands:

```powershell
cd D:\Forge\le-the-forge
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_resolver_prototype.py
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_resolver_prototype.py --json
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_resolver_prototype.py --output docs\generated\controlled_affix_resolver_prototype_report.md
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_resolver_prototype.py --json --output docs\generated\controlled_affix_resolver_prototype_report.json
.\backend\.venv\Scripts\python.exe backend\scripts\compare_controlled_affix_resolver_prototype.py
.\backend\.venv\Scripts\python.exe backend\scripts\compare_controlled_affix_resolver_prototype.py --json
.\backend\.venv\Scripts\python.exe backend\scripts\compare_controlled_affix_resolver_prototype.py --output docs\generated\controlled_affix_resolver_comparison_report.md
.\backend\.venv\Scripts\python.exe backend\scripts\compare_controlled_affix_resolver_prototype.py --json --output docs\generated\controlled_affix_resolver_comparison_report.json
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_per_affix_diagnostic.py
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_per_affix_diagnostic.py --json
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_per_affix_diagnostic.py --output docs\generated\controlled_affix_per_affix_diagnostic_records.md
.\backend\.venv\Scripts\python.exe backend\scripts\report_controlled_affix_per_affix_diagnostic.py --json --output docs\generated\controlled_affix_per_affix_diagnostic_records.json
```

Current boundary:

- `production_safe=false` remains required globally and per record.
- Phase 1-5 affix diagnostics remain warning-level.
- Phase 6 diagnostic consumer exists only for read-only inspection of generated diagnostic artifacts.
- Saved-vs-fresh resolver comparison is `comparison_status=warning` with zero count deltas, zero phase-status deltas, zero warning-category deltas, deterministic output agreement, and affix `910` duplicate evidence agreement.
- Per-affix diagnostic records exist only for read-only inspection and emit `diagnostic_only=true` plus `production_safe=false`.
- The non-production affix inspection stack milestone is complete through diagnostics, Phase 6 consumer, controlled resolver output, saved-vs-fresh resolver comparison, and per-affix diagnostic records.
- Current per-affix artifact state: 1227 records, 1112 equipment records, 115 idol records, 6959 embedded tiers, affix `910` duplicate evidence preserved, warning metadata preserved, `diagnostic_only=true`, `non_production_inspection_allowed=true`, and `production_safe=false`.
- Affix `910` duplicate eligibility evidence remains visible and must not be silently deduplicated.
- Production affix migration is not approved.

## 2. Resolver Scope

The controlled resolver prototype should:

- Consume only approved generated diagnostic artifacts.
- Validate all inputs before resolving.
- Resolve affix and embedded tier diagnostic structures into inspection-safe normalized objects.
- Preserve source identity, provenance, warning metadata, and error metadata.
- Preserve raw duplicate eligibility evidence separately from any diagnostic-only normalized views.
- Produce deterministic output for saved-vs-fresh comparison.
- Run as a developer-only module and CLI/report.
- Remain isolated from production importers, loaders, APIs, frontend code, crafting, simulation, build math, and gameplay output.

The prototype may summarize records if the current diagnostic artifacts do not yet contain full per-affix row data. If full normalized affix objects require fields not present in approved diagnostic artifacts, the resolver must report `needs_diagnostic_record_artifact` instead of reading raw source exports directly.

## 3. Explicit Non-Goals

The prototype must not:

- Read production bundle family data as an authority.
- Read `exports_json/affixes.json` directly unless a separate diagnostic input contract is approved first.
- Modify generated diagnostic artifacts.
- Modify source data.
- Deduplicate affix `910` or any other source evidence.
- Replace existing Forge affix/stat behavior.
- Power gameplay calculations, DPS, crafting, item generation, item legality, build math, APIs, frontend behavior, or runtime systems.
- Infer missing source identity from names, display text, shard names, tooltip prose, tags, or eligibility labels.
- Use `subtype_id` alone as identity.
- Treat name-only matching as valid identity.
- Treat `affix_tags` as affix identity.
- Treat `affix_eligibility` as production-safe legality.
- Claim production readiness.
- Set `production_safe=true`.

## 4. Allowed Inputs

Allowed inputs should be generated diagnostic artifacts only:

| Input | Required use | Notes |
| --- | --- | --- |
| `docs/generated/affix_diagnostic_consumer_report.json` | Primary Phase 6 inspection summary | Confirms Phase 1-5 statuses, `migration_gate_status`, warning categories, affix `910` evidence, and `production_safe=false`. |
| Phase 1 source/tier shape diagnostic JSON | Affix and embedded tier structural evidence | Must remain diagnostic-only. |
| Phase 2 identity/provenance diagnostic JSON | Stable source identity and provenance evidence | Must reject name-only and `subtype_id`-only identity. |
| Phase 3 eligibility diagnostic JSON | Eligibility warning state and duplicate evidence | Must preserve raw duplicate count and duplicate positions. |
| Phase 4 tag/category diagnostic JSON | Tag/category warning state | Must remain separate from identity and eligibility. |
| Phase 5 saved-vs-fresh comparison JSON | Gate state and drift evidence | Must be `warning` or `diagnostic_only_pass`; `blocked` must stop resolution. |

If a future per-affix diagnostic record artifact is needed, it must be explicitly generated and validated as diagnostic-only before the resolver consumes it.

## 5. Forbidden Inputs

Forbidden inputs:

- Production Forge loaders.
- Production Forge constants as affix authority.
- Production importers or importer output.
- Production APIs or frontend state.
- User builds, saved builds, or live gameplay data.
- Live LET URLs or network output.
- `data/items` production data.
- Direct raw `exports_json/affixes.json` reads without a separate approved diagnostic input contract.
- `data_bundle/families/*` as production authority.
- Name-only records.
- `subtype_id`-only records.
- Tooltip/prose-derived mechanics.

## 6. Proposed Normalized Affix Object Shape

The resolver should produce a serializable diagnostic object like:

```json
{
  "resolver": "controlled_affix_resolver_prototype",
  "production_safe": false,
  "source": "generated_diagnostic_artifacts",
  "input_artifacts": [],
  "validation_status": "warning",
  "migration_gate_status": "warning",
  "records": [
    {
      "resolver_affix_id": "equipment:910",
      "source_section": "equipment",
      "source_affix_id": 910,
      "identity": {
        "stable_source_identity": true,
        "source_identity": "equipment:910",
        "name_only": false,
        "subtype_id_only": false,
        "warnings": []
      },
      "display": {
        "name": null,
        "display_name": null
      },
      "tiers": {
        "status": "inspection_only",
        "embedded_tier_count": null,
        "normalized_tiers": [],
        "warnings": []
      },
      "eligibility": {
        "status": "warning",
        "raw_targets": ["IDOL_4x1", "IDOL_4x1"],
        "diagnostic_unique_targets": ["IDOL_4X1"],
        "diagnostic_unique_targets_label": "diagnostic_only_not_source_mutation",
        "duplicate_evidence": {
          "raw_duplicate_count": 2,
          "duplicate_positions": [0, 1],
          "source_path": "equipment[910].canRollOn",
          "policy_result": "warning_only"
        },
        "warnings": []
      },
      "tags": {
        "status": "warning",
        "categories": [],
        "warnings": []
      },
      "provenance": {
        "source_artifact": "docs/generated/affix_diagnostic_consumer_report.json",
        "source_phase": "phase_6_consumer",
        "source_path": null,
        "generated_at": null
      },
      "warnings": [],
      "errors": []
    }
  ],
  "summary": {
    "total_records": 0,
    "resolved_records": 0,
    "records_with_warnings": 0,
    "records_with_errors": 0,
    "records_requiring_additional_diagnostic_artifacts": 0
  }
}
```

This object is a diagnostic view. It must not be used as a production affix bundle family or Forge runtime model.

## 7. Tier Resolution Behavior

Tier resolution should be inspection-only.

Allowed behavior:

- Preserve embedded tier count evidence from Phase 1 diagnostics.
- Normalize tier diagnostics into deterministic arrays only when the approved inputs include enough per-tier data.
- Sort tiers deterministically by `source_section`, `source_affix_id`, tier number, and property/channel index.
- Preserve malformed tier range warnings.
- Preserve missing stat/modifier reference warnings.
- Preserve unsupported/unresolved field warnings.
- Mark tier values as diagnostic evidence, not gameplay math.

Forbidden behavior:

- Do not infer tier rows from display text.
- Do not interpret tier values as simulator-ready stat formulas.
- Do not collapse multi-property tiers unless the source channel and property index are preserved.
- Do not power crafting, item generation, planner legality, or DPS.
- Do not treat missing per-tier diagnostic rows as permission to read raw exports directly.

If approved artifacts only expose aggregate tier counts, the resolver should emit a tier summary and a warning such as `needs_diagnostic_record_artifact`.

## 8. Warning and Error Propagation

The resolver must preserve every warning/error state from upstream diagnostics.

Rules:

- Any input `production_safe=true` is a hard error.
- Any missing required artifact is a hard error.
- Phase 5 `migration_gate_status=blocked` is a hard error.
- Phase 1-5 warnings remain warnings in the resolver output.
- Warning-only affix `910` duplicate evidence remains warning-only and visible.
- Tag/category warnings remain warning-only and visible.
- Unknown or unsupported fields remain visible.
- No warning may be downgraded to pass by the resolver.
- No record may be emitted without a per-record warning/error list.

The resolver output should report:

- global validation status
- per-phase status
- per-record warnings
- per-record errors
- warning categories
- blocked records
- records requiring more diagnostic input

## 9. Provenance Requirements

Every resolver run should preserve enough provenance to explain what was consumed and how the normalized object was created.

Top-level provenance should include:

- resolver name and version
- generated timestamp
- input artifact paths
- input artifact hashes where practical
- Phase 1-5 validation statuses
- Phase 5 `migration_gate_status`
- `production_safe=false`

Per-record provenance should include:

- source phase
- source artifact path
- source section
- source affix ID
- source path if available
- original warning/error source
- duplicate evidence source path when applicable

Name, display name, shard name, tags, and eligibility labels may be displayed for inspection, but they must not become identity.

## 10. Duplicate Evidence Handling

The resolver must preserve duplicate source evidence separately from normalized views.

Affix `910` requirements:

- Preserve raw duplicate target values.
- Preserve normalized duplicate target values.
- Preserve raw duplicate count.
- Preserve duplicate positions.
- Preserve source path `equipment[910].canRollOn`.
- Preserve earliest available decoded source context when present.
- Preserve `policy_result=warning_only`.
- Preserve `diagnostic_unique_targets_label=diagnostic_only_not_source_mutation`.

The resolver may expose a diagnostic-only unique-target view for easier inspection, but that view must never replace the raw duplicate evidence. The output must state that no source or generated data has been deduplicated.

Any duplicate that does not satisfy the accepted exact duplicate policy must remain error/blocking.

## 11. Eligibility and Tag Handling Expectations

Eligibility and tags remain separate facets.

Eligibility expectations:

- Preserve Phase 3 status and warnings.
- Preserve raw evidence and diagnostic unique-target views separately.
- Do not claim eligibility is production-safe.
- Do not use eligibility as a production item legality source.
- Do not resolve item bases by name.
- Do not use `subtype_id` alone.

Tag/category expectations:

- Preserve Phase 4 status and warnings.
- Preserve unknown/unsupported values.
- Preserve ambiguous tag/category mappings.
- Do not use tags as affix identity.
- Do not merge tags into eligibility.
- Do not use tags for production filtering, crafting, or simulation.

## 12. Determinism Requirements

The resolver should be deterministic for the same input artifacts.

Requirements:

- Fixed artifact list or explicit artifact paths.
- Stable sorting for phases, records, warnings, errors, and normalized tiers.
- Stable resolver IDs derived from source section and source affix ID.
- No random IDs.
- No network calls.
- No dependency on current wall-clock time in deterministic comparison fields. If `generated_at` is included, saved-vs-fresh comparisons must ignore or separately account for it.
- JSON output should use deterministic key ordering where practical.
- Markdown output should be generated from the same serialized report model as JSON.

## 13. Failure Modes

The prototype should fail closed for unsafe inputs.

Hard failures:

- Missing required input artifact.
- Invalid JSON input.
- Any input report with `production_safe=true`.
- Phase 5 `migration_gate_status=blocked`.
- Missing Phase 1-5 status.
- Missing affix `910` duplicate evidence from inputs that claim Phase 3 is warning-only.
- Duplicate eligibility evidence reported without raw count or duplicate positions.
- Any record relying on name-only identity.
- Any record relying on `subtype_id`-only identity.
- Any attempt to write output into production data paths.

Warnings:

- Phase 1-5 warning statuses.
- Missing per-affix row data in approved artifacts.
- Aggregate-only tier information.
- Unknown/unsupported tag/category values.
- Ambiguous tag/category mappings.
- Warning-only duplicate eligibility evidence.

## 14. Validation and Testing Requirements Before Implementation

Implementation should not begin without tests for:

- Valid warning-only generated diagnostics produce an inspection-only resolver report.
- Missing artifact fails.
- Invalid JSON fails.
- `production_safe=true` in any input fails.
- Phase 5 `blocked` state fails.
- Phase 1-5 warning statuses propagate unchanged.
- Affix `910` duplicate evidence is preserved.
- Diagnostic-only unique-target view is separate from raw duplicate evidence.
- Duplicate positions are preserved.
- Name-only identity fails.
- `subtype_id`-only identity fails.
- Tag/category warnings are preserved.
- Tier aggregate-only inputs produce `needs_diagnostic_record_artifact`.
- Output is deterministic for the same inputs.
- Output path guard refuses production data directories.
- No production importer, loader, route, frontend, crafting, simulation, or build math module is imported.
- Source/generated input artifacts are not mutated.

## 15. Additional Milestones Before Production Migration Planning

Even after this resolver prototype exists, production migration planning remains blocked until later milestones are complete.

Required later milestones:

1. Implement the controlled resolver prototype as developer-only tooling. COMPLETE.
2. Add saved-vs-fresh comparison for resolver output. COMPLETE.
3. Add a validated per-affix diagnostic record artifact if full normalized records are needed. COMPLETE.
4. Define canonical bundle family shapes for `affixes`, `affix_tiers`, `affix_eligibility`, and `affix_tags`.
5. Validate each family independently.
6. Prove Forge non-production consumers can inspect resolver output without changing runtime behavior.
7. Define fallback and rollback strategy.
8. Define production safety criteria.
9. Run an explicit production readiness review.

Until those milestones complete, the resolver prototype remains diagnostic-only and `production_safe=false`.

## 16. Recommended Implementation Step

Implementation status: complete for the first controlled prototype, its saved-vs-fresh comparison, and the per-affix diagnostic record artifact.

Current generated report summary:

| Metric | Value |
| --- | ---: |
| total normalized affixes | 1227 |
| equipment affixes | 1112 |
| idol affixes | 115 |
| total embedded tiers | 6959 |
| warning categories | 10 |
| warning count | 1904 |
| Phase 5 migration gate | `warning` |
| non-production inspection allowed | `true` |
| production_safe | `false` |
| affix 910 duplicate evidence | preserved |

Current saved-vs-fresh comparison summary:

| Metric | Value |
| --- | ---: |
| comparison_status | `warning` |
| saved resolver status | `warning` |
| fresh resolver status | `warning` |
| total normalized affix delta | 0 |
| equipment affix delta | 0 |
| idol affix delta | 0 |
| embedded tier delta | 0 |
| phase status deltas | 0 |
| warning category deltas | 0 |
| deterministic output agreement | `true` |
| affix 910 duplicate evidence agreement | `true` |
| production_safe agreement | `true` |
| non-production inspection allowed agreement | `true` |

Current per-affix diagnostic artifact summary:

| Metric | Value |
| --- | ---: |
| total records | 1227 |
| equipment records | 1112 |
| idol records | 115 |
| embedded tier count | 6959 |
| warning category count | 17 |
| records with warnings | 1227 |
| diagnostic_only | `true` |
| production_safe | `false` |
| non-production inspection allowed | `true` |
| affix 910 duplicate evidence preserved | `true` |

Next implementation task, if approved:

```text
Design a diagnostic-only stat/modifier reference audit for affix modifier evidence.
```

That task should come before any controlled non-production affix modifier resolver. The current inspection stack proves record identity, provenance, eligibility warning state, tag/category warning state, and deterministic inspection output; it does not prove gameplay meaning for stat/modifier references. The next audit must remain read-only, warning-preserving, and `production_safe=false`, and it must not generate bundle families, change Forge production behavior, or claim production readiness.

Policy update:

- `docs/migration/MODIFIER_RESOLUTION_POLICY.md` now defines the diagnostic-only failure contract for any future controlled modifier resolver prototype.
- The policy allows only inspection-safe handling of structurally present references.
- It requires unresolved, malformed, and unsupported references to remain unresolved or unsupported in resolver output.
- It forbids guessing unsupported modifier semantics.
- It keeps warning metadata, provenance, `diagnostic_only=true`, and `production_safe=false` mandatory.
- The first controlled modifier resolver prototype is now implemented as CLI-only read-only diagnostic tooling in `backend/app/game_data/controlled_modifier_resolver_prototype.py` and `backend/scripts/report_controlled_modifier_resolver_prototype.py`.
- The generated reports are `docs/generated/controlled_modifier_resolver_prototype_report.md` and `docs/generated/controlled_modifier_resolver_prototype_report.json`.
- Current resolver summary: 6959 total modifier references, 5596 resolved structural inspection-only references, 115 unresolved references, 136 malformed references, and 1112 unsupported references.
- Saved-vs-fresh modifier resolver comparison is implemented in `backend/app/game_data/controlled_modifier_resolver_comparison.py` and `backend/scripts/report_controlled_modifier_resolver_comparison.py`.
- Current comparison summary: `comparison_status=warning`, zero count deltas, zero warning category deltas, provenance coverage agreement, deterministic output agreement, `diagnostic_only=true`, `production_safe=false`, and affix `910` duplicate evidence agreement.
- The implementation does not authorize gameplay correctness claims or production migration.
- Modifier inspection stack closeout: complete as diagnostic-only. The next recommended architecture target is unresolved modifier category triage, not production migration, because the unresolved, malformed, and unsupported evidence must be categorized before any useful gameplay semantics policy can be written.
