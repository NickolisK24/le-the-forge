# Affixes Source Audit and Migration Plan

## 1. Purpose

This document defines a diagnostic-first source audit and migration plan for `affixes` and `affix_tiers` in the Phase 1 data bundle. It is a planning artifact only. It does not generate bundle family files, modify extraction logic, change Forge loaders, or activate production consumption.

The immediate goal is to decide how The Forge should evaluate affix identity, tier values, provenance, and safety before any production migration is considered.

Current boundary:

- `production_safe` remains `false`.
- `affixes`, `affix_tiers`, `affix_eligibility`, and `affix_tags` remain deferred/blocking bundle families.
- `affix_eligibility` and `affix_tags` remain separate validation gates unless later source evidence clearly proves they are safe to merge.
- No Forge production loaders consume canonical affix bundle families yet.
- The Phase 3 affix `910` duplicate eligibility finding has a diagnostic disposition only: it is a known decoded-source duplicate, not a production-safe eligibility result.
- Phases 1-5 are implemented and stable as diagnostics; the combined migration gate is warning-only after accepted Phase 3 exact duplicate policy application.
- The readiness sweep in `docs/migration/AFFIX_MIGRATION_READINESS_SWEEP.md` currently reports `non_production_consumer_allowed=true` for planning a minimum read-only diagnostic consumer only.
- Phase 6 production work must not begin. Phase 6 diagnostic consumer planning is captured in `docs/migration/PHASE_6_AFFIX_DIAGNOSTIC_CONSUMER_PLAN.md`; the implemented consumer remains limited to `production_safe=false`, generated diagnostic artifacts only, warning preservation, and no generated data mutation.
- Controlled affix resolver prototype planning and implementation are captured in `docs/migration/CONTROLLED_AFFIX_RESOLVER_PROTOTYPE_PLAN.md`. The implemented prototype remains diagnostic-only, generated-artifact-backed, read-only, warning-preserving, and isolated from production loaders, APIs, crafting, simulation, and gameplay output.
- The non-production affix inspection stack milestone is complete through Phase 1-6 diagnostics, controlled resolver output, saved-vs-fresh resolver comparison, and per-affix diagnostic records. Current inspection state is `diagnostic_only=true`, `production_safe=false`, `non_production_inspection_allowed=true`, 1227 per-affix records, 1112 equipment records, 115 idol records, 6959 embedded tiers, affix `910` duplicate evidence preserved, and warning metadata preserved.

## 2. Current Known Affix Sources

Known source files and scripts:

| Path | Current role | Source confidence | Notes |
| --- | --- | --- | --- |
| `exports_json/affixes.json` | Current generated affix export | Partial / diagnostic source | Contains `_meta`, `equipment`, and `idol` sections. Current counts are 1112 equipment affixes and 115 idol affixes, 1227 total. |
| `tools/scripts/process_affixes_tt.py` | Current TypeTree-based affix processor | Stronger than legacy positional parser, still not canonical bundle migration | Reads `MasterAffixesList` via TypeTree and writes `exports_json/affixes.json`. Adds `derivedTags` and `_extra` diagnostics. |
| `tools/scripts/process_affixes.py` | Legacy/library decoder and idol CSV merger | Useful decoder source, not a bundle generator | Provides enum decoding, `build_affix_record`, and `AffixImport.csv` parsing. Its main path consumes `extracted_raw/MasterAffixesList.json`. |
| `tools/scripts/extract_master_affixes.py` | Raw MasterAffixesList extractor | Raw extraction source | Extracts `extracted_raw/MasterAffixesList.json` from `resources.assets` using TypeTrees. |
| `extracted_raw/MasterAffixesList.json` | Raw equipment affix source when present | Raw evidence | Expected to contain `singleAffixes` and `multiAffixes`; includes extraction metadata. |
| `extracted_raw/AffixImport.csv` | Idol affix source | Raw/CSV evidence | Parsed as 115 idol affix rows by the current processor. |
| `extracted_raw/enums/enums.json` | Enum decode source | Required support source | Used for SP properties, AT tags, EquipmentType, and WeaponEffect labels. |
| `data_bundle/manifest.json` | Bundle control-plane status | Authoritative for current bundle state | Currently lists `affixes`, `affix_tiers`, `affix_eligibility`, and `affix_tags` in the `block` action summary. |
| `data_bundle/validation_status.json` | Bundle validation status | Authoritative for current validation state | Currently reports these four families as intentionally deferred/manifest-only. |

