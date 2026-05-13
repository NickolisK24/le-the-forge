# v2.5 User-Facing Limitation Copy

v2.5 Checkpoint 4 adds shared limitation copy for trusted-data surfaces.

This is frontend copy and UX only. It does not change backend runtime behavior, planner calculations, crafting, simulation, stat aggregation, value normalization, or skill identity handling.

## Added

- `frontend/src/lib/v2Limitations.ts`
- `frontend/src/components/v2/V2LimitationNotice.tsx`
- `frontend/src/__tests__/components/v2-limitation-notice.test.tsx`

## Limitation Codes

The shared copy layer supports these limitation codes:

- `display_only`
- `audit_only_value_normalization`
- `not_planner_calculable`
- `unsupported_mechanics`
- `partial_support`
- `unresolved_skill_identity`
- `missing_provenance`
- `experimental_only`
- `stable_calculable_unavailable`
- `production_not_consuming_v2`
- `unknown_limitation`

Unknown or missing codes fall back to `unknown_limitation`.

## User-Facing Meanings

- Display-only data can be inspected, but it is not used for planner math.
- Audit-only value normalization means source values must not be treated as planner-normalized.
- Not planner-calculable means the data remains blocked by planner safety gates.
- Unsupported mechanics are visible so limitations are clear, not because behavior is implemented.
- Partial support means some metadata may be available while mechanical behavior remains blocked.
- Unresolved skill identity means no bridge is inferred from names, nested evidence, or tooltip text.
- Missing provenance means the UI should stay cautious about source and validation context.
- Experimental-only surfaces are read-only inspection tools.
- Stable calculation unavailable means backend safety policy has not allowed stable planner math.
- Production planner unchanged means v2 trusted data is not consumed by production calculations.

## Integration

`V2WarningSummaryPanel` now renders `V2LimitationNotice` from limitation codes derived from the current v2 API envelope. Existing warning messages remain visible, and the notice adds a concise "What this means" explanation below them.

The integration is intentionally narrow:

- no broad debug page redesign
- no backend route changes
- no production planner integration
- no value normalization promotion
- no skill identity bridge

## Safety Rules

The copy must not imply:

- DPS or EHP is accurate because trusted data exists
- planner calculations consume v2 data
- unsupported mechanics are solved
- source-unit values are normalized
- unresolved skill identities are bridged
- stable-calculable support is available

## Future UX Followups

- Add dedicated stats/modifiers debug pages.
- Promote the same limitation copy into user-facing planner-adjacent pages.
- Add a support matrix for trusted-data domains.
- Add non-developer explanations for provenance and blocked reasons.
- Build a pre-v3 mechanical readiness dashboard.
