# Bundle Item Migration Milestone Summary

This milestone summary freezes the completed bundle item migration diagnostic chain before any non-production consumer work begins.

It summarizes the current checkpoint between diagnostic architecture and future consumer architecture across `D:\Forge\le-the-forge` and `D:\Forge\last-epoch-data`. It is documentation only. It does not activate migration, change production behavior, change importer output, replace loaders, or mark any mapping `production_safe=true`.

## 1. Purpose

This document records the current diagnostic state for the first canonical item-family migration work. The ecosystem has now proven the bundle control plane, generated canonical item families, reviewed item type mappings, created dry-run diagnostics, and validated LET import context sidecars.

No production migration has started.

This milestone exists to make the safety boundary explicit before designing the first non-production diagnostic consumer. It preserves the no-false-confidence principle: diagnostics can prove that a migration path is measurable, but diagnostics are not production readiness.

## 2. Current Program State

The current migration program is diagnostics-first.

| Area | Current State |
| --- | --- |
| Bundle compatibility | `compatible_with_warnings` remains expected. |
| Bundle item families | `item_types` and `base_items` are generated in `last-epoch-data`. |
| Forge production consumers | None. No production bundle consumer exists. |
| Production safety | `production_safe=false` across mappings, translations, resolver output, sidecars, and validators. |
| Importer behavior | Production importer output remains unchanged. |
| Sidecar diagnostics | Complete as non-production validation surfaces. Developer-only. Not exposed in API responses or frontend behavior. |
| Loader behavior | Existing production loaders remain in place. |
| Follow-on affix diagnostics | `last-epoch-data` now has Phase 1 affix / embedded tier source-shape validation, Phase 2 affix identity/provenance validation, Phase 3 affix eligibility validation, Phase 4 tag/category validation, and Phase 5 saved-vs-fresh comparison. All are diagnostic-only and stable. Shape, identity/provenance, and tag/category are warning-level; eligibility remains error-level; the comparison gate is blocked with zero count/warning/error deltas. None generate or consume affix bundle families. Phase 6 affix consumer work is blocked. |
| Follow-on affix readiness | `docs/migration/AFFIX_MIGRATION_READINESS_SWEEP.md` records `non_production_consumer_allowed=false` because current generated diagnostics still show Phase 3 as `error` and Phase 5 as `blocked`. |

Current diagnostic counts:

| Metric | Current Value |
| --- | ---: |
| Bundle `item_types` | 50 |
| Bundle `base_items` | 1508 |
| Forge base items | 115 |
| Accepted item type mappings | 19 |
| Needs adapter mappings | 15 |
| Needs review mappings | 9 |
| Deferred mappings | 8 |
| Sidecar resolved records | 8 |
| Sidecar `needs_context` records | 2 |
| Sidecar `needs_review` records | 1 |
| Sidecar unresolved records | 1 |

These are current diagnostic values, not permanent truths. They should be updated when bundle generation, Forge diagnostics, or fixture coverage changes.

Current sidecar comparison checkpoint:

| Metric | Current Value |
| --- | --- |
| Saved sidecar status | `warning` |
| Fresh sidecar status | `warning` |
| Saved/fresh shape agreement | confirmed |
| Saved/fresh count deltas | zero |
| Warning deltas | intentional and visible |
| Production safety | `production_safe=false` |

Follow-on affix diagnostic checkpoint:

| Metric | Current Value |
| --- | ---: |
| Affix shape validation status | `warning` |
| Total affixes | 1227 |
| Equipment affixes | 1112 |
| Idol affixes | 115 |
| Total embedded tiers | 6959 |
| Missing required affix identity fields | 0 |
| Missing required tier fields | 0 |
| Duplicate source identities | 0 |
| Ambiguous name collisions | 28 |
| Malformed tier range warnings | 136 |
| Missing stat/modifier reference warnings | 115 |
| Unsupported/unresolved field warnings | 1112 |
| Production safety | `production_safe=false` |

