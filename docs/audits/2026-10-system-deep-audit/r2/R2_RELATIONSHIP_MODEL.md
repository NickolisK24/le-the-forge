# R2 Relationship Model (R2-04, R2-05)

**Status: design only.** Findings: REL-1, REL-2, REL-4, REL-6, REL-9, REL-10, EXT-6, LOSS-3, and EXT-12 (from R1).

## 1. General rules

1. **Edges reference canonical identities.** Every relationship is an edge between canonical identities (R2_IDENTITY_POLICY.md), built from source references:
   - PPtr path ids, joined within one snapshot;
   - numeric ids;
   - source indices.

   No edge is ever built by name.
2. **Every edge has a resolution state.** The states are `RESOLVED`, `NULL_REFERENCE`, `IMPLAUSIBLE_REFERENCE`, `TARGET_FAILED_TO_PARSE` and `UNRESOLVED_REFERENCE`; these are the R1 tree vocabulary, extended to all families. Only `RESOLVED` edges participate in calculations or validation. The rest are carried and reported, never dropped and never repaired by guessing.
3. **Required relationships gate trust.** A family whose *required* relationships (R2_CANONICAL_CONSUMPTION_CONTRACT.md) are DANGLING cannot be served TRUSTED (loader check L10).
4. **Keep the source's shape.** Graphs stay graphs. A node with several prerequisites keeps all of them.

## 2. Mastery relationships (R2-04, REL-1)

### Defect

- **The defect:** `scripts/sync_game_data.py` (`MASTERY_MAP`, around lines 324-330) assigns mastery names by a hard-coded per-class order.
- **Effect:** the order is wrong for Mage, Primalist and Sentinel, so 190 of 541 passive nodes carry the wrong mastery, and `/api/passives?mastery=` returns wrong nodes for 6 of 15 masteries.
- **Correct copies:** the v2 bundle and the frontend tree data use the correct order.

### Canonical derivation

```
mastery(node) = classes[node.class_id].masteries[node.mastery]      # source index; 0 = base class
mastery identity = (class_id, mastery_index)
mastery name     = presentation, from classes[class_id].masteries[i].localizationKey / name
```

Requirements:
- `node.mastery` comes from the canonical passive tree (`SkillTreeNode.mastery`, carried as `mastery` in `exports_canonical/passive_trees.json`).
- The class's ordered `masteries` list comes from the canonical class typed view (R2-P04, built from the `CharacterClassList` envelope).

Until that typed view exists, the 1.4.6 legacy `exports_json/classes.json` `masteries[]` array has the same source order. It is usable for **tests and fixtures only**, never as a production authority.

Validation (fail closed):

| Check | Rule |
| --- | --- |
| Index range | `0 <= node.mastery < len(class.masteries)`; otherwise the node is `MASTERY_UNRESOLVED` and the tree cannot be TRUSTED |
| Mastery requirement | `node.mastery_requirement` points-in-mastery gates apply to `(class_id, node.mastery)` |
| Mastery ability | `class.masteries[i].mastery_ability` (path id → `ability_id`) must resolve. Today `abilityPathIds` is empty for 20 of 20 masteries in the legacy export (EXT-6), which is an upstream relationship gate for R2-P04. |

### Consumers to migrate

Every consumer is listed with file:line in R2_CURRENT_CONSUMPTION_GRAPH.md, "Mastery consumers". Classes of consumer:

| Consumer class | Replacement |
| --- | --- |
| `MASTERY_MAP` in the sync | Deleted. The bundle importer carries canonical data unchanged. |
| Backend code comparing mastery **names** (schemas `CLASS_MASTERIES`, routes filtering by `mastery` string) | `MasteryId(class_id, index)` from `CanonicalDataStore`. API accepts and returns ids; names only for display. |
| Frontend hard-coded mastery arrays and orderings | Generated from the same bundle (R2_FRONTEND_AUTHORITY_PLAN.md) |
| Saved builds storing `mastery` as a name | `LEGACY_UNKNOWN` resolution (R2_DATABASE_PROVENANCE_PLAN.md). New builds store the index. |

### Migration tests for all 15 masteries (T5-M)

For each `(class_id, mastery_index)` with index 1–3 (15 masteries), plus the 5 base classes, golden fixtures from the canonical bundle assert:
1. the mastery's name and localization key equal the source list entry at that index;
2. the set of passive node ids with `node.mastery == index` equals the golden set from the canonical tree. 190 nodes change today relative to `data/classes/passives.json`, and the diff is part of the migration report;
3. `/api/passives?class_id=&mastery_index=` returns exactly that set;
4. the frontend artifact's mastery grouping equals the backend's (parity test T8);
5. no code path resolves a mastery by name (static check T11: grep-based allowlist).

## 3. Skill and specialization-tree relationships (R2-05)

### Defects today

- **REL-4 (incomplete resolver data):** `skill_tree_nodes.json` covers 2,190 of 3,693 nodes. Only 1 of 132 trees is complete. 9 trees cannot be found by skill name and 4 are absent. Unknown nodes are skipped at debug level.
- **REL-6 (name collisions):** `skills_metadata` is keyed by name, so 184 skills collapse to 161 and tree-less variants win. Anomaly resolves to `an0mz`.
- **REL-10 (frontend name-to-tree mapping):** the frontend maps names to trees and points skills at tree-less variants. A single `parentId` cannot represent the 675 nodes with multiple prerequisites.
- **REL-9 (unresolved class-to-skill links):** v2 class-to-skill links are reported unresolved because the bundle joins `skill:{code}` against `skill_path:{id}`. Joining on `source_ability_path_id` resolves 60 of 63.
- **EXT-12 (from R1):** legacy-decoded skill trees carry a one-field shift on 185 nodes, and 11 nodes failed to decode.

