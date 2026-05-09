# Affix Stat/Modifier Reference Audit

- diagnostic: affix_stat_modifier_reference_audit
- scope: non_production_read_only_stat_modifier_reference_audit
- diagnostic_only: true
- production_safe: false
- validation_status: warning

## Summary

- total_affixes: 1227
- equipment_affixes: 1112
- idol_affixes: 115
- total_affix_stat_modifier_references: 6959
- resolved_references: 6844
- unresolved_references: 115
- duplicate_references: 0
- ambiguous_references: 0
- unsupported_modifier_structures: 1112
- malformed_modifier_structures: 136
- missing_provenance_source_references: 0
- unsafe_identity_assumption_references: 0
- deterministic_inspection_output_stable: True
- production_safe: False

## Modifier Families / Categories

- family=equipment_affix_modifier_evidence, count=1112, status=diagnostic_only
- family=idol_affix_modifier_evidence, count=115, status=diagnostic_only
- family=embedded_tier_modifier_slots, count=6959, status=structurally_present_only
- family=tag_category_modifier_context, count=11, status=warning_metadata_only

## Structurally Safe Categories

- category=diagnostic_embedded_tier_reference_slots, count=6959, status=structurally_present_only, notes=Tier/reference slots are countable and deterministic, but not gameplay-ready.
- category=references_with_structural_evidence, count=6844, status=inspection_safe, notes=These references are present in diagnostics; formulas and gameplay semantics remain unaudited.

## Unsafe / Blocked Categories

- category=unresolved_references, count=115, status=unsafe_for_modifier_resolver
- category=malformed_modifier_structures, count=136, status=unsafe_until_semantics_audited
- category=unsupported_modifier_structures, count=1112, status=unsafe_until_modeled

## Minimum Guarantees Before Modifier Resolver

- Every modifier reference must have stable source identity and provenance.
- No modifier may rely on display-name-only identity.
- No modifier may rely on subtype_id-only identity.
- Unresolved stat/modifier references must be zero or explicitly policy-classified as warning-only.
- Malformed tier/modifier structures need a documented semantic policy before resolution.
- Unsupported TypeTree or extra fields must be modeled or explicitly excluded.
- Diagnostic output must remain deterministic with saved-vs-fresh comparison coverage.
- A future modifier resolver must stay non-production until a separate production readiness review.

## Findings

- code=malformed_modifier_structures, severity=warning, source=phase_1_source_shape, message=136 modifier/tier structures are malformed or semantically unresolved.
- code=unresolved_stat_modifier_references, severity=warning, source=phase_1_source_shape, message=115 stat/modifier references are unresolved.
- code=unsupported_modifier_structures, severity=warning, source=phase_1_source_shape, message=1112 records contain unsupported or unresolved modifier structures.

## Errors

- none

## Warnings

- 136 modifier/tier structures are malformed or semantically unresolved.
- 115 stat/modifier references are unresolved.
- 1112 records contain unsupported or unresolved modifier structures.

## Forbidden Production Usage

- Do not use this report to power build math.
- Do not use this report for item generation.
- Do not use this report for crafting legality.
- Do not expose this report through production APIs or frontend behavior.
- Do not replace existing Forge affix behavior.
- Do not generate or mutate bundle families from this report.
- Do not silently deduplicate affix 910.
- Do not mark production_safe=true.
- Do not use this audit as a gameplay modifier resolver.
- Do not treat structurally present references as gameplay-correct modifiers.

## Safety Boundary

- Diagnostic-only and non-production.
- Read-only over generated diagnostic artifacts.
- Does not modify source data or generated production output.
- Does not modify importers, loaders, runtime behavior, APIs, frontend, crafting, simulation, build math, or gameplay output.
- Does not create a gameplay modifier resolver.
- Does not claim gameplay correctness or production readiness.

