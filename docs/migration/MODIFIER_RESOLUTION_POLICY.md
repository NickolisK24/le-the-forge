# Modifier Resolution Policy

## 1. Purpose

This document defines the diagnostic-only policy for how Forge should treat affix stat/modifier reference evidence before and during the controlled modifier resolver prototype.

This is policy only. It does not implement a resolver, change production loaders, change importer behavior, change generated production output, change runtime behavior, power crafting/build math/simulation/gameplay, or mark anything `production_safe=true`.

Current policy state:

- `diagnostic_only=true`
- `production_safe=false`
- no gameplay correctness claim
- no production readiness claim
- the first controlled modifier resolver prototype exists as CLI-only diagnostic tooling

## 2. Current Diagnostic Inputs

The policy is based on the non-production affix inspection stack and the stat/modifier reference audit recorded in the migration tracker.

Current audited counts:

| Category | Count | Policy Status |
| --- | ---: | --- |
| structurally present references | 6844 | eligible for inspection-only normalized reference objects |
| unresolved references | 115 | unresolved; excluded from resolver semantics |
| malformed / semantically unresolved structures | 136 | unresolved; requires explicit semantic policy |
| unsupported / unresolved structures | 1112 | unsupported; must not be guessed |
| duplicate references | 0 | no current duplicate reference blocker |
| ambiguous references | 0 | no current ambiguous reference blocker |
| missing provenance/source references | 0 | currently no provenance blocker from the audit |
| unsafe identity assumption references | 0 | currently no name-only or subtype_id-only modifier identity blocker |

`structurally present` means the reference is present in diagnostic evidence. It does not mean the modifier is gameplay-correct, formula-ready, crafting-ready, or production-safe.

## 3. Core Policy

A future controlled modifier resolver prototype may include only references that satisfy all of the following:

- stable source identity exists
- provenance/source reference is attached
- the record does not rely on display name as identity
- the record does not rely on `subtype_id` alone
- the reference is structurally present in diagnostic evidence
- no unresolved reference warning is attached
- no malformed/semantically unresolved structure warning is attached
- no unsupported structure warning is attached
- warning metadata remains attached
- output remains `production_safe=false`

Any reference that fails one of these conditions must be excluded from resolved modifier semantics and carried as unresolved diagnostic evidence.

## 4. Structurally Present References

The 6844 structurally present references may be represented by a future controlled prototype only as inspection-safe reference objects.

Allowed:

- preserve source identity
- preserve source/provenance path
- preserve affix identity
- preserve tier/reference slot context where available
- attach warning metadata
- label output as diagnostic-only
- include a normalized inspection view if it is clearly not source mutation

Forbidden:

- treat structural presence as gameplay correctness
- infer a stat formula
- infer additive/more/increased semantics
- infer ailment, skill, class, minion, or conditional behavior from prose
- power simulation, crafting, item generation, APIs, frontend, or build math
- mark output `production_safe=true`

## 5. Unresolved References

The 115 unresolved references must remain unresolved.

Required behavior:

- carry the raw diagnostic warning
- preserve affix/source identity
- preserve provenance
- include the reference in unresolved counts
- exclude it from resolved modifier output
- fail or warn clearly if a prototype attempts to treat it as resolved

Unresolved references may be downgraded only by a future diagnostic policy that proves stable identity, source provenance, and non-ambiguous semantics. That policy must still be non-production unless a separate production readiness review exists.

## 6. Malformed Or Semantically Unresolved Structures

The 136 malformed or semantically unresolved structures must not be resolved as gameplay modifiers.

Current examples include tier/range structures that may be valid for negative-valued effects but are not semantically normalized.

Required behavior:

- preserve the malformed/semantic warning
- preserve the raw tier/reference evidence
- keep the record inspectable
- exclude it from gameplay semantics
- require an explicit semantic policy before any normalized modifier value is emitted

A future resolver prototype may show these as `semantic_status=unresolved`, but must not guess intended sign, direction, formula, or stacking behavior.

## 7. Unsupported Or Unresolved Structures

The 1112 unsupported/unresolved structures are not safe for modifier resolution.

Required behavior:

- preserve the unsupported/unresolved warning
- preserve source/provenance context
- expose the count and affected records
- keep them out of resolved modifier semantics
- require explicit modeling or explicit exclusion before resolver work

Unsupported structures cannot be guessed because guessing would convert extraction evidence into invented mechanics. That would violate the no-false-confidence boundary and could silently corrupt future gameplay calculations.