Current `exports_json/affixes.json` observed shape:

- Top level: `_meta`, `equipment`, `idol`.
- `_meta` includes `equipment_count`, `idol_count`, `pipeline`, `source`, `derived_tag_version`, `derived_tag_source`, and unknown decode counters.
- Equipment records include fields such as `id`, `name`, `displayName`, `type`, `levelRequirement`, `rollsOn`, `specialAffixType`, `classSpecificity`, `displayCategory`, `group`, `t6Compatibility`, `uniqueId`, `weaponEffect`, `canRollOn`, `weighting`, `tiers`, `property` or `affixProperties`, `tags`, `modifierType`, `derivedTags`, and `_extra`.
- Idol records include fields such as `id`, `name`, `displayName`, `levelRequirement`, `rollsOn`, `shardName`, `tiers`, and sometimes `tiers2`.

Verified source facts from current repo state:

- `exports_json/affixes.json` exists.
- It contains 1112 equipment affixes and 115 idol affixes.
- Equipment affixes are generated from `resources.assets (MasterAffixesList, parse_as_dict)` through the TypeTree pipeline.
- Idol affixes are parsed from `AffixImport.csv`.
- Tiers are currently embedded inside affix records, not emitted as a separate canonical `affix_tiers` bundle family.
- `derivedTags` exist but are derived fields, not yet an accepted canonical `affix_tags` family.
- Affix `910` has duplicate eligibility source evidence: `extracted_raw/MasterAffixesList.json` contains `multiAffixes[399].canRollOn == [31, 31]`; enum `31` resolves to `IDOL_4x1`; `exports_json/affixes.json` preserves this as duplicate `["IDOL_4x1", "IDOL_4x1"]`.

Assumptions that must not be promoted without validation:

- Affix IDs are globally stable across equipment and idol sources.
- Embedded tier rows are already normalized enough for production planner/crafting use.
- `canRollOn` is a complete eligibility model.
- Duplicate `canRollOn` entries can be silently collapsed for production use.
- `derivedTags` are authoritative category/tags.
- Display names, shard names, or tooltip text are stable identities.

## 3. What Affixes and Affix Tiers Can Be Trusted For

Until diagnostic validators exist, current affix exports can be used only as source evidence and planning input.

Reasonable diagnostic uses:

- Counting equipment and idol affix records.
- Inspecting raw affix identity candidates: `id`, `uniqueId`, `name`, `rollsOn`, `type`, `specialAffixType`.
- Inspecting embedded tier counts and min/max roll values.
- Inspecting decoded property/modifier/tag labels as extraction evidence.
- Comparing regenerated affix output against saved baselines.
- Designing canonical bundle shapes and validators.
- Building non-production reports that classify records as verified, partial, unknown, or unsafe.

Potentially canonical-ready only after validators:

- Affix identity, if a stable identity policy is proven.
- Affix tier rows, if tier identity and min/max roll semantics validate.
- Basic prefix/suffix/special classification, if enum decoding is proven stable.
- Basic source provenance, if every record carries source/build metadata and extraction path.

## 4. What Cannot Be Trusted Yet

The following must remain non-authoritative until separately audited and validated:

- Production affix legality.
- Crafting eligibility.
- Item type/subtype eligibility.
- Idol-specific affix placement rules.
- Tag/category semantics for planner filters.
- Derived tags as canonical truth.
- Name-only or display-name-only identity.
- Tier values as final simulator/crafting math without normalization checks.
- Special, personal, experimental, set, idol enchantment, and idol weaver semantics.
- Tooltip/prose interpretation.
- Runtime/scripted modifier behavior.
- Any Forge production loader behavior.

Affix data should not be called simulation-ready. A validated `affixes` family would still not prove `affix_eligibility`, `affix_tags`, crafting rules, or runtime mechanics.

## 5. Required Identity Fields

Future canonical `affixes` records should use deterministic, source-backed identity. The first validator should reject records that can only be identified by name or display text.

Required identity candidates to audit:

