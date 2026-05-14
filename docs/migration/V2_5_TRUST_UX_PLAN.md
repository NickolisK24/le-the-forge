# V2.5 Trust UX Plan

This audit plans the v2.5 trust and UX layer.
It does not implement UI behavior, planner remap, value normalization, or mechanical calculation changes.

## Safety State

- V2 infrastructure ready: `true`
- Production planner ready: `false`
- Mechanical remap ready: `false`
- Stable-calculable count: `0`
- Value normalization: `audit_only`
- Skill identity bridge: `unbridged`

## UX Item Summary

- UX items: `14`
- Ready for v2.5: `2`
- Needs copy design: `5`
- Needs frontend component: `5`
- Debug-only: `1`
- Blocked by v3 mechanics: `1`

## Proposed Sequence

| Order | Step | Description |
| ---: | --- | --- |
| `1` | `shared_trust_support_badges` | Build shared trust/support badge components. |
| `2` | `shared_provenance_warning_panels` | Build shared provenance and warning summary panels. |
| `3` | `user_facing_limitation_copy` | Write and apply limitation copy for unsupported, audit-only, and non-calculating states. |
| `4` | `stats_modifiers_debug_page` | Add a dedicated stats/modifiers debug page. |
| `5` | `trusted_data_explanation_page` | Add a non-developer trusted-data explanation page. |
| `6` | `planner_safe_adapter_status_panel` | Expose planner-safe adapter status as non-calculating context. |
| `7` | `report_debug_navigation_cleanup` | Improve navigation across reports and debug routes. |
| `8` | `user_facing_support_matrix` | Create a compact support matrix for domains and mechanics. |
| `9` | `pre_v3_mechanical_readiness_dashboard` | Create a readiness dashboard that remains warning-only until v3 gates pass. |

## UX Items

| Item | Classification | User-facing |
| --- | --- | --- |
| `support_trust_badges` | `needs_frontend_component` | `true` |
| `provenance_summaries` | `needs_frontend_component` | `true` |
| `limitation_warnings` | `needs_copy_design` | `true` |
| `unsupported_mechanic_messaging` | `ready_for_v2_5` | `true` |
| `stable_calculable_explanation` | `needs_copy_design` | `true` |
| `audit_only_value_policy_explanation` | `needs_copy_design` | `true` |
| `skill_identity_gap_explanation` | `needs_copy_design` | `true` |
| `planner_safe_adapter_explanation` | `needs_copy_design` | `true` |
| `stats_modifiers_debug_page` | `needs_frontend_component` | `false` |
| `report_navigation` | `needs_frontend_component` | `true` |
| `trusted_data_explanation_page` | `needs_frontend_component` | `true` |
| `what_can_calculate_messaging` | `ready_for_v2_5` | `true` |
| `raw_debug_payloads` | `debug_only` | `false` |
| `mechanical_delta_explanations` | `blocked_by_v3_mechanics` | `false` |

## Frontend Gaps

- `shared_user_facing_badges_missing`: Debug panels summarize support/provenance, but reusable user-facing trust badges are not yet implemented.
- `stats_modifiers_page_missing`: Stat and modifier registries do not yet have a dedicated frontend debug page.
- `trusted_data_explanation_page_missing`: There is no non-developer page explaining trusted data, limitations, and current calculation boundaries.
- `planner_status_panel_missing`: Planner-adjacent views do not yet show v2 adapter status as non-calculating context.
- `support_matrix_missing`: Users cannot yet scan a compact support matrix by domain and mechanic type.

## Developer-Only Concepts

- `raw_debug_payloads`: Keep raw API envelopes, full provenance paths, and sample blocked records in debug views rather than user-facing planner flows.

## Runtime Behavior

- No frontend behavior was changed.
- No backend runtime behavior was changed.
- No production planner route was added.
- No stat or modifier calculation behavior was changed.
- No value scale was promoted.
- No unresolved skill identity reference was bridged.
