# v4.1 Refresh Dependency Graph Infrastructure

## Architectural Purpose

v4.1 Phase 2 evolves refresh manifest governance into deterministic refresh dependency governance intelligence.

Phase 1 established deterministic refresh manifest foundations. Phase 2 adds deterministic dependency graph identity, dependency node modeling, dependency edge modeling, lineage chains, provenance chains, graph serialization, graph hashing, equality validation, continuity metadata, replay metadata, rollback metadata, drift visibility, diagnostics visibility, and integrity auditing.

This graph layer is governance intelligence only. It does not execute refreshes, sequence dependencies, resolve dependencies, remediate blockers, mutate runtime state, or authorize operational behavior.

## Scope

The phase creates deterministic refresh dependency graph infrastructure under `backend/app/operational_refresh/`, a deterministic report generator, focused validation tests, a generated graph report, a generated diagnostics report, and a generated integrity report.

The graph references v4.1 Phase 1 refresh manifest evidence and v4.0 closeout evidence as descriptive inputs. It does not consume production bundles and does not alter planner behavior.

## Deterministic Dependency Graph Guarantees

Dependency graph models are frozen dataclasses with explicit graph identity, dependency node identity, dependency edge identity, lineage chains, provenance chains, continuity metadata, replay metadata, rollback metadata, blocked-state visibility, unsupported-state visibility, drift visibility, diagnostics visibility, and governance visibility.

Serialization uses stable sorted JSON-compatible output. Unsupported, blocked, stale, prohibited, circular, lineage-gap, and provenance-gap dependency relationships remain visible. Prohibited dependency domains remain visible.

Hashing uses stable SHA-256 hashing over deterministic serialization. Repeated graph construction and reordered graph collections produce stable serialized equality and stable graph hashes.

## Dependency Relationship Visibility

The default graph includes supported source evidence relationships, unsupported future provider relationships, blocked dependency schema gaps, prohibited production runtime bundle relationships, circular dependency visibility, stale lifecycle dependency visibility, lineage-gap visibility, and provenance-gap visibility.

Circular dependency visibility is descriptive evidence. It is not graph traversal, dependency execution, sequencing, resolution, remediation, or orchestration.

## Integrity Rules

The integrity layer exposes circular dependency visibility, prohibited dependency domains, unsupported dependency providers, stale dependency relationships, lineage discontinuity, provenance discontinuity, replay discontinuity, rollback discontinuity, prohibited execution leakage, prohibited orchestration leakage, prohibited remediation leakage, and prohibited planner-integration leakage.

Integrity auditing does not correct, resolve, repair, migrate, recover, roll back, approve, authorize, execute, or mutate anything.

## Explicit Limitation Visibility

v4.1 Phase 2 creates deterministic refresh dependency governance metadata only.

v4.1 Phase 2 does not enable refresh execution.

v4.1 Phase 2 does not enable orchestration.

v4.1 Phase 2 does not enable dependency execution.

v4.1 Phase 2 does not enable automatic sequencing.

v4.1 Phase 2 does not enable automatic dependency resolution.

v4.1 Phase 2 does not enable planner integration.

v4.1 Phase 2 does not enable production consumption.

v4.1 Phase 2 does not enable remediation.

v4.1 Phase 2 does not enable mutation behavior.

## Explicit Prohibition Visibility

No orchestration exists.

No dependency execution exists.

No automatic sequencing exists.

No automatic dependency resolution exists.

No planner integration exists.

No production consumption exists.

No remediation exists.

No mutation behavior exists.

No recommendation, ranking, scoring, or selection behavior exists.

No approval or authorization behavior exists.

No silent dependency fallback behavior exists.

## Non-Execution Preservation

Refresh dependency graphs remain non-executable. The models expose disabled flags for refresh execution, graph execution, dependency execution, orchestration, automatic refresh sequencing, automatic dependency resolution, automatic migration, automatic rollback, automatic recovery, planner integration, production consumption, remediation, optimization, recommendation, ranking, scoring, selection, authorization, approval, runtime mutation, hidden orchestration behavior, implicit execution pathways, and silent dependency fallback.

The validation report treats any enabled capability flag as a blocker.

## Generated Evidence

Generated graph report:

`docs/generated/v4_1_refresh_dependency_graph_report.json`

Generated diagnostics report:

`docs/generated/v4_1_refresh_dependency_graph_diagnostics_report.json`

Generated integrity report:

`docs/generated/v4_1_refresh_dependency_graph_integrity_report.json`

All reports include deterministic hashes, visibility validation, continuity validation, non-execution validation, explicit limitations, and explicit prohibitions.