The affix checkpoint is outside this item milestone. It records that source-shape diagnostics have started for the next family area, not that affix migration is complete. `affix_eligibility` and `affix_tags` remain separate gates.

Follow-on affix identity/provenance checkpoint:

| Metric | Current Value |
| --- | ---: |
| Affix identity/provenance validation status | `warning` |
| Total affixes | 1227 |
| Equipment affixes | 1112 |
| Idol affixes | 115 |
| Affixes with stable source identity | 1227 |
| Affixes missing source identity | 0 |
| Affixes relying on name-only identity | 0 |
| Affixes relying on subtype_id-only identity | 0 |
| Duplicate source identities | 0 |
| Ambiguous display-name collisions | 137 |
| Missing source/provenance fields | 0 |
| Production safety | `production_safe=false` |

The identity/provenance checkpoint proves only that current records have source-section plus numeric `id` evidence and top-level source/pipeline provenance for diagnostic work. It does not prove eligibility, tags, tier semantics, simulation behavior, or production safety.

Follow-on affix eligibility checkpoint:

| Metric | Current Value |
| --- | ---: |
| Affix eligibility validation status | `error` |
| Total affixes inspected | 1227 |
| Affixes with eligibility evidence | 1227 |
| Affixes missing eligibility evidence | 0 |
| Eligibility target categories | 35 |
| Subtype_id-only eligibility records | 0 |
| Name-only eligibility records | 0 |
| Unresolved item references | 0 |
| Duplicate/ambiguous eligibility records | 1 |
| Equipment affixes with eligibility evidence | 1112 |
| Idol affixes with eligibility evidence | 115 |
| Unsupported/unresolved eligibility fields | 115 |
| Production safety | `production_safe=false` |

Current blocking finding:

- Equipment affix `910` at `exports_json/affixes.json` path `equipment[910].canRollOn` has duplicate raw target values `["IDOL_4x1", "IDOL_4x1"]`, normalized to duplicate target `IDOL_4X1`.
- Earliest available decoded source: `last-epoch-data/extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn`, where raw values are `[31, 31]`.
- Enum `31` resolves to `IDOL_4x1`.
- `exports_json/affixes.json` preserves the duplicate as `["IDOL_4x1", "IDOL_4x1"]`.
- Normalization changes only casing/format to `IDOL_4X1`; it does not change identity.
- Current evidence does not show `process_affixes.py` or `process_affixes_tt.py` introduced the duplicate after `MasterAffixesList.json`.
- Byte-level/game-raw origin remains unresolved.
- Disposition: known decoded-source duplicate for diagnostic planning only. Diagnostic-only consumers may report both raw duplicate count and a normalized unique target view, but source/generated data must not be deduplicated.
- Phase 3 remains `validation_status=error` until a separate accepted policy is implemented in diagnostics to classify raw-source exact duplicates as blocking or warning-only.

Proposed exact duplicate eligibility policy:

- Exact duplicate means the same raw target value appears more than once in the same eligibility target list for the same stable source affix identity and field.
- Raw evidence duplicate means the preserved source/export list with duplicate count and positions. A normalized unique-target view is only a diagnostic report convenience and must not mutate source or generated data.
- Exact duplicates remain error/blocking if source identity is unstable, target normalization changes identity, raw duplicate count or positions are hidden, targets conflict after normalization, item references are unresolved, or extraction/transformation origin is unclear enough to risk masking a tooling bug.
- Exact duplicates may be downgraded to warning-only diagnostically if stable source identity exists, no conflicting targets exist, normalized target identity is unchanged, raw duplicate count is preserved, duplicate positions are reported, and `production_safe=false` remains explicit.
- Affix `910` is a candidate for warning-only diagnostic classification under this proposal because both raw entries are enum `31`, both resolve to `IDOL_4x1`, and normalization only changes casing/format to `IDOL_4X1`.
- The proposal does not deduplicate source data, does not approve production output changes, does not claim eligibility is production-safe, and does not automatically unblock Phase 6.
- Phase 3 can become warning-only only if the policy is explicitly accepted and implemented in the diagnostic validator/report. Phase 6 can be planned only after Phase 3 and Phase 5 are rerun and show the gate is no longer blocked, while still keeping `production_safe=false`.

