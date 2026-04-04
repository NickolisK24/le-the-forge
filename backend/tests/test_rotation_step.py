"""G2 — RotationStep tests"""
import pytest
from rotation.models.rotation_step import RotationStep


class TestRotationStepCreation:
    def test_minimal(self):
        s = RotationStep(skill_id="fireball")
        assert s.skill_id == "fireball"
        assert s.delay_after_cast == 0.0
        assert s.priority == 0
        assert s.repeat_count == 1

    def test_full(self):
        s = RotationStep(skill_id="blast", delay_after_cast=0.5, priority=1, repeat_count=3)
        assert s.delay_after_cast == 0.5
        assert s.priority == 1
        assert s.repeat_count == 3


class TestRotationStepValidation:
    def test_empty_skill_id_raises(self):
        with pytest.raises(ValueError, match="skill_id"):
            RotationStep(skill_id="")

    def test_negative_delay_raises(self):
        with pytest.raises(ValueError, match="delay_after_cast"):
            RotationStep(skill_id="x", delay_after_cast=-0.1)

    def test_zero_repeat_count_raises(self):
        with pytest.raises(ValueError, match="repeat_count"):
            RotationStep(skill_id="x", repeat_count=0)

    def test_negative_repeat_count_raises(self):
        with pytest.raises(ValueError, match="repeat_count"):
            RotationStep(skill_id="x", repeat_count=-1)


class TestRotationStepPriority:
    def test_lower_priority_value_sorts_first(self):
        steps = [
            RotationStep(skill_id="c", priority=5),
            RotationStep(skill_id="a", priority=0),
            RotationStep(skill_id="b", priority=2),
        ]
        ordered = sorted(steps, key=lambda s: s.priority)
        assert [s.skill_id for s in ordered] == ["a", "b", "c"]

    def test_default_priority_zero(self):
        assert RotationStep(skill_id="x").priority == 0


class TestRotationStepRepeat:
    def test_repeat_count_one_default(self):
        assert RotationStep(skill_id="x").repeat_count == 1

    def test_repeat_count_many(self):
        s = RotationStep(skill_id="x", repeat_count=5)
        assert s.repeat_count == 5


class TestRotationStepSerialisation:
    def test_roundtrip(self):
        original = RotationStep(skill_id="shot", delay_after_cast=0.2, priority=3, repeat_count=2)
        restored = RotationStep.from_dict(original.to_dict())
        assert restored.skill_id         == original.skill_id
        assert restored.delay_after_cast == original.delay_after_cast
        assert restored.priority         == original.priority
        assert restored.repeat_count     == original.repeat_count

    def test_from_dict_defaults(self):
        s = RotationStep.from_dict({"skill_id": "x"})
        assert s.delay_after_cast == 0.0
        assert s.priority == 0
        assert s.repeat_count == 1
