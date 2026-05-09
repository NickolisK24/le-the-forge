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
| Follow-on affix diagnostics | `last-epoch-data` now has Phase 1 affix / embedded tier source-shape validation, Phase 2 affix identity/provenance validation, Phase 3 affix eligibility validation, Phase 4 tag/category validation, and Phase 5 saved-vs-fresh comparison. All are diagnostic-only and stable. Shape, identity/provenance, eligibility, and tag/category are warning-level; the comparison gate is warning-level with zero count/warning/error deltas. None generate or consume affix bundle families. |
| Follow-on affix readiness | The non-production affix inspection stack milestone is complete. `docs/migration/AFFIX_MIGRATION_READINESS_SWEEP.md` records `non_production_consumer_allowed=true` for a minimum read-only diagnostic consumer. The stack now includes Phase 6 consumer reports, controlled resolver prototype reports, saved-vs-fresh resolver comparison reports, and the per-affix diagnostic record artifact. All remain `diagnostic_only=true` / `production_safe=false`. Production migration remains forbidden. |

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
| Affix eligibility validation status | `warning` |
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

Current warning-only duplicate finding:

- Equipment affix `910` at `exports_json/affixes.json` path `equipment[910].canRollOn` has duplicate raw target values `["IDOL_4x1", "IDOL_4x1"]`, normalized to duplicate target `IDOL_4X1`.
- Earliest available decoded source: `last-epoch-data/extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn`, where raw values are `[31, 31]`.
- Enum `31` resolves to `IDOL_4x1`.
- `exports_json/affixes.json` preserves the duplicate as `["IDOL_4x1", "IDOL_4x1"]`.
- Normalization changes only casing/format to `IDOL_4X1`; it does not change identity.
- Current evidence does not show `process_affixes.py` or `process_affixes_tt.py` introduced the duplicate after `MasterAffixesList.json`.
- Byte-level/game-raw origin remains unresolved.
- Disposition: known decoded-source duplicate for diagnostic planning only. Diagnostic-only consumers may report both raw duplicate count and a normalized unique target view, but source/generated data must not be deduplicated.
- Phase 3 is now `validation_status=warning` after the accepted diagnostic exact duplicate policy classified this raw-source exact duplicate as warning-only.

Accepted exact duplicate eligibility policy:

- Exact duplicate means the same raw target value appears more than once in the same eligibility target list for the same stable source affix identity and field.
- Raw evidence duplicate means the preserved source/export list with duplicate count and positions. A normalized unique-target view is only a diagnostic report convenience and must not mutate source or generated data.
- Exact duplicates remain error/blocking if source identity is unstable, target normalization changes identity, raw duplicate count or positions are hidden, targets conflict after normalization, item references are unresolved, or extraction/transformation origin is unclear enough to risk masking a tooling bug.
- Exact duplicates may be downgraded to warning-only diagnostically if stable source identity exists, no conflicting targets exist, normalized target identity is unchanged, raw duplicate count is preserved, duplicate positions are reported, and `production_safe=false` remains explicit.
- Affix `910` satisfies warning-only diagnostic classification under this accepted policy because both raw entries are enum `31`, both resolve to `IDOL_4x1`, and normalization only changes casing/format to `IDOL_4X1`.
- The policy does not deduplicate source data, does not approve production output changes, does not claim eligibility is production-safe, and does not automatically authorize production migration.
- Phase 3 is warning-only because the policy has been explicitly accepted and implemented in the diagnostic validator/report. Phase 6 is implemented only as a CLI-only read-only diagnostic consumer while still keeping `production_safe=false`.

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

The tag/category checkpoint is a separate Phase 4 diagnostic gate. It does not make eligibility safe and does not generate or consume an `affix_tags` bundle family. The affix `910` warning-only eligibility policy is handled by Phase 3, not Phase 4.

Follow-on affix saved-vs-fresh comparison checkpoint:

| Metric | Current Value |
| --- | ---: |
| migration_gate_status | `warning` |
| Phases expected | 4 |
| Phases compared | 4 |
| Phases missing | 0 |
| Phases with error status | 0 |
| Phases with warning status | 4 |
| Count deltas | 0 |
| Warning deltas | 0 |
| Error deltas | 0 |
| Phase 3 affix 910 duplicate unresolved | `false` |
| Phase 3 affix 910 duplicate warning-only | `true` |
| Phase 4 tag/category warnings present | `true` |
| Production safety | `production_safe=false` |

The saved-vs-fresh comparison confirms current diagnostic agreement across Phase 1 through Phase 4. It is warning-level because all phases are warning-level diagnostics. It does not deduplicate affix `910` and does not approve affix bundle generation or Forge consumption.

Follow-on affix readiness sweep:

| Metric | Current Value |
| --- | --- |
| Report path | `docs/migration/AFFIX_MIGRATION_READINESS_SWEEP.md` |
| `non_production_consumer_allowed` | `true` for the minimum read-only diagnostic consumer |
| Phase 1 status | `warning` |
| Phase 2 status | `warning` |
| Phase 3 status | `warning` |
| Phase 4 status | `warning` |
| Phase 5 `migration_gate_status` | `warning` |
| Count deltas | 0 |
| Warning deltas | 0 |
| Error deltas | 0 |
| Production safety | `production_safe=false` |

The readiness sweep is diagnostic-only. It allowed the minimum safe Phase 6 affix consumer only as a read-only, developer-only diagnostic consumer because Phase 3 is warning-level and Phase 5 is warning-level with zero deltas. This does not authorize production migration or bundle family generation.

Affix diagnostics milestone closeout:

- Phase 1 affix source/tier shape diagnostic is complete with `warning` status.
- Phase 2 affix identity/provenance diagnostic is complete with `warning` status.
- Phase 3 affix eligibility diagnostic is complete with `warning` status after accepted exact duplicate policy application.
- Phase 4 affix tag/category diagnostic is complete with `warning` status.
- Phase 5 saved-vs-fresh comparison is complete and stable.
- Affix readiness sweep is complete and allowed the minimum Phase 6 diagnostic consumer.
- Phase 6 diagnostic consumer planning is complete in `docs/migration/PHASE_6_AFFIX_DIAGNOSTIC_CONSUMER_PLAN.md`.
- Phase 6 diagnostic consumer implementation is complete as a CLI-only read-only report over approved generated diagnostic artifacts.
- Phase 6 report status is `non_production_inspection_allowed=true`, with all Phase 1-5 statuses still warning-level and `production_safe=false`.
- Count deltas, warning deltas, and error deltas are all zero across the comparison.
- Combined `migration_gate_status` is `warning`.
- Affix `910` duplicate `canRollOn` evidence remains warning-only and is not deduplicated.
- `production_safe=false` remains unchanged.
- Phase 6 affix non-production consumer implementation is complete as a CLI-only read-only diagnostic report over approved generated diagnostic artifacts. No production consumer should be built.
- Controlled affix resolver prototype planning is complete in `docs/migration/CONTROLLED_AFFIX_RESOLVER_PROTOTYPE_PLAN.md`. The planned prototype remains isolated, read-only, generated-artifact-backed, warning-preserving, and `production_safe=false`.
- Controlled affix resolver prototype implementation is complete as CLI-only read-only diagnostic tooling. It emits `docs/generated/controlled_affix_resolver_prototype_report.md` and `docs/generated/controlled_affix_resolver_prototype_report.json`, with 1227 normalized inspection objects, 6959 embedded tiers summarized, affix `910` duplicate evidence preserved, and `production_safe=false`.
- Controlled affix resolver saved-vs-fresh comparison is complete as CLI-only read-only diagnostic tooling. It emits `docs/generated/controlled_affix_resolver_comparison_report.md` and `docs/generated/controlled_affix_resolver_comparison_report.json`, with `comparison_status=warning`, zero count deltas, zero phase-status deltas, zero warning-category deltas, deterministic output agreement, affix `910` duplicate evidence agreement, and `production_safe=false`.
- Controlled affix per-affix diagnostic record artifact is complete as CLI-only read-only diagnostic tooling. It emits `docs/generated/controlled_affix_per_affix_diagnostic_records.md` and `docs/generated/controlled_affix_per_affix_diagnostic_records.json`, with 1227 inspection-only records, 1112 equipment records, 115 idol records, 6959 embedded tiers summarized, affix `910` duplicate evidence preserved, `diagnostic_only=true`, and `production_safe=false`.

Non-production affix inspection stack closeout:

- The completed stack now covers diagnostics, Phase 6 read-only consumption, controlled resolver output, saved-vs-fresh resolver comparison, and per-affix diagnostic records.
- Current state is `diagnostic_only=true`, `production_safe=false`, and `non_production_inspection_allowed=true`.
- The per-affix artifact contains 1227 records: 1112 equipment records and 115 idol records, with 6959 embedded tiers summarized.
- Affix `910` raw duplicate eligibility evidence remains preserved; no source or generated data is deduplicated.
- Warning metadata remains attached and visible.
- This closes the inspection stack milestone only. Production migration is still forbidden.

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
- Affix eligibility has a Phase 3 diagnostic validator; it is warning-level after accepted exact duplicate policy application and remains non-production.
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

The next canonical planning target is not production consumption. The affix diagnostic milestone is complete as diagnostics, including the minimum Phase 6 read-only diagnostic consumer, controlled affix resolver prototype, saved-vs-fresh resolver comparison, and per-affix diagnostic record artifact, but production migration remains blocked.

