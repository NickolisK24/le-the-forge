# V3.1 Dual-Run Comparison

Phase 2 introduces deterministic dual-run comparison infrastructure around the trusted shadow layer.
It is observational only; production output remains legacy-owned and trusted data is not default production truth.

## Recommendation

- Recommendation: `OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING`
- Production default routing authorized: `false`

## Summary

- Total comparisons: `5`
- Equivalent: `1`
- Divergent: `1`
- Unsupported: `2`
- Blocked: `0`
- Legacy only: `1`
- Trusted only: `0`
- Unavailable: `0`
- Not evaluated: `0`
- Production affected: `0`
- Deterministic: `true`

## Drift Results

| Comparison | Legacy | Trusted Shadow | Classification | Reason |
| --- | --- | --- | --- | --- |
| `affix` | `available` | `available` | `equivalent` | `comparable_value_hash_match` |
| `idol` | `available` | `missing` | `legacy_only` | `trusted_shadow_summary_missing` |
| `item_base` | `available` | `available` | `divergent` | `comparable_value_hash_mismatch` |
| `monolith_echo` | `missing` | `unsupported` | `unsupported` | `unsupported_trusted_shadow_domain` |
| `passive_skill` | `unsupported` | `available` | `unsupported` | `unsupported_state_visible` |

## Phase 2 Boundaries

- dual-run comparison accepts summaries and shadow metadata only
- legacy production output remains the truth source
- trusted data is not default production truth
- drift visibility is established through explicit classifications
- unsupported and blocked states are intentionally surfaced

## Conclusion

Dual-run drift visibility is now available, but production routing remains unchanged and legacy-owned.