Warning-only context:

- Idol records expose `rollsOn=Idols` but no precise idol shape/base eligibility target in this source shape.

The eligibility checkpoint remains separate from affix identity and does not validate `affix_tags`.

Follow-on affix tag/category checkpoint:

| Metric | Current Value |
| --- | ---: |
| Affix tag/category validation status | `warning` |
| Total affixes inspected | 1227 |
| Affixes with tag/category evidence | 1227 |
| Affixes missing tag/category evidence | 0 |
| Known tag/category families | 11 |
| Unknown/unsupported tag/category values | 148 |
| Duplicate tag/category records | 0 |
| Ambiguous tag/category mappings | 110 |
| Name-only tag/category records | 0 |
| Subtype_id-only tag/category records | 0 |
| Missing tag/category provenance | 0 |
| Production safety | `production_safe=false` |

The tag/category checkpoint is a separate Phase 4 diagnostic gate. It does not resolve or downgrade the Phase 3 affix `910` eligibility error, does not make eligibility safe, and does not generate or consume an `affix_tags` bundle family.

Follow-on affix saved-vs-fresh comparison checkpoint:

| Metric | Current Value |
| --- | ---: |
| migration_gate_status | `blocked` |
| Phases expected | 4 |
| Phases compared | 4 |
| Phases missing | 0 |
| Phases with error status | 1 |
| Phases with warning status | 3 |
| Count deltas | 0 |
| Warning deltas | 0 |
| Error deltas | 0 |
| Phase 3 affix 910 duplicate unresolved | `true` |
| Phase 4 tag/category warnings present | `true` |
| Production safety | `production_safe=false` |

The saved-vs-fresh comparison confirms current diagnostic agreement across Phase 1 through Phase 4. It remains blocked because Phase 3 eligibility is still error-level. It does not deduplicate affix `910`, does not downgrade eligibility, and does not approve affix bundle generation or Forge consumption.

Follow-on affix readiness sweep:

| Metric | Current Value |
| --- | --- |
| Report path | `docs/migration/AFFIX_MIGRATION_READINESS_SWEEP.md` |
| `non_production_consumer_allowed` | `false` |
| Phase 1 status | `warning` |
| Phase 2 status | `warning` |
| Phase 3 status | `error` |
| Phase 4 status | `warning` |
| Phase 5 `migration_gate_status` | `blocked` |
| Count deltas | 0 |
| Warning deltas | 0 |
| Error deltas | 0 |
| Production safety | `production_safe=false` |

The readiness sweep is diagnostic-only. It concludes that a minimum safe Phase 6 affix consumer is not allowed yet because the generated reports still show Phase 3 eligibility as error-level and Phase 5 as blocked. The proposed duplicate eligibility policy is not enough by itself; it must be implemented in diagnostics and rerun before readiness can change.

Affix diagnostics milestone closeout:

- Phase 1 affix source/tier shape diagnostic is complete with `warning` status.
- Phase 2 affix identity/provenance diagnostic is complete with `warning` status.
- Phase 3 affix eligibility diagnostic is complete but `error` and blocking.
- Phase 4 affix tag/category diagnostic is complete with `warning` status.
- Phase 5 saved-vs-fresh comparison is complete and stable.
- Affix readiness sweep is complete and currently blocks Phase 6.
- Count deltas, warning deltas, and error deltas are all zero across the comparison.
- Combined `migration_gate_status` is `blocked`.
- Affix `910` duplicate `canRollOn` evidence remains unresolved and is not deduplicated.
- `production_safe=false` remains unchanged.
- No Phase 6 affix non-production consumer should be built until the eligibility duplicate policy is accepted, implemented in diagnostics, verified through Phase 5, and the readiness sweep reports `non_production_consumer_allowed=true`.

## 3. What Has Been Proven

### Bundle Control Plane

