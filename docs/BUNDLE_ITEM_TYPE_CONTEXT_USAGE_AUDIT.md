# Bundle Item Type Context Usage Audit

## 1. Purpose

This audit identifies where Forge item type values flow today and whether those paths have enough context to safely resolve canonical bundle `item_type` IDs later.

This does not modify production paths, activate bundle consumption, or thread `base_type_id` through the app. It documents current usage so the first non-production diagnostic consumer can be chosen without guessing.

## 2. Current Diagnostic Baseline

The developer-only dry-run and context reports currently show:

| Metric | Count |
| --- | ---: |
| Total inputs inspected | 64 |
| Inputs with `base_type_id` | 34 |
| Inputs missing `base_type_id` | 30 |
| Resolved | 34 |
| Needs context | 30 |
| Needs review | 0 |
| Deferred | 0 |
| Unresolved | 0 |
| Subtype-only matching attempted | false |

Collapsed Forge item type groups that require `base_type_id` context:

- `axe`
- `mace`
- `sword`
- `idol_1x1`

`base_type_id` is required because several Forge slugs collapse distinct canonical bundle item types. `subtype_id` alone is forbidden because Last Epoch `subTypeID` values are scoped under `baseTypeID`, not globally unique. All mappings remain `production_safe=false`; the current tooling is diagnostic-only.

## 3. Search Scope and Method

The audit searched backend, frontend, tests, scripts, constants, and static data for item type context terms including:

- `item_type`, `itemType`, `item_type_id`, `itemTypeId`
- `base_type_id`, `baseTypeID`, `baseTypeId`
- `subtype_id`, `subTypeID`, `subTypeId`
- `slot`, gear slot, base item, affix eligibility
- import, LE Tools import, Maxroll import
- crafting, optimizer, BIS, item browser, gear editor, idol, weapon type

No rewrites were performed. Findings below reflect current code and data shape only.

## 4. Backend Usage Sites

