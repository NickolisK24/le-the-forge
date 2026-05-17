# v4.0 Patch Lifecycle Drift Foundations

## Architectural Purpose

v4.0 Phase 2 extends the deterministic operational lifecycle foundation with the first lifecycle drift detection layer. It compares trusted lifecycle records and emits deterministic drift evidence for identity drift, patch version drift, extraction version drift, schema version drift, lifecycle generation drift, provenance drift, lineage drift, lifecycle state drift, visibility drift, replay continuity drift, rollback continuity drift, and integrity warning drift.

This phase is descriptive lifecycle intelligence only.

## Drift Detection Philosophy

Drift detection identifies and exposes differences between source and target lifecycle evidence. It preserves before and after values, provenance context, lineage context, visibility context, severity, explanations, deterministic keys, replay safety, rollback safety, and provenance safety.

Drift detection is not operational automation. It does not correct, resolve, approve, authorize, refresh, migrate, schedule, route, dispatch, or execute lifecycle behavior.

## Hard Prohibitions

This phase does not introduce patch execution, patch refresh execution, lifecycle mutation, drift repair, automatic remediation, automatic correction, automatic migration, approval systems, authorization systems, deployment behavior, scheduling, routing, dispatch, orchestration execution, recommendations, ranking, scoring, selection, optimization, runtime mutation, silent fallback behavior, hidden lifecycle state changes, or callable operational workflows.

All drift outputs remain descriptive-only.

## Deterministic Comparison Guarantees

Lifecycle drift comparison is stable and read-only. Source and target lifecycle records are not mutated. Comparison functions produce deterministic findings for patch identity, patch version, extraction version, schema version, lifecycle generation, provenance records, lineage records, lifecycle states, visibility records, replay continuity references, rollback continuity references, and integrity warning visibility.

Findings use deterministic keys derived from drift type, compared field, source identity, target identity, before value, and after value.

## Deterministic Serialization Guarantees

Drift serialization preserves deterministic finding order, before values, after values, explanations, provenance references, lineage references, visibility references, unsupported drift, prohibited drift, unknown drift, and blocking drift.

No hidden omissions are enabled. No silent normalization hides drift.

## Deterministic Hashing Guarantees

Drift report hashing uses stable JSON and SHA-256. The hash includes source identity, target identity, all finding deterministic keys, before and after values, visibility references, provenance references, lineage references, severity counts, drift counts, and safety booleans.

Repeated runs over the same lifecycle records produce the same drift report hash.

## Fail-Visible Drift Behavior

Unsupported drift, prohibited drift, unknown drift, blocking drift, integrity warning drift, replay continuity drift, rollback continuity drift, provenance continuity drift, and lineage continuity drift remain visible in the drift report and generated evidence.

Severity is descriptive only. It does not imply authorization, approval, selection, remediation, correction, or execution.

## Unsupported, Prohibited, And Unknown Drift Visibility

Unsupported lifecycle state visibility drift is counted and exposed. Prohibited lifecycle state visibility drift is counted and exposed. Unknown lifecycle state visibility drift is counted and exposed.

These categories do not trigger hidden fallback behavior or lifecycle state changes.

## Replay And Rollback Safety

Replay continuity drift and rollback continuity drift are reported as evidence only. Replay safety and rollback safety are preserved as report booleans. No replay or rollback execution behavior is introduced.

## Provenance And Lineage Safety

Provenance and lineage drift findings preserve source and target references. Provenance safety remains explicit and fail-visible. Lineage drift remains descriptive and does not apply lifecycle transitions.

## No Remediation Or Execution

Drift detection does not remediate or execute. v4.0 Phase 2 does not correct drift, resolve drift, authorize lifecycle changes, execute refresh behavior, mutate runtime state, enable orchestration, or create callable operational workflows.
