# Forge Migration Tracker

This is the living cross-repo migration tracker for:

- `D:\Forge\le-the-forge`
- `D:\Forge\last-epoch-data`

It tracks current migration state, completed milestones, known blockers, safety boundaries, canonical family status, Forge consumer status, and next actions. It is documentation/tracking only. It does not activate migration or change production behavior.

## 1. Current Program State

| Area | Current State |
| --- | --- |
| Current phase | Sidecar diagnostics milestone complete; affix source-shape diagnostics started. |
| Current boundary | Developer-only diagnostics; no production bundle consumption. |
| Current compatibility state | `compatible_with_warnings` expected from Forge compatibility reader. |
| Current production status | Existing Forge loaders, importers, API behavior, frontend behavior, and simulation behavior remain unchanged. |
| Current bundle status | `last-epoch-data` bundle validates as `WARN` with no critical errors. |
| Current item migration state | `item_types` and `base_items` are generated in the bundle and validated, but only diagnostic consumers exist in Forge. |
| Current importer migration state | LET diagnostics can inspect copied/synthetic/offline context; production importer output is unchanged. |
| Current sidecar state | Sidecar builder, validator, saved fixture validation, saved-sidecar diagnostic consumer, fresh-sidecar diagnostic validation, and saved-vs-fresh comparison diagnostics are complete as non-production validation surfaces; all remain developer-only and warning states stay visible. |
| Current affix diagnostic state | `last-epoch-data` Phase 1 shape validator, Phase 2 identity/provenance validator, and Phase 3 eligibility validator exist as diagnostic-only tooling. Shape and identity/provenance are `warning`; eligibility is `error` because one duplicate `canRollOn` target is present. No affix bundle family is generated or consumed. |
| Current production safety | `production_safe=false` across mapping fixtures, adapter translations, resolver output, sidecars, and validators. |

Short version:

- Diagnostics only.
- No production loaders replaced.
- No production bundle consumer activated.
- `item_types` and `base_items` are generated, but not production-consumed.
- LET importer context diagnostics exist, but live LET payload shape is not proven.
- The sidecar diagnostics milestone is complete for non-production validation.
- `affixes` / embedded `affix_tiers` now have Phase 1 source-shape and Phase 2 identity/provenance diagnostics in `last-epoch-data`; `affix_eligibility` now has a separate Phase 3 diagnostic with an error state; `affix_tags` remains out of scope.

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
- Affix source-shape and identity/provenance validation are warning-only. Affix eligibility validation is separate and currently error-level because it found a duplicate eligibility target. None of these diagnostics validate tags, importer use, loader use, or simulation semantics.

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
- Do not downgrade the Phase 3 eligibility error to passing without source-level review.

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
- Affix eligibility has a separate diagnostic validator but is blocked by an error-level duplicate target finding.
- Affix tags are not validated or migrated.

Current disposition:

- Affix `910` has a duplicate `canRollOn` target that is accepted as a known decoded-source duplicate for diagnostic planning only.
- Phase 3 remains `validation_status=error` until a separate policy decides whether raw-source exact duplicates are blocking or warning-only.
- Phase 4 `affix_tags` may be planned after this disposition, but it must not claim eligibility is safe and must remain a separate diagnostic gate.

Next safe step:

- Plan Phase 4 `affix_tags` as a separate diagnostic-only audit/validator. Do not generate bundle families or Forge consumers yet.

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

Status: COMPLETE for saved-sidecar diagnostic consumption, fresh-sidecar diagnostic validation, and saved-vs-fresh diagnostic comparison as non-production validation surfaces; NOT_STARTED for any live importer diagnostic consumer or production migration.

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

Current blockers:

- Consumer is intentionally limited to saved sidecar artifacts.
- Fresh-sidecar validation is diagnostic-only and does not make fresh sidecars production-safe.
- Saved/fresh shape agreement is confirmed and count deltas are zero.
- Comparison result remains `warning` because warning deltas remain visible by design.
- It does not prove live LET payload shape.
- It does not prove production importer or bundle consumption readiness.

Next safe step:

- Treat this sidecar milestone as complete for now and move to planning for the next canonical data family. Do not start production migration.

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
- [ ] affix tag/category diagnostic validator.
- [ ] saved-vs-fresh affix diagnostic comparison.

## 5. Canonical Family Status Table

| Family | last-epoch-data Source | Bundle Status | Forge Consumer Status | Confidence | Readiness | Current Boundary | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `metadata` | `exports_json/metadata.json` | generated; warning | compatibility reader only | High for patch/build; Partial for full extractor/source hash coverage | Normalized | control-plane only | Keep linked to bundle validation and compatibility checks. |
| `item_types` | `exports_json/items.json` base type records | generated; passed | diagnostics only; not production-consumed | Verified for base_type_id/name; Partial/Inferred for slug/slot/category | Canonical-ready for identity/type only | `production_safe=false` | Plan first non-production diagnostic consumer. |
| `base_items` | `exports_json/items.json` subtype records | generated; passed | diagnostics only; not production-consumed | Verified for composite IDs/name/requirements where present; Partial for implicits/tags | Canonical-ready for identity/basic requirements only | no name-only migration | Block production use until Forge has source IDs/composite matching. |
| `affixes` | `exports_json/affixes.json` | deferred; block; shape and identity/provenance diagnostics `warning`; eligibility diagnostic `error` | current Forge static/hardcoded paths | Partial | Raw Extracted; diagnostic identity/eligibility evidence only | not a bundle family; `production_safe=false` | Review eligibility error; do not generate family or Forge consumption. |
| `affix_tiers` | embedded rows in `exports_json/affixes.json` | deferred; block; embedded tier shape diagnostic `warning` | current Forge static/hardcoded paths | Partial | Raw Extracted; embedded shape diagnostic only | not a bundle family; eligibility out of scope | Validate tier normalization and semantics separately. |
| `affix_eligibility` | `exports_json/affixes.json` `canRollOn`, `rollsOn`, `classSpecificity`; `data_bundle/families/item_types.json` reference set | diagnostic `error`; deferred; block | current Forge simplified/static logic | Partial/Unknown | Raw Extracted; diagnostic evidence only | separate gate; not merged into affix identity | Review duplicate target and idol context warnings before any family generation. |
| `affix_tags` | derived/export data exists, not bundle family | deferred; block | current Forge static/derived assumptions | Partial | Raw Extracted | explicitly out of scope for affix Phases 1-3 | Audit tag derivation and schema separately. |
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
| validation_status | `error` |
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

