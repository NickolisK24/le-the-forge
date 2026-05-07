# LE Tools Offline BuildInfo Context Report

- production_safe: false
- fixture: `backend/tests/fixtures/le_tools_offline_buildinfo_equipment_sample.json`
- fixture source: synthetic offline, not captured from live LE Tools
- importer accepted fixture directly: true
- test-only diagnostic adaptation needed: true
- production importer output changed: false
- network calls made: false

## Summary

| Metric | Count |
| --- | ---: |
| total_items | 14 |
| resolved | 10 |
| needs_context | 2 |
| needs_review | 1 |
| deferred | 0 |
| unresolved | 1 |

## Resolved Records

| Forge item type | `base_type_id` | Bundle item type |
| --- | ---: | --- |
| `helm` | 0 | `helmet` |
| `chest` | 1 | `body_armor` |
| `axe` | 5 | `one_handed_axe` |
| `axe` | 12 | `two_handed_axe` |
| `mace` | 7 | `one_handed_maces` |
| `mace` | 13 | `two_handed_mace` |
| `sword` | 9 | `one_handed_sword` |
| `sword` | 16 | `two_handed_sword` |
| `idol_1x1` | 25 | `idol_1x1_eterra` |
| `idol_1x1` | 26 | `idol_1x1_lagon` |

## Context Gaps

| Case | Status | Reason |
| --- | --- | --- |
| `axe` without `baseTypeID` | `needs_context` | Collapsed weapon slug cannot resolve without base type context. |
| `belt` with `subTypeID` only | `needs_context` | `subtype_id` alone is not a valid identity. |
| `spear` with `baseTypeID=14` | `needs_review` | No reviewed safe `spear` mapping exists. |
| `unknown_type` | `unresolved` | No reviewed mapping exists. |

## What This Proves

- The existing importer path can preserve `base_type_id` in mapped gear output for ID-backed records.
- Developer-only copied mapped output can resolve canonical bundle item type IDs through the existing dry-run resolver.
- Missing `baseTypeID`, subtype-only context, `spear`, and unknown types do not silently resolve.

## What This Does Not Prove

- It does not prove that live LE Tools payloads use the same field shape.
- It does not prove production importer migration safety.
- It does not make any mapping `production_safe=true`.
- It does not change importer output, route behavior, frontend flow, or simulation behavior.
