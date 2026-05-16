# v3.5 Snapshot Diff and Drift Analysis

## Phase Boundary

v3.5 Phase 7 is a deterministic orchestration planning snapshot diff and drift-analysis layer.

It does not execute orchestration.

It does not dispatch orchestration.

It does not route requests.

It does not mutate state.

It does not write audit logs.

It does not perform graph execution.

It does not perform orchestration scheduling.

It does not capture runtime traces.

It does not read production state.

It does not perform live replay execution.

It only compares declarative orchestration planning snapshots and explains deterministic planning-state drift.

- Final diff status: `snapshot_diff_stable`
- Deterministic report hash: `cad50b397642a50b36cb53a7441a7b0136bbaefa6a50a512d12d18efd9fe29c0`
- Deterministic diff hash: `778b329afde021c4b896e1a38500526efe98f91f1bc3a77bae34f030dec42748`

## Supported Diff Statuses

- `snapshot_diff_prohibited`
- `snapshot_diff_unsupported`
- `snapshot_diff_replay_safety_compromised`
- `snapshot_diff_blocked_by_lineage_change`
- `snapshot_diff_blocked_by_replay_instability`
- `snapshot_diff_blocked_by_hash_mismatch`
- `snapshot_diff_drift_detected`
- `snapshot_diff_requires_manual_review`
- `snapshot_diff_changed_without_drift`
- `snapshot_diff_stable`

## Deterministic Priority Order

- `snapshot_diff_prohibited`
- `snapshot_diff_unsupported`
- `snapshot_diff_replay_safety_compromised`
- `snapshot_diff_blocked_by_lineage_change`
- `snapshot_diff_blocked_by_replay_instability`
- `snapshot_diff_blocked_by_hash_mismatch`
- `snapshot_diff_drift_detected`
- `snapshot_diff_requires_manual_review`
- `snapshot_diff_changed_without_drift`
- `snapshot_diff_stable`

## Diff Input Model

Inputs include source and target planning snapshots, expected snapshot hashes, replay stability, deterministic serialization verification, manual review, and explicit limitations.

## Diff Output Model

Outputs include final diff status, field-level diffs, replay-safety diffs, drift classifications, deterministic drift summary, deterministic explanation summary, and deterministic diff hash.

## Replay-Safety Model

Replay safety is modeled through snapshot hash stability, deterministic serialization preservation, lineage preservation, blocker preservation, unsupported/prohibited preservation, compatibility preservation, and environment preservation.

## Drift Classification Model

Drift classifications include governance, lineage, blocker, compatibility, environment, unsupported-state, prohibited-state, replay, hash, and limitation drift.

## Lineage Diff Model

Replay lineage, rollback lineage, and lineage gap changes remain explicit and fail-visible.

## Blocker Diff Model

Blocker changes are preserved without hidden inference or remediation.

## Unsupported and Prohibited Diff Model

Unsupported and prohibited states have high-priority statuses and cannot be silently suppressed.

## Compatibility and Environment Diff Model

Compatibility and environment changes remain distinct diff categories.

## Manual-Review Diff Model

Manual review remains explicit and does not approve replay, execution, or orchestration.

## Deterministic Diff Hash Behavior

Diff hashes use stable JSON serialization over caller-provided identifiers, snapshot hashes, diff categories, drift classifications, and replay-safety signals.

## Deterministic Report Hash Behavior

Report hashes use stable JSON serialization with sorted keys and deterministic scenario inputs.

## Scenario Coverage

- `fully_stable_snapshot_comparison` -> `snapshot_diff_stable`
- `changed_snapshot_without_drift` -> `snapshot_diff_changed_without_drift`
- `lineage_change_blocker` -> `snapshot_diff_blocked_by_lineage_change`
- `replay_instability_detection` -> `snapshot_diff_blocked_by_replay_instability`
- `hash_mismatch_detection` -> `snapshot_diff_blocked_by_hash_mismatch`
- `prohibited_diff_state` -> `snapshot_diff_prohibited`
- `unsupported_diff_state` -> `snapshot_diff_unsupported`
- `governance_drift_detection` -> `snapshot_diff_drift_detected`
- `compatibility_drift_detection` -> `snapshot_diff_drift_detected`
- `replay_safety_compromise` -> `snapshot_diff_replay_safety_compromised`
- `multiple_simultaneous_drift_constraints` -> `snapshot_diff_prohibited`

## Explicit Non-Execution Guarantees

- Runtime execution remains prohibited.
- Orchestration execution remains prohibited.
- Graph execution remains prohibited.
- Graph traversal remains prohibited.
- Scheduling behavior remains prohibited.
- Orchestration dispatch remains prohibited.
- Routing behavior remains prohibited.
- Mutation behavior remains prohibited.
- Audit log writing remains prohibited.
- Production consumption remains prohibited.
- Runtime trace capture remains prohibited.
- Production state reads remain prohibited.
- Live replay remains prohibited.
- The repository remains planning-only.

## Remaining Limitations

- snapshot diff analysis compares declarative planning snapshots only
- snapshot diff analysis does not approve replay or orchestration planning states
- snapshot diff analysis does not execute, route, mutate, write, schedule, or dispatch orchestration
- snapshot diff analysis does not perform live replay, capture runtime traces, or read production state
