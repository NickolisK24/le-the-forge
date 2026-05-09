# Forge Migration Tracker

This is the living cross-repo migration tracker for:

- `D:\Forge\le-the-forge`
- `D:\Forge\last-epoch-data`

It tracks current migration state, completed milestones, known blockers, safety boundaries, canonical family status, Forge consumer status, and next actions. It is documentation/tracking only. It does not activate migration or change production behavior.

## 1. Current Program State

| Area | Current State |
| --- | --- |
| Current phase | Sidecar diagnostics milestone complete; affix diagnostics Phases 1-5 complete with warning-only migration gate after accepted exact duplicate eligibility policy application. |
| Current boundary | Developer-only diagnostics; no production bundle consumption. |
| Current compatibility state | `compatible_with_warnings` expected from Forge compatibility reader. |
| Current production status | Existing Forge loaders, importers, API behavior, frontend behavior, and simulation behavior remain unchanged. |
| Current bundle status | `last-epoch-data` bundle validates as `WARN` with no critical errors. |
| Current item migration state | `item_types` and `base_items` are generated in the bundle and validated, but only diagnostic consumers exist in Forge. |
| Current importer migration state | LET diagnostics can inspect copied/synthetic/offline context; production importer output is unchanged. |
| Current sidecar state | Sidecar builder, validator, saved fixture validation, saved-sidecar diagnostic consumer, fresh-sidecar diagnostic validation, and saved-vs-fresh comparison diagnostics are complete as non-production validation surfaces; all remain developer-only and warning states stay visible. |
| Current affix diagnostic state | The non-production affix inspection stack milestone is complete. It includes Phase 1 source/tier shape diagnostics, Phase 2 identity/provenance diagnostics, Phase 3 eligibility diagnostics with accepted exact duplicate policy handling, Phase 4 tag/category diagnostics, Phase 5 saved-vs-fresh comparison, Phase 6 read-only diagnostic consumer, controlled affix resolver prototype, saved-vs-fresh resolver comparison, and the per-affix diagnostic record artifact. All reports remain diagnostic-only. Phase 1-5 are `warning`; Phase 5 has zero count/warning/error deltas; Phase 6 records `non_production_inspection_allowed=true`; the resolver comparison is `warning` with deterministic output agreement; the per-affix artifact has 1227 records, 1112 equipment records, 115 idol records, and 6959 embedded tiers. Affix `910` duplicate eligibility evidence and warning metadata remain preserved. `production_safe=false` remains explicit. No affix bundle family is generated or consumed. |
| Current production safety | `production_safe=false` across mapping fixtures, adapter translations, resolver output, sidecars, and validators. |

Short version:

- Diagnostics only.
- No production loaders replaced.
- No production bundle consumer activated.
- `item_types` and `base_items` are generated, but not production-consumed.
- LET importer context diagnostics exist, but live LET payload shape is not proven.
- The sidecar diagnostics milestone is complete for non-production validation.
- The non-production affix inspection stack is complete for diagnostics: Phase 1-6, controlled resolver prototype, resolver comparison, and per-affix diagnostic record artifact all exist, while production affix migration remains forbidden.
- The controlled modifier inspection stack milestone is complete for diagnostics: stat/modifier reference audit, modifier resolution policy, controlled modifier resolver prototype, saved-vs-fresh comparison, unresolved modifier category triage, missing modifier reference mapping policy, malformed tier/value shape policy, and malformed tier/value shape validation all exist as non-production, read-only planning/tooling. Current state is `diagnostic_only=true`, `production_safe=false`, `comparison_status=warning`, 6959 total modifier references, 5596 resolved inspection-only references, 115 unresolved references, 136 malformed references, and 1112 unsupported references. The unresolved triage classifies those blockers as missing reference mapping, malformed tier/value shape, and unsupported special behavior. The missing mapping policy requires the 115 references to remain unresolved until source-backed mapping evidence exists, and forbids display-name-only or `subtype_id`-only mapping inference. The malformed tier/value validator reports `validation_status=warning`: all 136 malformed records preserve raw min/max/order evidence, provenance, and warning metadata; 136 diagnostic normalized views are labeled `diagnostic_only_not_source_mutation`; 34 inverted negative ranges are surfaced; no raw evidence is missing. Count deltas and warning category deltas are zero; deterministic output, provenance coverage, and affix `910` duplicate evidence all agree. No gameplay/crafting/build-math semantics are inferred.

## 2. Current Safety Boundary

### Proven

- `last-epoch-data` can generate and validate the bundle control plane.
- `last-epoch-data` can generate `item_types` and `base_items` from `exports_json/items.json`.
- `subTypeID` is scoped under `baseTypeID`.
- `le-the-forge` can inspect bundle compatibility without replacing loaders.
- Item type mapping assumptions can be reviewed and tested.
- Adapter translations can require `base_type_id`.
- Dry-run resolver can resolve ID-backed mappings and warn on missing context.
- LET importer mapped output can preserve `base_type_id` when input has it.
- Sidecar builder and validator chain works.
- Saved sidecar JSON validates independently from the builder path.
- A CLI-only consumer can read the saved sidecar after validation and report resolver results without production behavior changes.
- Freshly built sidecars can be validated against saved-sidecar shape expectations and identity safety rules before any future consumer uses them.
- Saved and fresh sidecar diagnostic outputs can be compared in one non-production report with `migration_gate_status=warning`.

### Not Activated

- No production bundle IDs are consumed.
- No production item/base item loaders are replaced.
- No importer output shape is changed.
- No public API response includes sidecar data.
- No frontend behavior changes.
- No simulation behavior changes.
- No production adapter code exists.
- No mapping is `production_safe=true`.

### Warning-Only / Diagnostic-Only

