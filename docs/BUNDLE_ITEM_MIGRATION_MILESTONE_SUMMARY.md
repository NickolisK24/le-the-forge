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
| Follow-on affix diagnostics | `last-epoch-data` now has Phase 1 affix / embedded tier source-shape validation, Phase 2 affix identity/provenance validation, and Phase 3 affix eligibility validation. All are diagnostic-only. Shape and identity/provenance are warning-level; eligibility is error-level. None generate or consume affix bundle families. |

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

The affix checkpoint is outside this item milestone. It records that source-shape diagnostics have started for the next family area, not that affix migration is complete. `affix_eligibility` and `affix_tags` remain out of scope for this phase.

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
- Diagnostic classification: `exact_duplicate_in_current_export`.
- Origin assessment before `exports_json/affixes.json`: `unresolved/unknown`.

Warning-only context:

- Idol records expose `rollsOn=Idols` but no precise idol shape/base eligibility target in this source shape.

The eligibility checkpoint remains separate from affix identity and does not validate `affix_tags`.

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
- Affix tags are not validated in Phase 1, Phase 2, or Phase 3 and remain a separate gate.
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

The next canonical planning target is not production consumption. It should be a diagnostic-first source audit and migration plan for `affixes` and `affix_tiers`, with `affix_eligibility` and `affix_tags` kept separate unless source evidence is clear.

That planning has started in `last-epoch-data`: the affix source audit exists, Phase 1 source-shape validation for affix records and embedded tier records is complete as warning-level diagnostic output, Phase 2 identity/provenance validation is complete as warning-level diagnostic output, and Phase 3 eligibility validation is complete as error-level diagnostic output. This does not change the item milestone boundary and does not approve affix bundle generation or Forge consumption.

Any next data-family planning step should:

- Keep the sidecar diagnostics milestone as a completed diagnostic boundary.
- Avoid production loaders and production API responses.
- Remain explicitly developer-only.
- Preserve visible warning/deferred/block states.
- Prove the next data-family source and validation contract before implementation.
- Keep `affix_tags` out of scope until its own diagnostic gate exists; keep `affix_eligibility` separate from affix identity and blocked until its error state is reviewed or resolved.

Recommended output for the next step:

- Review or resolve the Phase 3 duplicate `canRollOn` target finding without changing production behavior, including whether it originated in raw source data or during extraction/transformation.
- Defer Phase 4 `affix_tags` planning until the duplicate eligibility evidence is understood; then make a separate decision on whether `affix_tags` has enough source evidence to plan now or should remain deferred.
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
- Merge `affix_eligibility` into affix identity or production consumers.
- Validate or consume `affix_tags` through the Phase 1 shape, Phase 2 identity/provenance, or Phase 3 eligibility diagnostics.

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
