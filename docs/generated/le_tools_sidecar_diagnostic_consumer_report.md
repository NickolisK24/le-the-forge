# LE Tools Sidecar Diagnostic Consumer Report

- sidecar_path: tests\fixtures\le_tools_import_context_sidecar_current.json
- validation_status: warning
- production_safe: false

## Validation

### Errors

- none

### Warnings

- mapped.has_item_type is false for all items.
- One or more items require test-only pairing.
- One or more raw records contain subtype_id without base_type_id.
- One or more records are unresolved.
- One or more records need base_type_id context.
- One or more records need manual review.
- Sidecar source appears synthetic/offline.

## Summary

- total_items: 12
- resolved: 8
- needs_context: 2
- needs_review: 1
- deferred: 0
- unresolved: 1

## Resolved Records

- index=0 slot=helmet raw_type=helm bundle=helmet match=adapter_translation
- index=1 slot=body_armour raw_type=chest bundle=body_armor match=adapter_translation
- index=2 slot=weapon raw_type=axe bundle=one_handed_axe match=adapter_translation
- index=3 slot=weapon raw_type=axe bundle=two_handed_axe match=adapter_translation
- index=4 slot=weapon raw_type=mace bundle=one_handed_maces match=adapter_translation
- index=5 slot=weapon raw_type=sword bundle=two_handed_sword match=adapter_translation
- index=6 slot=idol_altar raw_type=idol_1x1 bundle=idol_1x1_eterra match=adapter_translation
- index=7 slot=idol_altar raw_type=idol_1x1 bundle=idol_1x1_lagon match=adapter_translation

## Blocked Records

- index=8 slot=weapon raw_type=axe status=needs_context raw_base=None mapped_base=None bundle=null
  - warning: base_type_id is required; resolver will not guess from slug alone.
  - note: Provide base_type_id to use accepted direct mappings or adapter translations.
- index=9 slot=belt raw_type=belt status=needs_context raw_base=None mapped_base=None bundle=null
  - warning: subtype_id was provided but ignored; subtype_id alone is not a valid identity.
  - warning: base_type_id is required; resolver will not guess from slug alone.
  - note: Provide base_type_id to use accepted direct mappings or adapter translations.
- index=10 slot=weapon raw_type=spear status=needs_review raw_base=14 mapped_base=14 bundle=null
  - warning: Forge item type requires manual review before resolution.
  - note: No reviewed safe mapping exists.
- index=11 slot=helmet raw_type=null status=unresolved raw_base=None mapped_base=None bundle=null
  - warning: Missing forge_item_type.

## Context Gaps

- records_requiring_base_type_id: 2
- manual_review_records: 1
- unresolved_records: 1
- subtype_only_blocked_records: 1
- name_only_blocked_records: 1

## Recommendations

- Keep this consumer developer-only until a separate non-production migration review is complete.
- Do not consume bundle item type IDs in production from this report.
- Review validation warnings before using this report as a diagnostic baseline.
- Thread base_type_id context for needs_context records before resolution.
- Manually review needs_review records before adding adapter coverage.
- Keep unresolved records blocked; do not fall back to name-only matching.

## Safety

- This report is developer-only and reads a saved sidecar artifact.
- It does not call the LET importer, API routes, frontend code, or production loaders.
- production_safe remains false globally and per record.
- Warning-only validation is allowed only with visible warnings.

## What This Proves

- A saved sidecar artifact can be validated and consumed by diagnostic tooling.
- Resolver statuses can be reported without activating production migration.

## What This Does Not Prove

- Live LET payload shape.
- Production importer migration.
- Production bundle consumption.
- Base item production migration.