- Bundle compatibility remains `compatible_with_warnings`.
- Bundle validation remains `WARN`.
- `item_types` and `base_items` are generated but Forge-side use is diagnostic-only.
- Sidecar validation is `warning` because fixtures are synthetic/offline and mapped output lacks item type context.
- Current LET fixture evidence does not prove live LET payload shape.
- Saved/fresh sidecar shape agreement is confirmed and count deltas are zero, but warning deltas remain intentional and visible.
- Affix source-shape, identity/provenance, eligibility, and tag/category validation are warning-only. Affix eligibility validation is separate and only downgrades exact raw duplicate targets when every accepted policy condition is satisfied. None of these diagnostics validate importer use, loader use, or simulation semantics.
- Affix diagnostic Phases 1-5 are implemented and stable as diagnostics. This means the diagnostic milestone is complete, not that migration is unblocked.

### Must Not Be Done Yet

- Do not consume bundle IDs in production.
- Do not change importer output.
- Do not use `subtype_id` alone as identity.
- Do not migrate base items by name-only matching.
- Do not depend on live LET payload shape without captured/offline validation.
- Do not expose sidecars publicly.
- Do not create production adapter code.
- Do not mark `production_safe=true`.
- Do not treat affix source-shape or identity/provenance validation as affix migration completion.
- Do not merge `affix_eligibility` or `affix_tags` into the affix gate without separate source evidence and diagnostics.
- Do not downgrade Phase 3 eligibility warnings to passing without source-level review.

## 3. Migration Phases

### Phase 0 — Planning Foundation

Status: COMPLETE

Completed milestones:

- `last-epoch-data/FORGE_DATA_CONTRACT.md`
- `last-epoch-data/DATA_BUNDLE_SPEC.md`
- `last-epoch-data/BUNDLE_COMPATIBILITY_IMPLEMENTATION_PLAN.md`
- `last-epoch-data/FIRST_CANONICAL_MIGRATION_PLAN.md`
- `last-epoch-data/ITEM_TYPES_BASE_ITEMS_SOURCE_AUDIT.md`
- `le-the-forge/docs/FORGE_SYSTEM_PILLARS.md`
- `le-the-forge/docs/FULL_REPO_AUDIT.md`
- `last-epoch-data/FULL_REPO_AUDIT.md`
- `D:\Forge\FORGE_ECOSYSTEM_PROGRAM_SUMMARY.md`

Current blockers:

- None for planning foundation.

Next safe step:

- Keep this tracker current as later diagnostics and migrations land.

### Phase 1 — Bundle Control Plane

Status: COMPLETE

Completed milestones:

- Phase 1A bundle skeleton.
- Phase 1B bundle validator.
- Phase 1C Forge compatibility reader.
- Phase 1D cross-repo smoke test.

Current blockers:

- None for control-plane inspection.
- Overall compatibility remains warning-level because family migration is incomplete.

Next safe step:

- Continue running bundle generation/validation and Forge smoke checks after family changes.

### Phase 2 — First Canonical Families

Status: COMPLETE for generated `item_types` and `base_items`; IN_PROGRESS for broader item system.

Completed milestones:

- `item_types` generated.
- `base_items` generated.
- Bundle manifest integration.
- Bundle validation extended for generated item families.
- Known gaps and migration notes updated.

Current blockers:

- Forge production consumers are not migrated.
- Base item production migration is blocked by missing `base_type_id` / `subtype_id` in current Forge base item data.
- Implicit refs are not mechanics.
- Affixes and embedded tiers have diagnostic shape and identity/provenance validators; no canonical affix bundle family exists.
- Affix eligibility has a separate diagnostic validator and is warning-only after applying the accepted exact duplicate target policy for affix `910`.
- Affix tags/categories have a separate diagnostic validator but are not migrated.

Current disposition:

- Affix `910` has a duplicate `canRollOn` target that is accepted as a known decoded-source duplicate for diagnostic planning only.
- Accepted diagnostic policy: exact raw-source duplicate eligibility targets may be downgraded to warning-only diagnostically only when stable source identity exists, targets do not conflict, normalized target identity is unchanged, raw duplicate count is preserved, and duplicate positions remain visible.
- Affix `910` satisfies this accepted warning-only classification because both raw entries are source `31`, both resolve to `IDOL_4x1`, and normalization only changes casing/format to `IDOL_4X1`.
- Phase 3 now reports `validation_status=warning` after applying the accepted policy in the diagnostic validator/report.
- Phase 4 `affix_tags` / category validation exists as a warning-level diagnostic gate, but it does not claim eligibility is safe and remains separate from identity and eligibility.
- Phase 5 saved-vs-fresh comparison is stable with zero count, warning, and error deltas. Its combined `migration_gate_status` is `warning`.

Next safe step:

- Treat the non-production affix inspection stack as complete for read-only diagnostics. The controlled modifier resolver prototype and saved-vs-fresh comparison now follow the diagnostic-only modifier resolution policy in `docs/migration/MODIFIER_RESOLUTION_POLICY.md`; gameplay correctness cannot advance safely until unresolved references, unsupported fields, and malformed stat/modifier evidence have separate semantic policies or remain explicitly unresolved.

### Phase 3 — Forge Item Diagnostics

Status: COMPLETE for diagnostic chain; NOT_STARTED for non-production consumer.

Completed milestones:

- Bundle item diff diagnostic.
- Adapter map proposal.
- Adapter report command.
- Mapping assumption tests.
- Reviewed mapping fixture.
- Needs-adapter review.
- Adapter translation fixture.
- Dry-run resolver.
- Context coverage report.

Current blockers:

- No non-production consumer selected.
- `spear` remains `needs_review`.
- Collapsed groups require `base_type_id`.
- `production_safe=false` remains required.

Next safe step:

- Design a sidecar-backed or saved-fixture-backed non-production diagnostic consumer.

### Phase 4 — LET Import Context Diagnostics

Status: COMPLETE for current synthetic/offline diagnostics; BLOCKED for live payload proof.

Completed milestones:

- Import context dry-run report.
- Representative parsed gear fixture.
- Importer fixture context audit.
- Offline buildInfo fixture.
- Stage context comparison.

Current blockers:

- Live LET payload shape is unconfirmed.
- Mapped importer output preserves `base_type_id` but lacks item type context.
- Current sidecar/stage diagnostics rely on test-only pairing for most records.