That planning has reached a diagnostic-complete checkpoint in `last-epoch-data`: the affix source audit exists, Phase 1 source-shape validation for affix records and embedded tier records is complete as warning-level diagnostic output, Phase 2 identity/provenance validation is complete as warning-level diagnostic output, Phase 3 eligibility validation is complete as warning-level diagnostic output, Phase 4 tag/category validation is complete as warning-level diagnostic output, and Phase 5 saved-vs-fresh comparison is complete with `migration_gate_status=warning`. This does not change the item milestone boundary and does not approve affix bundle generation or Forge consumption.

The Phase 3 duplicate eligibility source trace is also complete as diagnostic evidence. It shows affix `910` has duplicate `canRollOn` target `IDOL_4x1` already in `last-epoch-data/extracted_raw/MasterAffixesList.json` at `multiAffixes[399].canRollOn` as raw values `[31, 31]`, before `exports_json/affixes.json` decodes them to `["IDOL_4x1", "IDOL_4x1"]`. Current decode and normalization preserve the duplicate; normalization only canonicalizes casing/format to `IDOL_4X1`. The byte-level game data versus TypeTree-walker boundary remains unresolved.

Disposition: treat this as a known decoded-source duplicate for diagnostic planning only. Diagnostic-only consumers may present both the raw duplicate count and a normalized unique-target view, but that view is a report convenience, not a mutation of source evidence. Production deduplication is not allowed. The diagnostic-only exact duplicate policy is now accepted and implemented: exact duplicates may become warning-only only when stable source identity, non-conflicting targets, unchanged normalized identity, preserved raw duplicate count, and visible duplicate positions are all present. Affix `910` satisfies that policy and Phase 3 now reports `validation_status=warning`. `production_safe=false` remains unchanged.

Any next data-family planning step should:

- Keep the sidecar diagnostics milestone as a completed diagnostic boundary.
- Avoid production loaders and production API responses.
- Remain explicitly developer-only.
- Preserve visible warning/deferred/block states.
- Prove the next data-family source and validation contract before implementation.
- Keep `affix_tags` separate from affix identity and eligibility; keep `affix_eligibility` warning-preserving and non-production after the accepted exact duplicate policy.
- Preserve the affix 910 raw duplicate report; do not deduplicate source or generated data as part of diagnostics.
- Keep Phase 4 `affix_tags` warning-level; it does not claim affix eligibility is safe and remains separate from the Phase 3 exact duplicate policy.

Recommended output for the next step:

