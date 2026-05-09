# Affix Migration Readiness Sweep

This is a diagnostic-only readiness audit. It does not modify production importers, production loaders, generated output, runtime behavior, or Forge consumers. It does not set `production_safe=true` and does not claim affix production readiness.

## 1. Readiness Result

| Field | Result |
| --- | --- |
| `non_production_consumer_allowed` | `false` |
| Reason | Current generated diagnostics still show Phase 3 eligibility as `error` and Phase 5 saved-vs-fresh comparison as `blocked`. |
| Production safety | `production_safe=false` |
| Consumer status | No Phase 6 affix consumer should be created yet. |

The exact duplicate eligibility policy has been proposed in Forge planning docs, but the current generated reports available under `D:\Forge\last-epoch-data\docs\generated` do not show the policy applied. The readiness sweep therefore treats the system as not ready for a minimum safe non-production affix consumer.

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
| Phase 3 affix eligibility | `error` | `false` | Yes | Affix `910` duplicate `canRollOn` target remains error-level in generated reports. |
| Phase 4 affix tag/category | `warning` | `false` | No | Tag/category evidence remains a separate warning-level gate. |
| Phase 5 saved-vs-fresh comparison | `blocked` | `false` | Yes, inherited from Phase 3 | Saved and fresh reports agree, but agreement is on a blocked state. |
| Affix 910 duplicate policy | Proposed only in Forge docs | `false` | Yes, until applied | No generated report currently shows Phase 3 downgraded to warning-only. |

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
| Validation status | `error` |
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

- Affix `910` retains duplicate raw-source `canRollOn` evidence for `IDOL_4x1`.
- The policy proposal classifies affix `910` as a candidate for warning-only diagnostic handling, but the generated Phase 3 report still records the duplicate as an error.
- No diagnostic report currently proves the policy was accepted, implemented, and rerun.

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
| `migration_gate_status` | `blocked` |
| Phases expected | 4 |
| Phases compared | 4 |
| Missing phase reports | 0 |
| Count deltas | 0 |
| Warning deltas | 0 |
| Error deltas | 0 |
| Phases with warning status | 3 |
| Phases with error status | 1 |
| Phase 3 affix 910 duplicate unresolved | `true` |
| Phase 4 tag/category warnings present | `true` |
| `production_safe` | `false` |

Phase agreement is stable, but it is stable on the current blocked state:

- Phase 1 saved `warning`, fresh `warning`.
- Phase 2 saved `warning`, fresh `warning`.
- Phase 3 saved `error`, fresh `error`.
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

- The affix `910` exact duplicate policy is proposed but not reflected in current generated Phase 3 output.
- Phase 3 remains `validation_status=error`.
- Phase 5 remains `migration_gate_status=blocked`.
- No affix bundle family exists.
- No Forge affix consumer scope has been implemented or validated.
- Affix eligibility remains separate from affix identity and tags.
- Affix tags remain a separate warning-level diagnostic gate.
- Tier semantics, stat/modifier reference resolution, and simulation behavior are not validated by these diagnostics.
- Name-only matching and subtype_id-only identity remain unsafe.
- Production deduplication of raw duplicate evidence remains forbidden.

## 7. Consumer Readiness Decision

`non_production_consumer_allowed=false`

The minimum safe non-production affix consumer is not allowed yet because:

1. Phase 3 eligibility still has `validation_status=error`.
2. Phase 5 saved-vs-fresh comparison still reports `migration_gate_status=blocked`.
3. The affix `910` exact duplicate policy has not been applied in generated diagnostics.
4. The Phase 6 consumer scope has not been separately designed against warning-only diagnostics.

## 8. Future Allowed Consumer Scope

If the duplicate policy is accepted, implemented, and rerun successfully, the first Phase 6 consumer may be planned only within this scope:

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

This scope would permit planning a consumer only after updated diagnostics show no error-level Phase 3 blocker and no blocked Phase 5 gate. It would not authorize production migration.

## 9. Required Next Step

Apply the proposed exact duplicate eligibility policy in the Phase 3 diagnostic validator/report, then regenerate Phase 3 and Phase 5 reports.

The readiness sweep should be rerun only after:

1. Phase 3 reports `warning` instead of `error` for the affix `910` exact duplicate class.
2. Phase 5 reports `warning` or `diagnostic_only_pass` instead of `blocked`.
3. Count, warning, and error deltas remain zero or are explicitly explained.
4. `production_safe=false` remains present in every report.

No Phase 6 consumer should be implemented in the same task as the policy application.
