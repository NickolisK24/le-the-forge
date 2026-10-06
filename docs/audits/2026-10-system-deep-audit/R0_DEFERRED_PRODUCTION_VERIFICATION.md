# R0 Deferred Production Verification (proof debt)

Tracking record only. It does not change any finding status.

R0 is deployed to production at `main` 80bd559. The operator confirmed:
- backend and frontend deployed;
- both migrations applied;
- the app booted and health checks are green;
- API routing works;
- the old Last Epoch Tools server-fetch user flow is gone;
- no immediate regression.

The production probes below have not been run yet, because the operator is mobile. Each passes the focused local R0 regression suite. None of them is VERIFIED.

The full verification record, including INFRA-1, IMP-1 and FE-1 marked VERIFIED, is in docs PR #573 (`docs/r0-production-verification`), which is not merged. On `main`, `AUDIT_EVIDENCE.json` still shows those findings as FIXED_LOCAL.

## Deferred checks

| Finding | Severity | Status on main | Production probe still owed | Harness gate |
| --- | --- | --- | --- | --- |
| SYS-1 | P0 | FIXED_LOCAL | Unauthenticated affix PATCH refused; affixes data unchanged | 4 |
| SYS-2 | P1 | FIXED_LOCAL | Unauthenticated game-data reload refused | 4 |
| API-4 | P1 | FIXED_LOCAL | Skill node allocation on another user's build refused | 5–7 |
| API-5 | P1 | FIXED_LOCAL | Anonymous build cannot be modified or deleted by others | 5–7 |
| API-6 | P1 | FIXED_LOCAL | Private build hidden from other users and signed-out visitors | 5–7 |
| DB-1 | P1 | FIXED_LOCAL | Deleting a viewed build succeeds (no 500) | 5–7 |
| IMP-2 | P1 | FIXED_LOCAL | LET URL returns `LET_SERVER_FETCH_UNSUPPORTED`; no server fetch | 9 |
| IMP-3 | P2 | FIXED_LOCAL | Maxroll failure alert shows `Not evaluated` (not `None`) and no raw payload | 9 + Discord check |
| API-2 | P1 | FIXED_LOCAL | Oversized multi-target request rejected with 422 | 10 |

Partially deferred, as planned:

| Finding | Severity | Status on main | Remaining work | Owner phase |
| --- | --- | --- | --- | --- |
| FE-4 | P1 | OPEN | Remaining importer dead ends (Maxroll 403 copy, Quick Fetch, footer) | R4 |
| OBS-1 | P1 | OPEN | Alert aggregation and replay; data/extractor version provenance | R7, with extraction provenance from R1 |

## Harness

- Branch `ops/r0-production-smoke` @ `270a81c` (not merged; must not ship).
- Command: `python3 scripts/verify_r0_production.py --target https://epochforge-api.onrender.com/api`
- Operator guide: `R0_OPERATOR_SMOKE_TEST.md` on that branch.
- Expected result: `TOTAL PASS=32 FAIL=0 SKIP=0`, plus the Discord alert fields and a clean Render log window.

## Rules while this debt is open

- Do not mark any finding above VERIFIED until its production probe passes.
- Do not delete the harness branch.
- R1 does not block on these checks. R1 must not modify the R0 code paths behind them unless an R1 change directly conflicts.
- `dev` is not reconciled and nothing is merged from `dev` into `main`.