Next safe step:

- Use saved sidecar fixture for the first non-production diagnostic consumer, not production importer output.

### Phase 5 — Sidecar Diagnostics

Status: COMPLETE for builder/validator/saved artifact validation.

Completed milestones:

- Sidecar design.
- Sidecar builder.
- Sidecar validator.
- Saved sidecar fixture.
- Saved sidecar validation report.

Current blockers:

- Sidecar is synthetic/offline and diagnostic-only.
- No production endpoint or loader should consume it.

Next safe step:

- Validate any future non-production diagnostic consumer against the saved sidecar fixture before reading live importer output.

### Phase 6 — First Non-Production Diagnostic Consumer

Status: COMPLETE for saved-sidecar diagnostic consumption, fresh-sidecar diagnostic validation, saved-vs-fresh sidecar comparison, and minimum affix diagnostic artifact consumption as non-production validation surfaces; NOT_STARTED for any live importer diagnostic consumer or production migration.

Target:

- A developer-only CLI/report that reads saved sidecar diagnostics and reports canonical bundle item type resolver results without changing app behavior.

Completed milestones:

- Sidecar-backed diagnostic consumer design.
- `backend/app/game_data/le_tools_sidecar_diagnostic_consumer.py`.
- `backend/scripts/consume_le_tools_sidecar_diagnostic.py`.
- `backend/tests/test_le_tools_sidecar_diagnostic_consumer.py`.
- `docs/generated/le_tools_sidecar_diagnostic_consumer_report.md`.
- `backend/app/game_data/le_tools_fresh_sidecar_diagnostic.py`.
- `backend/scripts/validate_fresh_le_tools_sidecar.py`.
- `backend/tests/test_le_tools_fresh_sidecar_diagnostic.py`.
- `docs/generated/fresh_le_tools_sidecar_diagnostic_report.md`.
- `backend/app/game_data/le_tools_sidecar_diagnostic_comparison.py`.
- `backend/scripts/compare_le_tools_sidecar_diagnostics.py`.
- `backend/tests/test_le_tools_sidecar_diagnostic_comparison.py`.
- `docs/generated/le_tools_sidecar_diagnostic_comparison_report.md`.
- Phase 6 affix diagnostic consumer design.
- `backend/app/game_data/affix_diagnostic_consumer.py`.
- `backend/scripts/report_affix_diagnostic_consumer.py`.
- `backend/tests/test_affix_diagnostic_consumer.py`.
- `docs/generated/affix_diagnostic_consumer_report.md`.
- `docs/generated/affix_diagnostic_consumer_report.json`.

Current blockers:

- Consumer is intentionally limited to saved sidecar artifacts.
- Fresh-sidecar validation is diagnostic-only and does not make fresh sidecars production-safe.
- Saved/fresh shape agreement is confirmed and count deltas are zero.
- Comparison result remains `warning` because warning deltas remain visible by design.
- It does not prove live LET payload shape.
- It does not prove production importer or bundle consumption readiness.
- The affix diagnostic consumer reads generated diagnostic artifacts only and does not consume production bundle data, source exports, loaders, importers, APIs, frontend behavior, crafting, simulation, or gameplay output.

Next safe step:

- Treat this diagnostic consumer milestone as complete for inspection-only use. Do not start production migration.

### Phase 7 — Future Production Migration

Status: NOT_STARTED / BLOCKED

Production blockers:

- No production-safe adapter.
- No production fallback/rollback strategy.
- No production consumer tests.
- Live LET payload shape unconfirmed.
- Base items cannot be migrated authoritatively without source IDs or validated composite matching.
- Required Now families beyond `item_types` / `base_items` remain deferred.

Next safe step:

- Do not start production migration until Phase 6 proves a non-production consumer safely.

## 4. Completed Milestones

### Planning Foundation

- [x] Forge data contract.
- [x] Data bundle spec.
- [x] Forge system pillars.
- [x] Bundle compatibility implementation plan.
- [x] First canonical migration plan.
- [x] Item types/base items source audit.
- [x] Full repo audit for `le-the-forge`.
- [x] Full repo audit for `last-epoch-data`.
- [x] Ecosystem program summary.

### Bundle Control Plane

- [x] Phase 1A bundle skeleton.
- [x] Phase 1B bundle validator.
- [x] Phase 1C Forge compatibility reader.
- [x] Phase 1D cross-repo smoke test.

### Canonical Families

- [x] `item_types` generated.
- [x] `base_items` generated.
- [x] bundle validation extended.
- [x] manifest integration.
- [x] known gaps updated.
- [x] migration notes updated.
- [x] bundle compatibility still `compatible_with_warnings`.

### Forge Diagnostics

- [x] bundle item diff diagnostic.
- [x] adapter map proposal.
- [x] adapter report command.
- [x] mapping assumption tests.
- [x] reviewed mapping fixture.
- [x] needs_adapter review.
- [x] adapter translation fixture.
- [x] dry-run resolver.
- [x] context coverage report.
- [x] context usage audit.

### LET Diagnostics

- [x] import context dry-run report.
- [x] representative parsed gear fixture.
- [x] importer fixture context audit.
- [x] offline buildInfo fixture.
- [x] stage context comparison.
- [x] sidecar design.
- [x] sidecar builder.
- [x] sidecar validator.
- [x] saved sidecar validation.
- [x] sidecar-backed diagnostic consumer design.
- [x] saved sidecar diagnostic consumer.
- [x] fresh sidecar diagnostic validation.
- [x] saved-vs-fresh sidecar diagnostic comparison.

### Affix Diagnostics