## 8. Warning Metadata Propagation

Every future controlled modifier resolver prototype must propagate warning metadata from the inspection stack.

Required output behavior:

- top-level warning summary
- per-record warnings
- unresolved reference count
- malformed structure count
- unsupported structure count
- provenance/source paths
- `production_safe=false`
- explicit `diagnostic_only=true`
- explicit forbidden production usage

Warnings must not be downgraded to passing by the resolver.

## 9. Provenance Requirements

Every modifier reference object must carry provenance.

Required provenance fields:

- source artifact path
- source phase or diagnostic layer
- source affix identity
- source section, such as `equipment` or `idol`
- source affix ID
- tier/reference slot context when available
- warning source when applicable

Missing provenance makes a reference unresolved for prototype purposes.

## 10. Failure Behavior

A future controlled modifier resolver prototype must fail or block resolution when:

- any input artifact has `production_safe=true`
- required diagnostic artifacts are missing
- source identity is missing
- provenance is missing
- name-only identity is used
- `subtype_id`-only identity is used
- unresolved references are marked resolved
- malformed structures are marked resolved without accepted semantic policy
- unsupported structures are marked resolved without accepted modeling policy
- warning metadata is dropped
- deterministic output comparison fails

Warning-only output may continue only if unresolved/malformed/unsupported references remain explicitly unresolved and visible.

## 11. Inspection-Only Resolver Scope

The controlled modifier resolver prototype produces inspection-only objects such as:

```json
{
  "diagnostic_only": true,
  "production_safe": false,
  "source_affix_identity": "equipment:910",
  "reference_status": "resolved | unresolved | malformed | unsupported",
  "stat_modifier_reference": "source-backed reference or null",
  "tier_context": {},
  "provenance": {},
  "warnings": [],
  "forbidden_usage": [
    "Do not use for gameplay math.",
    "Do not use for crafting.",
    "Do not expose through production APIs."
  ]
}
```

This object is not a runtime modifier model.

Current implementation:

- module: `backend/app/game_data/controlled_modifier_resolver_prototype.py`
- CLI: `backend/scripts/report_controlled_modifier_resolver_prototype.py`
- markdown report: `docs/generated/controlled_modifier_resolver_prototype_report.md`
- JSON report: `docs/generated/controlled_modifier_resolver_prototype_report.json`
- saved-vs-fresh comparison module: `backend/app/game_data/controlled_modifier_resolver_comparison.py`
- saved-vs-fresh comparison CLI: `backend/scripts/report_controlled_modifier_resolver_comparison.py`
- comparison markdown report: `docs/generated/controlled_modifier_resolver_comparison_report.md`
- comparison JSON report: `docs/generated/controlled_modifier_resolver_comparison_report.json`
- unresolved category triage module: `backend/app/game_data/modifier_unresolved_category_triage.py`
- unresolved category triage CLI: `backend/scripts/report_modifier_unresolved_category_triage.py`
- unresolved category triage markdown report: `docs/generated/modifier_unresolved_category_triage_report.md`
- unresolved category triage JSON report: `docs/generated/modifier_unresolved_category_triage_report.json`
- malformed tier/value shape validator module: `backend/app/game_data/malformed_tier_value_shape_validator.py`
- malformed tier/value shape validator CLI: `backend/scripts/report_malformed_tier_value_shape.py`
- malformed tier/value shape validator markdown report: `docs/generated/malformed_tier_value_shape_report.md`
- malformed tier/value shape validator JSON report: `docs/generated/malformed_tier_value_shape_report.json`
- missing modifier reference mapping validator module: `backend/app/game_data/missing_modifier_reference_mapping_validator.py`
- missing modifier reference mapping validator CLI: `backend/scripts/report_missing_modifier_reference_mapping.py`
- missing modifier reference mapping validator markdown report: `docs/generated/missing_modifier_reference_mapping_report.md`
- missing modifier reference mapping validator JSON report: `docs/generated/missing_modifier_reference_mapping_report.json`

The prototype emits deterministic aggregate inspection groups because the approved generated diagnostics expose modifier reference counts and warning categories, not validated per-reference gameplay semantics. This is intentional: it avoids inventing per-reference mechanics while still preserving unresolved, malformed, unsupported, and warning evidence.

## 12. Missing Modifier Reference Mapping Policy

Current missing reference mapping count: `115`.

