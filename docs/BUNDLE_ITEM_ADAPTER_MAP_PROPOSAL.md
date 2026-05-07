# Bundle Item Adapter Map Proposal

## 1. Purpose

This document proposes how current Forge item type and base item representations can eventually map to canonical bundle `item_types` and `base_items`.

It is a planning bridge between the read-only diff diagnostic and a future migration. It does not activate migration, replace loaders, assert full compatibility, change simulation behavior, or make bundle item data production-authoritative.

## 2. Current State Summary

The current read-only diff diagnostic found:

- bundle `item_types`: 50 records
- bundle `base_items`: 1508 records
- Forge static item types: 25 records in `data/items/item_types.json`
- Forge backend constant item type mappings: 30 item type IDs and 34 `base_type_id` mappings
- Forge base items: 115 flattened records
- base item name overlap: 17 normalized names
- precise base item comparison is not possible because `data/items/base_items.json` lacks `base_type_id` and `subtype_id`
- `subtype_id` repeats in the bundle and must be scoped by `base_type_id`
- current Forge subtype-only constant map is empty, so no active flat subtype identity table was detected
- bundle has 16 item types without Forge `base_type_id` mappings, mostly non-equipment or unmigrated types

Expected current diagnostic status is `WARN`, not `PASS`.

## 3. Current Forge Sources

| Source | Contains | Classification | Mapping value | Risks/caveats |
| --- | --- | --- | --- | --- |
| `data/items/item_types.json` | Static item type slugs, names, and slots. | Production-facing static game data. | Useful for Forge slug and slot vocabulary. | Only 25 records; does not include all backend constants or bundle types. |
| `data/items/base_items.json` | Curated base item records grouped by Forge item type slug, with names, level requirements, forging potential, armor, implicit text, and tags. | Production-facing or fallback static game data. | Useful for name/type comparison only. | No `base_type_id` or `subtype_id`; cannot support authoritative composite matching. |
| `backend/app/constants/base_type_id_to_item_type_id.py` | Mapping from Last Epoch `baseTypeID` to Forge item type slug. | Backend constant, likely production-adjacent import/normalization support. | Strongest current bridge from bundle `base_type_id` to Forge slugs. | Covers 34 equipment/idol base types; omits non-equipment types. Some many-to-one mappings collapse 1H/2H variants. |
| `backend/app/constants/item_type_ids.py` | Canonical Forge item type slug list. | Backend constant. | Defines current backend slug vocabulary. | Slugs do not always match bundle `item_type.id` directly. |
| `backend/app/constants/item_type_to_slot.py` | Forge item type slug to equipment slot. | Backend constant. | Useful for slot/legality adapter. | Slot vocabulary differs from bundle categories/slots and may need explicit translation. |
| `backend/app/constants/sub_type_id_to_item_type_id.py` | Empty subtype ID map with warning that subtype IDs are not globally unique. | Guardrail constant. | Confirms Forge currently avoids active flat subtype lookup. | If populated later, must require `base_type_id` context. |
| `backend/app/constants/game_type_to_item_type_id.py` | Raw game type string to Forge item type slug. | Backend constant. | Useful for string-backed mapping from bundle/source type names. | Many-to-one mappings collapse variants; non-equipment types are intentionally omitted. |

These sources are useful for a developer adapter, but they should not be treated as proof that production loaders can switch directly to bundle families.

## 4. Adapter Map Strategy

A future adapter should translate between:

- Forge item type slug
- Forge slot/category
- bundle `item_type.id`
- bundle `base_type_id` / `game_id`
- bundle base item composite ID

Recommended matching order:

1. `base_type_id`-backed match where `BASE_TYPE_ID_TO_ITEM_TYPE_ID` exists.
2. exact slug match where Forge slug equals bundle `item_type.id`.
3. raw game type match through `GAME_TYPE_TO_ITEM_TYPE_ID` when source type is available.
4. normalized name/slug match as advisory only.
5. manual review for non-equipment, collapsed, or ambiguous records.

Rules:

- Do not assume Forge IDs match bundle IDs exactly.
- Do not match base items authoritatively by name alone.
- Do not use `subtype_id` alone.
- Preserve bundle base item identity as a composite using `base_type_id`, `subtype_id`, and canonical bundle ID.
- Treat many-to-one item type mappings, such as one-handed and two-handed weapons collapsing to `axe` or `sword`, as `Needs adapter`.
- Treat non-equipment bundle types as `Deferred` until a consumer explicitly needs them.

## 5. Proposed Adapter Record Shape

Proposed item type adapter record:

