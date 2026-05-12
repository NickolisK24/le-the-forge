# EpochForge v2 Checkpoints

## Purpose

EpochForge v2 work must proceed phase by phase. Each checkpoint stops for human review before the next phase starts.

## Checkpoint Rules

- Work only on the active phase.
- Do not skip checkpoint review.
- Do not create later-phase contracts before the inventory checkpoint is reviewed.
- Keep stable behavior backward-compatible unless a reviewed phase explicitly changes it.
- Report files created, files modified, commands run, tests run, generated reports, important findings, remaining risks, and checkpoint readiness.

## Phase Checkpoints

| Checkpoint | Phase | Review output |
| --- | --- | --- |
| Checkpoint 0 | Phase 0, ground rules | Policy docs exist and define stable/experimental boundaries. |
| Checkpoint 1 | Phase 1, source inventory | Source inventory JSON and markdown report exist and are ready for review. |
| Checkpoint 2 | Phase 2, trust model contracts | Data contract proposals are ready for review. |
| Checkpoint 3 | Phase 3, source ingestion plan | Ingestion plan and validation expectations are ready for review. |
| Checkpoint 4 | Phase 4, validation design | Validator plan and failure modes are ready for review. |
| Checkpoint 5 | Phase 5, backend contract layer | Backend contract boundaries are ready for review. |
| Checkpoint 6 | Phase 6, frontend consumption plan | Frontend data access plan is ready for review. |
| Checkpoint 7 | Phase 7, planner compatibility | Compatibility and fallback behavior are ready for review. |
| Checkpoint 8 | Phase 8, unsupported mechanics surfacing | Unsupported mechanics display policy is ready for review. |
| Checkpoint 9 | Phase 9, debug transparency | Debug and provenance views are ready for review. |
| Checkpoint 10 | Phase 10, test expansion | Test plan and target coverage are ready for review. |
| Checkpoint 11 | Phase 11, patch refresh process | Patch refresh process is ready for review. |
| Checkpoint 12 | Phase 12, hardcoded data audit | Hardcoded data review is ready for review. |
| Checkpoint 13 | Phase 13, replacement sequencing | Replacement order is ready for review. |
| Checkpoint 14 | Phase 14, migration execution | Execution results are ready for review. |
| Checkpoint 15 | Phase 15, regression review | Regression findings are ready for review. |
| Checkpoint 16 | Phase 16, documentation update | User and maintainer docs are ready for review. |
| Checkpoint 17 | Phase 17, release readiness | Ship criteria are ready for review. |
| Checkpoint 18 | Phase 18, post-ship monitoring | Follow-up validation plan is ready for review. |
| Checkpoint 19 | Phase 19, cleanup | Deprecated source cleanup is ready for review. |

## Current Stop Point

This session stops at Checkpoint 1 after Phase 0 policy docs and Phase 1 inventory reports are complete. Phase 2 must not begin until the inventory is reviewed.
