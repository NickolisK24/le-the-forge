# V2 Value Normalization Policy

## Purpose

This Phase 10.5 audit reviews source-unit and unknown-scale v2 modifier rows before any planner adapter consumes them. It does not change production planner, stat aggregation, crafting, or simulation behavior.

## Generation command

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_value_normalization_policy.py --modifier-registry docs\generated\v2_modifier_registry.json --output docs\generated\v2_value_normalization_policy_report.json --candidate-output docs\generated\v2_value_normalization_candidate_families.json --markdown-output docs\migration\V2_VALUE_NORMALIZATION_POLICY.md
```

## Summary

- Total modifiers: `19398`
- Source-unit modifiers: `6248`
- Unknown-scale modifiers: `13150`
- Candidate families needing source validation: `373`
- Safe normalization families: `0`
- Blocked families: `729`
- Stable-calculable count changed: `false`

## Top Source-Unit Source Types

- `unique_modifier`: `2047`
- `affix`: `1624`
- `item_implicit`: `1182`
- `skill_structured_value`: `1081`
- `set_item_modifier`: `287`
- `set_bonus_modifier`: `27`

## Top Source-Unit Operations

- `flat`: `4095`
- `increased`: `942`
- `duration`: `744`
- `cooldown`: `197`
- `cost`: `140`
- `more`: `130`

## Top Source-Unit Stat Families

- `duration_cast`: `744`
- `added_playerproperty`: `594`
- `added_abilityproperty`: `589`
- `added_damage`: `482`
- `increased_damage`: `428`
- `added_levelofskills`: `282`
- `added_ailmentchance`: `249`
- `added_armour`: `207`
- `cooldown_cooldown`: `197`
- `cost_cost`: `140`

## Candidate Families

- `unique_modifier|flat|added_playerproperty`: `326` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `unique_modifier|flat|added_abilityproperty`: `313` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `item_implicit|flat|added_damage`: `259` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `affix|increased|increased_damage`: `231` rows, `candidate_percent_family_requires_source_validation`, confidence `none`
- `affix|flat|added_abilityproperty`: `216` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `affix|flat|added_playerproperty`: `205` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `item_implicit|flat|added_armour`: `175` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `affix|flat|added_levelofskills`: `135` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `unique_modifier|flat|added_damage`: `133` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`
- `unique_modifier|flat|added_levelofskills`: `127` rows, `candidate_numeric_family_requires_source_validation`, confidence `none`

## Blocked Families

- `skill_node_modifier|unknown|unknown`: `4460` rows, reasons `source_identity_gap, special_behavior_not_calculable, unknown_operation, unknown_stat_id, unknown_value_scale`
- `skill_node_modifier|unknown|54`: `1320` rows, reasons `source_identity_gap, special_behavior_not_calculable, unknown_operation, unknown_value_scale`
- `skill_structured_value|duration|duration_cast`: `744` rows, reasons `source_identity_gap, special_behavior_not_calculable`
- `skill_node_modifier|unknown|damage`: `323` rows, reasons `source_identity_gap, special_behavior_not_calculable, unknown_operation, unknown_value_scale`
- `skill_node_modifier|cost|mana`: `292` rows, reasons `source_identity_gap, special_behavior_not_calculable, unknown_value_scale`
- `passive_node_modifier|unknown|unknown`: `254` rows, reasons `special_behavior_not_calculable, unknown_operation, unknown_stat_id, unknown_value_scale`
- `skill_node_modifier|unknown|area`: `246` rows, reasons `source_identity_gap, special_behavior_not_calculable, unknown_operation, unknown_value_scale`
- `passive_node_modifier|unknown|54`: `224` rows, reasons `special_behavior_not_calculable, unknown_operation, unknown_value_scale`
- `skill_structured_value|cooldown|cooldown_cooldown`: `197` rows, reasons `source_identity_gap, special_behavior_not_calculable`
- `skill_node_modifier|duration|duration`: `196` rows, reasons `source_identity_gap, special_behavior_not_calculable, unknown_value_scale`

## Policy Conclusion

No family is promoted to planner-normalized in this audit. Existing planner code documents percent-point inputs, but that is not enough to prove how every v2 source-unit family should be scaled. Broad rules such as multiplying every `increased` or `chance` value by 100 are explicitly unsafe until backed by source contracts or golden planner baselines.

## Phase 11 Guidance

Future phases may consume this policy for debug and planning. Stable planner consumption must still require trusted support status, known stat IDs, known operations, resolved source identity, non-special behavior, and explicit value-scale evidence.
