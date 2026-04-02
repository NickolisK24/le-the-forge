"""Tests for spawn controller (Step 103)."""

import pytest
from encounter.enemy import EncounterEnemy
from encounter.spawn_controller import SpawnController, SpawnWave


def _enemy(health=100.0, name="add"):
    return EncounterEnemy(max_health=health, current_health=health,
                          armor=0.0, name=name)

def _wave(t, n=1, name="wave"):
    return SpawnWave(name=name, spawn_time=t,
                     enemies=[_enemy(name=f"{name}_e{i}") for i in range(n)])


class TestSpawnWave:
    def test_negative_spawn_time_raises(self):
        with pytest.raises(ValueError):
            SpawnWave("w", spawn_time=-1.0)

    def test_basic_construction(self):
        w = _wave(5.0, n=2)
        assert w.spawn_time == pytest.approx(5.0)
        assert len(w.enemies) == 2
        assert w.spawned is False


class TestSpawnController:
    def test_empty_tick_returns_empty(self):
        sc = SpawnController()
        assert sc.tick(100.0) == []

    def test_wave_fires_at_correct_time(self):
        sc = SpawnController([_wave(10.0, n=2)])
        assert sc.tick(9.9) == []
        spawned = sc.tick(10.0)
        assert len(spawned) == 2

    def test_wave_fires_only_once(self):
        sc = SpawnController([_wave(5.0, n=1)])
        sc.tick(5.0)
        assert sc.tick(10.0) == []

    def test_multiple_waves_fire_in_order(self):
        sc = SpawnController([_wave(10.0, n=2, name="w1"),
                               _wave(20.0, n=3, name="w2")])
        first  = sc.tick(10.0)
        second = sc.tick(20.0)
        assert len(first)  == 2
        assert len(second) == 3

    def test_all_waves_fire_at_once_when_past(self):
        sc = SpawnController([_wave(1.0, n=1), _wave(2.0, n=1), _wave(3.0, n=1)])
        spawned = sc.tick(5.0)
        assert len(spawned) == 3

    def test_enemy_reset_on_spawn(self):
        e = _enemy(health=100.0)
        e.apply_damage(80.0)  # damage before spawn
        wave = SpawnWave("w", spawn_time=5.0, enemies=[e])
        sc = SpawnController([wave])
        spawned = sc.tick(5.0)
        # reset() should have restored health
        assert spawned[0].current_health == pytest.approx(100.0)

    def test_pending_waves(self):
        sc = SpawnController([_wave(5.0), _wave(10.0)])
        sc.tick(5.0)
        assert len(sc.pending_waves()) == 1

    def test_spawned_waves(self):
        sc = SpawnController([_wave(5.0), _wave(10.0)])
        sc.tick(5.0)
        assert len(sc.spawned_waves()) == 1

    def test_add_wave(self):
        sc = SpawnController()
        sc.add_wave(_wave(3.0, n=2))
        assert sc.wave_count() == 1
        assert len(sc.tick(3.0)) == 2

    def test_add_wave_sorted(self):
        sc = SpawnController([_wave(10.0, name="late")])
        sc.add_wave(_wave(5.0, n=2, name="early"))
        assert sc._waves[0].name == "early"

    def test_reset_allows_respawn(self):
        sc = SpawnController([_wave(5.0, n=1)])
        sc.tick(5.0)
        sc.reset()
        spawned = sc.tick(5.0)
        assert len(spawned) == 1

    def test_wave_count(self):
        sc = SpawnController([_wave(1.0), _wave(2.0), _wave(3.0)])
        assert sc.wave_count() == 3
