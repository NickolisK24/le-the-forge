# Forge Migration Tracker

This is the living cross-repo migration tracker for:

- `D:\Forge\le-the-forge`
- `D:\Forge\last-epoch-data`

It tracks current migration state, completed milestones, known blockers, safety boundaries, canonical family status, Forge consumer status, and next actions. It is documentation/tracking only. It does not activate migration or change production behavior.

## 1. Current Program State

| Area | Current State |
| --- | --- |
| Current phase | Diagnostics and pre-consumer migration planning. |
| Current boundary | Developer-only diagnostics; no production bundle consumption. |
| Current compatibility state | `compatible_with_warnings` expected from Forge compatibility reader. |
| Current production status | Existing Forge loaders, importers, API behavior, frontend behavior, and simulation behavior remain unchanged. |
| Current bundle status | `last-epoch-data` bundle validates as `WARN` with no critical errors. |
| Current item migration state | `item_types` and `base_items` are generated in the bundle and validated, but only diagnostic consumers exist in Forge. |
| Current importer migration state | LET diagnostics can inspect copied/synthetic/offline context; production importer output is unchanged. |
| Current sidecar state | Sidecar builder, validator, saved fixture validation, saved-sidecar diagnostic consumer, fresh-sidecar diagnostic validation, and saved-vs-fresh comparison diagnostics exist; all remain developer-only. |
| Current production safety | `production_safe=false` across mapping fixtures, adapter translations, resolver output, sidecars, and validators. |

Short version:

- Diagnostics only.
- No production loaders replaced.
- No production bundle consumer activated.
- `item_types` and `base_items` are generated, but not production-consumed.
- LET importer context diagnostics exist, but live LET payload shape is not proven.
- The next safe work is deciding whether to keep hardening sidecar diagnostics or move to a new planning-only task for the next canonical data family.

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

### Must Not Be Done Yet

- Do not consume bundle IDs in production.
- Do not change importer output.
- Do not use `subtype_id` alone as identity.
- Do not migrate base items by name-only matching.
- Do not depend on live LET payload shape without captured/offline validation.
- Do not expose sidecars publicly.
- Do not create production adapter code.
- Do not mark `production_safe=true`.

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
- Affix eligibility is not migrated.

Next safe step:

- Summarize the item-family milestone and decide the first non-production diagnostic consumer.

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

Status: COMPLETE for saved-sidecar diagnostic consumption, fresh-sidecar diagnostic validation, and saved-vs-fresh diagnostic comparison; NOT_STARTED for any live importer diagnostic consumer.

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
- Comparison result is currently warning-level because warning deltas remain visible.
- It does not prove live LET payload shape.
- It does not prove production importer or bundle consumption readiness.

Next safe step:

- Decide whether to keep hardening sidecar diagnostics or move to planning for the next canonical data family. Do not start production migration.

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

## 5. Canonical Family Status Table

| Family | last-epoch-data Source | Bundle Status | Forge Consumer Status | Confidence | Readiness | Current Boundary | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `metadata` | `exports_json/metadata.json` | generated; warning | compatibility reader only | High for patch/build; Partial for full extractor/source hash coverage | Normalized | control-plane only | Keep linked to bundle validation and compatibility checks. |
| `item_types` | `exports_json/items.json` base type records | generated; passed | diagnostics only; not production-consumed | Verified for base_type_id/name; Partial/Inferred for slug/slot/category | Canonical-ready for identity/type only | `production_safe=false` | Plan first non-production diagnostic consumer. |
| `base_items` | `exports_json/items.json` subtype records | generated; passed | diagnostics only; not production-consumed | Verified for composite IDs/name/requirements where present; Partial for implicits/tags | Canonical-ready for identity/basic requirements only | no name-only migration | Block production use until Forge has source IDs/composite matching. |
| `affixes` | `exports_json/affixes.json` | deferred; block | current Forge static/hardcoded paths | Partial | Raw Extracted | not a bundle family yet | Plan `affixes` family migration. |
| `affix_tiers` | `exports_json/affixes.json` tier rows | deferred; block | current Forge static/hardcoded paths | Partial | Raw Extracted | not a bundle family yet | Plan with `affixes`, but keep eligibility separate. |
| `affix_eligibility` | not yet canonicalized | deferred; block | current Forge simplified/static logic | Deferred/Unknown | Raw Extracted | blocked | Audit source evidence before implementation. |
| `affix_tags` | derived/export data exists, not bundle family | deferred; block | current Forge static/derived assumptions | Partial | Raw Extracted | blocked | Audit tag derivation and schema separately. |
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

## 10. Next Safe Steps

### Immediate

1. Keep saved, fresh, and comparison sidecar diagnostics developer-only.
2. Review whether the warning-level sidecar diagnostic chain is sufficient for the current item-type milestone.
3. If yes, move to planning for the next canonical data family.
4. Keep production output unchanged.
5. Keep `production_safe=false`.

### Later

6. Plan `affixes` and `affix_tiers` as the next likely canonical families in `last-epoch-data`.
7. Plan `affix_eligibility` separately after source evidence is clear.
8. Plan `affix_tags` separately if derivation and schema are stable.
9. Plan passives, skills, enemies, corruption, and runtime/script mechanics only after their source audits and validation contracts are ready.
10. Only consider production migration after non-production diagnostics prove safe behavior, fallback, tests, and rollback.

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
