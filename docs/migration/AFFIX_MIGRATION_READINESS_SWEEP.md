# Affix Migration Readiness Sweep

This is a diagnostic-only readiness audit. It does not modify production importers, production loaders, generated output, runtime behavior, or Forge consumers. It does not set `production_safe=true` and does not claim affix production readiness.

## 1. Readiness Result

| Field | Result |
| --- | --- |
| `non_production_consumer_allowed` | `true` for planning a minimum read-only diagnostic consumer only |
| Reason | The accepted exact duplicate eligibility policy has been applied in generated diagnostics. Phase 3 is now `warning`, Phase 5 is now `warning`, no phase has error status, and saved/fresh count, warning, and error deltas are zero. |
| Production safety | `production_safe=false` |
| Consumer status | Phase 6 design/planning may begin; production migration and production consumers remain blocked. |

The exact duplicate eligibility policy has been accepted and applied only in the Phase 3 diagnostic validator/report. This does not deduplicate source data, does not generate affix bundle families, does not change Forge behavior, and does not make affix eligibility production-safe.

## 2. Sources Reviewed

Forge docs:

- `D:\Forge\le-the-forge\docs\FORGE_MIGRATION_TRACKER.md`
- `D:\Forge\le-the-forge\docs\BUNDLE_ITEM_MIGRATION_MILESTONE_SUMMARY.md`
- `D:\Forge\le-the-forge\docs\migration\AFFIXES_SOURCE_AUDIT_AND_MIGRATION_PLAN.md`

Generated diagnostic reports:

- `D:\Forge\last-epoch-data\docs\generated\affix_source_shape_diagnostic_report.json`
- `D:\Forge\last-epoch-data\docs\generated\affix_identity_provenance_diagnostic_report.json`
- `D:\Forge\last-epoch-data\docs\generated\affix_eligibility_diagnostic_report.json`
- `D:\Forge\last-epoch-data\docs\generated\affix_tag_category_diagnostic_report.json`
- `D:\Forge\last-epoch-data\docs\generated\affix_saved_vs_fresh_diagnostic_comparison_report.json`

Sidecar diagnostics:

- Forge tracker and milestone docs record the sidecar diagnostics milestone as complete for saved-sidecar validation, fresh-sidecar validation, and saved-vs-fresh comparison.
- Current sidecar diagnostics remain non-production and `production_safe=false`.

## 3. Diagnostic Status Matrix

| Area | Current status | `production_safe` | Error present? | Notes |
| --- | --- | ---: | ---: | --- |
| Sidecar diagnostics | `warning` comparison state | `false` | No | Saved/fresh shape agreement is confirmed; warning states remain visible. |
| Phase 1 affix source/tier shape | `warning` | `false` | No | Shape/tier report exists; eligibility and tags are out of scope. |
| Phase 2 affix identity/provenance | `warning` | `false` | No | Stable source identity exists for 1227 affixes; display-name collisions remain warnings. |
| Phase 3 affix eligibility | `warning` | `false` | No | Affix `910` duplicate `canRollOn` target satisfies the accepted exact-duplicate diagnostic policy and remains visible as warning-only raw duplicate evidence. |
| Phase 4 affix tag/category | `warning` | `false` | No | Tag/category evidence remains a separate warning-level gate. |
| Phase 5 saved-vs-fresh comparison | `warning` | `false` | No | Saved and fresh reports agree with zero count/warning/error deltas; the combined gate is warning-only because all phases remain diagnostic warnings. |
| Affix 910 duplicate policy | Applied in diagnostics only | `false` | No | The generated Phase 3 report records raw duplicate count, duplicate positions, and a diagnostic-only unique-target view. |

## 4. Current Generated Report Facts

### Phase 1 Source/Tier Shape

| Metric | Value |
| --- | ---: |
| Validation status | `warning` |
| Total affixes | 1227 |
| Equipment affixes | 1112 |
| Idol affixes | 115 |
| Total embedded tiers | 6959 |
| Missing required affix identity fields | 0 |
| Missing required tier fields | 0 |
| Duplicate source identities | 0 |
| Ambiguous name collisions | 28 |
| Malformed tier ranges | 136 |
| Missing stat/modifier references | 115 |
| Unsupported/unresolved fields | 1112 |
| `production_safe` | `false` |

### Phase 2 Identity/Provenance

| Metric | Value |
| --- | ---: |
| Validation status | `warning` |
| Total affixes | 1227 |
| Equipment affixes | 1112 |
| Idol affixes | 115 |
| Affixes with stable source identity | 1227 |
| Affixes missing source identity | 0 |
| Name-only identity records | 0 |
| Subtype_id-only identity records | 0 |
| Duplicate source identities | 0 |
| Ambiguous display-name collisions | 137 |
| Missing source/provenance fields | 0 |
| `production_safe` | `false` |

### Phase 3 Eligibility