- [x] affix source audit and migration plan.
- [x] affix / embedded affix tier source-shape validator.
- [x] generated affix source-shape diagnostic report.
- [x] affix identity and provenance validator.
- [x] generated affix identity/provenance diagnostic report.
- [x] affix eligibility diagnostic validator.
- [x] generated affix eligibility diagnostic report.
- [x] affix tag/category diagnostic validator.
- [x] saved-vs-fresh affix diagnostic comparison.
- [x] affix migration readiness sweep.
- [x] Phase 6 affix diagnostic consumer plan.
- [x] Phase 6 affix diagnostic consumer.
- [x] Phase 6 generated markdown and JSON reports.
- [x] controlled affix resolver prototype plan.
- [x] controlled affix resolver prototype implementation.
- [x] controlled affix resolver prototype generated markdown and JSON reports.
- [x] controlled affix resolver saved-vs-fresh comparison.
- [x] controlled affix resolver comparison generated markdown and JSON reports.
- [x] controlled affix per-affix diagnostic record artifact.
- [x] controlled affix per-affix generated markdown and JSON artifacts.

## 5. Canonical Family Status Table

| Family | last-epoch-data Source | Bundle Status | Forge Consumer Status | Confidence | Readiness | Current Boundary | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `metadata` | `exports_json/metadata.json` | generated; warning | compatibility reader only | High for patch/build; Partial for full extractor/source hash coverage | Normalized | control-plane only | Keep linked to bundle validation and compatibility checks. |
| `item_types` | `exports_json/items.json` base type records | generated; passed | diagnostics only; not production-consumed | Verified for base_type_id/name; Partial/Inferred for slug/slot/category | Canonical-ready for identity/type only | `production_safe=false` | Plan first non-production diagnostic consumer. |
| `base_items` | `exports_json/items.json` subtype records | generated; passed | diagnostics only; not production-consumed | Verified for composite IDs/name/requirements where present; Partial for implicits/tags | Canonical-ready for identity/basic requirements only | no name-only migration | Block production use until Forge has source IDs/composite matching. |
| `affixes` | `exports_json/affixes.json` | deferred; shape, identity/provenance, eligibility, tag/category diagnostics `warning`; saved-vs-fresh gate `warning` | current Forge static/hardcoded paths | Partial | Raw Extracted; diagnostic identity/eligibility evidence only | not a bundle family; `production_safe=false` | Non-production inspection stack is complete through Phase 6, controlled resolver prototype, resolver comparison, and per-affix diagnostic record artifact. Controlled modifier resolver prototype and saved-vs-fresh comparison exist for aggregate inspection-only modifier evidence; no production consumption. |
| `affix_tiers` | embedded rows in `exports_json/affixes.json` | deferred; block; embedded tier shape diagnostic `warning` | current Forge static/hardcoded paths | Partial | Raw Extracted; embedded shape diagnostic only | not a bundle family; eligibility out of scope | Validate tier normalization and semantics separately. |
| `affix_eligibility` | `exports_json/affixes.json` `canRollOn`, `rollsOn`, `classSpecificity`; `data_bundle/families/item_types.json` reference set | diagnostic `warning`; deferred | current Forge simplified/static logic | Partial/Unknown | Raw Extracted; diagnostic evidence only | separate gate; not merged into affix identity | Preserve affix 910 raw duplicate evidence and warning metadata in any broader non-production inspection or resolver prototype. |
| `affix_tags` | `exports_json/affixes.json` `tags`, `derivedTags`, display category, group, property, modifier type, special affix type, and `rollsOn` | diagnostic `warning`; deferred; block | current Forge static/derived assumptions | Partial | Raw Extracted; diagnostic evidence only | separate gate; not merged into affix identity or eligibility | Keep warning state visible; do not generate family or Forge consumption. |
| `uniques` | `exports_json/uniques.json` | deferred; degrade | current Forge static data/import resolution | Partial | Raw Extracted | tooltip/special effects not mechanics | Defer until item/affix foundations stabilize. |
| `idols` | `exports_json/items.json`, affixes, current Forge data | deferred; degrade | current Forge static item handling | Partial | Raw Extracted | shape/context risks | Keep covered by item type diagnostics; no production migration. |
| `blessings` | `exports_json/blessings.json` | deferred; degrade | current Forge static/fallback data | Partial | Raw Extracted | not migrated | Audit if promoted for planner/stat use. |
| `passives` | `exports_json/passive_trees.json` | deferred; degrade | current Forge static/resolver paths | Partial | Raw Extracted | stat/effect mapping incomplete | Plan after item/affix family work. |
| `passive_trees` | `exports_json/passive_trees.json` | deferred; degrade | current Forge tree UI/resolver paths | Partial/Fallback-backed | Raw Extracted | fallback risk | Separate legality/tree structure from stat effects. |
| `skills` | `exports_json/skills.json` | deferred; degrade | current Forge skill data/fallbacks | Partial/Hardcoded | Raw Extracted | combat metadata incomplete | Do not promote to DPS authority yet. |
| `skill_trees` | `exports_json/skills_with_trees.json` | deferred; degrade | current Forge tree UI/resolver paths | Partial/Fallback-backed | Raw Extracted | effect interpretation incomplete | Plan after passive/tree effect model matures. |
| `class_mastery_stats` | `exports_json/classes.json`, Forge constants | deferred; degrade | current Forge constants | Partial/Hardcoded | Raw Extracted | not migrated | Audit class/mastery stat ownership. |
| `enemy_profiles` | `exports_json/actors.json`, `monster_mods.json`, current Forge approximations | deferred; degrade | current Forge approximate profiles | Approximation | Raw Extracted | not simulation-ready | Defer until enemy extraction contract exists. |
| `corruption_scaling` | current Forge formulas / unresolved source | deferred; degrade | current Forge approximation/hardcoded formulas | Approximation | Raw Extracted | not migrated | Defer until source/validation exists. |

## 6. Current Counts and Facts

These are current diagnostic values, not permanent truths.

### Bundle and Forge Item Data

| Metric | Value |
| --- | ---: |
| Bundle `item_types` | 50 |
| Bundle `base_items` | 1508 |
| Forge static item types | 25 |
| Forge backend item type IDs | 30 |
| Forge `base_type_id` mappings | 34 |
| Forge base items | 115 flattened records |
| Base item name overlap | 17 |

