# v2 Skill Identity Alignment

## Purpose

This Phase 9.5 audit diagnoses the class/mastery to skill identity mismatch reported during Phase 9. It does not create a runtime bridge, change generators, or alter planner behavior.

## Generation Command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_skill_identity_alignment.py --class-mastery-bundle docs\generated\v2_class_mastery_bundle.json --skill-bundle docs\generated\v2_skill_bundle.json --skill-tree-bundle docs\generated\v2_skill_tree_bundle.json --source-classes D:\Forge\last-epoch-data\exports_json\classes.json --source-skills D:\Forge\last-epoch-data\exports_json\skills_with_trees.json --output docs\generated\v2_skill_identity_alignment_report.json --markdown-output docs\migration\V2_SKILL_IDENTITY_ALIGNMENT.md
```

## Summary

- Total class/mastery skill references: 63
- Total skill records: 184
- Exact ID matches: 0
- Exact raw path matches: 61
- Top-level path matches: 60
- Nested path-only matches: 0
- Normalized name matches: 0
- Ambiguous matches: 1
- Unresolved references: 2
- Bridge safe: false
- Recommended mapping strategy: `top_level_source_identity_partial_unresolved`

## Field Inventory

Class/mastery records use these fields for skill references:

- `linked_skill_source_ids`
- `skill_ids`

Skill records expose these source identity fields:

- `canonical_id`
- `display_name`
- `source_skill_id`
- `raw_reference.source_skill_id`
- `skill_tree_id`

Raw skill records expose these observed path-like fields:

- `comboAbility`
- `damageSources.0.pathId`
- `damageSources.0.sourcePath`
- `damageSources.1.pathId`
- `damageSources.1.sourcePath`
- `damageSources.2.pathId`
- `damageSources.2.sourcePath`
- `isZoneAbility`
- `minionsUseAbility`
- `mutatorHints.0.pathId`
- `mutatorHints.0.sourcePath`
- `mutatorHints.1.pathId`
- `mutatorHints.1.sourcePath`
- `mutatorHints.2.pathId`
- `mutatorHints.2.sourcePath`
- `sharedCooldownAbilityRefs`
- `skillTree.ability`
- `skillTree.nodes.0.effectHints.0.sourcePath`
- `skillTree.nodes.0.effectHints.1.sourcePath`
- `skillTree.nodes.0.effectHints.2.sourcePath`
- `skillTree.nodes.0.effectHints.3.sourcePath`
- `skillTree.nodes.1.effectHints.0.sourcePath`
- `skillTree.nodes.1.effectHints.1.sourcePath`
- `skillTree.nodes.1.effectHints.2.sourcePath`
- `skillTree.nodes.1.effectHints.3.sourcePath`
- `skillTree.nodes.1.effectHints.4.sourcePath`
- `skillTree.nodes.10.effectHints.0.sourcePath`
- `skillTree.nodes.10.effectHints.1.sourcePath`
- `skillTree.nodes.10.effectHints.2.sourcePath`
- `skillTree.nodes.10.effectHints.3.sourcePath`
- `skillTree.nodes.10.effectHints.4.sourcePath`
- `skillTree.nodes.10.effectHints.5.sourcePath`
- `skillTree.nodes.11.effectHints.0.sourcePath`
- `skillTree.nodes.11.effectHints.1.sourcePath`
- `skillTree.nodes.11.effectHints.2.sourcePath`
- `skillTree.nodes.11.effectHints.3.sourcePath`
- `skillTree.nodes.11.effectHints.4.sourcePath`
- `skillTree.nodes.11.effectHints.5.sourcePath`
- `skillTree.nodes.12.effectHints.0.sourcePath`
- `skillTree.nodes.12.effectHints.1.sourcePath`
- `skillTree.nodes.12.effectHints.2.sourcePath`
- `skillTree.nodes.12.effectHints.3.sourcePath`
- `skillTree.nodes.12.effectHints.4.sourcePath`
- `skillTree.nodes.13.effectHints.0.sourcePath`
- `skillTree.nodes.13.effectHints.1.sourcePath`
- `skillTree.nodes.13.effectHints.2.sourcePath`
- `skillTree.nodes.13.effectHints.3.sourcePath`
- `skillTree.nodes.13.effectHints.4.sourcePath`
- `skillTree.nodes.14.effectHints.0.sourcePath`
- `skillTree.nodes.14.effectHints.1.sourcePath`

## What Matched

Exact ID matching did not resolve the class/mastery `skill_path:*` references because generated v2 skills use source skill IDs such as `skill:ab0lh`, not numeric path IDs.

Raw path matching now includes upstream `sourceIdentity.skillPath` when present. Those top-level matches are accepted as safe identity evidence. Nested path evidence is still not accepted as a bridge.

Normalized name matching cannot resolve these references because the class/mastery `skill_path:*` values do not include display names.

## Examples

### Resolved By Safe Identity

- `skill_path:260926` (resolved; owners: class:acolyte) -> skill:evade1
- `skill_path:261173` (resolved; owners: class:acolyte) -> skill:bc53
- `skill_path:261591` (resolved; owners: class:mage) -> skill:en6
- `skill_path:262309` (resolved; owners: mastery:sentinel:void_knight) -> skill:es6ai
- `skill_path:262328` (resolved; owners: mastery:rogue:falconer) -> skill:falc0
- `skill_path:262431` (resolved; owners: class:mage) -> skill:fi9
- `skill_path:262458` (resolved; owners: class:mage) -> skill:fw3d
- `skill_path:262473` (resolved; owners: mastery:sentinel:forge_guard) -> skill:fs3e3
- `skill_path:262497` (resolved; owners: class:mage) -> skill:frc87w
- `skill_path:262531` (resolved; owners: class:primalist) -> skill:fl13

### Nested Path Matches Not Accepted As A Bridge

- None

### Ambiguous

- `skill_path:261142` (ambiguous; owners: class:acolyte, class:mage, class:primalist) -> skill:sps5l, skill:sr5t, skill:srtor

### Unresolved

- `skill_path:262953` (unresolved; owners: class:mage)
- `skill_path:263498` (unresolved; owners: class:acolyte, class:mage, class:primalist)

## Conclusion

A complete deterministic bridge is still not safe from the current evidence. The enriched upstream export resolves the references that have top-level `sourceIdentity.skillPath` evidence, but remaining unresolved or ambiguous references must stay blocked.

## Recommended Next Action

Before modifier/stat normalization consumes class/mastery skill ownership, either resolve the remaining source gaps upstream or carry them as an explicit identity gap. Do not infer the remaining bridge from nested summoned actor evidence or tooltip text.