| File/path | Function/class/constant | Current item type input | Has `base_type_id`? | Has `subtype_id`? | Uses slot/category only? | Surface | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `backend/app/constants/base_type_id_to_item_type_id.py` | `BASE_TYPE_ID_TO_ITEM_TYPE_ID` | Numeric base type to Forge slug | Present | No | No | Diagnostic/supporting constant | Low | Strongest current ID-backed bridge. Covers 34 base types and explicitly warns that `subTypeID` is not globally unique. |
| `backend/app/constants/item_type_ids.py` | `ITEM_TYPE_IDS` | Forge item type slugs | Missing | No | No | Production/supporting constant | Medium | Source of 30 missing-context dry-run inputs. Slugs alone are insufficient for collapsed groups. |
| `backend/app/constants/item_type_to_slot.py` | `ITEM_TYPE_TO_SLOT` | Forge slug to slot | Missing | No | Yes | Production/supporting constant | Medium | Useful for slot/category display, not canonical bundle resolution. |
| `backend/app/constants/sub_type_id_to_item_type_id.py` | `SUB_TYPE_ID_TO_ITEM_TYPE_ID` | Empty subtype map | No | No active map | No | Guardrail constant | Low | Explicitly avoids subtype-only identity. Should remain unused for adapter resolution. |
| `backend/app/constants/game_type_to_item_type_id.py` | `GAME_TYPE_TO_ITEM_TYPE_ID` | Game type strings to Forge slugs | Missing | No | No | Supporting constant | Medium | Can support advisory aliasing, but not authoritative without base type context. |
| `backend/app/services/importers/lastepochtools_importer.py` | `_get_item_subtype_map`, `_decode_base_item_id`, gear parsing | LE Tools gear IDs, `baseTypeID`, `subTypeID`, slot | Present when decoded | Present when decoded | Also has slot | Importer | Low for diagnostics | Best current non-production diagnostic surface. Parsed gear can emit `base_type_id` without changing production loaders. |
| `backend/app/services/importers/maxroll_importer.py` | gear parsing / slot normalization | Slot, item name, possible `baseTypeId` labels | Unclear/mostly missing | Unclear | Yes | Importer | Medium | Final parsed gear does not consistently preserve `base_type_id`; needs context threading before bundle resolution. |
| `backend/app/routes/ref.py` | `get_item_types` | Static item type records | Missing | No | Category/slot style | Production API | High | Public reference API should not be changed first. Current payload lacks bundle IDs. |
| `backend/app/routes/ref.py` | `_get_affixes_inner`, affix endpoints | Query `slot` / item type string | Missing | No | Yes | Production API | High | Affix eligibility is out of scope for first item type migration and lacks base type context. |
| `backend/app/routes/ref.py` | `get_base_items_endpoint` | Slot-filtered base item lists | Missing | No | Yes | Production API | High | Current `data/items/base_items.json` shape lacks `base_type_id` and `subtype_id`. |
| `backend/app/routes/ref.py` | `get_implicit_stat_endpoint(item_type)` | Path item type slug | Missing | No | No | Production API | High | Implicit mechanics remain out of scope; slug-only lookup is unsafe for canonical matching. |
| `backend/app/routes/profile.py` | profile/craft session output | `CraftSession.item_type` string | Missing | No | No | Production API | High | Existing persisted/session model is string-only. |
| `backend/app/models/__init__.py` | `CraftSession.item_type` | String item type | Missing | No | No | Production model | High | Persisted model change should not be first diagnostic step. |
| `backend/app/models/__init__.py` | `ItemType` | Name/category/base implicit | Missing | No | Category | Production model | Medium | Does not carry bundle source IDs. |
| `backend/app/schemas/__init__.py` | `CraftSessionCreateSchema.item_type` | Request item type string | Missing | No | No | Production schema | High | API contract is slug-only today. |
| `backend/app/services/craft_service.py` | craft session creation | `item_type` string | Missing | No | No | Production service | High | Creates items by string and persists string; not a safe first consumer. |
| `backend/app/engines/item_engine.py` | `create_item` | Base type string | Missing | No | No | Production engine | High | Simulation/crafting path must not be modified for diagnostics. |
| `backend/app/engines/base_engine.py` | base item lookup helpers | Slot/name/category | Missing | No | Yes | Production engine | High | Backward-compatible static base item lookup is not precise enough for canonical matching. |
| `backend/app/engines/affix_engine.py` | affix pool helpers | Item type string / applicable_to | Missing | No | Sometimes | Production engine | High | Affix eligibility migration is later; current usage is string-based. |
| `backend/app/engines/fp_engine.py` | `roll_base_fp` | Item type string | Missing | No | No | Production engine | Medium | Crafting rules are slug-based. |
| `backend/app/engines/craft_engine.py` | craft simulation output | Item type string | Missing | No | No | Production engine | High | Simulation behavior should remain unchanged. |
| `backend/app/engines/craft_simulator.py` | craft simulation output | Item type string | Missing | No | No | Production engine | High | Simulation behavior should remain unchanged. |
| `backend/app/engines/validators.py` | gear/slot validation | Slot and slot type | Missing | No | Yes | Production validation | High | Slot-only checks cannot resolve canonical bundle item types. |
| `backend/app/engines/gear_upgrade_ranker.py` | candidate generation | Slot/meta-slot | Missing | No | Yes | Production engine | High | Optimizer/BIS-style logic may depend on simplified categories. |
| `backend/app/engines/comparison_engine.py` | gear comparison | Gear slot/name | Missing | No | Yes | Production engine | Medium | No source IDs available. |
| `backend/app/engines/build_serializer.py` | build serialization | Gear slot/name | Missing | No | Yes | Production/supporting | Medium | Existing serialized builds likely lack source IDs. |
| `backend/app/services/stat_resolution_pipeline.py` | stat resolution | Gear/slot/stat inputs | Missing | No | Yes | Production service | High | Not an item type migration surface. |
| `backend/scripts/dry_run_bundle_item_type_resolver.py` | diagnostic dry run | Fixture/current constants | Present where constants provide it | No | No | Developer-only | Low | Existing diagnostic surface, safe to extend only for reporting. |
| `backend/scripts/report_bundle_item_type_context.py` | context report | Fixture/current constants | Present/missing by source | No | No | Developer-only | Low | Existing baseline for this audit. |
| `backend/tests/*bundle_item*` | diagnostic tests | Fixture data | Controlled | Controlled | No | Test-only | Low | Useful guardrails, not production consumers. |

## 5. Frontend Usage Sites