- `last-epoch-data` can generate the Phase 1 bundle control plane.
- `last-epoch-data` can validate the bundle and report warning/deferred states without overclaiming completeness.
- `le-the-forge` can inspect bundle compatibility without replacing production loaders.
- The cross-repo handoff smoke test can verify bundle readability from Forge.

Relevant artifacts:

- `D:\Forge\last-epoch-data\tools\scripts\generate_data_bundle_skeleton.py`
- `D:\Forge\last-epoch-data\tools\scripts\validate_data_bundle.py`
- `D:\Forge\last-epoch-data\data_bundle\manifest.json`
- `D:\Forge\last-epoch-data\data_bundle\validation_status.json`
- `D:\Forge\le-the-forge\backend\app\game_data\bundle_compat.py`
- `D:\Forge\le-the-forge\backend\scripts\check_data_bundle.py`
- `D:\Forge\le-the-forge\scripts\smoke_data_bundle_handoff.ps1`

### Canonical Item Families

- `item_types` can be generated from `exports_json/items.json`.
- `base_items` can be generated from `exports_json/items.json`.
- `subTypeID` is treated as scoped under `baseTypeID`, not globally unique.
- Bundle manifest and validation status can include generated `item_types` and `base_items`.
- Bundle validation can check generated family structure, record counts, IDs, references, and conservative readiness.

Relevant artifacts:

- `D:\Forge\last-epoch-data\data_bundle\families\item_types.json`
- `D:\Forge\last-epoch-data\data_bundle\families\base_items.json`
- `D:\Forge\last-epoch-data\FIRST_CANONICAL_MIGRATION_PLAN.md`
- `D:\Forge\last-epoch-data\ITEM_TYPES_BASE_ITEMS_SOURCE_AUDIT.md`
- `D:\Forge\last-epoch-data\FULL_REPO_AUDIT.md`

### Forge Diagnostics

- Forge can compare bundle `item_types` and `base_items` against current static data without changing loaders.
- Item type mapping assumptions are documented and covered by diagnostic tests.
- Reviewed mappings are separated into accepted, needs adapter, needs review, deferred, and unsafe categories.
- Explicit adapter translations exist for reviewed `needs_adapter` mappings.
- A dry-run resolver can resolve reviewed ID-backed mappings while warning on missing context.
- Context coverage diagnostics quantify which current Forge item type inputs have `base_type_id` context.

Relevant artifacts:

- `D:\Forge\le-the-forge\backend\app\game_data\bundle_item_diff.py`
- `D:\Forge\le-the-forge\backend\scripts\diff_bundle_items.py`
- `D:\Forge\le-the-forge\backend\app\game_data\bundle_item_adapter_report.py`
- `D:\Forge\le-the-forge\backend\scripts\report_bundle_item_adapter_map.py`
- `D:\Forge\le-the-forge\backend\tests\fixtures\bundle_item_type_mapping_review.json`
- `D:\Forge\le-the-forge\backend\tests\fixtures\bundle_item_type_adapter_translations.json`
- `D:\Forge\le-the-forge\backend\app\game_data\bundle_item_type_dry_run_resolver.py`
- `D:\Forge\le-the-forge\backend\app\game_data\bundle_item_type_context_report.py`
- `D:\Forge\le-the-forge\docs\BUNDLE_ITEM_ADAPTER_MAP_PROPOSAL.md`
- `D:\Forge\le-the-forge\docs\BUNDLE_ITEM_NEEDS_ADAPTER_REVIEW.md`
- `D:\Forge\le-the-forge\docs\BUNDLE_ITEM_TYPE_CONTEXT_USAGE_AUDIT.md`

### LET Diagnostics

- LE Tools import context diagnostics can inspect parsed/importer-shaped records without changing production importer output.
- Offline and synthetic fixtures demonstrate resolved, needs-context, needs-review, subtype-only, name-only, and unknown cases.
- Stage comparison can show raw/source-stage context versus mapped-output-stage context.
- The importer path can preserve `base_type_id` into mapped gear output when source input has it.
- Mapped production output does not expose enough item type context for resolver diagnostics without explicit sidecar or pairing.

