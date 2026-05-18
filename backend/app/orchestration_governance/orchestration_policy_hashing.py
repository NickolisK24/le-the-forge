"""Deterministic hashing for v4.3 orchestration policy visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_policy_models import (
    OrchestrationPolicyVisibility,
    PolicyDiagnostic,
    PolicyExplainability,
    PolicyRecord,
    PolicyRelationship,
    PolicyTarget,
    PolicyVisibilityIdentity,
)
from .orchestration_policy_serialization import (
    export_orchestration_policy_visibility,
    export_policy_diagnostic,
    export_policy_explainability,
    export_policy_record,
    export_policy_relationship,
    export_policy_target,
    export_policy_visibility_identity,
    stable_serialize,
)


def deterministic_policy_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_policy_visibility_identity(identity: PolicyVisibilityIdentity) -> str:
    return deterministic_policy_hash(export_policy_visibility_identity(identity))


def hash_policy_record(policy: PolicyRecord) -> str:
    return deterministic_policy_hash(export_policy_record(policy))


def hash_policy_target(target: PolicyTarget) -> str:
    return deterministic_policy_hash(export_policy_target(target))


def hash_policy_relationship(relationship: PolicyRelationship) -> str:
    return deterministic_policy_hash(export_policy_relationship(relationship))


def hash_policy_diagnostic(diagnostic: PolicyDiagnostic) -> str:
    return deterministic_policy_hash(export_policy_diagnostic(diagnostic))


def hash_policy_explainability(summary: PolicyExplainability) -> str:
    return deterministic_policy_hash(export_policy_explainability(summary))


def hash_orchestration_policy_visibility(visibility: OrchestrationPolicyVisibility) -> str:
    return deterministic_policy_hash(export_orchestration_policy_visibility(visibility))
