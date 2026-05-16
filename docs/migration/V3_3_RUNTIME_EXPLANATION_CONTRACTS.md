# V3.3 Runtime Explanation Contracts

Phase 5 establishes deterministic runtime explanation contracts for planning-only runtime intelligence foundations.

## Boundaries

Runtime explanations remain planning-only. Production runtime routing, default manifest consumption, production-authoritative manifest treatment, active runtime reasoning decisions, recommendation logic, and autonomous planner mutation remain disabled or prohibited.

## Compatibility

Every explanation contract references explicit classification IDs, evidence type IDs, provenance type IDs, and reasoning stage IDs from the Phase 1 through Phase 4 registries.

## Summary

- Total explanation contracts: `12`
- Deterministic ordering valid: `true`
- Stable hash valid: `true`
- Replay validation passed: `true`
- Duplicate detection passed: `true`
- Invalid evidence references: `0`
- Invalid provenance references: `0`
- Invalid classification references: `0`
- Invalid reasoning-stage references: `0`
- Required-section violations: `0`
- Production-authorized explanations: `0`

## Explanation Contracts

| Rank | Explanation | Blocker | Risk | Limitation | Confidence | Replay Safe |
| ---: | --- | --- | --- | --- | --- | --- |
| `10` | `evidence_summary` | `false` | `false` | `true` | `false` | `true` |
| `20` | `provenance_summary` | `false` | `false` | `true` | `false` | `true` |
| `30` | `classification_summary` | `false` | `false` | `true` | `true` | `true` |
| `40` | `reasoning_chain_summary` | `false` | `true` | `true` | `false` | `true` |
| `50` | `blocker_summary` | `true` | `false` | `true` | `false` | `false` |
| `60` | `risk_summary` | `false` | `true` | `true` | `false` | `false` |
| `70` | `limitation_summary` | `false` | `true` | `true` | `false` | `true` |
| `80` | `drift_summary` | `false` | `true` | `true` | `false` | `false` |
| `90` | `replay_summary` | `false` | `false` | `true` | `false` | `true` |
| `100` | `confidence_summary` | `false` | `true` | `true` | `true` | `true` |
| `110` | `decision_boundary_summary` | `true` | `true` | `true` | `false` | `false` |
| `120` | `unsupported_summary` | `true` | `true` | `true` | `false` | `false` |

## Explicit Visibility

- Blocker-visible explanations remain visible through `blocker_summary`, `decision_boundary_summary`, and `unsupported_summary`.
- Risk-visible explanations remain visible through risk, drift, confidence, decision-boundary, unsupported, and related summaries.
- Limitation-visible explanations remain visible across all explanation contracts.
- Confidence-visible explanations remain visible through `classification_summary` and `confidence_summary`.
- Unsupported explanations remain visible through `unsupported_summary`.
- Decision-boundary explanations remain visible through `decision_boundary_summary`.

## Conclusion

These contracts provide deterministic planning-only runtime explanation lineage. They do not authorize production enablement, runtime consumption, active reasoning decisions, recommendation logic, or autonomous planner mutation.
