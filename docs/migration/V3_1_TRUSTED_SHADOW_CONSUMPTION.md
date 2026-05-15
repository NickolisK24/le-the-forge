# V3.1 Trusted Shadow Consumption

Phase 1 introduces a disabled-by-default trusted production shadow-consumption gate.
It is observational only and does not authorize trusted repositories as production default routing.

## Recommendation

- Recommendation: `OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING`
- Production default routing authorized: `false`

## Summary

- Gate default enabled: `false`
- Disabled production output affected: `false`
- Enabled production output affected: `false`
- Trusted repositories available: `3`
- Trusted repositories unavailable: `0`
- Trusted entity count: `1645`
- Unsupported domains: `0`
- Legacy path still active: `true`
- Trusted path shadowed only: `true`
- Deterministic: `true`

## Shadow Rows

| Domain | Repository | Status | Entities | Production Output Affected |
| --- | --- | --- | ---: | --- |
| `affix` | `v2_affix_bundle` | `trusted_repository_shadowed` | `1098` | `false` |
| `item_base` | `v2_item_base_bundle` | `trusted_repository_shadowed` | `542` | `false` |
| `passive_skill` | `v2_passive_tree_bundle` | `trusted_repository_shadowed` | `5` | `false` |

## Phase 1 Boundaries

- trusted repositories may be inspected only in shadow mode
- legacy production routing remains the truth source
- trusted repository availability failures are reported explicitly
- unsupported trusted domains remain blocked
- production default routing is not authorized

## Conclusion

Trusted repository consumption remains shadow-only. Production planner/runtime outputs continue to come from legacy paths.
