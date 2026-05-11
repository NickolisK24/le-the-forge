# Fresh LE Tools Sidecar Diagnostic Validation Report

- status: warning
- validation_status: warning
- production_safe: false
- fixture_path: D:\Forge\le-the-forge\backend\tests\fixtures\le_tools_offline_buildinfo_stage_context_sample.json
- saved_sidecar_path: D:\Forge\le-the-forge\backend\tests\fixtures\le_tools_import_context_sidecar_current.json

## Summary

- total_items: 12
- resolved: 8
- needs_context: 2
- needs_review: 1
- deferred: 0
- unresolved: 1
- missing_identity: 3
- ambiguous: 1
- unsafe: 0
- subtype_only: 1
- name_only: 1

## Shape

- top_level_keys_match_saved: True
- summary_keys_match_saved: True
- item_count: 12
- saved_item_count: 12
- item_sections_present: True

## Errors

- none

## Warnings

- mapped.has_item_type is false for all items.
- One or more items require test-only pairing.
- One or more raw records contain subtype_id without base_type_id.
- One or more records are unresolved.
- One or more records need base_type_id context.
- One or more records need manual review.
- Sidecar source appears synthetic/offline.
- One or more fresh sidecar records are missing item type identity context.
- One or more fresh sidecar records require manual review.
- One or more fresh sidecar records need base_type_id context.
- One or more fresh sidecar records are unresolved.
- One or more fresh sidecar records contain subtype_id without base_type_id.
- One or more fresh sidecar records are name-only and remain blocked.

## Missing / Ambiguous / Unsafe Records

- index=8 slot=weapon raw_type=axe status=needs_context identity=missing reasons=base_type_id context required
- index=9 slot=belt raw_type=belt status=needs_context identity=missing reasons=subtype_id is present without base_type_id, base_type_id context required
- index=11 slot=helmet raw_type=null status=unresolved identity=missing reasons=missing raw item type signal, record unresolved
- index=10 slot=weapon raw_type=spear status=needs_review identity=ambiguous reasons=manual review required

## Recommendations

- Keep this validation diagnostic-only and non-production.
- Do not consume freshly built sidecars in production.
- Keep production_safe=false.
- Thread base_type_id and raw item type context before expanding consumers.
- Manually review ambiguous records before adding adapter coverage.
- Keep unresolved records blocked; do not use name-only matching.

## Safety Boundary

- This validation is diagnostic-only and non-production.
- It does not change importer output, loaders, API behavior, frontend behavior, or simulation.
- production_safe remains false.
- subtype_id-only identity and name-only matching remain blocked.

