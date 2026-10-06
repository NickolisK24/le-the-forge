# R2 Identity Policy (R2-03)

**Status: design only.**

## Rules

1. **Source identity wins.** Where the game serializes an id, that id (or a composite of ids) is the identity. A display name, slug, array position in a Forge file, or sequential order is never identity.
2. **Names are presentation.** Names may be empty, repeated or renamed by a patch:
   - the canonical affix contract says so explicitly;
   - 98 affix names are duplicated;
   - 184 skills collapse to 161 by name (REL-6).

   No lookup by name may resolve game data, except the explicitly versioned importer alias tables (see "Third-party ids" below).
3. **Positional identity only where the game defines it.** Where the game itself identifies a thing by its position in a serialized list (mastery index, property index within an ability), the identity is the composite `(owner id, source index)`. The index is the one in the **source** list, carried by the canonical export. It is never the position in a Forge-side array.
4. **Path ids are evidence, not identity.** Serialized-object `path_id`s are carried for joins *within one snapshot*, for example tree → ability. They change between builds, so they are never persisted in builds or URLs.
5. **Typed ids in code.** Every identity has a distinct type: Python `NewType`/dataclass, TypeScript branded type. An `AffixId` cannot be passed where a `UniqueId` is expected, and an `int` cannot be passed for either. Lookups return `Found | Missing(reason)`. They never return `None` or `0` silently (R2_FALLBACK_AUDIT.md).
6. **Persisted references carry `data_version`.** An id is meaningful only together with the dataset that defined it. Builds persist ids plus `data_version` (R2_DATABASE_PROVENANCE_PLAN.md).

## Canonical identities

The column "Source evidence" refers to the il2cpp layout and the 1.4.6 exports. Identities marked *confirm in dump* are expected from the layout but must be confirmed against the 1.5 TypeTree dump before the typed view is frozen (R2-P04).

| Family | Canonical identity | Type | Source evidence | Notes |
| --- | --- | --- | --- | --- |
| Class | `class_id` | int | `CharacterClass.classID`; exports `classes[].id` 0–4 | `treeID` (`pr-1`, `mg-1`, ...) identifies the passive tree, not the class |
| Mastery | `(class_id, mastery_index)` | composite | `CharacterClass.masteries` list; index 0 = base class, 1–3 = masteries in **source order** | The game identifies masteries by position. Source order is Mage [Sorcerer, Spellblade, Runemaster], Primalist [Beastmaster, Shaman, Druid], Sentinel [Void Knight, Forge Guard, Paladin], Acolyte [Necromancer, Lich, Warlock], Rogue [Bladedancer, Marksman, Falconer]. `MASTERY_MAP` contradicts this for three classes (REL-1). |
| Passive tree | `class_id` (one tree per class) + `tree_id` string | int + str | `CharacterTree.characterClassID`; canonical `tree_id` | |
| Passive node | `(class_id, node_id)` | composite | canonical identity contract: `(tree_class, node_id)`, `node_id` = `SkillTreeNode.id` (u8) | `node_id` is unique only within its tree. The mastery of a node is `node.mastery` (source index), resolved through the class's masteries. |
| Ability | `ability_id` | int (AbilityID enum) | `Ability.playerAbilityID` | Also has `path_id` (join only) |
| Skill | `ability_id` of a player-usable ability | int | Ability + class `knownAbilities` / `unlockableAbilities` | A "skill" is an ability a class can slot. Variants with different `ability_id`s (for example tree-less variants, REL-6) are different skills. |
| Skill (specialization) tree | `tree_id` | str | `Tree.treeID` (`an0my`, `fl45`, ...); canonical `tree_id` | Joins its ability by `SkillTree.ability` PPtr → `ability_id`. Never joined by skill name (REL-4, REL-10). |
| Skill tree node | `(tree_id, node_id)` | composite | canonical `(tree_class, node_id)`; `tree_class` ↔ `tree_id` 1:1 within a snapshot | |
| Prerequisite edge | `(tree_id, node_id) → (tree_id, required_node_id, points_required)` | edge | `SkillTreeNode.requirements[]` (`RequirementFromNode`) | A node may have 0..n edges (R2_RELATIONSHIP_MODEL.md) |
| Weaver node | `(tree_id, node_id)` | composite | canonical weaver tree | |
| Affix | `affix_id` | int | canonical `affix_id`; identity contract | 116 duplicate `affix_id` values in Forge `data/` (REL-16) are a Forge-side flattening artefact; canonical has 1,112 unique |
| Affix property | `(affix_id, property_index)` | composite | canonical `properties[].index` (0 = top-level, then extra rolls) | Each property keeps its own `property` (SP), `modifier_type`, `tags`, `special_tag` and its own rolls |
| Stat property (master) | `sp_id` | int (SP enum) | canonical property definitions | |
| Player property | `player_property_id` | int | canonical property definitions | |
| Ability property | `(ability_id, property_index)` | composite | canonical property definitions; affix encoding validated (`specialTag + 1`) | |
| Tree stat property reference | `raw` + resolution `{namespace, index}` | value object | canonical `stats[].property` | UNKNOWN_PROPERTY_TYPE / UNRESOLVED are explicit states, never coerced |
| Base item type | `base_type_id` | int | `baseTypeID` 0–41 in the 1.4.6 items export | Replaces the curated `base_items.json` identity and the truncated `BASE_TYPE_ID_TO_ITEM_TYPE_ID` map (DRIFT-7) |
| Item subtype | `(base_type_id, sub_type_id)` | composite | `subTypeID` within its base type | The game identifies items by this pair. Importer ids map to it, never to a sequential index (IMP-4). |
| Implicit | `(base_type_id, sub_type_id, implicit_index)` | composite | `EquipmentItem.implicits[]` | Structured property, modifier type, tags and values. Free text is presentation only (LOSS-4). |
| Unique | `unique_id` | int | uniques export `id`; `UniqueList.uniques` (*confirm in dump*) | Base type plus **a list** of subtypes. Never resolved by slug or first match. |
| Unique mod | `(unique_id, mod_index)` with `roll_id` | composite | uniques export `mods[]`, `rollId` | |
| Set | `set_id` | int | `UniqueList.setID` / set bonus data (*confirm in dump*) | Set members are uniques with `set_id`; bonuses keyed by `(set_id, pieces_required)` |
| Blessing | `(base_type_id, sub_type_id)` | composite | blessings export: item subtypes (`subTypeID`) with structured implicits (*confirm the base type in dump*) | A blessing is an item; it uses the item identity |
| Ailment | `ailment_id` | int (AilmentID enum) | `Ailment.id` | |
| Enum value | `(enum_full_name, int value)` | composite | `enums.json` (`fullName`, values) | Labels are presentation; unknown values stay `UNKNOWN_VALUE` with the raw int |
| Localization string | `key` | str | string table key | Text is presentation |
| Dataset | `data_version` | str | R2_CANONICAL_CONSUMPTION_CONTRACT.md | |