| File/path | Component/hook/store/type | Current item type input | Has `base_type_id`? | Uses slot/category only? | Surface | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `frontend/src/lib/api.ts` | `refApi.itemTypes` | `{ name, category }` records | Missing | Category | Production client API | High | Client contract does not expose source IDs. |
| `frontend/src/lib/api.ts` | `refApi.baseItems`, `baseItemsBySlot` | Slot-keyed base item records | Missing | Yes | Production client API | High | Mirrors backend static base item shape without `base_type_id` or `subtype_id`. |
| `frontend/src/lib/api.ts` | `BaseItemDef` | Base item fields | Missing | Mostly | Production type | High | No canonical identity fields. |
| `frontend/src/hooks/index.ts` | `useItemTypes`, `useBaseItems`, `useAffixes` | Item type/slot query values | Missing | Yes | Production hooks | High | Hook layer is not a safe first resolver surface. |
| `frontend/src/store/index.ts` | `CraftUIState.itemType` | Item type string | Missing | No | Production state | High | Crafting UI stores slug/name context only. |
| `frontend/src/types/index.ts` | `GearSlot`, craft payload types | Slot/item type strings | Missing | Yes | Production types | High | Types do not carry optional source IDs. |
| `frontend/src/lib/gameData.ts` | `GearItem` | `slot`, optional `item_type` | Missing | Yes | Production/supporting type | Medium | No `base_type_id` context. |
| `frontend/src/components/features/craft/CraftSimulatorPage.tsx` | Craft simulator UI | Store item type string, affix slot query | Missing | Yes | Production UI | High | Sends slug-only payloads to crafting API. |
| `frontend/src/components/crafting/BaseItemSelector.tsx` | Base item selector | Flattens base items by slot | Missing | Yes | Production UI | High | Synthesizes UI IDs from slot/name, not source IDs. |
| `frontend/src/components/features/build/GearEditor.tsx` | Gear editor | Gear slot/meta-slot | Missing | Yes | Production UI | High | Should not be first bundle consumer. |
| `frontend/src/components/features/build/ItemPicker.tsx` | Item picker | Meta slots and base items by slot | Missing | Yes | Production UI | High | `weapon`, `offhand`, and `idol` meta slots collapse meaningful bundle distinctions. |
| `frontend/src/components/features/build/UniqueItemPicker.tsx` | Unique picker | Slot/meta-slot filtering | Missing | Yes | Production UI | Medium | Unique/set mechanics are out of scope. |
| `frontend/src/components/bis/SlotSelector.tsx` | BIS slot selector | Slot type | Missing | Yes | Production UI | High | BIS/optimizer migration requires separate planning. |
| `frontend/src/pages/bis/*` | BIS pages | Slot/category inputs | Missing | Yes | Production UI | High | Depends on simplified categories. |
| `frontend/src/services/bisApi.ts` | BIS API client | Slot types | Missing | Yes | Production client API | High | No source IDs in request/response model. |
| `frontend/src/logic/conditionalStatEngine.ts` | conditional stat rules | `condition.itemType` string | Missing | No | Production logic | Medium | Name/slug-only matching is not authoritative. |

## 6. Data Source Usage Sites

| File/path | Carries item type slug? | Carries `base_type_id`? | Carries `subtype_id`? | Carries slot/category? | Surface | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `data/items/item_types.json` | Yes | No | No | Yes | Static production/fallback data | 25 records. Useful for current UI/API, not enough for bundle resolution. |
| `data/items/base_items.json` | Keyed by category/slot | No | No | Yes | Static production/fallback data | 115 flattened records. Name/slot only, not suitable for canonical base item matching. |
| `data/items/items.json` | Source-like base type records | Yes, `baseTypeID` | Yes, nested `subTypes[].subTypeID` | Derivable | Static source/supporting data | Best local source for ID-bearing diagnostics; not the current production base item API shape. |
| `backend/app/constants/base_type_id_to_item_type_id.py` | Yes | Yes | No | Indirect | Supporting constant | Best current bridge from source ID to Forge slug. |
| `backend/app/constants/item_type_ids.py` | Yes | No | No | No | Supporting constant | Slug-only list. |
| `backend/app/constants/item_type_to_slot.py` | Yes | No | No | Yes | Supporting constant | Slot normalization only. |
| `backend/app/constants/game_type_to_item_type_id.py` | Yes | No | No | No | Supporting constant | String aliases only. |
| `backend/app/constants/sub_type_id_to_item_type_id.py` | No active map | No | Empty | No | Guardrail constant | Confirms subtype-only identity should not be used. |
| `data/world/loot_tables.json` | Numeric item type fields | Unclear | Unclear | Loot categories | Generated/static data | Deferred. Loot table fields are not a safe first item type migration surface. |

## 7. Context Availability Classification

### A. Ready For Diagnostic Resolver

These sites have `forge_item_type` plus `base_type_id`, or can derive it from existing ID-backed constants without production changes:

- `backend/app/constants/base_type_id_to_item_type_id.py`
- `backend/app/services/importers/lastepochtools_importer.py` parsed gear entries where `base_type_id` is decoded or emitted
- `data/items/items.json` as a local source-like artifact for diagnostics
- Existing developer-only dry-run and context report modules/scripts

### B. Needs Context Threading

These sites have Forge item type or slot values but lack reliable `base_type_id`:

- `backend/app/constants/item_type_ids.py`
- `backend/app/constants/item_type_to_slot.py`
- `data/items/item_types.json`
- `data/items/base_items.json`
- `backend/app/routes/ref.py` reference item, base item, affix, and implicit endpoints
- `backend/app/services/craft_service.py` and `CraftSession` model/schema paths
- `backend/app/services/importers/maxroll_importer.py`
- Frontend craft, gear editor, item picker, BIS, API, hook, and type layers