Current blocking finding:

- Equipment affix `910` at `exports_json/affixes.json` path `equipment[910].canRollOn` has duplicate raw target values `["IDOL_4x1", "IDOL_4x1"]`, normalized to duplicate target `IDOL_4X1`.
- Earliest available decoded source: `last-epoch-data/extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn`, where raw values are `[31, 31]`.
- Enum `31` resolves to `IDOL_4x1`.
- `exports_json/affixes.json` preserves the duplicate as `["IDOL_4x1", "IDOL_4x1"]`.
- Normalization changes only casing/format to `IDOL_4X1`; it does not change identity.
- Current evidence does not show `process_affixes.py` or `process_affixes_tt.py` introduced the duplicate after `MasterAffixesList.json`.
- Byte-level/game-raw origin remains unresolved.
- Diagnostic disposition: known decoded-source duplicate; keep raw duplicate count visible and allow diagnostic-only unique-target views, but do not mutate or deduplicate source/generated data.
- Phase 3 policy state: keep `validation_status=error` until a separate policy decides whether raw-source exact duplicates are blocking or warning-only.

Warning-only context:

- Idol records expose `rollsOn=Idols` but no precise idol shape/base eligibility target in this source shape.
- Phase 4 `affix_tags` may be planned after this disposition is recorded, but it must not claim affix eligibility is safe.

Out of scope for this phase:

- `affix_tags`

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
- Affix Phase 1 validates source shape and Phase 2 validates identity/provenance evidence only; eligibility, tags, tier normalization, and production semantics are still blocked.

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
- Treating affix shape or identity/provenance validation as evidence that affix eligibility, tags, tier semantics, or simulation behavior are safe.

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
  -> future tag/category validator
```

This affix chain is also diagnostic-only. The completed Phase 1 and Phase 2 validators report warning-level diagnostic status; the completed Phase 3 eligibility validator reports error-level status. The affix 910 source trace shows the duplicate `IDOL_4x1` eligibility target is already present in the earliest available decoded source, `last-epoch-data/extracted_raw/MasterAffixesList.json`, before `exports_json/affixes.json`. The diagnostic disposition accepts this as a known decoded-source duplicate for planning only: diagnostics may report both raw duplicate count and normalized unique target view, but source/generated data must not be deduplicated. The byte-level game-data versus TypeTree-walker boundary remains unresolved, so Phase 3 stays `validation_status=error` until an explicit policy decides whether raw-source exact duplicates are blocking or warning-only. All keep `production_safe=false`.

## 10. Next Safe Steps

### Immediate

1. Treat the saved/fresh/comparison sidecar diagnostics milestone as complete for non-production validation.
2. Preserve the current warning state; do not downgrade warning-level diagnostics to passing.
3. Treat the `affixes` / embedded `affix_tiers` Phase 1 source-shape validator as complete only for diagnostic shape safety.
4. Treat the Phase 2 affix identity/provenance validator as complete only for diagnostic identity evidence.
5. Treat the Phase 3 affix eligibility validator as complete only as a diagnostic gate, currently blocked by one error-level duplicate target.
6. Treat the affix 910 source trace as complete diagnostic evidence that the duplicate exists in `extracted_raw/MasterAffixesList.json` and is preserved by later decode/normalization; do not deduplicate generated output.
7. Allow Phase 4 `affix_tags` planning to start only as a separate diagnostic-first gate; it must not claim eligibility is safe.
8. Keep production output unchanged.
9. Keep `production_safe=false`.

### Later

9. Decide whether to keep the Phase 3 raw-source exact duplicate policy as blocking or downgrade it to warning-only in a separate policy task; until then, Phase 3 remains `error`.
10. Plan Phase 4 `affix_tags` separately if derivation and schema are stable, but do not use tag planning to bypass the Phase 3 eligibility error.
11. Plan `affixes`, `affix_tiers`, and `affix_eligibility` as likely canonical families only after eligibility/tag boundaries are clear and warning/error states are accepted or resolved.
12. Plan passives, skills, enemies, corruption, and runtime/script mechanics only after their source audits and validation contracts are ready.
13. Only consider production migration after non-production diagnostics prove safe behavior, fallback, tests, and rollback.

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
- Do not treat affix source-shape or identity/provenance validation as canonical affix migration.
- Do not merge `affix_eligibility` into affix identity or production consumers.
- Do not validate or consume `affix_tags` through the Phase 1 shape, Phase 2 identity/provenance, or Phase 3 eligibility diagnostics.

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
