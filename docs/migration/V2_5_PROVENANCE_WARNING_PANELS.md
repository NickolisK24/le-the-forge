# V2.5 Provenance Warning Panels

This checkpoint adds shared frontend panels for concise v2 provenance and warning summaries.

## Components Added

- `V2ProvenanceSummaryPanel`
- `V2WarningSummaryPanel`
- `V2TrustSummaryPanels`
- `v2TrustSummaries` helpers

## Summary Behavior

The provenance panel summarizes:

- source path
- source label where available
- validation status where available
- compact provenance details
- safe fallback text when provenance is missing

The warning panel summarizes:

- explicit warnings from the v2 envelope
- unsupported status
- audit-only value normalization
- display-only status
- not planner-calculable status
- blocked reason summaries
- unresolved skill identity gaps when surfaced by the response
- missing provenance

## Copy Meanings

- "Source information is available for this data" means provenance can be inspected.
- "This data is display-only and is not used for planner calculations" means the data must not feed production planner math.
- "This mechanic is not currently planner-calculable" means the record is blocked from stable mechanical use.
- "Value normalization is still audit-only" means source units are visible but not planner-normalized.
- "Some skill identity references are unresolved" means unresolved/ambiguous references remain unbridged.

## Integration

`V2EnvelopePanels` now uses the provenance summary panel and warning summary panel while preserving the existing support, provenance, and debug contract sections.

## Safety Rules

- Panels do not imply DPS, EHP, stat math, crafting, or planner support.
- Panels do not infer mechanics from tooltip text.
- Panels do not normalize values.
- Panels do not bridge unresolved skill identity references.
- Raw debug payloads remain developer-facing.

## Future UX Followups

- Add dedicated stats/modifiers debug page.
- Apply summary panels more specifically inside v2 debug tables.
- Add a non-developer trusted-data explanation page.
- Add a compact support matrix.

## Runtime Behavior

- No backend runtime behavior was changed.
- No production planner behavior was changed.
- No value normalization was promoted.
- No unresolved skill identity reference was bridged.
