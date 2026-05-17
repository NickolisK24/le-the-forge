# v4.1 Refresh Diagnostics Explainability

## Architectural Purpose

v4.1 Phase 8 evolves replay and rollback visibility into unified deterministic refresh diagnostics and explainability intelligence.

Phase 1 established refresh manifest governance foundations. Phase 2 established deterministic refresh dependency graph governance. Phase 3 established deterministic refresh lineage certification. Phase 4 established deterministic schema evolution governance. Phase 5 established deterministic refresh sequencing visibility. Phase 6 established deterministic refresh drift certification. Phase 7 established deterministic replay and rollback visibility. Phase 8 adds a unified explainability layer across manifest, dependency, lineage, schema, sequencing, drift, replay, and rollback governance evidence.

This diagnostics and explainability layer is governance visibility infrastructure only. It does not remediate, correct, repair, recommend, rank, score, select, approve, authorize, execute refreshes, orchestrate work, automatically sequence work, migrate schemas, roll back state, recover state, consume production bundles, mutate runtime state, or alter planner behavior.

## Scope

The phase creates deterministic refresh diagnostics and explainability infrastructure under `backend/app/operational_refresh/`, a deterministic report generator, focused validation tests, a generated diagnostics explainability report, a generated unified diagnostics report, a generated unified explainability report, a generated diagnostics continuity certification report, and a generated diagnostics integrity certification report.

The explainability layer references v4.1 refresh manifest foundations, v4.1 dependency graph infrastructure, v4.1 lineage certification evidence, v4.1 schema evolution governance evidence, v4.1 refresh sequencing visibility evidence, v4.1 refresh drift certification evidence, and v4.1 replay/rollback visibility evidence as descriptive inputs. It does not consume production bundles and does not alter planner behavior.

## Deterministic Diagnostics Guarantees

Refresh diagnostics and explainability models are frozen dataclasses with explicit diagnostics identity, explanation identity, diagnostic summaries, explanation summaries, cross-layer diagnostic aggregation, cross-layer explanation aggregation, continuity metadata, integrity boundary visibility, and governance visibility.

Serialization uses stable sorted JSON-compatible output. Manifest diagnostics, dependency diagnostics, lineage diagnostics, schema diagnostics, sequencing diagnostics, drift diagnostics, replay diagnostics, rollback diagnostics, unsupported-state explanations, blocked-state explanations, prohibited-state explanations, limitation explanations, stale evidence, missing coverage, inconsistent severity, inconsistent categories, and cross-layer conflicts remain visible.

Hashing uses stable SHA-256 hashing over deterministic serialization. Repeated construction and reordered diagnostic/explanation summaries produce stable serialized equality and stable diagnostics explainability hashes.

## Explainability Boundaries

The default explainability layer explains what the refresh governance stack sees, why it matters, what is blocked, what is unsupported, which evidence is stale, where coverage is missing, where severity or category visibility is inconsistent, and which capabilities remain prohibited.

Explanations are descriptive only. They do not imply remediation, correction, recommendation, ranking, scoring, selection, approval, authorization, orchestration, execution, planner integration, production consumption, or mutation capability.

## Integrity Rules

The integrity layer exposes missing diagnostic coverage, missing explanation coverage, inconsistent diagnostic severity, inconsistent explanation category, unsupported diagnostic providers, unsupported explanation providers, prohibited diagnostic domains, prohibited explanation domains, blocked diagnostic states, blocked explanation states, stale diagnostic evidence, stale explanation evidence, cross-layer diagnostic conflicts, cross-layer explanation conflicts, prohibited remediation leakage, prohibited correction leakage, prohibited recommendation leakage, prohibited ranking leakage, prohibited scoring leakage, prohibited selection leakage, prohibited approval leakage, prohibited authorization leakage, prohibited orchestration leakage, prohibited execution leakage, prohibited planner-integration leakage, and prohibited production-consumption leakage.

Integrity auditing does not remediate, correct, repair, recommend, rank, score, select, approve, authorize, orchestrate, execute, migrate, recover, roll back, or mutate anything.

## Explicit Limitation Visibility

v4.1 Phase 8 creates deterministic diagnostics and explainability metadata only.

v4.1 Phase 8 does not enable remediation.

v4.1 Phase 8 does not enable automatic correction.

v4.1 Phase 8 does not enable recommendation ranking scoring or selection.

v4.1 Phase 8 does not enable approval or authorization.

v4.1 Phase 8 does not enable orchestration execution.

v4.1 Phase 8 does not enable automatic sequencing.

v4.1 Phase 8 does not enable refresh execution.

v4.1 Phase 8 does not enable migration execution.

v4.1 Phase 8 does not enable recovery execution.

v4.1 Phase 8 does not enable rollback execution.

v4.1 Phase 8 does not enable planner integration.

v4.1 Phase 8 does not enable production consumption.

v4.1 Phase 8 does not enable mutation behavior.

## Explicit Prohibition Visibility

No remediation exists.

No automatic correction exists.

No recommendation ranking scoring or selection exists.

No approval or authorization exists.

No orchestration execution exists.

No automatic sequencing exists.

No refresh execution exists.

No migration execution exists.

No recovery execution exists.

No rollback execution exists.

No planner integration exists.

No production consumption exists.

No mutation behavior exists.

No diagnostic becomes an action.

No explanation becomes a recommendation ranking scoring or selection system.

No summary implies authorization or approval.

## Non-Remediation And Non-Execution Preservation

Refresh diagnostics and explainability remains non-remediating, non-correcting, non-recommending, non-ranking, non-scoring, non-selecting, non-approving, non-authorizing, and non-executable. The models expose disabled flags for remediation, automatic correction, automatic repair, refresh execution, orchestration execution, automatic sequencing, dependency resolution, schema migration execution, automatic migration, rollback execution, recovery execution, planner integration, production consumption, recommendation, ranking, scoring, selection, optimization, authorization, approval, runtime mutation, hidden remediation behavior, hidden orchestration behavior, and implicit execution pathways.

The validation report treats any enabled capability flag as a blocker.

## Generated Evidence

Generated diagnostics explainability report:

`docs/generated/v4_1_refresh_diagnostics_explainability_report.json`

Generated unified diagnostics report:

`docs/generated/v4_1_unified_refresh_diagnostics_report.json`

Generated unified explainability report:

`docs/generated/v4_1_unified_refresh_explainability_report.json`

Generated diagnostics continuity certification report:

`docs/generated/v4_1_refresh_diagnostics_continuity_certification_report.json`

Generated diagnostics integrity certification report:

`docs/generated/v4_1_refresh_diagnostics_integrity_certification_report.json`

All reports include deterministic hashes, diagnostics visibility validation, explanation visibility validation, continuity certification, non-remediation validation, non-correction validation, non-recommendation validation, non-approval validation, non-execution validation, explicit limitations, and explicit prohibitions.