- The diagnostic-only modifier resolution policy is now captured in `docs/migration/MODIFIER_RESOLUTION_POLICY.md`.
- The policy permits only inspection-safe resolution. It does not claim gameplay correctness.
- Structurally present references, currently 6844, may be included only as inspection-safe normalized reference objects.
- Unresolved references, currently 115, must remain unresolved.
- Malformed or semantically unresolved structures, currently 136, must remain unresolved until a semantic policy exists.
- Unsupported or unresolved structures, currently 1112, must remain unsupported until explicitly modeled or excluded.
- Keep the next step CLI-only or otherwise explicitly developer-only, read-only, warning-preserving, and `production_safe=false`; do not generate affix bundle families or production consumers.
- Preserve raw-source warning/error metadata, including affix `910` duplicate count and duplicate positions.
- The controlled modifier resolver prototype is now implemented as CLI-only read-only diagnostic tooling in `backend/app/game_data/controlled_modifier_resolver_prototype.py` and `backend/scripts/report_controlled_modifier_resolver_prototype.py`.
- Generated reports exist at `docs/generated/controlled_modifier_resolver_prototype_report.md` and `docs/generated/controlled_modifier_resolver_prototype_report.json`.
- Current modifier resolver summary: 6959 total modifier references, 5596 resolved structural inspection-only references, 115 unresolved references, 136 malformed references, and 1112 unsupported references.
- The prototype uses the policy as a failure contract and keeps unresolved/malformed/unsupported references out of resolved modifier semantics.
- Saved-vs-fresh modifier resolver comparison is implemented in `backend/app/game_data/controlled_modifier_resolver_comparison.py` and `backend/scripts/report_controlled_modifier_resolver_comparison.py`.
- Generated comparison reports exist at `docs/generated/controlled_modifier_resolver_comparison_report.md` and `docs/generated/controlled_modifier_resolver_comparison_report.json`.
- Current comparison summary: `comparison_status=warning`, zero count deltas, zero warning category deltas, deterministic output agreement, provenance coverage agreement, diagnostic-only agreement, production-safe agreement, and affix `910` duplicate evidence agreement.
- Explicit preservation of the production boundary and `production_safe=false`.
- Unresolved modifier category triage is implemented in `backend/app/game_data/modifier_unresolved_category_triage.py` and `backend/scripts/report_modifier_unresolved_category_triage.py`.
- Generated triage reports exist at `docs/generated/modifier_unresolved_category_triage_report.md` and `docs/generated/modifier_unresolved_category_triage_report.json`.
- Current triage summary: 115 unresolved references are classified as likely missing reference mapping, 136 malformed structures as malformed tier/value shape, and 1112 unsupported structures as unsupported special behavior. All three categories remain unresolved and diagnostic-only.
- Missing modifier reference mapping policy is documented in `docs/migration/MODIFIER_RESOLUTION_POLICY.md`.
- The policy keeps the current 115 missing mappings unresolved until source-backed mapping evidence exists, requires raw reference evidence, provenance/source path, and warning metadata to remain attached, and forbids mapping inference from display names or `subtype_id` alone.
- Missing mappings continue to block gameplay correctness claims; they may be carried by future resolver prototypes only as unresolved diagnostic objects with `diagnostic_only=true` and `production_safe=false`.
- Missing modifier reference mapping validation is implemented in `backend/app/game_data/missing_modifier_reference_mapping_validator.py` and `backend/scripts/report_missing_modifier_reference_mapping.py`.
- Generated validation reports exist at `docs/generated/missing_modifier_reference_mapping_report.md` and `docs/generated/missing_modifier_reference_mapping_report.json`.
- Current missing mapping validation summary: `validation_status=warning`, `production_safe=false`, 115 total missing mapping records, 115 raw reference evidence records preserved, 115 stable affix source identities preserved, 115 provenance records preserved, 115 warning metadata records preserved, 115 records remaining unresolved, 0 name-only mapping inference records, 0 `subtype_id`-only mapping inference records, saved-vs-fresh agreement available, and saved-vs-fresh unresolved delta 0.
- The validator does not add modifier mappings and does not convert missing mapping records into resolved modifier behavior.
- Malformed tier/value shape policy is documented in `docs/migration/MODIFIER_RESOLUTION_POLICY.md`. It covers the current 136 malformed structures and requires raw `minRoll`, `maxRoll`, source order, provenance, and warning metadata to remain visible.
- The policy allows diagnostic-only normalized views only when they are explicitly labeled as inspection views, preserve raw evidence, and do not infer sign direction, desirability, stacking, formula, or gameplay meaning.
- The policy forbids normalization when raw bounds or provenance are missing, numeric shape is ambiguous, or normalization would become gameplay truth.
- Malformed tier/value shape validation is implemented in `backend/app/game_data/malformed_tier_value_shape_validator.py` and `backend/scripts/report_malformed_tier_value_shape.py`.
- Generated validation reports exist at `docs/generated/malformed_tier_value_shape_report.md` and `docs/generated/malformed_tier_value_shape_report.json`.
- Current malformed tier/value validation summary: `validation_status=warning`, `production_safe=false`, 136 total malformed records, 136 raw min/max values preserved, 136 raw source orders preserved, 136 provenance records preserved, 136 warning metadata records preserved, 136 diagnostic normalized views labeled `diagnostic_only_not_source_mutation`, 136 inverted numeric ranges, 34 inverted negative ranges, 0 records missing raw evidence, and 0 unlabeled normalized views.
- The validator does not infer gameplay semantics and does not convert malformed records into resolved modifier behavior.

Controlled modifier inspection stack closeout:

- The diagnostic-only stack is complete through the stat/modifier reference audit, modifier resolution policy, controlled modifier resolver prototype, and saved-vs-fresh controlled modifier resolver comparison.
- Current state is `diagnostic_only=true` and `production_safe=false`.
- Saved-vs-fresh comparison is `comparison_status=warning`, not pass, because unresolved, malformed, and unsupported modifier evidence remains visible.
- Current counts are 6959 total modifier references, 5596 resolved inspection-only references, 115 unresolved references, 136 malformed references, and 1112 unsupported references.
- Triage classifies the remaining unresolved evidence into actionable diagnostic categories without resolving gameplay semantics.
- Count deltas are 0 and warning category deltas are 0.
- Deterministic output agreement is `true`.
- Provenance coverage agreement is `true`.
- Affix `910` duplicate eligibility evidence agreement is `true`.
- No gameplay, crafting, simulation, build-math, API, frontend, or production loader semantics are inferred.
- Production migration remains forbidden.
- Next recommended architecture target: document and validate policy for unsupported special behavior. That target is safer than a broader inspection UI, item-affix-modifier join, or gameplay stat semantics policy because it continues to preserve raw evidence before any resolver output changes.

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
- Treat Phase 6 affix consumer planning or implementation as production migration or production readiness.
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
- Affix eligibility warning policy preserved, and tag boundaries clear before affix family generation or Forge consumption begins.
- Separate eligibility and tag diagnostics complete before affix eligibility or tag consumption begins.
- Tests covering collapsed groups, missing context, blocked mappings, and unsafe mutation cases.

Until those conditions are satisfied, the program remains in the diagnostic checkpoint phase.
