# Trusted Gameplay Data Coverage Audit

## Purpose

This diagnostics phase certifies the actual trusted gameplay data coverage state
before v4.6 governance aggregation planning.

It is read-only, descriptive-only, fail-visible, and non-operational. It does
not introduce planner execution, recommendations, ranking, scoring, approval,
authorization, orchestration execution, runtime mutation, operational runtime
behavior, autonomous decision systems, or inferred gameplay support claims.

## Generated Evidence

The audit produces five deterministic JSON reports:

- `docs/generated/trusted_gameplay_data_coverage_report.json`
- `docs/generated/gameplay_schema_alignment_report.json`
- `docs/generated/gameplay_visibility_coverage_report.json`
- `docs/generated/gameplay_support_matrix_report.json`
- `docs/generated/gameplay_extraction_gap_report.json`

Each report includes deterministic serialization, a SHA-256 report hash, and a
hash replay confirmation.

## Audited Scope

The audit inspects and classifies coverage for:

- classes and masteries
- passive trees and passives
- skills, skill trees, and skill nodes
- items, uniques, set items, affixes, and idols
- blessings and crafting materials
- monolith systems, echo systems, and bosses
- ailments, damage types, mechanics, and tags
- gameplay backend payloads and frontend payloads
- trusted extraction manifests and generated assets
- schema mappings
- planner-facing gameplay contracts

Coverage is derived from repository files, generated v2 reports, backend route
declarations, frontend route/API references, schema/type files, trusted-source
inventory, and planner remap readiness evidence.

## Current Coverage Result

The current certification is:

```text
trusted_gameplay_coverage_partial_fail_visible
```

The current gameplay maturity state is:

```text
generated_trusted_assets_exist_but_planner_completeness_not_certified
```

The audit found 27 audited systems. All 27 are present in some form, but all 27
remain partial because source trust, generated asset coverage, unsupported
states, schema drift, stale manifest signals, hardcoded remnants, or planner
dependency gaps remain visible.

## Trusted Coverage

Trusted generated evidence exists for the core v2 gameplay bundles, including:

- class and mastery bundles
- passive tree bundles
- skill and skill tree bundles
- item, unique, set, affix, idol, stat, and modifier bundles
- backend repository and API contract reports

These assets are read-only and generated from game data, but they are not
production-consumed planner authority. The audit records 17 trusted systems and
keeps untrusted or unknown-source remnants visible separately.

## Partial Coverage

Every audited gameplay domain is currently partial. Important partial states
include:

- skill ownership has unresolved links and validation warnings
- passive and skill nodes include scripted, text-only, and unsupported behavior
- unique, set, and mechanic behavior remains non-calculable in places
- frontend/backend visibility is not aligned for every gameplay system
- planner-calculable gameplay coverage is not certified

Partial support is intentionally retained as a first-class classification rather
than being collapsed into success or failure.

## Unsupported Coverage

Unsupported-state visibility is present for:

- passive trees
- passives
- skills
- skill trees
- skill nodes
- uniques
- set items
- mechanics
- trusted generated assets

Unsupported gameplay states are reportable coverage states. They are not hidden
and are not treated as generic failures.

## Missing Coverage

Missing expected support components are visible for:

- blessings
- crafting materials
- monolith systems
- echo systems
- bosses
- ailments
- damage types
- mechanics
- planner-facing gameplay contracts

These systems may have raw data, frontend references, or backend references, but
they do not yet have complete trusted generated coverage, route visibility,
schema coverage, or planner-facing certification.

## Stale And Hardcoded Signals

The repository still has stale or unknown-source manifest signals:

- `data/version.json` reports `patch_version=unknown`
- `v2_source_inventory.json` records unknown trust and unknown source-kind
  counts

Hardcoded or legacy gameplay remnants remain visible for 10 systems, including
classes, masteries, skills, skill trees, skill nodes, items, affixes, crafting
materials, mechanics, and planner-facing gameplay contracts.

## Schema Drift

Schema drift or schema mismatch visibility is recorded for:

- skills
- skill trees
- skill nodes
- gameplay backend payloads
- gameplay frontend payloads
- trusted extraction manifests
- trusted generated assets
- schema mappings

This includes validation warnings, absent schema versions in some report-level
artifacts, and incomplete mapping coverage.

## Frontend And Backend Visibility

The audit confirms static source visibility for the stabilized route set:

- `/api/health`
- `/api/trust/visibility`
- `/classes`
- `/passives`
- `/trusted-data`
- `/trusted-data/frontend-trust`

Backend gameplay visibility is currently visible for 20 audited systems.
Frontend gameplay visibility is currently visible for 23 audited systems.
Visibility is not equivalent to completeness or planner support.

## Planner Dependency Blockers

Planner-facing gameplay completeness is still blocked. The v2 planner remap
readiness evidence keeps these blockers visible:

- eligible planner-calculable count is zero
- stable calculable count is zero
- skill identity bridge remains unbridged
- value normalization remains audit-only
- blocked modifier count remains visible
- legacy and hardcoded source count remains visible

No planner remap was performed by this phase.

## Why v4.6 Governance Aggregation Was Deferred

Governance aggregation depends on trustworthy gameplay inputs. The governance
and trust surfaces are now more mature than the verified gameplay data
completeness layer, so aggregation would risk presenting governance maturity
over incomplete or partially trusted gameplay evidence.

v4.6 governance aggregation is therefore deferred until gameplay coverage,
unsupported states, schema drift, stale manifests, hardcoded remnants, and
planner dependency gaps remain explicit and certifiable.

## Preserved Boundaries

This phase preserves:

```text
READ-ONLY
DESCRIPTIVE-ONLY
FAIL-VISIBLE
NON-operational
NON-mutating
NON-authorizing
NON-approving
NON-recommending
NON-ranking
NON-scoring
NON-orchestrating
```

The reports do not enable planner behavior, route production consumption,
recommend gameplay choices, rank options, score records, mutate runtime state,
or authorize operational workflows.