`missing_reference_mapping` means the diagnostic stack can see that an affix tier or modifier record carries modifier-like evidence, but the current generated diagnostic artifacts do not provide a stable, source-backed mapping from that evidence to an inspection-safe modifier identity. These references are currently classified by unresolved modifier triage as likely missing mapping evidence, not as gameplay-ready modifier objects.

Required raw evidence to preserve:

- source affix identity
- source section, such as `equipment` or `idol`
- source affix ID
- tier index or modifier slot context when available
- raw reference key, warning message, or source field that caused the unresolved classification
- raw tier/value context when available
- source artifact path
- diagnostic phase or report that emitted the unresolved evidence

Required provenance and warning metadata:

- source path must remain attached to every unresolved reference
- source phase or diagnostic layer must remain attached
- warning category must remain attached
- warning message must remain attached when present
- affected affix identity must remain attached
- future saved-vs-fresh comparisons must preserve count and warning-category agreement

Future resolver prototypes must carry missing reference mappings as unresolved diagnostic objects. They may include these fields for inspection:

```json
{
  "diagnostic_only": true,
  "production_safe": false,
  "source_affix_identity": "equipment:<id> or idol:<id>",
  "reference_status": "unresolved",
  "unresolved_category": "missing_reference_mapping",
  "raw_reference_evidence": {},
  "provenance": {},
  "warnings": []
}
```

A missing reference may become resolved only after a separate diagnostic policy or validator provides source-backed mapping evidence. Required evidence before adding a mapping:

- stable source identity for the affix and reference
- source-backed modifier identity that does not depend on display text alone
- provenance showing where the mapping came from
- evidence that the mapping is not a `subtype_id`-only identity
- no conflicting mapping for the same raw reference evidence
- deterministic saved-vs-fresh agreement for the mapped count and warning metadata
- tests proving unresolved records are not silently converted when mapping evidence is missing

Mappings must not be guessed from display names. Display names are labels only: they may be localized, duplicated, stale, abbreviated, or semantically incomplete. Name-only matching would turn presentation text into mechanics and would violate the no-false-confidence boundary.

Mappings must not be guessed from `subtype_id` alone. `subtype_id` is scoped under its source family or base identity in the existing item-family diagnostics, and using it alone risks collisions or false joins. A valid mapping must carry enough source context to identify the modifier reference without relying on `subtype_id`-only identity.

Missing mappings block gameplay correctness claims. As long as 115 modifier references remain unmapped, Forge cannot claim complete affix modifier interpretation, stat math correctness, crafting correctness, or production migration readiness. Future prototypes may show these records for inspection, but they must remain unresolved and excluded from gameplay semantics.

`production_safe=false` remains required because the current evidence supports diagnostic visibility, not production-safe modifier resolution. The policy permits future diagnostic validation of mapping evidence; it does not authorize semantic modifier resolution, loader changes, runtime behavior changes, or production consumption.

Current missing modifier reference mapping validation summary:

- validation status: `warning`
- `production_safe=false`
- total missing reference mapping records: 115
- raw reference evidence preserved: 115
- stable affix source identity preserved: 115
- provenance preserved: 115
- warning metadata preserved: 115
- records remaining unresolved: 115
- name-only mapping inference records: 0
- `subtype_id`-only mapping inference records: 0
- saved-vs-fresh agreement available: `true`
- saved-vs-fresh unresolved delta: 0

This validation does not add modifier mappings. It only confirms the current missing mapping records preserve enough diagnostic evidence to remain visible and unresolved until source-backed mapping evidence exists.

## 13. Malformed Tier/Value Shape Policy

Current malformed or semantically unresolved count: `136`.

`malformed_tier_value_shape` currently means a tier record has value/range evidence that cannot be safely interpreted by the diagnostic stack. The known current pattern is `affix_tier.inverted_numeric_range`, where a tier row has `minRoll` greater than `maxRoll`. Current examples are negative-valued ranges such as `minRoll=-0.07000000029802322` and `maxRoll=-0.07999999821186066`.

Raw source evidence must be preserved exactly:

- raw `minRoll`
- raw `maxRoll`
- raw tier index or warning message when available
- raw source order
- source affix identity
- source section
- source provenance path
- warning code and message

Diagnostic-only normalization may be allowed only as an additional view when all of the following are true:

- the raw values and raw order remain present in the report
- the normalized view is explicitly labeled `diagnostic_only_not_source_mutation`
- normalization only sorts or pairs values for inspection and does not infer sign direction, desirability, stacking, formula, or gameplay meaning
- the record remains warning-level and `production_safe=false`
- provenance and warning metadata are preserved