| Field | Requirement | Notes |
| --- | --- | --- |
| `id` | Required if present in source | Current equipment and idol records expose numeric `id`. Validate uniqueness within scope and across combined family. |
| `uniqueId` | Required for equipment records if source provides it | Current equipment records expose `uniqueId`. Determine whether it is globally meaningful or redundant with `id`. |
| `rollsOn` | Required | Separates `Equipment` vs `Idols`; may be part of canonical scoping. |
| `type` | Required where source provides it | Prefix/suffix/special classification. |
| `name` | Required as display/source label, not sole identity | Names may be useful for readability but must not be canonical identity alone. |
| `source_section` | Required in canonical bundle | Proposed values: `equipment`, `idol`. Prevents accidental collision between different source shapes. |
| `canonical_id` | Required in bundle shape | Proposed deterministic form should include stable numeric/source context, for example `equipment_affix__<id>__<slug>` or `idol_affix__<id>__<slug>`. The numeric/source portion must carry identity; slug is readability only. |

Identity rules:

- Do not use display name alone.
- Do not use `name` alone.
- Do not use shard name alone.
- Do not infer affix identity from property/modifier/tags alone.
- Do not mix equipment and idol records without explicit source scope.
- Do not use item `subtype_id` alone anywhere in affix eligibility planning.

## 6. Required Provenance Fields

Every future canonical family and record should carry provenance sufficient to explain where it came from and how it was decoded.

Recommended top-level provenance:

- `family`
- `schema_version`
- `generated_at`
- `source`
- `record_count`
- `source_patch`
- `source_build`
- `pipeline`
- `source_files`
- `validation_status`
- `production_safe: false`

Recommended per-record provenance:

- `source_file`
- `source_section`
- `source_pipeline`
- `source_record_id`
- `source_unique_id` where available
- `source_confidence`
- `field_confidence`
- `decode_warnings`
- `unknown_decode_counts` if applicable

Known provenance sources:

- `exports_json/affixes.json` `_meta.pipeline`: currently `typetree`.
- `exports_json/affixes.json` `_meta.source`: currently `resources.assets (MasterAffixesList, parse_as_dict)`.
- `tools/scripts/process_affixes_tt.py` `derived_tag_version` and `derived_tag_source`.
- `extracted_raw/MasterAffixesList.json` `_meta.game_build` when regenerated from raw extraction.
- `exports_json/metadata.json` for patch/build-level bundle context.

## 7. Relationship Between Affix Families

### `affixes`

The `affixes` family should define affix identity and stable descriptive/source fields. It should not silently include eligibility or tag semantics as authoritative data.

Candidate content:

- canonical affix ID
- source IDs
- source section
- name/display labels
- prefix/suffix/special type
- rolls-on domain
- source property/modifier evidence
- references to tier records
- references to tag records only after `affix_tags` validates
- references to eligibility records only after `affix_eligibility` validates

### `affix_tiers`

The `affix_tiers` family should normalize embedded tier rows into their own records. It should not rely on list position alone without preserving `affix_id`, `source_section`, `tier`, and property index/scope.

Candidate identity:

- `affix_id`
- `source_section`
- `tier`
- `property_index` for multi-property records
- `roll_channel` if needed for `tiers2` or `affixProperties`

Required values:

- `min_roll`
- `max_roll`
- source tier number
- source property reference
- source confidence

### `affix_eligibility`

Eligibility must remain a separate gate. It answers which affixes can roll on which item types, base types, subtypes, idol shapes, classes, or other constraints.

Known source candidates:

- `canRollOn` on equipment affixes.
- `rollsOn`.
- class specificity.
- idol CSV structure and any idol-specific placement context.
- item family records from `data_bundle/families/item_types.json` and `data_bundle/families/base_items.json`.

Do not treat `canRollOn` alone as full eligibility until validated against item base/type/subtype identity and Forge consumer needs.

Current Phase 3 duplicate disposition:

- Affix `910` has duplicate `canRollOn` target evidence for `IDOL_4x1`.
- Earliest available decoded source: `extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn`, with raw values `[31, 31]`.
- `extracted_raw/enums/enums.json` maps EquipmentType enum `31` to `IDOL_4x1`.
- `exports_json/affixes.json` preserves the duplicate as `["IDOL_4x1", "IDOL_4x1"]`.
- Normalization changes only casing/format to `IDOL_4X1`; it does not change identity.
- Current evidence does not show `process_affixes.py` or `process_affixes_tt.py` introduced the duplicate after `MasterAffixesList.json`.
- Byte-level/game-raw origin remains unresolved at the resources.assets / TypeTree-walker boundary.
- Production deduplication is not allowed yet.
- Diagnostic-only reports may show both raw duplicate count and normalized unique-target view. The normalized view is a diagnostic presentation aid, not source mutation.
- Phase 3 now reports `validation_status=warning` after the accepted exact duplicate policy was implemented in diagnostics.
- Phase 4 `affix_tags` may be planned only after this disposition is recorded, and it must not claim affix eligibility is safe.

Accepted diagnostic policy for exact duplicate eligibility targets:

- This policy is diagnostic-only. It does not mutate source data, generated exports, bundle candidates, Forge loaders, or production behavior.
- An exact duplicate eligibility target is the same raw target value appearing more than once in the same eligibility target list for the same stable source affix identity and source field. Example: `MasterAffixesList.json` `multiAffixes[399].canRollOn == [31, 31]`.
- A raw evidence duplicate is the source-preserved duplicate list, including duplicate count and positions. A normalized unique-target view is a diagnostic presentation that may show the unique normalized target once, while still reporting the raw duplicate evidence.
- Exact duplicates should remain `error` / blocking when source identity is unstable or missing, target normalization changes identity, duplicate positions are not reported, raw duplicate count is not preserved, targets conflict after normalization, item references are unresolved, or the duplicate could have been introduced by extraction/transformation.
- Exact duplicates may be downgraded to `warning` diagnostically only when all required evidence is present: stable source identity, no conflicting targets, normalized target identity unchanged, raw duplicate count preserved, duplicate positions exposed, no unresolved item target references, and a report label that the unique-target view is diagnostic-only.
- Production data must not be silently deduplicated because that would erase source evidence, hide upstream anomalies, mask future extractor regressions, and change generated output without a production migration review.
- Under this accepted policy, affix `910` is classified as diagnostic warning-only because the available evidence is stable and exact: source `multiAffixes[399]`, raw values `[31, 31]`, enum `31` resolving both entries to `IDOL_4x1`, exported values `["IDOL_4x1", "IDOL_4x1"]`, and normalization only changing casing/format to `IDOL_4X1`.
- The affix `910` candidate classification does not prove byte-level/game-raw origin, does not approve production deduplication, and does not make eligibility production-safe.
- Phase 3 is warning-only for this exact duplicate class. Phase 6 is implemented only as a read-only diagnostic consumer. That remains diagnostic-only and `production_safe=false`; it does not authorize production migration.

### `affix_tags`

Tags must remain a separate gate. Current `derivedTags` are deterministic derivations from decoded fields, but they are not yet a canonical tag family.

Known source candidates:

- SP property.
- AT tags.
- modifier type.
- rolls-on.
- canRollOn.
- special affix type.
- display category and group.

Tag validation must prove derivation rules, unknown decode behavior, and intended consumer semantics before tags are used authoritatively.

### Item Base/Subtype Identity

Affix eligibility cannot be production-safe unless it relates to canonical item identity correctly:

- `item_types` and `base_items` are generated, but Forge production consumption is not migrated.
- `subtype_id` is scoped under `base_type_id`.
- `subtype_id` alone must never be used as identity.
- Name-only base item matching is unsafe.
- Eligibility validators must reference canonical item type/base identity, not display names or prose.

## 8. Diagnostic Checks Required Before Migration

### Shape checks

- `exports_json/affixes.json` exists and is valid JSON.
- Top-level `_meta`, `equipment`, and `idol` sections exist.
- Equipment and idol record counts match `_meta`.
- Required record fields exist per section.
- Tier arrays exist and are arrays where expected.
- Multi-property records preserve property/tier structure.

### Identity checks

- `id` values are present.
- `id` uniqueness is checked within `equipment`, within `idol`, and across a proposed combined family.
- `uniqueId` behavior is audited for equipment records.
- Proposed canonical IDs are deterministic and unique.
- Names/display names are never sole identity.
- Records with missing source IDs are blocked or marked unsafe.

