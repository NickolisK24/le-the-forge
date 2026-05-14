# V2 Planner Remap Readiness

Phase 16 audits planner-facing dependencies and defines a safe future remap order.
It does not change production planner, crafting, simulation, or stat behavior.

## Safety State

- Production consumed: `false`
- Planner remap performed: `false`
- Stable-calculable count: `0`
- Eligible planner-calculable count: `0`
- Blocked modifier records: `19398`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## Production Entrypoints

- Backend planner/runtime entrypoints found: `18`
- Frontend planner/runtime entrypoints found: `6`
- Legacy or hardcoded data sources found: `12`

Key backend entrypoints include production reference routes, craft routes, simulate routes,
stat aggregation engines, crafting engines, combat simulation engines, and legacy game-data loaders.

## Dependency Classifications

- `item/base display metadata`: `ready_for_adapter_later` (needs non-calculating API adapter tests)
- `affix display and provenance`: `ready_for_adapter_later` (must stay display-only until value policy is proven)
- `affix modifier math`: `blocked_by_value_normalization` (source_units_value_scale, unstable_support_status)
- `item implicit modifier math`: `blocked_by_value_normalization` (source_units_value_scale, unstable_support_status)
- `unique and set mechanics`: `blocked_by_unsupported_mechanics` (unsupported/text-only report remains intentionally visible)
- `idol base and idol affix math`: `blocked_by_value_normalization` (source_units_value_scale, IDOL_ALTAR warnings remain display-only)
- `class/mastery metadata`: `ready_for_adapter_later` (metadata can be inspected; planner skill ownership remains partially unresolved)
- `skill ownership`: `blocked_by_identity_resolution` (unresolved_refs=2, ambiguous_refs=1)
- `passive node behavior`: `blocked_by_unsupported_mechanics` (scripted and unsupported passive records remain non-calculable)
- `skill and skill tree behavior`: `blocked_by_unsupported_mechanics` (scripted and unsupported skill records remain non-calculable)
- `stat/modifier adapter math`: `blocked_by_value_normalization` (unknown_value_scale=13150, source_units_value_scale=6248)
- `crafting engine`: `blocked_by_behavioral_risk` (production behavior depends on legacy craft engine and FP constants)
- `simulation/combat engine`: `blocked_by_behavioral_risk` (production behavior depends on legacy stat fields and combat formulas)
- `production reference routes`: `manual_only_currently` (routes expose legacy DB/static data and must not switch without compatibility tests)
- `frontend planner API clients`: `blocked_by_missing_tests` (needs adapter dry-run and UI compatibility tests before remap)

## Future Remap Sequence

1. **Read-only planner diagnostics using v2 adapter** - Expose v2 adapter explanations beside current planner output without changing calculations.
   - Required tests: production non-consumption, adapter read-only, no output delta
2. **Non-calculating metadata remap** - Use v2 IDs, provenance, support status, and debug labels only.
   - Required tests: API compatibility, frontend rendering, unsupported visibility
3. **Item/base display metadata remap** - Remap item base display and restriction metadata without stat math.
   - Required tests: item compatibility fixtures, legacy route comparison, no stat output delta
4. **Affix display and provenance remap** - Show v2 affix identity/provenance while legacy math remains authoritative.
   - Required tests: affix list comparison, crafting UI compatibility, blocked reason visibility
5. **Passive/skill identity-only remap where safe** - Use resolved identities for inspection only and keep unresolved skill references blocked.
   - Required tests: identity audit, unresolved bridge guard, tree layout comparison
6. **Stat/modifier adapter dry-run comparison** - Compare v2 adapter rows against legacy stat outputs without consumption.
   - Required tests: golden build fixtures, blocked reason snapshots, value-scale guard
7. **Golden baseline test creation** - Create stable expected outputs for representative builds and crafting flows.
   - Required tests: golden planner outputs, crafting baselines, simulation baselines
8. **Limited opt-in experimental planner adapter mode** - Add explicitly opt-in experimental comparison mode after stable gates pass.
   - Required tests: feature flag guard, default-off production guard, route contract tests
9. **Production remap after stable-calculable gates pass** - Switch production only after value scale, identity, support, and behavior gates are proven.
   - Required tests: full planner regression, crafting regression, simulation regression, rollback checks

## Planner Shape Gaps

- `legacy_stat_fields_vs_canonical_stats`: Production BuildStats uses fixed Python/TypeScript fields while v2 has canonical stat IDs. Impact: Needs an audited stat field adapter before planner math can consume v2 modifiers.
- `source_units_value_scale`: Many v2 modifier rows preserve raw source units. Impact: Planner-normalized values must not be inferred without scale evidence.
- `unsupported_scripted_mechanics`: Unique, passive, and skill records include scripted/text-only mechanics. Impact: These must remain display/debug-only until explicitly modeled.
- `skill_identity_gap`: A small number of class/mastery skill references remain unresolved or ambiguous. Impact: Skill ownership-sensitive calculations cannot depend on those links.
- `legacy_routes_and_db_models`: Production reference routes still use legacy DB/static sources. Impact: Route-level remap requires compatibility wrappers and regression fixtures.

## Remaining Blockers

- Value scale is still audit-only; source-unit and unknown-scale values cannot feed planner math.
- Stable-calculable modifier count is still zero.
- Remaining skill identity gaps stay unbridged.
- Unsupported, text-only, and scripted mechanics remain debug/display-only.
- Current production engines use legacy schemas and hardcoded/manual mappings that need golden baselines before replacement.

## Non-Goals Confirmed

- No production planner consumption was added.
- No planner output changed.
- No crafting, simulation, or stat engine behavior changed.
- No value scale was promoted.
- No skill identity bridge was added.
