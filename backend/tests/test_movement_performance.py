"""
L — Movement performance tests (marked slow).
Verify the engine handles 100 entities at 60 ticks/sec within acceptable time.
"""
import time
import math
import pytest
from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.aggressive_behavior import AggressiveBehavior
from movement.behaviors.random_behavior import RandomBehavior
from movement.behaviors.orbit_behavior import OrbitBehavior
from movement.behaviors.defensive_behavior import DefensiveBehavior
from movement.timeline.movement_sync import MovementTimelineSynchronizer
from movement.pathfinding.navigation_grid import NavigationGrid
from movement.pathfinding.pathfinder import Pathfinder
from movement.distance.distance_tracker import DistanceTracker
from movement.collision.avoidance_engine import AvoidanceEngine
from movement.kiting.kiting_engine import KitingEngine
from services.movement_simulation_integration import (
    MovementSimulationIntegration, EntityConfig
)


pytestmark = pytest.mark.slow


class TestSyncPerformance:
    def test_100_aggressive_entities_10s(self):
        """100 entities × 600 ticks (10s @ 60Hz) completes under 5 seconds."""
        n = 100
        sync = MovementTimelineSynchronizer(tick_size=1 / 60, record_snapshots=False)
        states = {
            f"e{i}": MovementState(
                entity_id=f"e{i}",
                position=Vector2(i * 2.0, 0),
                max_speed=5.0,
                target_position=Vector2(0, 0),
            )
            for i in range(n)
        }
        behaviors = {f"e{i}": AggressiveBehavior(speed=5.0) for i in range(n)}

        start = time.perf_counter()
        sync.run(states, behaviors, duration=10.0)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Took {elapsed:.2f}s — too slow"

    def test_100_random_entities_5s(self):
        """100 random-behavior entities for 5s."""
        n = 100
        sync = MovementTimelineSynchronizer(tick_size=1 / 60, record_snapshots=False)
        states = {
            f"e{i}": MovementState(entity_id=f"e{i}", position=Vector2(i, 0), max_speed=3.0)
            for i in range(n)
        }
        behaviors = {f"e{i}": RandomBehavior(speed=3.0, seed=i) for i in range(n)}

        start = time.perf_counter()
        sync.run(states, behaviors, duration=5.0)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0

    def test_mixed_behaviors_100_entities_5s(self):
        """25 each of aggressive / defensive / orbit / random."""
        n_each = 25
        sync = MovementTimelineSynchronizer(tick_size=0.05, record_snapshots=False)
        states = {}
        behaviors = {}
        for i in range(n_each):
            for tag, beh in [
                ("agg", AggressiveBehavior(speed=5.0)),
                ("def", DefensiveBehavior()),
                ("orb", OrbitBehavior(orbit_radius=3.0)),
                ("rnd", RandomBehavior(speed=3.0, seed=i)),
            ]:
                eid = f"{tag}_{i}"
                states[eid] = MovementState(entity_id=eid, position=Vector2(i, 0), max_speed=5.0)
                behaviors[eid] = beh

        start = time.perf_counter()
        sync.run(states, behaviors, duration=5.0)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0


class TestPathfinderPerformance:
    def test_1000_astar_queries_on_20x20_grid(self):
        """1000 A* searches on a 20×20 grid complete in under 3 seconds."""
        grid = NavigationGrid(rows=20, cols=20, cell_size=1.0)
        # Add some obstacles
        for i in range(5, 15):
            grid.block_cell(10, i)
        pf = Pathfinder(grid)

        start = time.perf_counter()
        for _ in range(1000):
            pf.find_path_grid((0, 0), (19, 19))
        elapsed = time.perf_counter() - start
        assert elapsed < 3.0

    def test_pathfinder_50x50_grid(self):
        """Single A* on 50×50 grid completes quickly."""
        grid = NavigationGrid(rows=50, cols=50, cell_size=1.0)
        pf = Pathfinder(grid)
        start = time.perf_counter()
        result = pf.find_path_grid((0, 0), (49, 49))
        elapsed = time.perf_counter() - start
        assert result.found is True
        assert elapsed < 0.5


class TestAvoidancePerformance:
    def test_100_entity_avoidance(self):
        """Separation computation for 100 entities in under 1 second."""
        eng = AvoidanceEngine()
        positions = {f"e{i}": Vector2(i * 0.5, 0) for i in range(100)}
        start = time.perf_counter()
        for _ in range(100):
            eng.apply_separation_all(positions, avoidance_radius=2.0, max_speed=5.0)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0


class TestDistanceTrackerPerformance:
    def test_50_pairs_1000_updates(self):
        """50 tracked pairs × 1000 update calls in under 1 second."""
        tracker = DistanceTracker()
        n = 50
        for i in range(n):
            tracker.track_pair(f"a{i}", f"b{i}", threshold=5.0)

        positions = {}
        for i in range(n):
            positions[f"a{i}"] = Vector2(i, 0)
            positions[f"b{i}"] = Vector2(i + 3, 0)

        start = time.perf_counter()
        for t in range(1000):
            tracker.update(positions, now=t * 0.01)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0


class TestKitePerformance:
    def test_kite_10000_evaluations(self):
        """10,000 kite evaluations with 50 enemies in under 1 second."""
        engine = KitingEngine()
        player = Vector2(0, 0)
        enemies = [Vector2(i * 2, i * 0.5) for i in range(50)]
        start = time.perf_counter()
        for _ in range(10000):
            engine.evaluate(player, enemies)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0


class TestIntegrationPerformance:
    def test_50_entities_5s_integration(self):
        """Full integration run: 50 entities, 5 seconds, tick_size=0.05."""
        sim = MovementSimulationIntegration(tick_size=0.05)
        configs = [
            EntityConfig(
                entity_id=f"e{i}",
                start_pos=Vector2(i * 3, 0),
                max_speed=5.0,
                behavior=AggressiveBehavior(speed=4.0),
            )
            for i in range(50)
        ]
        start = time.perf_counter()
        result = sim.run_simulation(
            entity_configs=configs,
            player_start=Vector2(0, 0),
            duration=5.0,
        )
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"Took {elapsed:.2f}s"
        assert result.ticks_executed == 100

    def test_memory_stable_long_run(self):
        """Ensure no unbounded memory growth over 10s with record_snapshots=False."""
        import sys
        sync = MovementTimelineSynchronizer(tick_size=0.05, record_snapshots=False)
        n = 50
        states = {
            f"e{i}": MovementState(entity_id=f"e{i}", position=Vector2(i, 0), max_speed=5.0)
            for i in range(n)
        }
        behaviors = {f"e{i}": RandomBehavior(speed=3.0, seed=i) for i in range(n)}

        start = time.perf_counter()
        records = sync.run(states, behaviors, duration=10.0)
        elapsed = time.perf_counter() - start
        assert records == []   # no memory accumulated
        assert elapsed < 10.0