### Tier checks

- Every tier record has an affix reference, tier number, min roll, and max roll.
- Tier order is deterministic.
- Tier counts match source arrays.
- Multi-property tier channels are represented explicitly.
- `tiers2` idol rows are represented explicitly or blocked until modeled.
- No tier row is inferred from display text.

### Provenance checks

- Top-level metadata includes source file, extraction pipeline, patch/build, generated timestamp, and source confidence.
- Per-record source section and source ID are present.
- Unknown enum/decode counters are surfaced.
- Derived fields identify derivation source and version.

### Relationship checks

- `affixes` tier references resolve to `affix_tiers`.
- `affix_tiers` references resolve back to `affixes`.
- Eligibility references, when introduced, resolve to `affixes`, `item_types`, and `base_items`.
- Tag references, when introduced, resolve to `affixes` and tag definitions.

### Safety checks

- `production_safe` remains `false`.
- Families remain advisory/diagnostic until Forge-side non-production reports validate consumption.
- No eligibility or tag data is silently promoted with affix identity.
- No `subtype_id`-only item identity is accepted.
- No name-only matching is accepted.

## 9. Non-Production Reports Needed Before Loader Changes

Before any importer or loader changes in The Forge, last-epoch-data should produce or enable these reports:

1. Affix source shape report
   - Counts equipment/idol records.
   - Lists missing required fields.
   - Lists unknown enum/decode counters.
   - Reports top-level provenance.

2. Affix identity/provenance report
   - Proposes canonical affix IDs.
   - Reports ID collisions.
   - Reports name/display duplicate risks.
   - Confirms no name-only identity.

3. Affix tier normalization report
   - Flattens proposed tier records in diagnostic output.
   - Reports tier count deltas against embedded source.
   - Reports multi-property/`tiers2` representation risks.

4. Affix eligibility audit report
   - Evaluates `canRollOn`, `rollsOn`, class specificity, and item type/base relationships.
   - Reports unresolved references to `item_types` and `base_items`.
   - Keeps eligibility separate from affix/tier identity.

5. Affix tag derivation report
   - Lists source fields used for tags.
   - Reports derivation version.
   - Reports unknown tags or enum gaps.
   - Keeps tags separate from affix/tier identity.

6. Saved-vs-fresh diagnostic comparison
   - Compares saved diagnostic artifacts against freshly generated diagnostics.
   - Reports count deltas, ID deltas, tier deltas, warnings, and errors.
   - Must remain diagnostic-only.

Forge should not change production loaders until these reports exist and pass their documented gates.

## 10. Explicit Blocked or Unsafe Assumptions

Blocked assumptions:

- Affix migration is complete.
- Affix tiers are production-ready because tiers appear in `exports_json/affixes.json`.
- Eligibility is solved by `canRollOn`.
- Tags are solved by `derivedTags`.
- Tags can be merged into `affixes` without separate validation.
- Eligibility can be merged into `affixes` without separate validation.
- Names, display names, shard names, or tooltip text are stable identities.
- Item subtype IDs are globally unique.
- Base item names can identify eligibility targets.
- Affix records are simulation-ready.
- Runtime/scripted modifier behavior is represented by raw affix rows.
- Forge production loaders can consume bundle affix IDs without an adapter/report phase.

Unsafe migration behavior:

- Setting `production_safe=true`.
- Replacing Forge production affix loaders from this plan.
- Inferring missing IDs from prose or display text.
- Collapsing equipment and idol affixes without source scope.
- Dropping tier/property channel information for multi-stat affixes.
- Treating warnings as passes.
- Removing hardcoded/static Forge fallbacks before rollback and validation exist.

## 11. Proposed Bundle Shapes

These are planning shapes only. They are not implemented by this document.

### `affixes`

