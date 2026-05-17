"""Stable hashing for v4.1 replay and rollback visibility evidence."""

from __future__ import annotations

from typing import Any

from operational_lifecycle.lifecycle_hashing import deterministic_lifecycle_hash

from .refresh_replay_rollback_visibility_models import (
    RefreshReplayRollbackVisibility,
    ReplayRollbackContinuityMetadata,
    ReplayRollbackDiagnostics,
    ReplayRollbackVisibilityIdentity,
)
from .refresh_replay_rollback_visibility_serialization import (
    _export_record,
    export_refresh_replay_rollback_visibility,
    export_replay_rollback_identity,
)


def deterministic_replay_rollback_hash(payload: Any) -> str:
    return deterministic_lifecycle_hash(payload)


def hash_replay_rollback_identity(identity: ReplayRollbackVisibilityIdentity) -> str:
    return deterministic_replay_rollback_hash(export_replay_rollback_identity(identity))


def hash_replay_rollback_continuity(metadata: ReplayRollbackContinuityMetadata) -> str:
    return deterministic_replay_rollback_hash(_export_record(metadata))


def hash_replay_rollback_diagnostics(diagnostics: ReplayRollbackDiagnostics) -> str:
    return deterministic_replay_rollback_hash(_export_record(diagnostics))


def hash_refresh_replay_rollback_visibility(visibility: RefreshReplayRollbackVisibility) -> str:
    return deterministic_replay_rollback_hash(export_refresh_replay_rollback_visibility(visibility))
