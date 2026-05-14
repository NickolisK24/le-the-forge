# V2.5 Release Readiness

This audit closes the v2.5 Trust & UX layer. It is documentation and report-only.
It does not start v3 mechanical intelligence, production planner remap, or runtime behavior changes.

## Readiness Decision

- V2.5 trust/UX ready: `true`
- Production planner ready: `false`
- V3 mechanical ready: `false`
- Recommended next track: `v3_mechanical_intelligence_planning`

## Completed V2.5 Surfaces

| Surface | Status | Coverage |
| --- | --- | --- |
| Trust & UX planning audit | `complete` | planned the v2.5 trust and UX layer |
| Shared trust/support badges | `complete` | renders support, trust, audit-only, display-only, and non-calculating status badges |
| Provenance/warning summary panels | `complete` | summarizes provenance, warnings, blocked reasons, and limitations |
| User-facing limitation copy | `complete` | explains display-only, audit-only, unsupported, and not planner-calculable states |
| Stats/modifiers debug page | `complete` | shows stat/modifier counts, blocked reasons, value scales, and planner safety status |
| Trusted-data explanation page | `complete` | explains trusted data, provenance, display-only use, and v3 boundaries |
| Planner adapter status panel | `complete` | shows adapter-visible, blocked, planner-calculable, and baseline readiness status |
| Report/debug navigation cleanup | `complete` | links the trusted-data explanation, debug routes, support matrix, and pre-v3 dashboard |
| User-facing support matrix | `complete` | summarizes domain support, display-only status, blockers, and next tracks |
| Pre-v3 mechanical readiness dashboard | `complete` | summarizes what remains blocked before mechanical planner work can start |

## Route Checklist

| Route | Surface | Coverage |
| --- | --- | --- |
| `/trusted-data` | Trusted-data explanation page | `static_route_inventory` |
| `/trusted-data/support` | User-facing support matrix | `static_route_inventory` |
| `/trusted-data/pre-v3-readiness` | Pre-v3 mechanical readiness dashboard | `static_route_inventory` |
| `/debug/v2` | V2 debug navigation page | `static_route_inventory` |
| `/debug/v2-stats-modifiers` | Stats/modifiers debug page | `static_route_inventory` |
| `/debug/forge-safe-affixes` | Forge-safe affixes debug page | `static_route_inventory` |
| `/debug/v2-affixes` | Alias redirect to forge-safe affixes | `static_route_inventory` |

## Manual QA Checklist

- [ ] Trusted-data page loads. (`/trusted-data`)
- [ ] Support matrix page loads. (`/trusted-data/support`)
- [ ] Pre-v3 readiness page loads. (`/trusted-data/pre-v3-readiness`)
- [ ] Debug navigation page loads. (`/debug/v2`)
- [ ] Stats/modifiers debug page loads. (`/debug/v2-stats-modifiers`)
- [ ] Affixes debug page loads through the actual route. (`/debug/forge-safe-affixes`)
- [ ] Affix alias route works. (`/debug/v2-affixes`)
- [ ] Limitation copy appears. (`v2.5 pages`)
- [ ] Planner-calculable count remains 0. (`v2.5 pages`)
- [ ] Stable-calculable count remains 0. (`v2.5 pages`)
- [ ] No copy implies production planner math is active. (`v2.5 pages`)

## Known Limitations

- `value_normalization_contracts` (v3_mechanical_blocker): Define and prove value normalization contracts before mechanical math.
- `operation_semantics` (v3_mechanical_blocker): Resolve operation semantics for additive, increased, more, flat, conditional, scripted, and unsupported behaviors.
- `stat_identity_resolution` (v3_mechanical_blocker): Resolve blocked stat identities before stable stat aggregation.
- `skill_identity_policy` (v3_mechanical_blocker): Keep unresolved and ambiguous skill identities unbridged until source evidence is sufficient.
- `golden_mechanical_baselines` (v3_mechanical_blocker): Implement golden mechanical baseline tests before production planner remap.
- `stable_calculable_zero` (known_intentional_limitation): Stable-calculable count remains intentionally 0 until v3 gates pass.

## Post-v2.5 Polish

- `visual_polish`: Tighten spacing and visual hierarchy across trusted-data pages after user review.
- `copy_review`: Review all trust and limitation copy with real player feedback.
- `route_discoverability`: Consider broader application navigation entry points after v2.5 release.

## V3 Mechanical Blockers

- `value_normalization_contracts`: Define and prove value normalization contracts before mechanical math.
- `operation_semantics`: Resolve operation semantics for additive, increased, more, flat, conditional, scripted, and unsupported behaviors.
- `stat_identity_resolution`: Resolve blocked stat identities before stable stat aggregation.
- `skill_identity_policy`: Keep unresolved and ambiguous skill identities unbridged until source evidence is sufficient.
- `golden_mechanical_baselines`: Implement golden mechanical baseline tests before production planner remap.

## Safety State

- Production consumed: `false`
- Production planner remap performed: `false`
- Planner-calculable count: `0`
- Stable-calculable count: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`
- Experimental adapter mode enabled by default: `false`

## Recommended Next Track

`v3_mechanical_intelligence_planning` should focus on value normalization contracts, operation semantics, stat identity resolution, skill identity policy, golden mechanical baselines, and deterministic dry-run comparison before production planner remap.