### Reviewed Mapping Fixture

| Category | Count |
| --- | ---: |
| accepted | 19 |
| needs_adapter | 15 |
| needs_review | 9 |
| deferred | 8 |
| unsafe | 0 |

### Context Coverage

| Metric | Value |
| --- | ---: |
| total inspected | 64 |
| with `base_type_id` | 34 |
| missing `base_type_id` | 30 |
| resolved | 34 |
| needs_context | 30 |
| subtype-only matching attempted | false |

Collapsed groups requiring `base_type_id`:

- `axe`
- `mace`
- `sword`
- `idol_1x1`

### Current Sidecar

| Metric | Value |
| --- | ---: |
| total_items | 12 |
| resolved | 8 |
| needs_context | 2 |
| needs_review | 1 |
| deferred | 0 |
| unresolved | 1 |
| raw_with_base_type_id | 9 |
| mapped_with_base_type_id | 9 |
| mapped_missing_item_type | 12 |
| requires_test_pairing | 11 |
| raw_with_subtype_only | 1 |

### Current Affix Source Shape Diagnostic

These values come from the diagnostic-only Phase 1 validator in `D:\Forge\last-epoch-data`. They do not mean affix migration is complete.

| Metric | Value |
| --- | ---: |
| validation_status | `warning` |
| total affixes | 1227 |
| equipment affixes | 1112 |
| idol affixes | 115 |
| total embedded tiers | 6959 |
| missing required affix identity fields | 0 |
| missing required tier fields | 0 |
| duplicate source identities | 0 |
| ambiguous name collisions | 28 |
| malformed tier range warnings | 136 |
| missing stat/modifier reference warnings | 115 |
| unsupported/unresolved field warnings | 1112 |
| `production_safe` | `false` |

Out of scope for this phase:

- `affix_eligibility`
- `affix_tags`

### Current Affix Identity/Provenance Diagnostic

These values come from the diagnostic-only Phase 2 validator in `D:\Forge\last-epoch-data`. They show source-backed identity evidence for future non-production work, not production readiness.

| Metric | Value |
| --- | ---: |
| validation_status | `warning` |
| total affixes | 1227 |
| equipment affixes | 1112 |
| idol affixes | 115 |
| affixes with stable source identity | 1227 |
| affixes missing source identity | 0 |
| affixes relying on name-only identity | 0 |
| affixes relying on subtype_id-only identity | 0 |
| duplicate source identities | 0 |
| ambiguous display-name collisions | 137 |
| missing source/provenance fields | 0 |
| `production_safe` | `false` |

Out of scope for this phase:

- `affix_eligibility`
- `affix_tags`

### Current Affix Eligibility Diagnostic

These values come from the diagnostic-only Phase 3 validator in `D:\Forge\last-epoch-data`. Eligibility remains separate from affix identity and does not prove production legality.

| Metric | Value |
| --- | ---: |
| validation_status | `warning` |
| total affixes inspected | 1227 |
| affixes with eligibility evidence | 1227 |
| affixes missing eligibility evidence | 0 |
| eligibility target categories | 35 |
| subtype_id-only eligibility records | 0 |
| name-only eligibility records | 0 |
| unresolved item references | 0 |
| duplicate/ambiguous eligibility records | 1 |
| equipment affixes with eligibility evidence | 1112 |
| equipment affixes missing eligibility evidence | 0 |
| idol affixes with eligibility evidence | 115 |
| idol affixes missing eligibility evidence | 0 |
| unsupported/unresolved eligibility fields | 115 |
| `production_safe` | `false` |

Current warning-only duplicate finding:

- Equipment affix `910` at `exports_json/affixes.json` path `equipment[910].canRollOn` has duplicate raw target values `["IDOL_4x1", "IDOL_4x1"]`, normalized to duplicate target `IDOL_4X1`.
- Earliest available decoded source: `last-epoch-data/extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn`, where raw values are `[31, 31]`.
- Enum `31` resolves to `IDOL_4x1`.
- `exports_json/affixes.json` preserves the duplicate as `["IDOL_4x1", "IDOL_4x1"]`.
- Normalization changes only casing/format to `IDOL_4X1`; it does not change identity.
- Current evidence does not show `process_affixes.py` or `process_affixes_tt.py` introduced the duplicate after `MasterAffixesList.json`.
- Byte-level/game-raw origin remains unresolved.
- Diagnostic disposition: known decoded-source duplicate; keep raw duplicate count visible and allow diagnostic-only unique-target views, but do not mutate or deduplicate source/generated data.
- Phase 3 policy state: the accepted diagnostic-only exact duplicate policy is implemented. Affix `910` is warning-only because all policy conditions are satisfied: stable source identity exists, duplicate values are exact raw duplicates in the same field, normalized target identity is unchanged, no conflicting target values are present, raw duplicate count is preserved, duplicate positions remain visible, and the unique-target view is labeled diagnostic-only.

Current readiness sweep:

- Report: `docs/migration/AFFIX_MIGRATION_READINESS_SWEEP.md`.
- Result: `non_production_consumer_allowed=true` for planning a minimum read-only diagnostic consumer only.
- Reason: current generated diagnostics show Phase 3 eligibility as `warning` and Phase 5 saved-vs-fresh comparison as `warning`.
- The sweep confirms count, warning, and error deltas are zero in Phase 5. This permits Phase 6 diagnostic consumer planning, not production migration.

Warning-only context:

- Idol records expose `rollsOn=Idols` but no precise idol shape/base eligibility target in this source shape.
- Phase 4 `affix_tags` is separate and must not claim affix eligibility is safe.

### Current Affix Tag/Category Diagnostic

These values come from the diagnostic-only Phase 4 validator in `D:\Forge\last-epoch-data`. Tags/categories remain separate from affix identity and eligibility. This does not prove production filtering, crafting, simulation, or loader readiness.

