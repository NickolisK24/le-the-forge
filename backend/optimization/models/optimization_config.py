"""
F1 — OptimizationConfig

Defines the complete configuration for a build optimization run.
All fields have safe defaults; callers override only what they need.
"""

from __future__ import annotations
from dataclasses import dataclass, field

VALID_METRICS = ("dps", "total_damage", "ttk", "uptime", "composite")


@dataclass
class OptimizationConfig:
    """
    Configuration for a single optimization run.

    target_metric:
        Objective function for scoring. One of: dps, total_damage, ttk, uptime, composite.
        "ttk" (time-to-kill) is minimized; all others are maximized.

    max_variants:
        Maximum number of build variants to generate and simulate.
        Range: [1, 1000].

    mutation_depth:
        Number of independent mutations applied to produce each variant.
        Range: [1, 10].

    constraints:
        Dict of named constraint rules applied before simulation.
        Example: {"min_health": 500.0, "max_passive_nodes": 20}

    random_seed:
        Seed for the RNG used in variant generation.
        Same seed + same base build → identical variant list (deterministic).
    """
    target_metric:  str  = "dps"
    max_variants:   int  = 50
    mutation_depth: int  = 2
    constraints:    dict = field(default_factory=dict)
    random_seed:    int  = 42

    def __post_init__(self) -> None:
        if self.target_metric not in VALID_METRICS:
            raise ValueError(
                f"Invalid target_metric '{self.target_metric}'. "
                f"Must be one of: {VALID_METRICS}"
            )
        if not (1 <= self.max_variants <= 1000):
            raise ValueError(
                f"max_variants must be in [1, 1000], got {self.max_variants}"
            )
        if not (1 <= self.mutation_depth <= 10):
            raise ValueError(
                f"mutation_depth must be in [1, 10], got {self.mutation_depth}"
            )

    def to_dict(self) -> dict:
        return {
            "target_metric":  self.target_metric,
            "max_variants":   self.max_variants,
            "mutation_depth": self.mutation_depth,
            "constraints":    dict(self.constraints),
            "random_seed":    self.random_seed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "OptimizationConfig":
        return cls(
            target_metric  = d.get("target_metric",  "dps"),
            max_variants   = d.get("max_variants",   50),
            mutation_depth = d.get("mutation_depth", 2),
            constraints    = dict(d.get("constraints", {})),
            random_seed    = d.get("random_seed",    42),
        )
