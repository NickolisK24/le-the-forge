"""
F7 — OptimizationResult

Stores a single ranked optimization outcome: the build variant that produced
the result, its score, the raw simulation output, and a summary of the
mutations applied to derive it from the base build.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from builds.build_definition import BuildDefinition


@dataclass
class OptimizationResult:
    """
    One entry in the ranked output of an optimization run.

    rank:               1-based position in the ranked list.
    build_variant:      The mutated BuildDefinition that achieved this rank.
    score:              Numeric score from the ScoringEngine (higher = better).
    simulation_output:  Full serialised EncounterRunResult dict.
    mutations_applied:  Human-readable list of mutations vs. the base build.
    """
    rank:              int
    build_variant:     BuildDefinition
    score:             float
    simulation_output: dict
    mutations_applied: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    @property
    def total_damage(self) -> float:
        return self.simulation_output.get("total_damage", 0.0)

    @property
    def dps(self) -> float:
        return self.simulation_output.get("dps", 0.0)

    @property
    def elapsed_time(self) -> float:
        return self.simulation_output.get("elapsed_time", 0.0)

    @property
    def all_enemies_dead(self) -> bool:
        return bool(self.simulation_output.get("all_enemies_dead", False))

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "rank":              self.rank,
            "score":             self.score,
            "build_variant":     self.build_variant.to_dict(),
            "simulation_output": self.simulation_output,
            "mutations_applied": list(self.mutations_applied),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "OptimizationResult":
        return cls(
            rank              = d["rank"],
            build_variant     = BuildDefinition.from_dict(d["build_variant"]),
            score             = float(d["score"]),
            simulation_output = dict(d["simulation_output"]),
            mutations_applied = list(d.get("mutations_applied", [])),
        )
