"""V3.1 trusted production shadow-consumption safety scaffolds."""

from .dual_run_comparison import (
    DRIFT_CLASSIFICATIONS,
    V31DualRunComparison,
    build_sample_dual_run_inputs,
)
from .trusted_shadow_consumption import (
    SUPPORTED_TRUSTED_SHADOW_DOMAINS,
    V31TrustedProductionShadowConsumption,
    build_default_trusted_repository_probes,
    deterministic_hash,
)

__all__ = [
    "DRIFT_CLASSIFICATIONS",
    "SUPPORTED_TRUSTED_SHADOW_DOMAINS",
    "V31DualRunComparison",
    "V31TrustedProductionShadowConsumption",
    "build_sample_dual_run_inputs",
    "build_default_trusted_repository_probes",
    "deterministic_hash",
]