| Metric | Value |
| --- | ---: |
| validation_status | `warning` |
| total affixes inspected | 1227 |
| affixes with tag/category evidence | 1227 |
| affixes missing tag/category evidence | 0 |
| known tag/category families | 11 |
| unknown/unsupported tag/category values | 148 |
| duplicate tag/category records | 0 |
| ambiguous tag/category mappings | 110 |
| name-only tag/category records | 0 |
| subtype_id-only tag/category records | 0 |
| missing source/provenance fields | 0 |
| `production_safe` | `false` |

Current warning-level findings:

- Some records map the same normalized token through multiple tag/category fields, such as `displayCategory` and `specialAffixType` or `displayCategory` and `tags`.
- Numeric `displayCategory` / `specialAffixType` values remain unknown or unsupported as tag/category evidence.
- Phase 3 eligibility is `validation_status=warning` after the accepted exact duplicate policy. Phase 4 remains separate and does not prove eligibility safety.

### Current Affix Saved-vs-Fresh Diagnostic Comparison

These values come from the diagnostic-only Phase 5 comparison in `D:\Forge\last-epoch-data`. The comparison checks saved/generated Phase 1-4 reports against freshly built reports and does not create a production consumer.

| Metric | Value |
| --- | ---: |
| migration_gate_status | `warning` |
| phases expected | 4 |
| phases compared | 4 |
| phases missing | 0 |
| phases with error status | 0 |
| phases with warning status | 4 |
| phases with count deltas | 0 |
| phases with warning deltas | 0 |
| phases with error deltas | 0 |
| Phase 3 affix 910 duplicate unresolved | `false` |
| Phase 3 affix 910 duplicate warning-only | `true` |
| Phase 4 tag/category warnings present | `true` |
| `production_safe` | `false` |

Phase status agreement:

- Phase 1 source/tier shape: saved `warning`, fresh `warning`.
- Phase 2 identity/provenance: saved `warning`, fresh `warning`.
- Phase 3 eligibility: saved `warning`, fresh `warning`.
- Phase 4 tag/category: saved `warning`, fresh `warning`.

The gate is warning-only because all phases remain diagnostic warnings. The comparison does not deduplicate affix `910`, generate affix bundle families, create Forge consumers, or mark any output production-safe.

### Current Phase 6 Affix Diagnostic Consumer

These values come from the CLI-only read-only diagnostic consumer in `D:\Forge\le-the-forge`. The consumer reads generated diagnostic artifacts from `D:\Forge\last-epoch-data\docs\generated` only. It does not read production bundle data, production loaders, importers, APIs, frontend code, crafting, simulation, build math, or gameplay output.

| Metric | Value |
| --- | ---: |
| consumer report path | `docs/generated/affix_diagnostic_consumer_report.md` |
| JSON report path | `docs/generated/affix_diagnostic_consumer_report.json` |
| non_production_inspection_allowed | `true` |
| production_safe | `false` |
| total affixes | 1227 |
| equipment affixes | 1112 |
| idol affixes | 115 |
| embedded tiers | 6959 |
| Phase 1 source/tier shape status | `warning` |
| Phase 2 identity/provenance status | `warning` |
| Phase 3 eligibility status | `warning` |
| Phase 4 tag/category status | `warning` |
| Phase 5 migration_gate_status | `warning` |
| affix 910 duplicate evidence | preserved |
| tag/category warning state | preserved |

This is the first minimum affix diagnostic consumer. It proves inspection-only consumption of generated diagnostics, not production readiness.

### Current Controlled Affix Resolver Prototype

These values come from the CLI-only read-only controlled resolver prototype in `D:\Forge\le-the-forge`. The prototype reads generated diagnostic artifacts from `D:\Forge\last-epoch-data\docs\generated` only and emits inspection-safe normalized affix objects. It does not read production bundle data directly, source exports directly, loaders, importers, APIs, frontend behavior, crafting, simulation, build math, or gameplay output.

| Metric | Value |
| --- | ---: |
| Markdown report path | `docs/generated/controlled_affix_resolver_prototype_report.md` |
| JSON report path | `docs/generated/controlled_affix_resolver_prototype_report.json` |
| non_production_inspection_allowed | `true` |
| production_safe | `false` |
| total normalized affixes | 1227 |
| equipment affixes | 1112 |
| idol affixes | 115 |
| total embedded tiers | 6959 |
| warning categories | 10 |
| warning count | 1904 |
| Phase 5 migration_gate_status | `warning` |
| affix 910 duplicate evidence | preserved |

The normalized objects carry stable source identity, display labels as labels only, source family/classification, tier inspection summaries, provenance, eligibility/tag summaries, warning metadata, and `production_safe=false`. Full per-affix display rows and full per-tier rows are not invented; the prototype reports that those require a separate validated diagnostic record artifact.

### Current Controlled Affix Resolver Saved-vs-Fresh Comparison

These values come from the diagnostic-only saved-vs-fresh comparison for the controlled resolver prototype. The comparison checks the saved JSON report at `docs/generated/controlled_affix_resolver_prototype_report.json` against a freshly generated resolver output from approved diagnostic artifacts. It does not read production bundle data directly, mutate generated artifacts, or approve production use.

| Metric | Value |
| --- | ---: |
| Markdown report path | `docs/generated/controlled_affix_resolver_comparison_report.md` |
| JSON report path | `docs/generated/controlled_affix_resolver_comparison_report.json` |
| comparison_status | `warning` |
| saved resolver status | `warning` |
| fresh resolver status | `warning` |
| production_safe agreement | `true` |
| non_production_inspection_allowed agreement | `true` |
| deterministic output agreement | `true` |
| total normalized affix delta | 0 |
| equipment affix delta | 0 |
| idol affix delta | 0 |
| embedded tier delta | 0 |
| phase status deltas | 0 |
| warning category deltas | 0 |
| affix 910 duplicate evidence agreement | `true` |

The comparison remains warning-level because the underlying resolver output remains warning-level. It proves deterministic diagnostic output agreement, not production readiness.

### Current Controlled Affix Per-Affix Diagnostic Artifact

