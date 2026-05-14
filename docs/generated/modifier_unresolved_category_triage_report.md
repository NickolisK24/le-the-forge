# Modifier Unresolved Category Triage Report

- diagnostic: modifier_unresolved_category_triage
- diagnostic_only: true
- production_safe: false
- scope: non_production_read_only_cli_report

## Summary

- total_unresolved_modifier_evidence: 1363
- unresolved_references: 115
- malformed_structures: 136
- unsupported_structures: 1112
- categories: 3
- categories_eligible_for_future_diagnostic_policy: 3
- categories_that_must_remain_unresolved: 3
- affix_910_duplicate_evidence_preserved: True

## Triage Categories

### unresolved_references

- count: 115
- likely_issue: missing_reference_mapping
- eligible_for_future_diagnostic_policy: true
- must_remain_unresolved: true
- affected_affix_count: 115
- representative_examples:
  - idol:826 idol[826]: Idol affix stat/modifier references are not modeled in this source shape validator.
  - idol:827 idol[827]: Idol affix stat/modifier references are not modeled in this source shape validator.
  - idol:828 idol[828]: Idol affix stat/modifier references are not modeled in this source shape validator.
  - idol:829 idol[829]: Idol affix stat/modifier references are not modeled in this source shape validator.
  - idol:830 idol[830]: Idol affix stat/modifier references are not modeled in this source shape validator.
### malformed_structures

- count: 136
- likely_issue: malformed_tier_value_shape
- eligible_for_future_diagnostic_policy: true
- must_remain_unresolved: true
- affected_affix_count: 103
- representative_examples:
  - equipment:74 equipment[74].tiers: tiers[3] has minRoll greater than maxRoll: minRoll=-0.07000000029802322, maxRoll=-0.07999999821186066. This may be valid for negative-valued effects but must remain diagnostic until tier semantics are normalized.
  - equipment:74 equipment[74].tiers: tiers[4] has minRoll greater than maxRoll: minRoll=-0.09000000357627869, maxRoll=-0.10000000149011612. This may be valid for negative-valued effects but must remain diagnostic until tier semantics are normalized.
  - equipment:74 equipment[74].tiers: tiers[5] has minRoll greater than maxRoll: minRoll=-0.12999999523162842, maxRoll=-0.14000000059604645. This may be valid for negative-valued effects but must remain diagnostic until tier semantics are normalized.
  - equipment:74 equipment[74].tiers: tiers[6] has minRoll greater than maxRoll: minRoll=-0.15000000596046448, maxRoll=-0.17000000178813934. This may be valid for negative-valued effects but must remain diagnostic until tier semantics are normalized.
  - equipment:74 equipment[74].tiers: tiers[7] has minRoll greater than maxRoll: minRoll=-0.25, maxRoll=-0.30000001192092896. This may be valid for negative-valued effects but must remain diagnostic until tier semantics are normalized.
### unsupported_structures

- count: 1112
- likely_issue: unsupported_special_behavior
- eligible_for_future_diagnostic_policy: true
- must_remain_unresolved: true
- affected_affix_count: 1112
- representative_examples:
  - equipment:0 equipment[0]._extra: Record carries _extra TypeTree fields that are preserved but not modeled by this diagnostic phase.
  - equipment:1 equipment[1]._extra: Record carries _extra TypeTree fields that are preserved but not modeled by this diagnostic phase.
  - equipment:2 equipment[2]._extra: Record carries _extra TypeTree fields that are preserved but not modeled by this diagnostic phase.
  - equipment:3 equipment[3]._extra: Record carries _extra TypeTree fields that are preserved but not modeled by this diagnostic phase.
  - equipment:4 equipment[4]._extra: Record carries _extra TypeTree fields that are preserved but not modeled by this diagnostic phase.

## Warning Categories

- category=unresolved_references, likely_issue=missing_reference_mapping, count=115, must_remain_unresolved=True
- category=malformed_structures, likely_issue=malformed_tier_value_shape, count=136, must_remain_unresolved=True
- category=unsupported_structures, likely_issue=unsupported_special_behavior, count=1112, must_remain_unresolved=True

## Affix 910 Duplicate Evidence

- record_id: 910
- section: equipment
- record_path: equipment[910].canRollOn
- raw_canRollOn: ['IDOL_4x1', 'IDOL_4x1']
- normalized_canRollOn: ['IDOL_4X1', 'IDOL_4X1']
- raw_duplicate_count: 2
- duplicate_positions: [0, 1]
- diagnostic_unique_targets: ['IDOL_4X1']
- diagnostic_unique_targets_label: diagnostic_only_not_source_mutation
- policy_result: warning_only
- origin_assessment: unresolved/unknown before exports_json/affixes.json
- message: Eligibility target 'IDOL_4X1' appears 2 times for this affix. Classification: exact_duplicate_in_current_export; origin assessment: unresolved/unknown before exports_json/affixes.json; policy result: warning_only.

## Errors

- none

## Warnings

- unresolved_references has 115 records and remains unresolved for diagnostic planning.
- malformed_structures has 136 records and remains unresolved for diagnostic planning.
- unsupported_structures has 1112 records and remains unresolved for diagnostic planning.
- This triage classifies evidence only; it does not infer gameplay semantics.

## Forbidden Production Usage

- Do not use this report to power build math.
- Do not use this report for item generation.
- Do not use this report for crafting legality.
- Do not expose this report through production APIs or frontend behavior.
- Do not replace existing Forge affix behavior.
- Do not generate or mutate bundle families from this report.
- Do not silently deduplicate affix 910.
- Do not mark production_safe=true.
- Do not use this triage as gameplay modifier semantics.
- Do not infer behavior for unresolved, malformed, or unsupported modifier evidence.
- Do not use this triage to power crafting, simulation, build math, APIs, frontend, or gameplay output.

## Safety Boundary

- This triage is diagnostic-only and non-production.
- It classifies unresolved evidence; it does not resolve gameplay semantics.
- It does not modify source data or generated production output.
- It does not modify production importers, loaders, APIs, frontend, crafting, simulation, build math, or gameplay output.
- It does not guess unsupported modifier behavior.

