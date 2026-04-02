"""G16 — Rotation regression tests: determinism and structural invariants."""
import pytest

from rotation.models.rotation_step import RotationStep
from rotation.models.rotation_definition import RotationDefinition
from rotation.rotation_executor import execute_rotation, CastResult
from rotation.metrics import compute_metrics
from skills.models.skill_definition import SkillDefinition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_skills():
    return {
        "fireball":  SkillDefinition("fireball",  base_damage=200.0, cooldown=1.0),
        "frostbolt": SkillDefinition("frostbolt", base_damage=150.0, cooldown=1.5),
        "lightning": SkillDefinition("lightning", base_damage=100.0, cooldown=0.5),
    }


def _make_rotation(loop=True):
    rot = RotationDefinition("reg_test")
    rot.add_step(RotationStep("fireball",  priority=0))
    rot.add_step(RotationStep("frostbolt", priority=1))
    rot.add_step(RotationStep("lightning", priority=2))
    rot.loop = loop
    return rot


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_input_same_output(self):
        """Identical inputs always produce identical cast lists."""
        skills = _make_skills()
        rot    = _make_rotation()
        r1 = execute_rotation(rot, skills, duration=10.0)
        r2 = execute_rotation(rot, skills, duration=10.0)
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.skill_id    == b.skill_id
            assert a.cast_at     == pytest.approx(b.cast_at,     abs=1e-9)
            assert a.resolves_at == pytest.approx(b.resolves_at, abs=1e-9)
            assert a.damage      == pytest.approx(b.damage,      abs=1e-9)

    def test_determinism_with_gcd(self):
        """GCD does not introduce non-determinism."""
        skills = _make_skills()
        rot    = _make_rotation()
        r1 = execute_rotation(rot, skills, duration=15.0, gcd=0.5)
        r2 = execute_rotation(rot, skills, duration=15.0, gcd=0.5)
        assert [c.skill_id for c in r1] == [c.skill_id for c in r2]

    def test_different_durations_prefix_identical(self):
        """Casts in a shorter run are a prefix of the longer run's cast list."""
        skills = _make_skills()
        rot    = _make_rotation()
        short = execute_rotation(rot, skills, duration=5.0)
        long_ = execute_rotation(rot, skills, duration=10.0)
        # Every cast in the short run should appear identically in the long run
        assert len(short) <= len(long_)
        for i, c in enumerate(short):
            assert c.skill_id == long_[i].skill_id
            assert c.cast_at  == pytest.approx(long_[i].cast_at, abs=1e-9)


# ---------------------------------------------------------------------------
# Structural invariants
# ---------------------------------------------------------------------------

class TestStructuralInvariants:
    def test_cast_times_non_decreasing(self):
        """All cast_at timestamps must be non-decreasing."""
        results = execute_rotation(_make_rotation(), _make_skills(), duration=20.0)
        for i in range(1, len(results)):
            assert results[i].cast_at >= results[i - 1].cast_at - 1e-9

    def test_resolves_at_after_cast_at(self):
        """resolves_at >= cast_at for every cast."""
        results = execute_rotation(_make_rotation(), _make_skills(), duration=20.0)
        for c in results:
            assert c.resolves_at >= c.cast_at - 1e-9

    def test_no_casts_beyond_duration(self):
        """No cast starts at or after the fight duration."""
        duration = 10.0
        results = execute_rotation(_make_rotation(), _make_skills(), duration=duration)
        for c in results:
            assert c.cast_at < duration + 1e-9

    def test_cast_at_zero_or_positive(self):
        """First cast must be at time >= 0."""
        results = execute_rotation(_make_rotation(), _make_skills(), duration=5.0)
        assert results[0].cast_at >= 0.0

    def test_damage_non_negative(self):
        """All damage values are non-negative."""
        results = execute_rotation(_make_rotation(), _make_skills(), duration=20.0)
        for c in results:
            assert c.damage >= 0.0

    def test_skill_ids_from_rotation(self):
        """Only skill IDs present in the rotation appear in results."""
        rot    = _make_rotation()
        skills = _make_skills()
        valid  = set(rot.skill_ids())
        results = execute_rotation(rot, skills, duration=10.0)
        for c in results:
            assert c.skill_id in valid

    def test_no_cooldown_violation(self):
        """No skill is cast before its cooldown expires."""
        skills = _make_skills()
        rot    = _make_rotation()
        results = execute_rotation(rot, skills, duration=30.0)
        last_cast: dict[str, float] = {}
        for c in results:
            cd = skills[c.skill_id].cooldown
            if c.skill_id in last_cast:
                gap = c.cast_at - last_cast[c.skill_id]
                assert gap >= cd - 1e-6, (
                    f"{c.skill_id} cast too soon: gap={gap:.4f} < cd={cd}"
                )
            last_cast[c.skill_id] = c.cast_at

    def test_gcd_respected(self):
        """No two consecutive casts happen with less than gcd seconds between them."""
        gcd    = 1.0
        results = execute_rotation(_make_rotation(), _make_skills(), duration=20.0, gcd=gcd)
        for i in range(1, len(results)):
            gap = results[i].cast_at - results[i - 1].cast_at
            assert gap >= gcd - 1e-6, f"GCD violated at cast {i}: gap={gap:.4f}"


# ---------------------------------------------------------------------------
# Metrics invariants
# ---------------------------------------------------------------------------

class TestMetricsInvariants:
    def test_metrics_total_damage_matches_sum(self):
        """metrics.total_damage == sum of individual cast damages."""
        results = execute_rotation(_make_rotation(), _make_skills(), duration=10.0)
        m = compute_metrics(results, 10.0)
        assert m.total_damage == pytest.approx(sum(c.damage for c in results), rel=1e-6)

    def test_metrics_total_casts_matches_list_length(self):
        results = execute_rotation(_make_rotation(), _make_skills(), duration=10.0)
        m = compute_metrics(results, 10.0)
        assert m.total_casts == len(results)

    def test_uptime_fraction_in_range(self):
        results = execute_rotation(_make_rotation(), _make_skills(), duration=10.0)
        m = compute_metrics(results, 10.0)
        assert 0.0 <= m.uptime_fraction <= 1.0

    def test_efficiency_in_range(self):
        results = execute_rotation(_make_rotation(), _make_skills(), duration=10.0)
        m = compute_metrics(results, 10.0)
        assert 0.0 <= m.efficiency <= 1.0

    def test_damage_by_skill_sums_to_total(self):
        results = execute_rotation(_make_rotation(), _make_skills(), duration=10.0)
        m = compute_metrics(results, 10.0)
        assert sum(m.damage_by_skill.values()) == pytest.approx(m.total_damage, rel=1e-6)

    def test_cast_counts_sum_to_total(self):
        results = execute_rotation(_make_rotation(), _make_skills(), duration=10.0)
        m = compute_metrics(results, 10.0)
        assert sum(m.cast_counts.values()) == m.total_casts