These values come from the diagnostic-only per-affix record artifact generated from the controlled resolver prototype. The artifact reshapes resolver inspection objects into explicit per-affix diagnostic records. It remains generated-artifact-backed, read-only, non-production, and `production_safe=false`.

| Metric | Value |
| --- | ---: |
| Markdown artifact path | `docs/generated/controlled_affix_per_affix_diagnostic_records.md` |
| JSON artifact path | `docs/generated/controlled_affix_per_affix_diagnostic_records.json` |
| production_safe | `false` |
| diagnostic_only | `true` |
| non_production_inspection_allowed | `true` |
| total records | 1227 |
| equipment records | 1112 |
| idol records | 115 |
| embedded tier count | 6959 |
| warning category count | 17 |
| records with warnings | 1227 |
| affix 910 duplicate evidence preserved | `true` |

Each record carries stable source identity, display label as display-only, equipment/idol classification, tier inspection summary, provenance, eligibility summary, tag/category summary, attached warning categories, raw duplicate evidence where present, diagnostic-only normalized views where present, `production_safe=false`, and `diagnostic_only=true`. This artifact does not silently deduplicate affix `910` and does not approve production consumption.

## 7. Current Blockers

- Live LET payload shape is unconfirmed.
- Mapped importer output lacks item type context.
- Base item production migration is blocked because current Forge base items lack `base_type_id` and `subtype_id`.
- Collapsed groups require `base_type_id`: `axe`, `mace`, `sword`, `idol_1x1`.
- `spear` remains unresolved / `needs_review`.
- Many Required Now bundle families remain deferred.
- Production loaders still use static/hardcoded/fallback data.
- No first non-production bundle item consumer has been selected.
- No production-safe adapter, fallback behavior, or rollback strategy exists.
- Affix Phases 1-4 validate source shape, identity/provenance, eligibility, and tag/category evidence only; all are warning-level and tier normalization plus production semantics are still blocked.
- Affix Phase 5 saved-vs-fresh comparison is stable with zero deltas, and the combined gate is warning-only.
- Controlled affix resolver saved-vs-fresh comparison is stable with zero count, phase-status, and warning-category deltas, deterministic output agreement, and affix `910` duplicate evidence agreement.
- Controlled affix per-affix diagnostic records exist for inspection only, but they are not a canonical bundle family and do not contain gameplay-safe tier semantics.

## 8. Current Risks

- False confidence from treating generated bundle families as production-ready.
- Name-only base item matching.
- `subtype_id`-only identity.
- Premature production migration.
- Tooltip/prose mechanics.
- Approximate combat data.
- Hardcoded fallback data.
- Unresolved runtime/script mechanics.
- Silent fallback from missing `base_type_id`.
- Treating synthetic/offline LET fixtures as proof of live LET payload shape.
- Treating sidecar diagnostics as importer output.
- Treating affix shape, identity/provenance, or tag/category validation as evidence that affix eligibility, tier semantics, or simulation behavior are safe.

## 9. Current Diagnostic Chain

Current diagnostic chain:

```text
last-epoch-data bundle generator
  -> last-epoch-data bundle validator
  -> le-the-forge compatibility reader
  -> bundle item diff diagnostic
  -> adapter report
  -> reviewed mapping fixture
  -> adapter translation fixture
  -> dry-run resolver
  -> context coverage report
  -> LET import context diagnostics
  -> stage context comparison
  -> sidecar builder
  -> sidecar validator
  -> saved artifact validation
  -> saved sidecar diagnostic consumer
  -> fresh sidecar diagnostic validation
  -> saved-vs-fresh sidecar diagnostic comparison
```

This chain is diagnostic-only. It proves contract, mapping, context, and validation behavior before production migration. It does not replace loaders, change importer output, expose sidecars publicly, or activate bundle IDs in the app.

Current affix diagnostic chain:

```text
affix source audit and migration plan
  -> affix / embedded tier source-shape validator
  -> generated source-shape diagnostic report
  -> affix identity/provenance validator
  -> generated identity/provenance diagnostic report
  -> affix eligibility validator
  -> generated eligibility diagnostic report
  -> affix 910 eligibility source trace
  -> generated affix 910 source trace report
  -> affix tag/category validator
  -> generated tag/category diagnostic report
  -> saved-vs-fresh affix diagnostic comparison
  -> Phase 6 affix diagnostic consumer
  -> controlled affix resolver prototype
  -> saved-vs-fresh controlled resolver comparison
  -> controlled per-affix diagnostic record artifact
```

This affix chain is also diagnostic-only. The completed Phase 1 and Phase 2 validators report warning-level diagnostic status; the completed Phase 3 eligibility validator now reports warning-level status after applying the accepted exact duplicate policy; the completed Phase 4 tag/category validator reports warning-level status; the completed Phase 5 comparison reports `migration_gate_status=warning`; the controlled resolver comparison reports `comparison_status=warning` with deterministic output agreement; the per-affix artifact emits 1227 inspection-only records. The affix 910 source trace shows the duplicate `IDOL_4x1` eligibility target is already present in the earliest available decoded source, `last-epoch-data/extracted_raw/MasterAffixesList.json`, before `exports_json/affixes.json`. The diagnostic disposition accepts this as a known decoded-source duplicate for planning only: diagnostics report both raw duplicate count and normalized unique target view, but source/generated data is not deduplicated. All keep `production_safe=false`.

## 10. Next Safe Steps

### Immediate

