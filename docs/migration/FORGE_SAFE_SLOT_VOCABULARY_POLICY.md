# Forge-Safe Slot Vocabulary Policy

Generated: 2026-05-11

## Purpose

This read-only policy records which slot vocabulary translations are approved for future test-only adapter work. It does not approve production migration, does not build a runtime adapter, and does not address value-scale normalization.

## Source

Source slot equivalence report: `docs\generated\forge_safe_slot_vocabulary_equivalence.json`

Generation command:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\report_forge_safe_slot_vocabulary_policy.py --slot-equivalence docs\generated\forge_safe_slot_vocabulary_equivalence.json --output docs\generated\forge_safe_slot_vocabulary_policy.json --markdown-output docs\migration\FORGE_SAFE_SLOT_VOCABULARY_POLICY.md
```

## Policy Summary

| Metric | Count |
| --- | ---: |
| candidate_count | 560 |
| policy_approved_slot_candidate_count | 559 |
| slot_blocked_candidate_count | 1 |
| needs_manual_review_count | 0 |
| production_consumed | False |

## Approved Slot Policy

559 candidates are approved only for future test-only adapter consideration from a slot-vocabulary perspective. These candidates still have unresolved value-scale blockers and are not production-safe.

## health_on_kill Decision

`health_on_kill` remains blocked from adapter candidate approval.

- Affix count: 2
- Example affix IDs: 20, 44
- Reason: inconsistent applicability evidence across two affixes.
- Required resolution: manual policy decision or source audit.
- Initial adapter subset: excluded.

## Production Boundary

This policy is for future test-only adapter work. It is marked `read_only=true`, `candidate_only=true`, `production_safe=false`, and `consumption_status=not_consumed`. Planner, crafting, stat aggregation, simulation, registries, and `/api/ref/affixes` must not consume it.

## Value-Scale Boundary

Value-scale blockers remain unresolved. Slot policy approval does not prove numerical equivalence, tier compatibility, gameplay correctness, or simulation behavior.

## Migration Implications

Slot vocabulary policy is now mostly settled for candidate planning: pure vocabulary differences can proceed to value-scale audit, while `health_on_kill` stays blocked until a manual policy or source audit resolves its applicability mismatch.

Recommended next task: run a value-scale normalization audit for the 559 slot-policy-approved candidates, excluding `health_on_kill` from the initial subset.