## Composite identities the game genuinely requires

| Composite | Why it cannot be flattened |
| --- | --- |
| `(class_id, mastery_index)` | Masteries have no id of their own in the layout. The passive node's `mastery` field is the index. |
| `(class_id, node_id)` / `(tree_id, node_id)` | Node `id` is a u8 unique only within its tree |
| `(base_type_id, sub_type_id)` | `subTypeID` restarts at 0 in every base type |
| `(affix_id, property_index)` | Hybrid affixes carry 2+ properties with independent rolls (REL-7, LOSS-2) |
| `(ability_id, property_index)` | Ability properties are indexed per ability |
| `(enum_full_name, value)` | Nested enums share bare names (`AffixList.AffixType` vs others) |

String forms for URLs and JSON keys must be lossless and unambiguous, for example:
- `node:ac-1:86`;
- `item:34:3`;
- `affix:1112:1`.

They are always produced by one formatter and parsed by one parser per type.

## Third-party ids (importers, R4)

Last Epoch Tools and Maxroll ids are **external identities**. R2 defines the mapping shape; R4 repairs the importers.

```
external_id_map/<provider>/<data_version>.json
{ "provider": "lastepochtools", "data_version": "...",
  "maps": { "base_item": {"<external id>": "item:<base>:<sub>"}, "skill_tree": {"<external>": "tree:<tree_id>"},
            "passive_node": {...}, "affix": {...}, "unique": {...} },
  "unmapped": [{"kind": "...", "external_id": "...", "reason": "..."}] }
```

Rules:
- the map is versioned per `data_version`;
- every unmapped external id is listed, never guessed;
- an import that hits an unmapped id reports it to the user (IMP-5, IMP-7, R4);
- the integer-`baseTypeID`-by-sequential-index lookup (IMP-4) is replaced by `(base_type_id, sub_type_id)` matching.

## Current identity hazards

The forge-side hazards (name, slug, index and first-match resolutions) are listed with file and line in R2_CURRENT_CONSUMPTION_GRAPH.md, "Identity hazards". Each is assigned to the package that removes it in R2_MIGRATION_DAG.md.