```json
{
  "family": "affixes",
  "schema_version": "1.0.0",
  "generated_at": "ISO-8601",
  "production_safe": false,
  "source": {
    "primary": "exports_json/affixes.json",
    "sections": ["equipment", "idol"],
    "pipeline": "typetree"
  },
  "record_count": 0,
  "records": [
    {
      "id": "equipment_affix__0__void_penetration",
      "source_section": "equipment",
      "game_id": 0,
      "unique_id": 0,
      "name": "Void Penetration",
      "display_name": "",
      "affix_type": "PREFIX",
      "rolls_on": "Equipment",
      "special_affix_type": "Standard",
      "tier_refs": [],
      "eligibility_ref_status": "deferred",
      "tag_ref_status": "deferred",
      "source": {
        "file": "exports_json/affixes.json",
        "section": "equipment"
      },
      "source_confidence": {
        "identity": "Partial",
        "tiers": "Partial",
        "eligibility": "Deferred",
        "tags": "Deferred"
      }
    }
  ]
}
```

### `affix_tiers`

```json
{
  "family": "affix_tiers",
  "schema_version": "1.0.0",
  "generated_at": "ISO-8601",
  "production_safe": false,
  "source": {
    "primary": "exports_json/affixes.json"
  },
  "record_count": 0,
  "records": [
    {
      "id": "equipment_affix__0__tier__1__property__0",
      "affix_id": "equipment_affix__0__void_penetration",
      "source_section": "equipment",
      "source_affix_id": 0,
      "tier": 1,
      "property_index": 0,
      "min_roll": 0.04,
      "max_roll": 0.04,
      "source_confidence": {
        "identity": "Partial",
        "values": "Partial"
      }
    }
  ]
}
```

## 12. Proposed Phased Migration Sequence

### Phase 0 — Source Audit Only

Status: this document.

Outputs:

- Source inventory.
- Trusted vs untrusted field classification.
- Required identity/provenance rules.
- Separate gates for eligibility and tags.

No code or generated data changes.

### Phase 1 — Affix/Affix Tier Diagnostic Shape Validator

Goal:

- Validate current `exports_json/affixes.json` shape.
- Validate top-level counts and section presence.
- Validate tier arrays and multi-property shapes.

Output:

- Non-production diagnostic report.
- Tests using small fixtures.

Still no bundle family generation.

### Phase 2 — Affix Identity/Provenance Validator

Goal:

- Propose deterministic canonical IDs.
- Validate source IDs and provenance fields.
- Reject name-only identity.
- Report ID collisions and duplicate display names.

Output:

- Diagnostic identity/provenance report.
- Saved-vs-fresh fixture if useful.

Still no Forge loader changes.

### Phase 3 — Eligibility Diagnostic Validator

Goal:

- Evaluate `canRollOn`, `rollsOn`, class specificity, idol context, and item type/base references.
- Validate that item/base references use canonical `item_types` and scoped `base_items`.
- Reject `subtype_id`-only identity.

Output:

- Separate `affix_eligibility` diagnostic report.

This gate remains separate from affix/tier identity.

Current disposition for the affix `910` duplicate target:

- Treat as a known decoded-source duplicate for diagnostic planning only.
- Keep raw duplicate reporting visible.
- Permit diagnostic-only normalized unique-target presentation.
- Do not deduplicate source data, generated exports, or bundle candidates.
- Keep `production_safe=false`.
- Keep Phase 3 warning-only exact duplicate policy visible; do not silently deduplicate or hide raw duplicate evidence.

### Phase 4 — Tag/Category Diagnostic Validator

Goal:

- Evaluate `tags`, `derivedTags`, display category, group, property, modifier type, and derivation rules.
- Validate `derived_tag_version` and unknown decode behavior.
- Do not use Phase 4 to bypass the Phase 3 duplicate eligibility policy.
- Do not claim affix eligibility is safe.

Output:

- Separate `affix_tags` diagnostic report.

This gate remains separate from affix/tier identity.

Current status:

- Implemented as diagnostic-only tooling in `last-epoch-data`.
- Current validation status is `warning`.
- Current report inspects 1227 affixes, finds tag/category evidence for all 1227, reports 148 unknown or unsupported tag/category values, 110 ambiguous tag/category mappings, 0 duplicate tag/category records, 0 name-only records, 0 subtype_id-only records, and 0 missing provenance records.
- Phase 3 eligibility is `validation_status=warning` after accepted exact duplicate policy application. Phase 4 remains separate and does not prove eligibility safety.
- `production_safe=false` remains unchanged.

### Phase 5 — Saved-vs-Fresh Diagnostic Comparison

Goal:

- Compare saved diagnostic reports with freshly generated reports.
- Surface count, ID, tier, warning, and provenance drift.

Output:

- Combined comparison report with `production_safe=false`.

Current status:

- Implemented as diagnostic-only tooling in `last-epoch-data`.
- Current `migration_gate_status` is `warning`.
- Saved and fresh diagnostics agree for all four phases: Phase 1 `warning`, Phase 2 `warning`, Phase 3 `warning`, Phase 4 `warning`.
- Count deltas are zero, warning deltas are zero, and error deltas are zero.
- Phase 3 affix `910` duplicate eligibility is warning-only under the accepted diagnostic policy and remains visible in the combined gate.
- Phase 4 tag/category warnings remain present and visible.
- `production_safe=false` remains unchanged.

Milestone closeout:

- Phase 1 affix source/tier shape diagnostic is complete with `warning` status.
- Phase 2 affix identity/provenance diagnostic is complete with `warning` status.
- Phase 3 affix eligibility diagnostic is complete with `warning` status.
- Phase 4 affix tag/category diagnostic is complete with `warning` status.
- Phase 5 saved-vs-fresh comparison is complete and stable.
- Affix readiness sweep is complete and currently reports `non_production_consumer_allowed=true` for planning a minimum read-only diagnostic consumer only.
- Diagnostic agreement unblocked only the minimum Phase 6 diagnostic consumer; it does not unblock production migration.
- Affix `910` duplicate `canRollOn` evidence remains warning-only and is not deduplicated.
- No production consumer should be built; Phase 6 work must remain diagnostic-only and warning-preserving.

### Phase 6 — Non-Production Consumer Only

Status: implemented as read-only diagnostic tooling; production migration not started.

Goal:

- Allow Forge or last-epoch-data developer tools to consume validated diagnostic artifacts.
- No production loader replacement.
- No public API behavior changes.

Output:

- Developer-only report or CLI consumer.
- Explicit warning labels.
- Generated markdown and JSON reports in `docs/generated/affix_diagnostic_consumer_report.md` and `docs/generated/affix_diagnostic_consumer_report.json`.

Current boundary:

- Phase 3 eligibility is warning-only because affix `910` satisfies the accepted exact duplicate diagnostic policy.
- Phase 5 saved-vs-fresh comparison is `migration_gate_status=warning`.
- The readiness sweep reports `non_production_consumer_allowed=true` for the minimum read-only diagnostic consumer.
- The Phase 6 plan is documented in `docs/migration/PHASE_6_AFFIX_DIAGNOSTIC_CONSUMER_PLAN.md`.
- The Phase 6 consumer is implemented in `backend/app/game_data/affix_diagnostic_consumer.py` and `backend/scripts/report_affix_diagnostic_consumer.py`.
- The generated Phase 6 reports are `docs/generated/affix_diagnostic_consumer_report.md` and `docs/generated/affix_diagnostic_consumer_report.json`.
- The Phase 6 report states `non_production_inspection_allowed=true` and `production_safe=false`.
- Phase 1-5 remain warning-level, Phase 5 remains `migration_gate_status=warning`, affix `910` evidence remains preserved, and tag/category warnings remain preserved.
- Phase 6 must not generate bundle families, replace loaders, change runtime behavior, or set `production_safe=true`.
- The broader non-production affix inspection stack now also includes the controlled resolver prototype, saved-vs-fresh resolver comparison, and per-affix diagnostic record artifact. These layers remain inspection-only and do not advance Phase 7 production migration planning.

### Phase 7 — Production Migration Planning

Goal:

- Start production migration planning only after prior diagnostic gates pass.

Required before this phase:

- Bundle family files generated and validated.
- Forge-side diagnostic consumers complete.
- Rollback behavior defined.
- Fallback visibility defined.
- Production-safe criteria documented.
- `production_safe` remains false until a separate explicit production readiness review.

### Controlled Affix Resolver Prototype — Diagnostic Step

Status: implemented as CLI-only read-only diagnostic tooling.

Goal:

- Resolve validated/generated affix diagnostic artifacts into deterministic, inspection-safe normalized affix objects.
- Preserve identity, provenance, warnings, errors, eligibility evidence, tag/category warning state, and affix `910` duplicate evidence.
- Keep raw duplicate evidence separate from any diagnostic-only normalized unique-target views.