Relevant artifacts:

- `D:\Forge\le-the-forge\backend\app\game_data\le_tools_import_context_report.py`
- `D:\Forge\le-the-forge\backend\scripts\report_le_tools_import_context.py`
- `D:\Forge\le-the-forge\backend\tests\fixtures\le_tools_parsed_gear_context_sample.json`
- `D:\Forge\le-the-forge\backend\tests\fixtures\le_tools_offline_buildinfo_equipment_sample.json`
- `D:\Forge\le-the-forge\backend\tests\fixtures\le_tools_offline_buildinfo_stage_context_sample.json`
- `D:\Forge\le-the-forge\backend\app\game_data\le_tools_import_stage_context_report.py`
- `D:\Forge\le-the-forge\docs\LE_TOOLS_IMPORT_CONTEXT_DRY_RUN.md`
- `D:\Forge\le-the-forge\docs\LE_TOOLS_IMPORTER_FIXTURE_CONTEXT_AUDIT.md`

### Safety Guarantees

Current diagnostic tests and validators prove these safety rules:

- `subtype_id` alone never resolves an item type.
- Name-only matching never resolves an item type.
- `spear` remains blocked as `needs_review` or unresolved.
- Collapsed slugs such as `axe`, `mace`, `sword`, and `idol_1x1` require `base_type_id`.
- Unsafe sidecar mutations fail validation.
- Production importer output shape remains unchanged.
- `production_safe` remains `false` globally and per record.

Sidecar artifacts:

- `D:\Forge\le-the-forge\docs\LE_TOOLS_IMPORT_CONTEXT_SIDECAR_DESIGN.md`
- `D:\Forge\le-the-forge\backend\app\game_data\le_tools_import_context_sidecar.py`
- `D:\Forge\le-the-forge\backend\scripts\build_le_tools_import_context_sidecar.py`
- `D:\Forge\le-the-forge\backend\app\game_data\le_tools_import_context_sidecar_validator.py`
- `D:\Forge\le-the-forge\backend\scripts\validate_le_tools_import_context_sidecar.py`
- `D:\Forge\le-the-forge\backend\tests\fixtures\le_tools_import_context_sidecar_current.json`
- `D:\Forge\le-the-forge\docs\generated\le_tools_import_context_sidecar_report.md`
- `D:\Forge\le-the-forge\docs\generated\le_tools_import_context_sidecar_validation_report.md`
- `D:\Forge\le-the-forge\docs\generated\le_tools_import_context_sidecar_saved_fixture_validation_report.md`

## 4. Current Safety Boundary

The current milestone proves diagnostic capability, not production readiness.

Current boundary:

- Diagnostics only.
- No production bundle consumers.
- No production loader changes.
- No production importer changes.
- No frontend changes.
- No simulation changes.
- No public sidecar exposure.
- No production adapter code.
- `production_safe=false` everywhere.

Production behavior remains anchored to existing Forge static data, loaders, importers, APIs, frontend flows, and simulation systems. The diagnostic chain may inspect, compare, resolve, or validate copied/offline data, but it does not feed production behavior.

## 5. What Remains Blocked

### Data/Bundle

- Many Required Now families remain deferred or warning-only.
- Affixes and embedded affix tiers have Phase 1 source-shape and Phase 2 identity/provenance validators only; they are not generated as bundle families and are not migrated.
- Affix eligibility has a Phase 3 diagnostic validator, but it is error-level and remains non-production.
- Affix tags/categories have a separate Phase 4 diagnostic validator, but it is warning-level and remains non-production.
- Implicit references are preserved only as references; they are not resolved mechanics.
- Enemy profiles and corruption scaling remain unresolved.
- Tooltip/prose-derived mechanics are not sufficient for canonical simulation behavior.

### Forge Consumers

- No first non-production consumer has been selected.
- No production-safe adapter exists.
- Current Forge base item data is much smaller than the bundle base item family.
- Current Forge base items lack source `base_type_id` and `subtype_id` fields needed for precise bundle identity.
- Base item migration remains blocked for production use.