```json
{
  "forge_item_type": "helm",
  "forge_slot": "head",
  "bundle_item_type_id": "helmet",
  "bundle_base_type_id": 0,
  "match_method": "base_type_id",
  "confidence": "Verified",
  "production_safe": false,
  "notes": []
}
```

Allowed `match_method` values should start with:

- `base_type_id`
- `exact_slug`
- `game_type`
- `normalized_name`
- `manual_review`

Proposed base item adapter record:

```json
{
  "forge_base_item_id": "string or null",
  "forge_name": "string",
  "bundle_base_item_id": "helmet__0__example",
  "bundle_base_type_id": 0,
  "bundle_subtype_id": 0,
  "match_method": "normalized_name_with_type",
  "confidence": "Partial",
  "production_safe": false,
  "notes": []
}
```

Allowed base item `match_method` values should start with:

- `composite_id`
- `exact_name_with_type`
- `normalized_name_with_type`
- `manual_review`

These are proposed shapes, not production data.

## 6. Migration Readiness Categories

Future mappings should be classified as:

- `Ready candidate`: strong ID-backed match, usually via `base_type_id`, with compatible Forge slot behavior.
- `Needs adapter`: Forge slug differs from bundle slug, but `base_type_id` or game type mapping exists.
- `Needs review`: only name/slug matching is available.
- `Not comparable`: Forge lacks required IDs, usually `base_type_id` and `subtype_id`.
- `Deferred`: non-equipment or unsupported type with no current Forge consumer.
- `Unsafe`: would require `subtype_id` alone, prose inference, or implicit stat interpretation.

Current likely classification:

- Equipment/idol item types with `BASE_TYPE_ID_TO_ITEM_TYPE_ID`: `Ready candidate` or `Needs adapter`.
- Collapsed weapon groups where multiple bundle base types map to one Forge slug: `Needs adapter`.
- Non-equipment bundle types such as blessings, lenses, shards, runes, glyphs, keys, bags, and gold piles: `Deferred`.
- Current Forge base items: mostly `Not comparable` because they lack source IDs.
- Name-only base item overlaps: `Needs review`.

## 7. Known Mapping Risks

- Forge base item set is much smaller than the bundle set.
- Forge base items lack `base_type_id` and `subtype_id`.
- Name-only matching is not authoritative.
- Some bundle item types are non-equipment or unmigrated.
- Forge constants may be partial or stale.
- Current production consumers may depend on simplified item categories.
- Migrating item types before an adapter could break filters, imports, crafting, or item pickers.
- Base items should not be consumed authoritatively until composite IDs are available or current Forge records gain source IDs.
- Many-to-one mappings can lose distinctions between one-handed and two-handed base types.
- Implicit references in bundle `base_items` are not stat mechanics.

## 8. Recommended Migration Path

1. Create a developer-only adapter report.
2. Review item type mappings manually.
3. Add test coverage for mapping assumptions.
4. Migrate item type read-only diagnostics first.
5. Migrate a non-production or developer-only consumer first.
6. Add production fallback visibility.
7. Migrate item type and slot legality consumers.
8. Delay base item production migration until composite IDs can be preserved or current Forge base items gain source IDs.

The adapter should be treated as a bridge, not a new source of truth. The long-term source of truth should remain the validated bundle family plus explicit consumer mapping metadata.

## 9. What Not To Do Yet

- Do not replace item loaders yet.
- Do not migrate `base_items` by name-only matching.
- Do not use `subtype_id` alone.
- Do not mark current base item migration `Authoritative`.
- Do not remove current Forge fallback data.
- Do not map non-equipment types into equipment slots without review.
- Do not treat implicit refs as stat mechanics.
- Do not collapse one-handed and two-handed bundle records without documenting the lost distinction.
- Do not change imports, item pickers, crafting, or planner legality until adapter diagnostics are tested.

## 10. Open Questions

- Which Forge routes/components currently require item type slugs?
- Should Forge adopt bundle `item_type.id` values directly or maintain an adapter permanently?
- Should `base_type_id` be added to current Forge base item records before migration?
- Should current `data/items/base_items.json` be treated as legacy, fallback, or generated cache?
- Which 16 bundle item types lack Forge mapping, and should all be deferred?
- Should non-equipment types be visible in Forge at all?
- What should be the first production consumer of canonical `item_types`?
- How should imports resolve old Forge IDs to bundle IDs?
- How should many-to-one mappings for weapon types be represented without losing legality details?
- Should current Forge slot names be preserved or aligned to bundle slots/categories through an adapter?
