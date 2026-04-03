"""L10 — NavigationGrid tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.pathfinding.navigation_grid import NavigationGrid


def _grid(rows: int = 5, cols: int = 5, cell_size: float = 1.0) -> NavigationGrid:
    return NavigationGrid(rows=rows, cols=cols, cell_size=cell_size)


class TestConstruction:
    def test_all_walkable_by_default(self):
        g = _grid(3, 3)
        assert g.walkable_count() == 9

    def test_zero_rows_raises(self):
        with pytest.raises(ValueError):
            NavigationGrid(rows=0, cols=5)

    def test_zero_cell_size_raises(self):
        with pytest.raises(ValueError):
            NavigationGrid(rows=5, cols=5, cell_size=0.0)

    def test_valid_cell(self):
        g = _grid()
        assert g.is_valid(0, 0) is True
        assert g.is_valid(4, 4) is True
        assert g.is_valid(5, 0) is False


class TestWalkability:
    def test_block_cell(self):
        g = _grid()
        g.block_cell(2, 2)
        assert g.is_walkable(2, 2) is False

    def test_clear_cell(self):
        g = _grid()
        g.block_cell(1, 1)
        g.clear_cell(1, 1)
        assert g.is_walkable(1, 1) is True

    def test_block_rect(self):
        g = _grid(10, 10)
        g.block_rect(2, 2, 3, 3)
        # Check some cells in the blocked rect
        assert g.is_walkable(2, 2) is False
        assert g.is_walkable(4, 4) is False
        assert g.is_walkable(5, 5) is True

    def test_out_of_bounds_not_walkable(self):
        g = _grid()
        assert g.is_walkable(-1, 0) is False
        assert g.is_walkable(0, 10) is False

    def test_set_walkable_out_of_bounds_raises(self):
        g = _grid()
        with pytest.raises(IndexError):
            g.set_walkable(10, 10, False)


class TestCoordinateConversion:
    def test_world_to_grid_origin(self):
        g = NavigationGrid(rows=5, cols=5, cell_size=1.0, origin=Vector2(0, 0))
        assert g.world_to_grid(Vector2(0.5, 0.5)) == (0, 0)

    def test_world_to_grid_offset(self):
        g = NavigationGrid(rows=5, cols=5, cell_size=1.0, origin=Vector2(0, 0))
        assert g.world_to_grid(Vector2(1.5, 2.5)) == (2, 1)

    def test_grid_to_world_center(self):
        g = NavigationGrid(rows=5, cols=5, cell_size=1.0, origin=Vector2(0, 0))
        pos = g.grid_to_world(0, 0)
        assert pos.x == pytest.approx(0.5)
        assert pos.y == pytest.approx(0.5)

    def test_world_to_grid_clamped(self):
        g = _grid()
        row, col = g.world_to_grid(Vector2(-5, -5))
        assert row == 0 and col == 0


class TestNeighbors:
    def test_cardinal_neighbors_center(self):
        g = _grid(3, 3)
        n = g.neighbors(1, 1, allow_diagonal=False)
        assert len(n) == 4

    def test_eight_dir_neighbors_center(self):
        g = _grid(3, 3)
        n = g.neighbors(1, 1, allow_diagonal=True)
        assert len(n) == 8

    def test_corner_fewer_neighbors(self):
        g = _grid(5, 5)
        n = g.neighbors(0, 0, allow_diagonal=True)
        assert len(n) == 3  # right, down, diagonal

    def test_blocked_neighbor_excluded(self):
        g = _grid(3, 3)
        g.block_cell(0, 1)
        n = g.neighbors(0, 0, allow_diagonal=False)
        assert (0, 1) not in n

    def test_to_dict(self):
        d = _grid().to_dict()
        assert "rows" in d and "cols" in d and "walkable_count" in d
