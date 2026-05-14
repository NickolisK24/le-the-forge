# LE Tools Import Context Sidecar Report

- production_safe: false
- source: le_tools_import_diagnostic
- importer: lastepochtools
- build_id: le_tools_offline_buildinfo_stage_context_sample
- generated_at: 2026-05-07T01:50:05+00:00

## Summary

- total_items: 12
- resolved: 8
- needs_context: 2
- needs_review: 1
- deferred: 0
- unresolved: 1
- raw_with_base_type_id: 9
- mapped_with_base_type_id: 9
- mapped_missing_item_type: 12
- requires_test_pairing: 11
- raw_with_subtype_only: 1

## Items

- index=0 slot=helmet raw_type=helm raw_base=0 mapped_base=0 status=resolved bundle=helmet
- index=1 slot=body_armour raw_type=chest raw_base=1 mapped_base=1 status=resolved bundle=body_armor
- index=2 slot=weapon raw_type=axe raw_base=5 mapped_base=5 status=resolved bundle=one_handed_axe
- index=3 slot=weapon raw_type=axe raw_base=12 mapped_base=12 status=resolved bundle=two_handed_axe
- index=4 slot=weapon raw_type=mace raw_base=7 mapped_base=7 status=resolved bundle=one_handed_maces
- index=5 slot=weapon raw_type=sword raw_base=16 mapped_base=16 status=resolved bundle=two_handed_sword
- index=6 slot=idol_altar raw_type=idol_1x1 raw_base=25 mapped_base=25 status=resolved bundle=idol_1x1_eterra
- index=7 slot=idol_altar raw_type=idol_1x1 raw_base=26 mapped_base=26 status=resolved bundle=idol_1x1_lagon
- index=8 slot=weapon raw_type=axe raw_base=None mapped_base=None status=needs_context bundle=null
  - warning: base_type_id is required; resolver will not guess from slug alone.
- index=9 slot=belt raw_type=belt raw_base=None mapped_base=None status=needs_context bundle=null
  - warning: subtype_id was provided but ignored; subtype_id alone is not a valid identity.
  - warning: base_type_id is required; resolver will not guess from slug alone.
- index=10 slot=weapon raw_type=spear raw_base=14 mapped_base=14 status=needs_review bundle=null
  - warning: Forge item type requires manual review before resolution.
- index=11 slot=helmet raw_type=null raw_base=None mapped_base=None status=unresolved bundle=null
  - warning: Missing forge_item_type.

## Safety

- Sidecar is developer-only and production_safe remains false.
- Production importer output is copied for diagnostics and not mutated.
- subtype_id alone and name-only records do not resolve.
- Missing base_type_id for collapsed item type slugs remains needs_context.

## What This Proves

- Raw and mapped import context can be preserved in one diagnostic object.
- The existing importer path preserves mapped base_type_id for ID-backed records.
- Resolver decisions can be attached without changing importer output.

## What Remains Unresolved

- Fixture is synthetic/offline and not a live LET capture.
- Mapped production output still does not expose item_type context.
- No production or non-production consumer is activated by this report.

