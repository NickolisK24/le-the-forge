# V2 Validation CI Hardening

## Purpose

Phase 14 adds a focused validation entrypoint for the v2 trusted-data system before planner-safe adapter work begins.

The validation target is the v2 infrastructure itself: generated reports, repository/API contract reports, production non-consumption guards, frontend v2 debug envelope handling, and known safety blockers.

This phase does not remap planner behavior, consume v2 data in production planner systems, normalize additional values, bridge unresolved skill identities, or alter crafting, simulation, or stat engine behavior.

## Validation Entrypoint

Run the static v2 validation summary with:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\validate_v2_trusted_data.py
```

The script writes:

```text
docs/generated/v2_validation_ci_report.json
```

It validates:

- required `docs/generated/v2_*.json` reports exist
- required generated reports are valid JSON
- backend repository and API contract reports are present
- production consumption remains false
- stable-calculable count remains intentionally `0`
- value normalization remains audit-only
- unresolved skill identity references remain unbridged
- known frontend full-suite caveat remains documented

## Backend Validation Commands

Use these PowerShell-friendly commands for backend v2 validation:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend\tests\test_v2_* -q
.\backend\.venv\Scripts\python.exe -m pytest backend\tests\test_forge_safe_production_non_consumption.py -q
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_backend_repository_layer.py
.\backend\.venv\Scripts\python.exe backend\scripts\report_v2_api_contract.py
.\backend\.venv\Scripts\python.exe backend\scripts\validate_v2_trusted_data.py
python -m json.tool docs\generated\v2_backend_repository_report.json
python -m json.tool docs\generated\v2_api_contract_report.json
python -m json.tool docs\generated\v2_validation_ci_report.json
git diff --check
```

If the `test_v2_*` wildcard is not supported by the shell in a given environment, run the explicit `backend/tests/test_v2_*.py` files individually.

## Frontend Validation Commands

Use these commands for frontend v2 debug validation:

```powershell
npm --prefix frontend run type-check
npm --prefix frontend test -- v2-api-envelope.test.ts v2-items-debug-page.test.tsx v2-idols-debug-page.test.tsx v2-unique-set-debug-page.test.tsx v2-class-mastery-debug-page.test.tsx v2-passives-debug-page.test.tsx v2-skills-debug-page.test.tsx forge-safe-affixes-debug-page.test.tsx --run
```

These commands validate the Phase 13 envelope helpers and affected v2/debug pages without requiring unrelated broad frontend tests to pass.

## Known Frontend Caveat

The full frontend suite currently has unrelated navigation/layout search assertion failures outside the v2 trusted-data cleanup scope.

Phase 14 does not fix those unrelated assertions. The focused frontend validation target is:

- TypeScript type-check
- v2 API envelope helper tests
- v2/debug page tests

## CI Recommendation

No workflow file was changed in this phase. The current CI already runs broad backend tests and frontend type-check.

Recommended future CI refinement:

- Add a focused backend step that runs `backend/scripts/validate_v2_trusted_data.py`.
- Add a focused frontend debug step that runs the v2 envelope/debug page test command above.
- Keep these focused checks separate from the unrelated full frontend suite caveat.

## Current Report Summary

The generated report currently records:

- Required generated reports: `32`
- Valid generated reports: `32`
- Missing generated reports: `0`
- Invalid JSON reports: `0`
- Backend repository domains: `10`
- Experimental API routes: `38`
- Production consumed: `false`
- Stable-calculable count: `0`
- Value normalization policy: `audit_only`
- Skill identity bridge status: `unbridged`
- Validation status: `pass`

## Safety Status

- Production v2 consumption remains blocked.
- Stable-calculable count remains intentionally `0`.
- Value normalization remains audit-only.
- Skill identity gaps remain visible and unbridged.
- Unsupported/scripted mechanics remain excluded from planner-safe behavior.

## Remaining Risks

- The validation script checks generated report presence, JSON validity, and high-level safety invariants; it does not replace focused unit tests.
- Frontend full-suite failures remain outside this checkpoint and should be resolved separately.
- Planner-safe adapter work remains blocked on value normalization and stable eligibility policy.