Diagnostic-only normalization is forbidden when:

- either raw bound is missing
- either raw bound is non-numeric or ambiguous
- the diagnostic cannot identify the tier/source affix provenance
- normalization would require guessing whether a negative range is beneficial, harmful, additive, more/increased, conditional, class-specific, minion/player-targeted, or otherwise semantic
- downstream output would treat the normalized order as gameplay truth

Normalization never implies gameplay correctness. Inverted negative ranges may be valid game data, may require sign-aware display handling, or may represent effects where lower numeric values are stronger. The diagnostic stack is not allowed to choose among those meanings without a separate semantic policy.

Future resolver prototypes must carry malformed tier/value records as unresolved diagnostic objects unless an accepted diagnostic policy proves that a specific structure can be normalized for inspection without changing source evidence. Even then, the output must keep both raw evidence and normalized view side by side and must remain `production_safe=false`.

A downgrade from malformed to warning-only normalized inspection requires:

- stable source affix identity
- stable tier/reference provenance
- raw min/max/order evidence preserved
- normalized view labeled as diagnostic-only
- no missing raw bounds
- no ambiguous numeric shape
- no inferred gameplay semantics
- saved-vs-fresh agreement for counts and warning metadata

Those conditions are now implemented and tested as a diagnostic validation layer, not as semantic modifier resolution. The validator confirms the current 136 malformed tier/value records preserve raw evidence and may expose a labeled diagnostic-only normalized inspection view, while all 136 records remain unresolved for semantic resolver purposes.

Current malformed tier/value shape validation summary:

- validation status: `warning`
- `production_safe=false`
- total malformed tier/value records: 136
- raw `minRoll` / `maxRoll` preserved: 136
- raw source order preserved: 136
- provenance preserved: 136
- warning metadata preserved: 136
- diagnostic-only normalized views labeled `diagnostic_only_not_source_mutation`: 136
- inverted numeric ranges detected: 136
- inverted negative ranges detected: 34
- records missing raw evidence: 0
- unlabeled normalized views: 0

This validation does not infer sign direction, desirability, stacking behavior, formulas, or gameplay meaning. It only proves the diagnostic artifacts preserve enough raw evidence to inspect malformed tier/value shapes without mutating source data.

## 14. Unsupported Special Behavior Policy

Current unsupported special behavior count: `1112`.

`unsupported_special_behavior` means the diagnostic stack found preserved modifier-adjacent source evidence that is not modeled by the controlled modifier resolver and cannot be safely represented as a generic stat modifier. The current unresolved category triage derives this category from `affix_record.extra_typetree_fields`, where equipment affix records carry preserved TypeTree fields that remain intentionally outside resolver semantics.

Required raw evidence to preserve:

- source affix identity
- source section, such as `equipment` or `idol`
- source affix ID
- raw field name or source warning field that exposed the unsupported evidence
- raw warning message
- any preserved raw source payload path or diagnostic record path available
- diagnostic phase or report that emitted the unsupported evidence

Required provenance and warning metadata:

- source artifact path must remain attached when available
- source phase or diagnostic layer must remain attached
- source warning code must remain attached
- warning category must remain attached
- warning message must remain attached
- affected affix identity must remain attached
- future saved-vs-fresh comparisons must preserve count and warning-category agreement

Future resolver prototypes must carry unsupported special behavior as unsupported diagnostic objects, not as resolved modifier semantics. They may include these fields for inspection:

```json
{
  "diagnostic_only": true,
  "production_safe": false,
  "source_affix_identity": "equipment:<id> or idol:<id>",
  "reference_status": "unsupported",
  "unresolved_category": "unsupported_special_behavior",
  "raw_unsupported_evidence": {},
  "provenance": {},
  "warnings": []
}
```

Unsupported structures must not be guessed from prose, text, labels, display names, tags, or categories. Those fields can be useful for inspection, but they are not source-backed mechanics. Treating them as semantics would turn descriptive or grouping metadata into gameplay behavior.

Unsupported structures must not be collapsed into generic stat modifiers. Generic stat objects lose the distinctions that may matter for correctness, such as condition, target, entity scope, trigger timing, skill binding, or scripted behavior. Collapsing them would create false confidence by making unknown mechanics appear resolved.

Potentially unsafe unsupported behavior categories include:

- conditional behavior
- entity-scope behavior
- minion/player target behavior
- skill-specific behavior
- triggered or special behavior
- unique scripted behavior
- unknown behavior

