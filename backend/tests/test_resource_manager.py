"""G9 — ResourceManager tests"""
import pytest
from rotation.resource_manager import ResourceManager


class TestResourceDepletion:
    def test_full_on_init(self):
        r = ResourceManager(maximum=100.0)
        assert r.current == 100.0

    def test_custom_initial(self):
        r = ResourceManager(maximum=100.0, initial=50.0)
        assert r.current == 50.0

    def test_initial_clamped_to_max(self):
        r = ResourceManager(maximum=100.0, initial=200.0)
        assert r.current == 100.0

    def test_initial_clamped_to_zero(self):
        r = ResourceManager(maximum=100.0, initial=-10.0)
        assert r.current == 0.0

    def test_spend_succeeds(self):
        r = ResourceManager(maximum=100.0)
        assert r.spend(30.0) is True
        assert r.current == pytest.approx(70.0)

    def test_spend_exact(self):
        r = ResourceManager(maximum=100.0)
        assert r.spend(100.0) is True
        assert r.current == pytest.approx(0.0)

    def test_spend_fails_insufficient(self):
        r = ResourceManager(maximum=100.0, initial=20.0)
        assert r.spend(30.0) is False
        assert r.current == pytest.approx(20.0)  # unchanged

    def test_spend_fails_empty(self):
        r = ResourceManager(maximum=100.0, initial=0.0)
        assert r.spend(1.0) is False

    def test_can_afford_true(self):
        r = ResourceManager(maximum=100.0)
        assert r.can_afford(50.0)

    def test_can_afford_false(self):
        r = ResourceManager(maximum=50.0)
        assert not r.can_afford(51.0)

    def test_is_empty(self):
        r = ResourceManager(maximum=100.0, initial=0.0)
        assert r.is_empty


class TestResourceRecovery:
    def test_restore_adds_amount(self):
        r = ResourceManager(maximum=100.0, initial=0.0)
        r.restore(40.0)
        assert r.current == pytest.approx(40.0)

    def test_restore_clamped_at_max(self):
        r = ResourceManager(maximum=100.0)
        r.restore(50.0)
        assert r.current == pytest.approx(100.0)

    def test_tick_regenerates(self):
        r = ResourceManager(maximum=100.0, initial=0.0, regen_per_sec=10.0)
        r.tick(3.0)
        assert r.current == pytest.approx(30.0)

    def test_tick_capped_at_max(self):
        r = ResourceManager(maximum=100.0, initial=90.0, regen_per_sec=10.0)
        r.tick(5.0)
        assert r.current == pytest.approx(100.0)

    def test_tick_zero_elapsed(self):
        r = ResourceManager(maximum=100.0, initial=50.0, regen_per_sec=10.0)
        r.tick(0.0)
        assert r.current == pytest.approx(50.0)


class TestSkillBlockOnZeroResource:
    def test_zero_cost_always_succeeds(self):
        r = ResourceManager(maximum=100.0, initial=0.0)
        assert r.spend(0.0) is True

    def test_sequence_depletes_then_blocks(self):
        r = ResourceManager(maximum=100.0)
        assert r.spend(40.0) is True
        assert r.spend(40.0) is True
        assert r.spend(40.0) is False  # only 20 left

    def test_regen_then_afford(self):
        r = ResourceManager(maximum=100.0, initial=0.0, regen_per_sec=10.0)
        assert not r.can_afford(30.0)
        r.tick(3.0)
        assert r.can_afford(30.0)

    def test_invalid_max_raises(self):
        with pytest.raises(ValueError):
            ResourceManager(maximum=0.0)

    def test_negative_regen_raises(self):
        with pytest.raises(ValueError):
            ResourceManager(maximum=100.0, regen_per_sec=-1.0)