### Canonical graph

```
Class ──knows/unlocks──▶ Ability (ability_id)           [CharacterClass.knownAbilities / unlockableAbilities, PPtr→ability_id]
Mastery ──grants──▶ Ability                              [masteries[i] mastery ability PPtr]
Ability ──has tree──▶ SkillTree (tree_id)                [SkillTree.ability PPtr; 0..1 tree per ability; variants are separate abilities]
SkillTree ──contains──▶ TreeNode (tree_id, node_id)
TreeNode ──requires(points)──▶ TreeNode                  [requirements[]: 0..n edges, each with points_required]
TreeNode ──stat──▶ PropertyRef (raw, namespace, index, status)   [stats[].property]
TreeNode ──grants──▶ Ability                             [abilityGrantedByNode PPtr]
TreeNode ──conversion/trigger──▶ (from node stats; see below)
PassiveTree(class) ──contains──▶ PassiveNode (class_id, node_id) ──mastery──▶ (class_id, mastery_index)
```

Representation, which the backend and the frontend artifact share:

```json
{
  "tree_id": "an0my", "ability_id": 74, "kind": "skill",
  "nodes": [{"node_id": 7, "max_points": 5, "mastery": null,
             "stats": [{"property": {"raw": 21, "namespace": "SP", "index": 21, "status": "RESOLVED"},
                        "value_text": "+8%", "tags": {...}, "downside": false}],
             "grants_ability_id": null}],
  "edges": [{"from": 7, "to": 3, "points_required": 2, "resolution": "RESOLVED"},
            {"from": 7, "to": 5, "points_required": 1, "resolution": "RESOLVED"}],
  "unresolved_edges": [{"from": 9, "raw_target": 1684808296038400, "resolution": "IMPLAUSIBLE_REFERENCE"}],
  "integrity": {"status": "CLEAN | DEFECTIVE", "problems": []}
}
```

- `edges` is a list, not a `parentId`. "Is node allocatable" means **all** incoming requirement edges are satisfied. Allocation order validation uses the edge list.
- Tree lookup goes `ability_id → tree_id` through the `SkillTree.ability` join. Skill name lookups are removed. A skill with no tree (a variant) is explicit: `tree: null` is not the same as a missing tree.
- Layout: the coordinates used for drawing are **presentation**. The frontend currently takes them from `skill-tree-layout.json` and community data. If the source has no positions, layout stays a presentation-only overlay keyed by `(tree_id, node_id)`, generated or curated, and it can never add, remove or rewire nodes. The parity test T8 checks that the layout node-id set equals the canonical node set.

### Stat, conversion and trigger relationships

- **Node stats** reference properties through the R1 resolution (`RESOLVED` / `UNKNOWN_PROPERTY_TYPE` / `UNRESOLVED`; 5,724 of 7,855 resolved on 1.4.6).
- **Unresolved or untyped stats:** a node whose stats are not `RESOLVED` contributes **no** calculated modifier. It is reported in the build analysis as `unsupported_stats` (count and node ids); it is never treated as zero silently.
- **Numeric node stats:** `nodeStats` (`AutomaticNodeStat`, the structured numeric values) arrive with the operator TypeTree dump. Until R2-P04 types them, tree stat **values** are tooltip text only. The calculation side therefore cannot consume specialization values as TRUSTED (CALC-14, R6). R2 delivers the graph and references; R6 consumes values.
- **Conversions and triggers:** no source relationship type for conversions and triggers is decoded yet. They are carried as stats whose property is in the 5000–9999 band, which is `UNDECODED_NAMESPACE`. R2 represents them as unresolved property refs. No hand-authored conversion table may be attached to canonical nodes; any such rule is a declared `FORGE_RULE` (R2_MIXED_PATCH_POLICY.md M5).

### Validation gates (consumer side)

| Gate | Rule |
| --- | --- |
| G1 | Every tree with an `ability_id` resolves to an ability in the same dataset |
| G2 | Every `(tree_id, node_id)` referenced by a build exists |
| G3 | Every RESOLVED edge's target exists in the same tree |
| G4 | DEFECTIVE trees (R1 integrity) are served ADVISORY at most, with the R1 problems attached |
| G5 | No duplicate `(tree_id, node_id)`; no ability with two trees |
| G6 | Frontend artifact node and edge sets equal the backend's (T8) |

## 4. Item-side relationships (R2-07)

| Edge | Source | Rule |
| --- | --- | --- |
| Subtype → base type | `(base_type_id, sub_type_id)` | Composite identity; never by display name or sequential index |
| Subtype → implicit properties | `implicits[]` structured (property SP id, modifier type, tags, values) | Free-text implicits are presentation only |
| Unique → base type + subtypes | `unique.base_type_id`, `unique.sub_type_ids[]` | A unique can span several subtypes. Resolution is by `unique_id`, never slug or first match. |
| Unique → mods | `(unique_id, mod_index)` with `roll_id`; property id, modifier type, tags, ranges | Structured, numeric |
| Set member → set; set → bonuses | `set_id`; bonuses keyed by `(set_id, pieces)` | |
| Affix → properties | `(affix_id, property_index)` | Each property has its own rolls (REL-7) |
| Affix → item types | `can_roll_on[]` (EquipmentType enum) | Replaces the slot-name vocabularies (REL-16) |
| Blessing → item identity | `(base_type_id, sub_type_id)` | |

Upstream gates (EXT-6) that R2-P04 must add on the extraction side for the typed views:
- monster-mod timeline keys resolve (4 of 31 do today);
- dungeon mods resolve (0 of 3 today);
- mastery ability path ids are present (0 of 20 today);
- no duplicate ailment rows (Ignite appears 3 times).

`validate_exports.py` passing while these fail is the defect; the R1 relationship metrics become the gate instead.
