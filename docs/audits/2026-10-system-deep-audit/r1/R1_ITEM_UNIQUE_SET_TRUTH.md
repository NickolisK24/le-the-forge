# R1 Item / Unique / Set Truth (R1.8)

## Raw evidence available

None. `MasterItemsList`, `UniqueList` and `SetBonusesList` were parsed during the 1.4.6 run, but the raw TypeTree dicts were never kept (`.gitignore` excludes them). Without raw, the 1.4.6 exports cannot be re-derived or checked field by field.

The denominator reports these classes as RAW_MISSING, and field survival reports them as `BLOCKED_NO_RAW`.

## R1 extraction path (runs in the operator extraction)

1. `r1_operator_dumps.py typetrees` dumps every instance of `ItemList`, `UniqueList` and `SetBonusesList`, plus every other in-scope class, to `extracted_raw/typetree/<Class>.json`. Dumps carry the game build stamp and fail loud.
2. `build_canonical_typetree_domains.py` wraps each dump in a **lossless canonical envelope** (`exports_canonical/typetree/<Class>.json`):
   - every raw field is carried unchanged;
   - identity is the source `path_id`, plus the numeric ids inside the data (`baseTypeID`, `subTypeID`, unique `id`, `setID`);
   - nothing is keyed by name.
3. Field survival automatically checks layout → raw (decoder coverage, including TypeTreeGenerator's inherited-field gap, Known Bug #3) and raw → canonical (must be 100% CARRIED).

This preserves everything R1.8 lists:
- numeric ids, `baseTypeID` and `subTypeID`;
- requirements, level and attack rate;
- structured implicits;
- unique and set modifiers with numeric property ids;
- variants as separate records;
- `effectiveLevelForLP`;
- legendary and forging fields;
- every source relationship.

Typed domain views come later and are layered on top of the envelope, never instead of it.

## Legacy export measurements (1.4.6, informational)

| Topic | Legacy `exports_json` | Note |
| --- | --- | --- |
| Item identity | `baseTypeID` and `subTypeID` present; 1,508 subtypes, 0 duplicates | Forge's curated `base_items.json` uses names, and 98 of 115 do not exist (LOSS-4). That is a Forge-side loss (R2). |
| Implicits | Structured (`property`, `modifierType`, `tags`, `value`, `maxValue`) | `property` is the decoded SP name. The numeric id is derivable from the SP table but not stored. |
| Requirements, attack rate | `classRequirement`, `subClassRequirement`, `levelRequirement` and `attackRate` per subtype | Carried |
| Unique identity | Numeric `id`; 409 uniques, 0 duplicate ids or names | Variants are distinct records in the export. Forge's sync keys them by slug (LOSS-5). |
| Unique mods | 2,047 mods with `value`, `maxValue`, `rollId`, `canRoll` and `modifierType` | `property` is a string name; the numeric id is not stored |
| `effectiveLevelForLP` | Present on 201 of 409 uniques | Absent in Forge's v2 bundle and TS types (Forge-side) |
| Set bonuses | 24 groups, `mappingConfidence` from a manual `SET_NAMES` table | Set names are partly hand-mapped |

Layout-based field survival (informational, because the layout index lacks `UniqueList_Entry`, `ItemList_BaseItem`, `ItemList_SubItem` and `ItemList_EquipmentImplicit`) cannot attribute most legacy item and unique fields to a source path. That is why the gate requires raw dumps.

## Status

| Domain | Classification | Raw | Canonical | Consumer state |
| --- | --- | --- | --- | --- |
| item_bases (`ItemList`) | REQUIRED_NOW | RAW_MISSING | none (operator) | UNSUPPORTED until extracted; legacy QUARANTINED |
| uniques (`UniqueList`) | REQUIRED_NOW | RAW_MISSING | none (operator) | same |
| set_bonuses (`SetBonusesList`) | REQUIRED_NOW | RAW_MISSING | none (operator) | same |
| unique_item_mechanics (37 `UniqueItemComponent` classes) | REQUIRED_FUTURE | RAW_MISSING | none (operator) | UNSUPPORTED |