An unsupported behavior may become resolved only after a separate diagnostic policy or validator provides source-backed semantic evidence. Required evidence before resolving unsupported behavior:

- stable source identity for the affix and unsupported field
- raw source field semantics documented from decoded source, schema, or verified extraction evidence
- provenance showing where the semantic interpretation came from
- evidence that the behavior is not inferred from prose, display names, labels, tags, or categories
- no conflicting interpretation for the same raw evidence
- deterministic saved-vs-fresh agreement for counts and warning metadata
- tests proving unsupported records are not silently converted when semantic evidence is missing

Unsupported structures block gameplay correctness claims. As long as 1112 structures remain unsupported, Forge cannot claim complete affix modifier interpretation, stat math correctness, crafting correctness, or production migration readiness. Future prototypes may expose these structures for inspection, but they must remain unsupported and excluded from gameplay semantics.

`production_safe=false` remains required because the current evidence supports diagnostic visibility, not production-safe modifier resolution. This policy does not authorize semantic modifier resolution, loader changes, runtime behavior changes, or production consumption.

## 15. Requirements Before Gameplay Correctness Claims

Forge must not claim gameplay correctness until all of the following are true:

- unresolved references are resolved or explicitly excluded by accepted policy
- malformed structures have accepted semantic policies
- unsupported structures are modeled or explicitly excluded
- tier direction/sign/range semantics are validated
- modifier stacking/additive/increased/more behavior is validated
- conditional/class/skill/minion/idol-specific behavior is validated where relevant
- saved-vs-fresh deterministic comparison exists for modifier resolver output
- no warning metadata is lost
- production migration criteria and rollback strategy exist
- a separate production readiness review approves any production use

Until then, modifier resolution remains diagnostic-only and `production_safe=false`.

## 16. Current Disposition

Current disposition after the controlled modifier inspection stack:

- 5596 references are represented as resolved structural inspection-only modifier objects after excluding unresolved, malformed, and unsupported evidence.
- 115 unresolved references must remain unresolved.
- 136 malformed or semantically unresolved structures must remain unresolved.
- 1112 unsupported/unresolved structures must remain unsupported.
- no current duplicate or ambiguous reference blocker is reported.
- no current missing provenance or unsafe identity blocker is reported.
- affix `910` duplicate eligibility evidence remains visible as upstream warning metadata.
- saved-vs-fresh comparison status is `warning`.
- count deltas are 0.
- warning category deltas are 0.
- deterministic output agreement is `true`.
- provenance coverage agreement is `true`.
- affix `910` duplicate evidence agreement is `true`.
- `production_safe=false` remains explicit.
- unresolved modifier category triage classifies 115 unresolved references as likely missing reference mapping.
- missing modifier reference mapping policy is documented; those 115 references must stay unresolved until source-backed mapping evidence exists, and mappings must not be inferred from display names or `subtype_id` alone.
- missing modifier reference mapping validation confirms all 115 records preserve raw evidence, source identity, provenance, and warning metadata; all 115 remain unresolved; no name-only or `subtype_id`-only mapping inference is present; saved-vs-fresh unresolved delta is 0.
- malformed modifier category triage classifies 136 malformed structures as malformed tier/value shape.
- unsupported modifier category triage classifies 1112 unsupported structures as unsupported special behavior.
- unsupported special behavior policy is documented; those 1112 structures must stay unsupported until source-backed semantic evidence exists, must not be inferred from text/name/tag/category evidence, and must not be collapsed into generic stat modifiers.
- all triaged categories remain unresolved and diagnostic-only.
- malformed tier/value shape validation confirms raw min/max/order evidence, provenance, and warning metadata are preserved for all 136 records; any normalized bounds are explicitly labeled diagnostic-only and not source mutation.

This closes the controlled modifier inspection stack as diagnostic-complete, not production-ready. The stack proves stable inspection output, not gameplay correctness.

Recommended next architecture target: diagnostic validation for unsupported special behavior. That validation must preserve raw evidence, provenance, and warning metadata without resolving gameplay semantics, mutating source data, or changing production behavior.

Malformed tier/value policy status: documented and diagnostically validated. No semantic resolver behavior has been implemented from it.
Missing modifier reference mapping policy status: documented and diagnostically validated. No modifier mappings or semantic resolver behavior have been implemented from it.
Unsupported special behavior policy status: documented. No unsupported behavior validator or semantic resolver behavior has been implemented from it.