Boundary:

- Consume generated diagnostic artifacts only.
- Do not consume production bundle data as authority.
- Do not read raw source exports directly unless a separate diagnostic input contract is approved.
- Do not power gameplay calculations, crafting, item generation, build math, APIs, frontend behavior, or runtime systems.
- Do not deduplicate source evidence.
- Do not set `production_safe=true`.

Reference:

- `docs/migration/CONTROLLED_AFFIX_RESOLVER_PROTOTYPE_PLAN.md`
- `docs/generated/controlled_affix_resolver_prototype_report.md`
- `docs/generated/controlled_affix_resolver_prototype_report.json`

## 13. Forge Evaluation Criteria

The Forge should evaluate future affix/tier artifacts only through diagnostics at first.

Minimum criteria before non-production Forge consumption:

- Bundle compatibility reader can inspect affix family metadata.
- Affix identity/provenance diagnostics have no errors.
- Tier diagnostics have no unresolved tier references.
- Eligibility and tags are either validated or explicitly deferred.
- All reports keep `production_safe=false`.
- Missing eligibility/tag data warns or blocks; it does not silently pass.

Minimum criteria before production migration planning:

- Forge has adapter/consumer tests for affix identity.
- Forge has rollback behavior.
- Forge labels advisory/partial surfaces honestly.
- Forge does not replace crafting/planner legality until eligibility validates.
- Forge does not use base item names or subtype IDs alone.

## 14. Documentation and Tracker Updates Later

When later implementation starts, update these documents:

- `FULL_REPO_AUDIT.md`
- `DATA_BUNDLE_SPEC.md`
- `FORGE_DATA_CONTRACT.md`
- `BUNDLE_COMPATIBILITY_IMPLEMENTATION_PLAN.md`
- `data_bundle/reports/migration_notes.md`
- `data_bundle/reports/known_gaps.json`
- `le-the-forge/docs/FORGE_MIGRATION_TRACKER.md`

Do not update them to claim production readiness unless a separate production migration review has passed.

## 15. Recommended Next Implementation Prompt

Recommended next task:

```text
Create a diagnostic-only stat/modifier reference audit for affix modifier evidence.

Scope:
- Keep the next step diagnostic-only and developer-only.
- Read approved generated diagnostic artifacts and explicit diagnostic source evidence only under a documented input contract.
- Audit stat/modifier references, unsupported fields, missing references, malformed tier/modifier evidence, and warning categories before any controlled modifier resolver exists.
- Preserve raw duplicate reporting.
- Preserve duplicate positions.
- Preserve diagnostic-only normalized unique-target views as report presentation only.
- Keep source/generated data unchanged.
- Consume saved/generated diagnostics only.
- Preserve Phase 1-5 warning metadata, including affix `910` raw duplicate count and duplicate positions.
- Keep Phase 6 consumer output diagnostic-only and `production_safe=false`.

Constraints:
- Do not deduplicate affix 910.
- Do not generate affix bundle families.
- Do not create production Forge consumers.
- Do not power gameplay calculations, crafting, build math, APIs, frontend behavior, or runtime systems.
- Do not change production Forge behavior.
- Keep production_safe=false.
```

Rationale: the inspection stack now proves affix record identity, provenance, eligibility warning state, tag/category warning state, deterministic resolver output, and per-affix diagnostic records. The next step that most directly moves toward safe gameplay correctness is not a UI/report surface or production consumer; it is a stat/modifier reference audit that determines whether affix modifier evidence can be trusted enough to design a later controlled, non-production modifier resolver.

Policy update:

- `docs/migration/MODIFIER_RESOLUTION_POLICY.md` defines the current diagnostic-only modifier resolution policy.
- The policy records current audited categories: 6844 structurally present references, 115 unresolved references, 136 malformed or semantically unresolved structures, and 1112 unsupported or unresolved structures.
- A future controlled modifier resolver prototype may include only inspection-safe structurally present references and must keep unresolved, malformed, and unsupported evidence out of resolved semantics.
- Unsupported structures cannot be guessed.
- Warning metadata and provenance must propagate.
- The policy does not implement a resolver, does not change generated data, and does not make affixes production-safe.
