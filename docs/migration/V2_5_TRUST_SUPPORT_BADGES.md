# V2.5 Trust Support Badges

This checkpoint adds shared frontend badges for v2 trusted-data status.

## Components Added

- `V2TrustBadge`
- `V2SupportBadge`
- `V2StatusBadgeGroup`
- `v2TrustStatus` helpers

## Supported Status Copy

- Trusted Data
- Supported
- Partial Support
- Unsupported
- Audit Only
- Display Only
- Experimental
- Not Planner-Calculable
- Unknown Status
- Generated
- Validated
- Provenance Available
- Blocked
- Warning
- Unknown Trust

## Integration

The first integration point is `V2EnvelopePanels`.

The panel now renders a compact badge group from standardized v2 API envelope data while preserving the existing support summary, provenance, and debug contract text.

## Safety Rules

- Not planner-calculable is distinct from unsupported.
- Audit-only and display-only are distinct visible states.
- Stable-calculable count remains backend-controlled.
- Badges do not imply DPS, EHP, stat math, crafting, or planner support.
- Unknown values normalize to safe unknown badges.

## Future UX Followups

- Apply badges across individual v2 debug tables.
- Add shared provenance and warning summary panels.
- Add user-facing limitation copy.
- Add a dedicated stats/modifiers debug page.
- Add a trusted-data explanation page.

## Runtime Behavior

- No backend runtime behavior was changed.
- No production planner behavior was changed.
- No value normalization was promoted.
- No unresolved skill identity reference was bridged.
