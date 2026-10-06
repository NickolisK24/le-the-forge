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
| Dangling or implausible prerequisites | Passive: all 5 class trees DEFECTIVE. Skill: 8 trees DEFECTIVE. Weaver: clean. |
| Declared vs decoded node count | Consistent |

### Missing Warlock nodes

The six "Forge-only Acolyte nodes" the audit found (ids 86, 88, 97, 98, 101, 103) are exactly the six AcolyteTree nodes that `extract_skill_trees_fast.py` failed to decode. The failures are buffer overruns when nodes carry 2–4 alt-text properties.

So they are an extraction miss, not removed game content.

### Garbage prerequisite ids

These come from misaligned reads near failed or variable-length records. Every class tree has a node whose prerequisites read ASCII bytes as pathIds.

## Decoder coverage (layout → raw)

`SkillTreeNode` declares two fields the binary walker never decodes:
- `nodeStats` (`List<AutomaticNodeStat>`, the structured numeric stats);
- `propertiesForAltText`.

The walker only decodes the tooltip `stats`, whose `value` is display text ("+8%"). Field survival marks both fields UNKNOWN.

## Provenance gaps

- The raw tree dump carries no GameAssembly hash, so it cannot be proven to be 1.4.6.
- The node-failure classification was produced by a different walker run: its tree path ids match none in the raw dump.

## What clears the blockers

The binary walker's variable-length parsing cannot be fixed without the asset bytes, and the TypeTree tree extractor (`extract_skill_trees_tt.py`) is marked deprecated and incomplete.

The operator run produces a build-stamped `raw_skill_trees_from_game.json` and the canonical gates are re-evaluated. If nodes still fail, the trees stay DEFECTIVE and QUARANTINED, and the walker fix becomes a tracked R1 remediation item with real bytes to test against.

Forge mastery-order and prerequisite consumption is R2.
