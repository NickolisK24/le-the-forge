# R1 Passive Truth (R1.7)

Canonical exports: `exports_canonical/passive_trees.json` (5 class trees, 535 nodes), `skill_trees.json` (137 trees, 3,936 nodes) and `weaver_tree.json` (77 nodes). All three are built by `tools/scripts/build_canonical_trees.py` from `extracted_raw/raw_skill_trees_from_game.json`. Tests: `test_r1_canonical_trees.py`.

## Identity and fields

- **Node identity:** `(tree_class, node_id)`, plus the source `path_id`. Names are presentation.
- **Fields carried for every node:**
  - `max_points`, `mastery`, `mastery_requirement`;
  - `point_bonus_description`, `no_scaling_type`, `no_scaling_point_threshold`;
  - descriptions, alt and lore text, `ability_granted_by_node`;
  - stats with `property` (raw), `tags` (AT flags), `downside`, `no_scaling`, `value_text`, `override_sprite`.

Field survival: raw → canonical has 24 of 24 paths carried and 0 UNKNOWN.

**LOSS-3 is a Forge-sync loss, not an extraction loss.** The legacy `passive_trees.json` already carried `property`, `tags`, `downside` and `noScaling`; `scripts/sync_game_data.py` drops them (R2).

## Prerequisites

Every prerequisite keeps its raw `node_path_id` and gets a resolution class. Garbage ids are never turned into node ids.

| Resolution | Passive | Skill | Weaver |
| --- | --- | --- | --- |
| RESOLVED | 187 | 4,465 | 148 |
| NULL_REFERENCE | 48 | 7 | 0 |
| IMPLAUSIBLE_REFERENCE (decoder fault, e.g. `1684808296038400`) | 16 | 0 | 0 |
| UNRESOLVED_REFERENCE | 3 | 4 | 0 |

## Gates (fail closed)

| Gate | Result |
| --- | --- |
| Duplicate node ids | 0 |
| Missing nodes (walker failed to decode) | **6 in AcolyteTree**, plus 5 in skill trees (ShatterStrike 2, BlackHole 1, ChaosBolts 1, Flurry 1) |
| Dangling or implausible prerequisites | Passive: all 5 class trees DEFECTIVE. Skill: 8 trees DEFECTIVE on prerequisites. Weaver: prerequisites clean. R1.15 also marks every tree containing a legacy-decoder field-shift node DEFECTIVE (all 137 skill trees and the weaver tree). |
| Declared vs decoded node count | Consistent |

### Missing Warlock nodes

The six "Forge-only Acolyte nodes" the audit found (ids 86, 88, 97, 98, 101, 103) are exactly the six AcolyteTree nodes that `extract_skill_trees_fast.py` failed to decode. They are an extraction miss, not removed game content.

### Root cause (R1.15, proven from the committed 1.4.6 evidence)

The il2cpp layout serializes `SkillTreeNode` as: ... `pointBonusDescription`, **`nodeStats` (`List<AutomaticNodeStat>`)**, `stats` (`List<NodeTooltipStat>`), `nodeDescription`, `altText`, `propertiesForAltText`, `loreText`, `requirements`, `abilityGrantedByNode`.

The legacy walker never read `nodeStats`. It read **one** u32 where the bytes hold **two** list counts, then patched the resulting 4-byte shift with three peek heuristics:
- the zero-prefixed stats count;
- the "optional secondary string" (actually the real `altText`, read and discarded);
- the "optional lore prefix" (actually the real `propertiesForAltText` count).

| Evidence (committed `raw_skill_trees_from_game.json`) | Nodes with empty `stats` | Nodes with `stats` |
| --- | --- | --- |
| `nodeDescription` non-empty | **0 / 185** | 3,014 / 4,373 |
| Skill description found in `altText` | yes (shifted one field) | no |

Mechanisms by symptom:
- **Shifted text fields:** affect all 185 empty-stats nodes (167 skill, 18 weaver, 0 passive).
- **Garbage prerequisites:** the requirements heuristic can read past an empty list into the `abilityGrantedByNode` PPtr; a regression test demonstrates this. The 16 IMPLAUSIBLE and 55 NULL prerequisite references in the dump are consistent with this mechanism and the field shift. Per-node attribution needs the bytes.
- **The six passive failures:** these nodes have `stats`, so they are not shifted. The remaining mechanism consistent with the layout is a non-empty `nodeStats`, whose count the legacy walker reads as the stats count. That is the strongest candidate. It cannot be proven per node without the bytes.

### Fix (last-epoch-data `02e4b34`)

- **Strict decoder:** the strict layout-ordered decoder (`layout-strict-1`) reads the layout in order with no heuristics and validates every count and string.
- **Fail loudly:** it fails a node with `NODE_STATS_LAYOUT_UNKNOWN` rather than guessing `AutomaticNodeStat`'s size, which is absent from the layout index (EXT-15).
- **Provenance:** its output is build-stamped and records same-run, tree-attributed failures.
- **Lossless source:** the operator run dumps every `*TreeNode` MonoBehaviour through TypeTree, which carries the real `nodeStats` layout and is the source for these nodes.
- **Regression tests:**
  - synthetic layout blobs that reproduce the shift and the garbage prerequisite;
  - a gate on the six Acolyte ids. While the dump is legacy, the six must be missing and the tree DEFECTIVE. Once the dump is strict, they must be present, or carry a strict reason.
- **Flagging:** canonical trees flag every legacy-decoded empty-stats node with `field_shift_suspect`. Text is never moved and never fabricated.

## Decoder coverage (layout → raw)

The walker still decodes only the tooltip `stats`, whose `value` is display text ("+8%"). Field survival keeps `nodeStats` and `propertiesForAltText` UNKNOWN until the TypeTree dump lands.

## Provenance gaps

- The committed raw tree dump predates the strict decoder. It carries no GameAssembly hash, so it cannot be proven to be 1.4.6.
- The node-failure classification was produced by a different walker run: its tree path ids match none in the raw dump. Strict-decoder output records its own failures, so that file is no longer joined.

## What clears the blockers

- **Operator run:** it produces a build-stamped, strictly decoded `raw_skill_trees_from_game.json` plus TypeTree dumps of every tree and tree node.
- **Re-evaluated gates:** the canonical gates are re-evaluated against that output.
- **If nodes still fail:** the trees stay DEFECTIVE and QUARANTINED with the exact strict failure reason. The TypeTree dump is then the source to decode `AutomaticNodeStat`.

Forge mastery-order and prerequisite consumption is R2.
