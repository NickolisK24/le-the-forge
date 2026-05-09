# Malformed Tier/Value Shape Policy Validation Report

- validation_status: warning
- diagnostic_only: true
- production_safe: false

## Summary

- total_malformed_tier_value_shape_records: 136
- raw_min_max_preserved: 136
- raw_source_order_preserved: 136
- provenance_preserved: 136
- warning_metadata_preserved: 136
- diagnostic_normalized_views: 136
- inverted_numeric_ranges: 136
- inverted_negative_ranges: 34
- records_missing_raw_evidence: 0
- records_with_unlabeled_normalized_view: 0

## Representative Records

- equipment:74 equipment[74].tiers[3]: minRoll=-0.07000000029802322 maxRoll=-0.07999999821186066 inverted_negative=true
- equipment:74 equipment[74].tiers[4]: minRoll=-0.09000000357627869 maxRoll=-0.10000000149011612 inverted_negative=true
- equipment:74 equipment[74].tiers[5]: minRoll=-0.12999999523162842 maxRoll=-0.14000000059604645 inverted_negative=true
- equipment:74 equipment[74].tiers[6]: minRoll=-0.15000000596046448 maxRoll=-0.17000000178813934 inverted_negative=true
- equipment:74 equipment[74].tiers[7]: minRoll=-0.25 maxRoll=-0.30000001192092896 inverted_negative=true
- equipment:165 equipment[165].tiers[0]: minRoll=-0.05999999865889549 maxRoll=-0.1599999964237213 inverted_negative=true
- equipment:262 equipment[262].tiers[0]: minRoll=-0.05000000074505806 maxRoll=-0.11999999731779099 inverted_negative=true
- equipment:267 equipment[267].tiers[0]: minRoll=-0.03999999910593033 maxRoll=-0.10000000149011612 inverted_negative=true
- equipment:289 equipment[289].tiers[0]: minRoll=-0.03999999910593033 maxRoll=-0.09000000357627869 inverted_negative=true
- equipment:369 equipment[369].tiers[0]: minRoll=-0.11999999731779099 maxRoll=-0.15000000596046448 inverted_negative=true
- ... 126 additional records omitted from markdown.

## Errors

- none

## Warnings

- 136 malformed tier/value shape records remain unresolved for semantic resolver purposes.
- Diagnostic-only normalized views are inspection aids only and are not source mutation.
- Inverted negative ranges may be valid game data, but no gameplay meaning is inferred.

## Forbidden Production Usage

- Do not use this report to power build math.
- Do not use this report for item generation.
- Do not use this report for crafting legality.
- Do not expose this report through production APIs or frontend behavior.
- Do not replace existing Forge affix behavior.
- Do not generate or mutate bundle families from this report.
- Do not silently deduplicate affix 910.
- Do not mark production_safe=true.
- Do not treat normalized range order as gameplay truth.
- Do not infer whether negative ranges are beneficial, harmful, additive, increased, more, conditional, or scoped.
- Do not use this report to power gameplay, crafting, simulation, build math, APIs, or frontend behavior.

## Safety Boundary

- This validator checks diagnostic evidence preservation only.
- It does not implement semantic modifier resolution.
- It does not infer gameplay semantics or guess unsupported behavior.
- It does not modify source data, generated production output, loaders, importers, APIs, frontend, crafting, simulation, build math, or gameplay output.