### C. Adapter Needed

These mappings have ID-backed evidence but Forge and bundle names differ or Forge slugs collapse multiple bundle concepts:

- Simple slug aliases such as `helm -> helmet`
- Slot/category normalization such as `chest -> body_armor`
- Weapon splits for `axe`, `mace`, and `sword`
- Legacy alias `polearm -> two_handed_spear`
- Idol splits for `idol_1x1` into Eterra/Lagon bundle item types

### D. Unsafe / Not Enough Information

These are not safe for canonical resolution:

- Name-only base item matching
- Slot/meta-slot-only paths such as `weapon`, `offhand`, and `idol`
- Frontend-only item state without source IDs
- Current `data/items/base_items.json` flattened records
- Any path that would require `subtype_id` without `base_type_id`

### E. Deferred

These are outside the first item type context migration:

- Non-equipment bundle-only item types
- Loot table/world item type group fields
- Blessings, lenses, crafting materials, and other non-equipment categories
- Unique/set special mechanics
- Affix eligibility and implicit stat mechanics

## 8. First Safe Non-Production Diagnostic Surface Recommendation

The first safe surface should be a developer-only LE Tools import context dry-run report built around `backend/app/services/importers/lastepochtools_importer.py`.

Why this is safe:

- The importer already decodes or preserves `base_type_id` for parsed gear.
- It has access to slot context and, in decoded paths, `(baseTypeID, subTypeID)`.
- It can call the existing dry-run resolver and report diagnostics without changing importer output.
- It does not require frontend, API, production loader, simulation, database, or static data changes.
- It can warn on missing context instead of falling back to slug/name matching.

Inputs it has today:

- Forge slot or equipment slot
- LE Tools encoded base item ID in supported paths
- `baseTypeID` from import payloads or decoded item IDs
- `subTypeID` in decoded paths, only usable together with `baseTypeID`

Context still needed:

- Ensure every diagnostic input passed to the resolver includes `forge_item_type` and `base_type_id`.
- Treat missing `base_type_id` as `needs_context`.
- Never derive canonical bundle item type from `subtype_id` alone.

Recommended output:

- Import item slot
- Current Forge item type or slot
- `base_type_id` if available
- `subtype_id` if available, clearly scoped under `base_type_id`
- Dry-run status
- Bundle item type ID when resolved
- Warnings for collapsed groups and missing context

Tests required before use:

- LE Tools sample gear with `baseTypeID` resolves through accepted direct mapping.
- Collapsed weapon slugs without `base_type_id` return `needs_context`.
- `idol_1x1` without `base_type_id` returns `needs_context`.
- `subtype_id` alone is ignored or rejected.
- Import diagnostics do not alter importer return payloads.
- `production_safe` remains false.

Production behavior remains unchanged because this should be implemented as a separate developer-only script/report, not as a route, model change, loader replacement, or importer output mutation.

## 9. Risks Found

- Item type slug alone is insufficient for collapsed groups.
- `axe`, `mace`, and `sword` need one-handed/two-handed `base_type_id` context.
- `idol_1x1` needs Eterra/Lagon `base_type_id` context.
- Current `data/items/base_items.json` lacks composite game IDs.
- Forge constants may be partial or stale.
- Frontend state and API payloads commonly use slot/category only.
- Imports may lose source IDs if not preserved at parse time.
- Optimizer/BIS logic may depend on simplified categories.
- Name-only base item matching is unsafe.
- `subtype_id` alone must never become sufficient context.

## 10. Recommended Next Step

Create a developer-only LE Tools import context dry-run script that feeds parsed import item type context into the existing bundle item type dry-run resolver and reports `resolved`, `needs_context`, `needs_review`, `deferred`, and `unresolved` without changing importer output or production behavior.

## 11. Open Questions

- Which importer payload examples should become the first diagnostic fixtures?
- Where should `base_type_id` enter the Forge data model later if production migration becomes appropriate?
- Should item importers preserve source `base_type_id` and `subtype_id` in a diagnostic-only sidecar before any model/API changes?
- Should `data/items/base_items.json` eventually be expanded with source IDs before bundle-backed base item migration?
- Should frontend item type types include optional `base_type_id` only after backend support exists?
- Which collapsed item groups affect current user-facing features most?
- How should old builds/imports without `base_type_id` be handled later?
- Should Maxroll imports get a separate context audit before any resolver integration?
- Should non-equipment bundle item types stay permanently deferred for Forge, or become separate non-equipment families later?
