# Missing Modifier Reference Mapping Policy Validation Report

- validation_status: warning
- diagnostic_only: true
- production_safe: false

## Summary

- total_missing_reference_mapping_records: 115
- raw_reference_evidence_preserved: 115
- stable_affix_source_identity_preserved: 115
- provenance_preserved: 115
- warning_metadata_preserved: 115
- records_remaining_unresolved: 115
- name_only_mapping_inference_records: 0
- subtype_id_only_mapping_inference_records: 0
- saved_vs_fresh_agreement_available: True
- saved_vs_fresh_unresolved_delta: 0

## Saved-vs-Fresh Agreement

- available: True
- path: D:\Forge\le-the-forge\docs\generated\controlled_modifier_resolver_comparison_report.json
- production_safe: False
- diagnostic_only: True
- comparison_status: warning
- unresolved_delta: 0
- warning_category_delta: 0

## Representative Records

- idol:826 idol[826]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:827 idol[827]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:828 idol[828]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:829 idol[829]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:830 idol[830]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:831 idol[831]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:832 idol[832]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:833 idol[833]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:834 idol[834]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- idol:835 idol[835]: status=unresolved code=affix_record.idol_stat_modifier_reference_unmodeled
- ... 105 additional records omitted from markdown.

## Errors

- none

## Warnings

- 115 missing modifier reference mappings remain unresolved.
- Missing mappings are carried as unresolved diagnostic evidence only.
- No mappings are inferred from display names or subtype_id-only identity.

## Forbidden Production Usage

- Do not use this report to power build math.
- Do not use this report for item generation.
- Do not use this report for crafting legality.
- Do not expose this report through production APIs or frontend behavior.
- Do not replace existing Forge affix behavior.
- Do not generate or mutate bundle families from this report.
- Do not silently deduplicate affix 910.
- Do not mark production_safe=true.
- Do not add modifier mappings from this validator.
- Do not infer mappings from display names.
- Do not infer mappings from subtype_id-only identity.
- Do not use missing mapping records for gameplay, crafting, simulation, build math, APIs, or frontend behavior.

## Safety Boundary

- This validator checks missing reference mapping evidence preservation only.
- It does not implement semantic modifier resolution.
- It does not add modifier mappings.
- It does not infer gameplay semantics or guess unsupported behavior.
- It does not modify source data, generated production output, loaders, importers, APIs, frontend, crafting, simulation, build math, or gameplay output.

