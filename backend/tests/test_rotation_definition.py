"""G3 — RotationDefinition tests"""
import pytest
from rotation.models.rotation_step import RotationStep
from rotation.models.rotation_definition import RotationDefinition


def _step(skill_id, **kw):
    return RotationStep(skill_id=skill_id, **kw)


class TestRotationDefinitionCreation:
    def test_empty(self):
        r = RotationDefinition(rotation_id="test")
        assert r.rotation_id == "test"
        assert r.steps == []
        assert r.loop is True
        assert r.is_empty()

    def test_with_steps(self):
        r = RotationDefinition(
            rotation_id="basic",
            steps=[_step("a"), _step("b"), _step("c")],
        )
        assert len(r.steps) == 3
        assert not r.is_empty()

    def test_empty_rotation_id_raises(self):
        with pytest.raises(ValueError, match="rotation_id"):
            RotationDefinition(rotation_id="")

    def test_loop_false(self):
        r = RotationDefinition(rotation_id="x", loop=False)
        assert r.loop is False


class TestRotationDefinitionStepOrdering:
    def test_add_step_appends(self):
        r = RotationDefinition(rotation_id="r")
        r.add_step(_step("a"))
        r.add_step(_step("b"))
        assert r.skill_ids() == ["a", "b"]

    def test_steps_maintain_insertion_order(self):
        steps = [_step("x"), _step("y"), _step("z")]
        r = RotationDefinition(rotation_id="r", steps=steps)
        assert r.skill_ids() == ["x", "y", "z"]

    def test_skill_ids(self):
        r = RotationDefinition(rotation_id="r", steps=[_step("a"), _step("b"), _step("a")])
        assert r.skill_ids() == ["a", "b", "a"]

    def test_unique_skill_ids(self):
        r = RotationDefinition(rotation_id="r", steps=[_step("a"), _step("b"), _step("a")])
        assert r.unique_skill_ids() == {"a", "b"}


class TestRotationDefinitionLoopIntegrity:
    def test_default_loop_true(self):
        r = RotationDefinition(rotation_id="r")
        assert r.loop is True

    def test_no_loop(self):
        r = RotationDefinition(rotation_id="r", loop=False)
        assert not r.loop


class TestRotationDefinitionSerialisation:
    def test_roundtrip(self):
        original = RotationDefinition(
            rotation_id="combo",
            steps=[_step("a", priority=1), _step("b", repeat_count=2)],
            loop=False,
        )
        restored = RotationDefinition.from_dict(original.to_dict())
        assert restored.rotation_id == original.rotation_id
        assert restored.loop        == original.loop
        assert len(restored.steps)  == len(original.steps)
        assert restored.steps[0].skill_id    == "a"
        assert restored.steps[0].priority    == 1
        assert restored.steps[1].repeat_count == 2

    def test_from_dict_defaults(self):
        r = RotationDefinition.from_dict({"rotation_id": "x"})
        assert r.steps == []
        assert r.loop is True
