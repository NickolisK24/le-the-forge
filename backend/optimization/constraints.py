"""
F3 — Constraint Engine

Validates that a build variant satisfies all configured rules before
it is submitted to the simulation batch.  Returning a failed check early
avoids wasted simulation cycles.

Built-in constraints
--------------------
min_health          float   stats.max_health >= value
max_passive_nodes   int     len(build.passive_ids) <= value
required_skill      str     build.skill_id == value
min_base_damage     float   compile_params["base_damage"] >= value
max_buffs           int     len(build.buffs) <= value
"""

from __future__ import annotations
from dataclasses import dataclass

from builds.build_definition import BuildDefinition


@dataclass
class ConstraintViolation:
    rule:    str
    message: str


class ConstraintEngine:
    """
    Validates a build against the constraint rules in an OptimizationConfig.

    Usage
    -----
    engine   = ConstraintEngine(config.constraints)
    ok, msgs = engine.check(build, stats, encounter_params)
    """

    def __init__(self, constraints: dict | None = None) -> None:
        self._rules = dict(constraints or {})

    def check(
        self,
        build: BuildDefinition,
        stats,                      # BuildStats from stat_engine
        encounter_params: dict | None = None,
    ) -> tuple[bool, list[ConstraintViolation]]:
        """
        Returns (passed, violations).

        Stops at the first violation for each rule but collects all.
        """
        violations: list[ConstraintViolation] = []

        for rule, threshold in self._rules.items():
            v = self._evaluate(rule, threshold, build, stats, encounter_params or {})
            if v is not None:
                violations.append(v)

        return (len(violations) == 0, violations)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _evaluate(
        self,
        rule: str,
        threshold,
        build: BuildDefinition,
        stats,
        enc_params: dict,
    ) -> ConstraintViolation | None:
        if rule == "min_health":
            if stats.max_health < float(threshold):
                return ConstraintViolation(
                    rule, f"max_health {stats.max_health:.1f} < {threshold}"
                )

        elif rule == "max_passive_nodes":
            if len(build.passive_ids) > int(threshold):
                return ConstraintViolation(
                    rule, f"passive_ids count {len(build.passive_ids)} > {threshold}"
                )

        elif rule == "required_skill":
            if build.skill_id != str(threshold):
                return ConstraintViolation(
                    rule, f"skill_id '{build.skill_id}' != '{threshold}'"
                )

        elif rule == "min_base_damage":
            bd = enc_params.get("base_damage", 0.0)
            if bd < float(threshold):
                return ConstraintViolation(
                    rule, f"effective base_damage {bd:.1f} < {threshold}"
                )

        elif rule == "max_buffs":
            if len(build.buffs) > int(threshold):
                return ConstraintViolation(
                    rule, f"buff count {len(build.buffs)} > {threshold}"
                )

        # Unknown rules are silently ignored (forward-compatible)
        return None