### LET Context

- Live LET payload shape is unconfirmed.
- Existing offline fixtures are synthetic and developer-only.
- Mapped importer output preserves `base_type_id` but does not expose item type context.
- Sidecar diagnostics still require explicit sidecar construction or test-only pairing.
- Source ID preservation from live LET inputs is not proven.

### Runtime Mechanics

- Tooltip/prose mechanics are unresolved.
- Runtime/scripted mechanics are unresolved.
- DPS and combat systems remain advisory or partial where they depend on incomplete extracted mechanics.
- Skill, enemy, proc, ailment, and corruption systems are not part of this milestone.

## 6. What This Milestone Does NOT Mean

This milestone does not mean:

- Bundle item type IDs are production-safe.
- Bundle base item IDs are production-migrated.
- Importer migration is complete.
- Item legality is fully canonical.
- Simulation is fully canonical.
- A production rollout is approved.
- Live LET support is proven.
- Diagnostics are production consumers.
- Sidecars are public API outputs.
- `base_items` can be migrated by name.
- `implicit_refs` are resolved stat mechanics.

The milestone only means the diagnostic chain is mature enough to design a first non-production diagnostic consumer.

## 7. Current Diagnostic Chain

Current chain:

```text
bundle generator
-> bundle validator
-> compatibility reader
-> adapter report
-> reviewed mappings
-> translation fixture
-> dry-run resolver
-> context coverage
-> LET diagnostics
-> stage comparison
-> sidecar builder
-> sidecar validator
-> saved artifact validation
-> saved sidecar diagnostic consumer
-> fresh sidecar diagnostic validation
-> saved-vs-fresh sidecar diagnostic comparison
```

This chain is intentionally isolated from production behavior. It validates that context can be generated, reviewed, resolved, persisted, consumed, revalidated from fresh sidecar builds, and compared against saved expectations by developer-only diagnostics without changing loaders, importer output, API behavior, frontend behavior, or simulation behavior.

The sidecar diagnostics milestone is complete as a non-production validation surface. It is not production migration completion. The comparison remains warning-level because warning deltas are intentionally preserved and visible.

## 8. Criteria Before First Non-Production Consumer

Before any non-production consumer is allowed, all of the following criteria must be satisfied:

- Saved sidecar validation passes or remains warning-only with no errors.
- The consumer scope is explicitly non-production and developer-only.
- The consumer reads saved sidecar diagnostics or explicitly generated diagnostic artifacts first, not live production importer output.
- Fallback behavior is defined and visible.
- No production loader is replaced.
- No silent fallback behavior is allowed.
- Missing `base_type_id` produces warnings or `needs_context`, not guessed mappings.
- Collapsed groups have tests: `axe`, `mace`, `sword`, and `idol_1x1`.
- `spear` behavior is tested and remains blocked until reviewed.
- `subtype_id`-only records are tested and cannot resolve.
- Name-only records are tested and cannot resolve.
- The output is labeled diagnostic-only.
- `production_safe` remains `false`.
- A rollback or removal plan exists.
- The consumer has focused tests and does not require network access.

Passing these criteria would allow a developer-only diagnostic consumer. It would not approve production migration.

## 9. Recommended Next Step

The first saved-sidecar diagnostic consumer, fresh-sidecar diagnostic validation layer, and saved-vs-fresh comparison report now exist. The comparison is warning-level, not production-ready. This closes the current sidecar diagnostics milestone as complete for non-production validation.

The next canonical planning target is not production consumption. The affix diagnostic milestone is complete as diagnostics but migration-blocked.

That planning has reached a diagnostic-complete checkpoint in `last-epoch-data`: the affix source audit exists, Phase 1 source-shape validation for affix records and embedded tier records is complete as warning-level diagnostic output, Phase 2 identity/provenance validation is complete as warning-level diagnostic output, Phase 3 eligibility validation is complete as error-level diagnostic output, Phase 4 tag/category validation is complete as warning-level diagnostic output, and Phase 5 saved-vs-fresh comparison is complete with `migration_gate_status=blocked`. This does not change the item milestone boundary and does not approve affix bundle generation or Forge consumption.

