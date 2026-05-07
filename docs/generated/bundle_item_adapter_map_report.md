# Bundle Item Adapter Map Report

Bundle path: `D:\Forge\last-epoch-data\data_bundle`

## Summary

- Bundle item_types: 50
- Forge static item types: 25
- Forge item type IDs: 30
- Forge base_type_id mappings: 34
- Adapter records: 51
- production_safe: false for every proposed record

## Readiness Counts

- Deferred: 8
- Needs adapter: 15
- Needs review: 8
- Not comparable: 1
- Ready candidate: 19

## Match Method Counts

- base_type_id: 34
- manual_review: 8
- none: 9

## Unmapped Forge Types

- spear

## Unmapped Bundle Item Types

- blessing (base_type_id=34, readiness=Needs review)
- greater_lens (base_type_id=35, readiness=Needs review)
- arctus_lens (base_type_id=36, readiness=Needs review)
- mesembria_lens (base_type_id=37, readiness=Needs review)
- eos_lens (base_type_id=38, readiness=Needs review)
- dysis_lens (base_type_id=39, readiness=Needs review)
- unused (base_type_id=40, readiness=Needs review)
- idol_altar (base_type_id=41, readiness=Needs review)
- affix_shard (base_type_id=101, readiness=Deferred)
- rune (base_type_id=102, readiness=Deferred)
- glyph (base_type_id=103, readiness=Deferred)
- key (base_type_id=104, readiness=Deferred)
- lost_memory (base_type_id=105, readiness=Deferred)
- resonance (base_type_id=106, readiness=Deferred)
- woven_echo (base_type_id=107, readiness=Deferred)
- bag (base_type_id=108, readiness=Deferred)

## Subtype Identity Risk

No active subtype_id-only mapping was detected.

## Proposed Adapter Records

- forge=helm slot=head bundle=helmet base_type_id=0 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=chest slot=body bundle=body_armor base_type_id=1 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=belt slot=waist bundle=belt base_type_id=2 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=boots slot=feet bundle=boots base_type_id=3 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=gloves slot=hands bundle=gloves base_type_id=4 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=axe slot=weapon bundle=one_handed_axe base_type_id=5 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=dagger slot=weapon bundle=one_handed_dagger base_type_id=6 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=mace slot=weapon bundle=one_handed_maces base_type_id=7 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=sceptre slot=weapon bundle=one_handed_sceptre base_type_id=8 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=sword slot=weapon bundle=one_handed_sword base_type_id=9 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=wand slot=weapon bundle=wand base_type_id=10 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=fist slot=weapon bundle=one_handed_fist base_type_id=11 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=axe slot=weapon bundle=two_handed_axe base_type_id=12 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=mace slot=weapon bundle=two_handed_mace base_type_id=13 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=polearm slot=weapon bundle=two_handed_spear base_type_id=14 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=staff slot=weapon bundle=two_handed_staff base_type_id=15 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=sword slot=weapon bundle=two_handed_sword base_type_id=16 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=quiver slot=offhand bundle=quiver base_type_id=17 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=shield slot=offhand bundle=shield base_type_id=18 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=catalyst slot=offhand bundle=catalyst base_type_id=19 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=amulet slot=neck bundle=amulet base_type_id=20 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=ring slot=finger bundle=ring base_type_id=21 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=relic slot=relic bundle=relic base_type_id=22 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=bow slot=weapon bundle=bow base_type_id=23 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=crossbow slot=weapon bundle=crossbow base_type_id=24 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_1x1 slot=idol bundle=idol_1x1_eterra base_type_id=25 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=idol_1x1 slot=idol bundle=idol_1x1_lagon base_type_id=26 method=base_type_id readiness=Needs adapter confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
  - Forge slug differs from bundle item_type.id; adapter translation is required.
- forge=idol_2x1 slot=idol bundle=idol_2x1 base_type_id=27 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_1x2 slot=idol bundle=idol_1x2 base_type_id=28 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_3x1 slot=idol bundle=idol_3x1 base_type_id=29 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_1x3 slot=idol bundle=idol_1x3 base_type_id=30 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_4x1 slot=idol bundle=idol_4x1 base_type_id=31 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_1x4 slot=idol bundle=idol_1x4 base_type_id=32 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=idol_2x2 slot=idol bundle=idol_2x2 base_type_id=33 method=base_type_id readiness=Ready candidate confidence=Verified production_safe=false
  - ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID.
- forge=spear slot=null bundle=null base_type_id=None method=none readiness=Not comparable confidence=Unknown production_safe=false
  - No bundle item_type match found from ID or normalized name.
- forge=null slot=null bundle=blessing base_type_id=34 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=greater_lens base_type_id=35 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=arctus_lens base_type_id=36 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=mesembria_lens base_type_id=37 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=eos_lens base_type_id=38 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=dysis_lens base_type_id=39 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=unused base_type_id=40 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=idol_altar base_type_id=41 method=manual_review readiness=Needs review confidence=Partial production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=affix_shard base_type_id=101 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=rune base_type_id=102 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=glyph base_type_id=103 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=key base_type_id=104 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=lost_memory base_type_id=105 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=resonance base_type_id=106 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=woven_echo base_type_id=107 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.
- forge=null slot=null bundle=bag base_type_id=108 method=none readiness=Deferred confidence=Unknown production_safe=false
  - Bundle item_type has no current Forge mapping.

## Recommendation

Review Needs adapter and Deferred records manually, then add tests for accepted item type mappings before any production loader migration.

