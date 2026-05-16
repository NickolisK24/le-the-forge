# V3.2 Limited Runtime Consumption Experiment Contracts

Phase 10 defines deterministic limited runtime consumption experiment governance for non-production runtime planning.
This is not production runtime enablement and does not enable default runtime manifest consumption.

## Explicit Governance

Limited runtime consumption experiments require explicit authorization, explicit intent, and explicit scope before eligibility can be considered.

## Limited Scope

Experiment scope must be limited, isolated, reversible, and non-production. Unsafe or missing scope fails visibly.

## Manifest Authority

Experiment manifests remain non-production-authoritative. Production-authoritative manifest treatment remains prohibited.

## Prior Governance Chain

Phase 10 builds on entrypoint, isolation, session, safety rollback, diff audit, determinism, traceability, replayability, and drift detection contracts.

## Summary

- Records evaluated: `1`
- Experiment eligible: `1`
- Experiment blocked: `0`
- Authorization missing: `0`
- Unsafe scope: `0`
- Runtime manifest consumption enabled: `false`
- Production routing authorized: `false`
- Production-authoritative manifest treatment: `false`
- Deterministic: `true`

## Experiment Blockers

| Blocker | Count |
| --- | ---: |

## Contracts

| Contract | Manifest | Fixture Set | Eligibility | Mode |
| --- | --- | --- | --- | --- |
| `v3_2_limited_runtime_experiment_8433ac3695793b4a` | `v3_1_admission_manifest_198a3e2110f9e5e4` | `v3_1_fixture_set_6d3b668a84cfbb69` | `limited_runtime_experiment_eligible` | `limited_runtime_experiment_eligible` |

## Future Phases

- future kill-switch phases may consume deterministic experiment eligibility evidence
- future closeout phases must preserve non-production manifest authority
- future runtime planning must continue to block default manifest consumption and production routing

## Conclusion

Limited runtime experiment eligibility is governance-only. Production runtime routing remains prohibited, default runtime manifest consumption remains disabled, and production-authoritative manifest treatment remains prohibited.