The Phase 3 duplicate eligibility source trace is also complete as diagnostic evidence. It shows affix `910` has duplicate `canRollOn` target `IDOL_4x1` already in `last-epoch-data/extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn` as raw values `[31, 31]`, before `exports_json/affixes.json` decodes them to `["IDOL_4x1", "IDOL_4x1"]`. Current decode and normalization preserve the duplicate; normalization only canonicalizes casing/format to `IDOL_4X1`. The byte-level game data versus TypeTree-walker boundary remains unresolved.

Disposition: treat this as a known decoded-source duplicate for diagnostic planning only. Diagnostic-only consumers may present both the raw duplicate count and a normalized unique-target view, but that view is a report convenience, not a mutation of source evidence. Production deduplication is not allowed. A diagnostic-only exact duplicate policy is now proposed: exact duplicates may become warning-only only when stable source identity, non-conflicting targets, unchanged normalized identity, preserved raw duplicate count, and visible duplicate positions are all present. Affix `910` is a candidate under that proposal, but Phase 3 remains `validation_status=error` until the policy is accepted and implemented in the diagnostic validator/report. `production_safe=false` remains unchanged.

Any next data-family planning step should:

- Keep the sidecar diagnostics milestone as a completed diagnostic boundary.
- Avoid production loaders and production API responses.
- Remain explicitly developer-only.
- Preserve visible warning/deferred/block states.
- Prove the next data-family source and validation contract before implementation.
- Keep `affix_tags` separate from affix identity and eligibility; keep `affix_eligibility` blocked until its error state is reviewed or resolved.
- Preserve the affix 910 raw duplicate report; do not deduplicate source or generated data as part of diagnostics.
- Keep Phase 4 `affix_tags` warning-level; it does not claim affix eligibility is safe and does not bypass the Phase 3 error policy.

Recommended output for the next step:

- Accept and implement the proposed exact duplicate eligibility policy in the Phase 3 diagnostic validator/report.
- Rerun Phase 3, Phase 5, and the readiness sweep after implementation; keep Phase 6 affix consumer work blocked unless Phase 3 becomes warning-only, Phase 5 is no longer blocked, and the readiness sweep reports `non_production_consumer_allowed=true`.
- Explicit preservation of the production boundary and `production_safe=false`.

## 10. What Not To Do Next

Do not:

- Replace production loaders.
- Consume bundle IDs in production.
- Migrate `base_items` by name.
- Expose sidecars publicly.
- Use `subtype_id` alone.
- Remove static or fallback data.
- Wire adapter translations into production paths.
- Change importer output.
- Treat `implicit_refs` as stat mechanics.
- Jump into DPS, enemy, corruption, or runtime mechanic migration before data architecture is stable.
- Mark anything `production_safe=true`.
- Treat affix source-shape or identity/provenance validation as migration completion.
- Treat Phase 5 saved-vs-fresh affix agreement as migration unblocked.
- Begin Phase 6 affix consumer work while Phase 3 remains error-level.
- Merge `affix_eligibility` into affix identity or production consumers.
- Merge `affix_tags` into affix identity, eligibility, production loaders, or Forge consumers.

## 11. Milestone Exit Conditions

Moving beyond this milestone requires more than diagnostics existing. Exit conditions should include:

- A validated non-production diagnostic consumer.
- Proven sidecar-backed diagnostic consumption.
- An explicit migration contract for the next consumer.
- A fallback strategy.
- Production-safe criteria documented before any production migration.
- Validated source ID preservation for the relevant input path.
- Confirmed live LET payload shape if LET migration is in scope.
- Affix eligibility error reviewed or resolved, and tag boundaries clear before affix family generation or Forge consumption begins.
- Separate eligibility and tag diagnostics complete before affix eligibility or tag consumption begins.
- Tests covering collapsed groups, missing context, blocked mappings, and unsafe mutation cases.

Until those conditions are satisfied, the program remains in the diagnostic checkpoint phase.