| Metric | Value |
| --- | ---: |
| Validation status | `warning` |
| Total affixes inspected | 1227 |
| Affixes with eligibility evidence | 1227 |
| Affixes missing eligibility evidence | 0 |
| Eligibility target categories | 35 |
| Subtype_id-only eligibility records | 0 |
| Name-only eligibility records | 0 |
| Unresolved item references | 0 |
| Duplicate/ambiguous eligibility records | 1 |
| Equipment affixes with eligibility evidence | 1112 |
| Idol affixes with eligibility evidence | 115 |
| Unsupported/unresolved eligibility fields | 115 |
| `production_safe` | `false` |

Current blocker:

- Affix `910` retains duplicate raw-source `canRollOn` evidence for `IDOL_4x1`, but it now satisfies the accepted exact-duplicate diagnostic policy and is warning-only.
- The generated Phase 3 report preserves raw duplicate count `2`, duplicate positions `[0, 1]`, and labels the normalized unique-target view as diagnostic-only.
- This is still not production-safe and does not deduplicate source or generated data.

### Phase 4 Tag/Category

| Metric | Value |
| --- | ---: |
| Validation status | `warning` |
| Total affixes inspected | 1227 |
| Affixes with tag/category evidence | 1227 |
| Affixes missing tag/category evidence | 0 |
| Known tag/category families | 11 |
| Unknown/unsupported tag/category values | 148 |
| Duplicate tag/category records | 0 |
| Ambiguous tag/category mappings | 110 |
| Name-only tag/category records | 0 |
| Subtype_id-only tag/category records | 0 |
| Missing tag/category provenance | 0 |
| `production_safe` | `false` |

### Phase 5 Saved-vs-Fresh Comparison

| Metric | Value |
| --- | ---: |
| `migration_gate_status` | `warning` |
| Phases expected | 4 |
| Phases compared | 4 |
| Missing phase reports | 0 |
| Count deltas | 0 |
| Warning deltas | 0 |
| Error deltas | 0 |
| Phases with warning status | 4 |
| Phases with error status | 0 |
| Phase 3 affix 910 duplicate unresolved | `false` |
| Phase 3 affix 910 duplicate warning-only | `true` |
| Phase 4 tag/category warnings present | `true` |
| `production_safe` | `false` |

Phase agreement is stable and warning-only:

- Phase 1 saved `warning`, fresh `warning`.
- Phase 2 saved `warning`, fresh `warning`.
- Phase 3 saved `warning`, fresh `warning`.
- Phase 4 saved `warning`, fresh `warning`.

## 5. Remaining Warning Categories

- Phase 1 malformed tier ranges.
- Phase 1 missing stat/modifier references.
- Phase 1 unsupported/unresolved fields.
- Phase 1 ambiguous name collisions.
- Phase 2 ambiguous display-name collisions.
- Phase 3 unsupported/unresolved idol eligibility fields.
- Phase 4 unknown or unsupported tag/category values.
- Phase 4 ambiguous tag/category mappings.
- Sidecar diagnostics retain warning-level status and are not production consumers.

These warnings are intentionally visible. They should not be downgraded or hidden to make a consumer appear safer.

## 6. Remaining Blocked Assumptions

- No affix bundle family exists.
- No Forge affix consumer scope has been implemented or validated.
- Affix eligibility remains separate from affix identity and tags.
- Affix tags remain a separate warning-level diagnostic gate.
- Tier semantics, stat/modifier reference resolution, and simulation behavior are not validated by these diagnostics.
- Name-only matching and subtype_id-only identity remain unsafe.
- Production deduplication of raw duplicate evidence remains forbidden.

## 7. Consumer Readiness Decision

`non_production_consumer_allowed=true`

The minimum safe non-production affix consumer may now be planned because:

1. Phase 3 eligibility now has `validation_status=warning`, not `error`.
2. Phase 5 saved-vs-fresh comparison now reports `migration_gate_status=warning`, not `blocked`.
3. Affix `910` raw duplicate evidence remains visible and warning-only under the accepted policy.
4. Count, warning, and error deltas remain zero.

This permits only a future read-only, diagnostic-only, developer-only Phase 6 consumer design. It does not authorize production migration.

## 8. Future Allowed Consumer Scope

The first Phase 6 consumer may be planned only within this scope:

- Read-only.
- Diagnostic-only.
- Developer-only.
- No production API replacement.
- No production loader replacement.
- No runtime build math replacement.
- No silent deduplication.
- No name-only matching.
- No subtype_id-only identity.
- Must preserve raw duplicate evidence and duplicate positions.
- Must preserve warning metadata from all phases.
- Must keep `production_safe=false`.
- Must fail or warn visibly when eligibility, tag/category, tier, or stat reference diagnostics are incomplete.

This scope permits planning only. It would not authorize production migration.

## 9. Required Next Step

Design the minimum safe Phase 6 non-production affix diagnostic consumer.

The consumer design must be read-only, developer-only, warning-preserving, and explicitly scoped to saved/generated diagnostics. It must not generate bundle families, replace loaders, feed runtime math, silently deduplicate affix `910`, or set `production_safe=true`.
