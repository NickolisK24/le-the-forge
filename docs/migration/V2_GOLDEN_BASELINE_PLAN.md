# V2 Golden Baseline Plan

Phase 23 defines the baseline categories and fixture scaffold required before any future mechanical planner remap.
It does not use v2 stat or modifier data for production planner calculations.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Baseline categories: `13`
- Safe-now fixtures: `7`
- Blocked fixtures: `6`
- Mechanical fixture categories: `6`
- Non-mechanical fixture categories: `7`
- Stable-calculable count: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Baseline Categories

| Category | Status | Fixture | Mechanical |
| --- | --- | --- | --- |
| `item_base_display_metadata` | `safe_non_mechanical_now` | `backend/tests/fixtures/v2/golden_baselines/item_base_display_metadata.json` | `false` |
| `affix_display_provenance` | `safe_non_mechanical_now` | `backend/tests/fixtures/v2/golden_baselines/affix_display_provenance.json` | `false` |
| `passive_identity_metadata` | `safe_non_mechanical_now` | `backend/tests/fixtures/v2/golden_baselines/passive_identity_metadata.json` | `false` |
| `skill_identity_metadata` | `safe_non_mechanical_now` | `backend/tests/fixtures/v2/golden_baselines/skill_identity_metadata.json` | `false` |
| `stat_registry_identity` | `safe_non_mechanical_now` | `backend/tests/fixtures/v2/golden_baselines/stat_registry_identity.json` | `false` |
| `modifier_identity` | `safe_non_mechanical_now` | `backend/tests/fixtures/v2/golden_baselines/dry_run_summary_snapshot.json` | `false` |
| `known_item_affix_stat_output` | `blocked_by_value_normalization` | `backend/tests/fixtures/v2/golden_baselines/future_item_affix_stat_output.json` | `true` |
| `known_passive_node_stat_output` | `blocked_by_unsupported_mechanics` | `backend/tests/fixtures/v2/golden_baselines/future_passive_node_stat_output.json` | `true` |
| `known_skill_node_stat_output` | `blocked_by_identity_resolution` | `backend/tests/fixtures/v2/golden_baselines/future_skill_node_stat_output.json` | `true` |
| `unique_set_unsupported_exclusions` | `blocked_by_unsupported_mechanics` | `backend/tests/fixtures/v2/golden_baselines/unique_set_unsupported_exclusions.json` | `false` |
| `value_scale_normalization_examples` | `blocked_by_value_normalization` | `backend/tests/fixtures/v2/golden_baselines/future_value_scale_examples.json` | `true` |
| `operation_examples` | `blocked_by_missing_existing_baseline` | `backend/tests/fixtures/v2/golden_baselines/future_operation_examples.json` | `true` |
| `planner_output_vs_v2_dry_run_snapshots` | `future_mechanical_required` | `backend/tests/fixtures/v2/golden_baselines/future_planner_output_vs_v2_dry_run.json` | `true` |

## Blocker Summary

| Status | Count |
| --- | ---: |
| `blocked_by_identity_resolution` | `1` |
| `blocked_by_missing_existing_baseline` | `1` |
| `blocked_by_unsupported_mechanics` | `2` |
| `blocked_by_value_normalization` | `2` |
| `future_mechanical_required` | `1` |

## Required Preconditions Before Mechanical Remap

- stable-calculable gates pass for a limited modifier family
- value scale policy has explicit source contracts or legacy parity baselines
- unresolved and ambiguous skill identity refs remain blocked or are proven by source data
- unsupported/scripted/text-only mechanics remain excluded from stable math
- legacy planner output snapshots exist for representative builds
- v2 dry-run comparison explains every accepted and blocked delta

## Fixture Scaffold

- `backend/tests/fixtures/v2/golden_baselines/affix_display_provenance.json`
- `backend/tests/fixtures/v2/golden_baselines/dry_run_summary_snapshot.json`
- `backend/tests/fixtures/v2/golden_baselines/future_item_affix_stat_output.json`
- `backend/tests/fixtures/v2/golden_baselines/future_operation_examples.json`
- `backend/tests/fixtures/v2/golden_baselines/future_passive_node_stat_output.json`
- `backend/tests/fixtures/v2/golden_baselines/future_planner_output_vs_v2_dry_run.json`
- `backend/tests/fixtures/v2/golden_baselines/future_skill_node_stat_output.json`
- `backend/tests/fixtures/v2/golden_baselines/future_value_scale_examples.json`
- `backend/tests/fixtures/v2/golden_baselines/item_base_display_metadata.json`
- `backend/tests/fixtures/v2/golden_baselines/passive_identity_metadata.json`
- `backend/tests/fixtures/v2/golden_baselines/skill_identity_metadata.json`
- `backend/tests/fixtures/v2/golden_baselines/stat_registry_identity.json`
- `backend/tests/fixtures/v2/golden_baselines/unique_set_unsupported_exclusions.json`

## Runtime Behavior

- No production planner route was added.
- No stat or modifier calculation behavior was changed.
- No crafting, simulation, or stat aggregation behavior was changed.
- No value scale was promoted.
- No unresolved skill identity reference was bridged.
- Safe-now fixtures are non-mechanical planning fixtures only.
