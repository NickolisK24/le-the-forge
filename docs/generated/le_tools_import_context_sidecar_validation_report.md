# LE Tools Import Context Sidecar Validation Report

- status: warning
- production_safe: false

## Summary

- total_items: 12
- resolved: 8
- needs_context: 2
- needs_review: 1
- deferred: 0
- unresolved: 1

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

## Safe Properties

- Validation is developer-only and does not mutate sidecar files.
- production_safe must remain false globally and per item.
- subtype-only, name-only, spear, and collapsed-without-context records cannot resolve.

## Failure Conditions

- production_safe=true anywhere.
- Resolved subtype-only or name-only records.
- Resolved spear records.
- Resolved collapsed slugs without base_type_id context.
- Summary counts that do not match item statuses.

