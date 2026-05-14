# LE Tools Import Stage Context Report

- production_safe: false
- fixture: `le_tools_offline_buildinfo_stage_context_sample`
- fixture source: synthetic_offline_not_captured_from_live_let
- importer accepted fixture directly: true
- test-only pairing used: true
- total items: 12

## Stage Summary

- raw_with_base_type_id: 9
- mapped_with_base_type_id: 9
- raw_missing_base_type_id: 3
- mapped_missing_item_type: 12
- needs_test_only_pairing: 11
- raw_with_subtype_only: 1

## Resolver Status Counts

- resolved: 8
- needs_context: 2
- needs_review: 1
- deferred: 0
- unresolved: 1

## Records

- index=0 slot=helmet raw_base=0 mapped_base=0 mapped_item_type=false status=resolved bundle=helmet
- index=1 slot=body_armour raw_base=1 mapped_base=1 mapped_item_type=false status=resolved bundle=body_armor
- index=2 slot=weapon raw_base=5 mapped_base=5 mapped_item_type=false status=resolved bundle=one_handed_axe
- index=3 slot=weapon raw_base=12 mapped_base=12 mapped_item_type=false status=resolved bundle=two_handed_axe
- index=4 slot=weapon raw_base=7 mapped_base=7 mapped_item_type=false status=resolved bundle=one_handed_maces
- index=5 slot=weapon raw_base=16 mapped_base=16 mapped_item_type=false status=resolved bundle=two_handed_sword
- index=6 slot=idol_altar raw_base=25 mapped_base=25 mapped_item_type=false status=resolved bundle=idol_1x1_eterra
- index=7 slot=idol_altar raw_base=26 mapped_base=26 mapped_item_type=false status=resolved bundle=idol_1x1_lagon
- index=8 slot=weapon raw_base=None mapped_base=None mapped_item_type=false status=needs_context bundle=null
  - warning: base_type_id is required; resolver will not guess from slug alone.
- index=9 slot=belt raw_base=None mapped_base=None mapped_item_type=false status=needs_context bundle=null
  - warning: subtype_id was provided but ignored; subtype_id alone is not a valid identity.
  - warning: base_type_id is required; resolver will not guess from slug alone.
  - warning: subtype_id is present without base_type_id; this is not sufficient context.
- index=10 slot=weapon raw_base=14 mapped_base=14 mapped_item_type=false status=needs_review bundle=null
  - warning: Forge item type requires manual review before resolution.
- index=11 slot=helmet raw_base=None mapped_base=None mapped_item_type=false status=unresolved bundle=null
  - warning: Missing forge_item_type.
  - warning: No item_type-like field was found; name-only matching is not attempted.

## Recommendations

- Keep this comparison developer-only; production importer output is unchanged.
- Thread base_type_id and reviewed item type context explicitly before any non-production consumer uses bundle IDs.
- Do not use subtype_id alone or name-only matching for canonical item type resolution.
- Mapped output preserving base_type_id is useful, but item_type context still needs an explicit diagnostic source.
- Records missing baseTypeID must remain needs_context.
- Review spear or other blocked aliases before adding translations.

