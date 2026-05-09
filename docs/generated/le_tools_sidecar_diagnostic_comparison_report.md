# LE Tools Sidecar Diagnostic Comparison Report

- migration_gate_status: warning
- production_safe: false
- saved_sidecar_status: warning
- fresh_sidecar_status: warning

## Shape Agreement

- fresh_matches_saved_top_level_keys: True
- fresh_matches_saved_summary_keys: True
- fresh_item_count_matches_saved: True
- fresh_item_sections_present: True

## Count Deltas

- total_items: saved=12 fresh=12 delta=0
- resolved: saved=8 fresh=8 delta=0
- needs_context: saved=2 fresh=2 delta=0
- needs_review: saved=1 fresh=1 delta=0
- deferred: saved=0 fresh=0 delta=0
- unresolved: saved=1 fresh=1 delta=0
- missing_identity: saved=3 fresh=3 delta=0
- ambiguous: saved=1 fresh=1 delta=0
- unsafe: saved=0 fresh=0 delta=0
- subtype_only: saved=1 fresh=1 delta=0
- name_only: saved=1 fresh=1 delta=0

## Warning Delta

- saved_count: 7
- fresh_count: 13
- added_in_fresh:
  - One or more fresh sidecar records are missing item type identity context.
  - One or more fresh sidecar records are name-only and remain blocked.
  - One or more fresh sidecar records are unresolved.
  - One or more fresh sidecar records contain subtype_id without base_type_id.
  - One or more fresh sidecar records need base_type_id context.
  - One or more fresh sidecar records require manual review.
- missing_from_fresh:
  - none

## Error Delta

- saved_count: 0
- fresh_count: 0
- added_in_fresh:
  - none
- missing_from_fresh:
  - none

## Recommendations

- Keep this comparison diagnostic-only and non-production.
- Do not consume bundle item type IDs in production from this report.
- Keep production_safe=false.
- Review warning/count deltas before using fresh sidecars as a broader diagnostic baseline.
- Review warning deltas; do not treat warning drift as migration readiness.

## Safety Boundary

- This comparison is diagnostic-only and non-production.
- It does not modify importers, loaders, production output, APIs, frontend behavior, or simulation.
- production_safe remains false.
- subtype_id-only identity and name-only matching remain blocked.
- This report does not claim production readiness.