1. Treat the saved/fresh/comparison sidecar diagnostics milestone as complete for non-production validation.
2. Preserve the current warning state; do not downgrade warning-level diagnostics to passing.
3. Treat the `affixes` / embedded `affix_tiers` Phase 1 source-shape validator as complete only for diagnostic shape safety.
4. Treat the Phase 2 affix identity/provenance validator as complete only for diagnostic identity evidence.
5. Treat the Phase 3 affix eligibility validator as complete only as a warning-level diagnostic gate after accepted exact duplicate policy application.
6. Treat the affix 910 source trace as complete diagnostic evidence that the duplicate exists in `extracted_raw/MasterAffixesList.json` and is preserved by later decode/normalization; do not deduplicate generated output.
7. Treat Phase 4 `affix_tags` / category validation as complete only as a separate warning-level diagnostic gate; it does not claim eligibility is safe.
8. Treat Phase 5 saved-vs-fresh affix diagnostic comparison as complete and warning-only.
9. Phase 6 affix non-production consumer implementation is complete as a CLI-only read-only diagnostic report over approved generated diagnostic artifacts.
10. Treat the controlled affix resolver prototype and saved-vs-fresh resolver comparison as complete for inspection-only use.
11. Treat the controlled per-affix diagnostic record artifact as complete for inspection-only use.
12. Treat the non-production affix inspection stack milestone as closed: `diagnostic_only=true`, `non_production_inspection_allowed=true`, `production_safe=false`, 1227 per-affix records, 1112 equipment records, 115 idol records, and 6959 embedded tiers are documented as inspection-only facts.
13. Preserve affix `910` raw duplicate eligibility evidence and all warning metadata in every future diagnostic layer.
14. Treat the controlled modifier resolver prototype as complete for aggregate inspection-only modifier evidence: 6959 total modifier references, 5596 resolved structural inspection objects, 115 unresolved references, 136 malformed references, and 1112 unsupported references; all remain `diagnostic_only=true` and `production_safe=false`.
15. Treat the controlled modifier resolver saved-vs-fresh comparison as complete with `comparison_status=warning`, zero count deltas, zero warning category deltas, deterministic output agreement, provenance coverage agreement, and affix `910` duplicate evidence agreement.
16. Treat unresolved modifier category triage as complete for diagnostic planning: 115 unresolved references are classified as likely missing reference mapping, 136 malformed structures as malformed tier/value shape, and 1112 unsupported structures as unsupported special behavior. All categories remain unresolved and eligible only for future diagnostic policy.
17. Treat missing modifier reference mapping policy as documented in `docs/migration/MODIFIER_RESOLUTION_POLICY.md`: the 115 missing mappings must stay unresolved until source-backed mapping evidence exists; display-name-only and `subtype_id`-only mapping inference are forbidden.
18. Treat malformed tier/value shape policy validation as complete: `backend/app/game_data/malformed_tier_value_shape_validator.py` and `backend/scripts/report_malformed_tier_value_shape.py` generate `docs/generated/malformed_tier_value_shape_report.md` and `.json`. Current status is `warning`; all 136 malformed records preserve raw min/max/order evidence, provenance, and warning metadata; 34 inverted negative ranges remain visible; diagnostic normalized views are labeled `diagnostic_only_not_source_mutation`.
19. Keep production output unchanged.
20. Keep `production_safe=false`.

### Later

1. Treat `docs/migration/MODIFIER_RESOLUTION_POLICY.md` as the contract for the controlled modifier resolver prototype and any later modifier diagnostics.
2. Next recommended architecture target: implement diagnostic validation for the missing modifier reference mapping policy, or document policy for unsupported special behavior. This should preserve provenance and warning metadata before any resolver output changes.
3. Defer a broader non-production inspection UI/report surface until the CLI/report artifacts remain stable enough to justify presentation work.
4. Defer a controlled item-affix-modifier join prototype until triaged modifier categories have diagnostic policies and no name-only or `subtype_id`-only joins are needed.
5. Defer gameplay stat semantics policy until the unresolved/malformed/unsupported categories have specific diagnostic policies.
6. Plan item-family eligibility cross-checks after item family identity and affix eligibility diagnostics can be joined without name-only or `subtype_id`-only assumptions.
7. Plan `affixes`, `affix_tiers`, `affix_eligibility`, and `affix_tags` as likely canonical families only after broader non-production diagnostics prove safe behavior.
8. Plan passives, skills, enemies, corruption, and runtime/script mechanics only after their source audits and validation contracts are ready.
9. Only consider production migration after non-production diagnostics prove safe behavior, fallback, tests, and rollback.

## 11. What Not To Do Yet

- Do not replace production loaders.
- Do not consume bundle IDs in production.
- Do not migrate `base_items` by name.
- Do not use `subtype_id` alone.
- Do not mark `production_safe=true`.
- Do not expose sidecars publicly.
- Do not change importer output shape.
- Do not wire bundle IDs into simulation.
- Do not wire bundle IDs into frontend item UI.
- Do not remove current Forge fallback/static data.
- Do not jump into DPS, enemy, corruption, or runtime mechanics before item/affix architecture is stable.
- Do not infer mechanics from tooltip/prose.
- Do not treat affix source-shape, identity/provenance, or tag/category validation as canonical affix migration.
- Do not treat Phase 5 saved-vs-fresh affix agreement as production migration unblocked.
- Do not treat Phase 6 affix consumer planning or implementation as production migration or production readiness.
- Do not merge `affix_eligibility` into affix identity or production consumers.
- Do not merge `affix_tags` into affix identity, eligibility, production loaders, or Forge consumers.

## 12. Update Instructions

This file is the living tracker. Update it whenever a diagnostic, validation, family migration, or consumer migration changes the current state.

Update rules:

- Update completed milestones when diagnostics or migrations land.
- Update current counts when data is regenerated or diagnostics are rerun.
- Update blockers when they are resolved or new blockers appear.
- Preserve the distinction between:
  - diagnostics
  - non-production tooling
  - production migration
- Never silently move a feature from diagnostic to production-safe.
- Never mark `production_safe=true` without an explicit safety review.
- Do not remove warning/degrade/block statuses just because a file exists.
- Keep known gaps visible until validation and consumer behavior prove they are resolved.

Every production migration must have:

- validated source data
- explicit confidence/readiness labels
- tests
- fallback behavior
- rollback strategy
- compatibility review
- production safety review
- documentation update

Suggested update workflow:

1. Add or update the completed milestone.
2. Update the family status table.
3. Update current counts/facts if any changed.
4. Update blockers and risks.
5. Update next safe steps.
6. Note whether the change is diagnostic-only, non-production, or production.
