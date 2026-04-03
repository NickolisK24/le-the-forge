"""
L10 — Navigation Grid

Represents a 2D tile map for pathfinding. Each cell is either walkable or
blocked. Provides coordinate conversion between world-space (Vector2) and
grid-space (row, col) integer tuples.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2


@dataclass
class NavigationGrid:
    """
    Uniform-tile navigation grid.

    rows       — number of rows (y axis)
    cols       — number of columns (x axis)
    cell_size  — world-unit size of each cell (default 1.0)
    origin     — world-space position of the top-left corner of cell (0, 0)

    Coordinate mapping:
        world x ↔ col  (increases right)
        world y ↔ row  (increases down)
    """

    rows:      int
    cols:      int
    cell_size: float  = 1.0
    origin:    Vector2 = field(default_factory=Vector2.zero)

    # Internal: True = walkable, False = blocked
    _cells: list[list[bool]] = field(default=None, init=False, repr=False)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("rows and cols must be > 0")
        if self.cell_size <= 0:
            raise ValueError("cell_size must be > 0")
        self._cells = [[True] * self.cols for _ in range(self.rows)]

    # ------------------------------------------------------------------
    # Cell access
    # ------------------------------------------------------------------

    def is_valid(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_walkable(self, row: int, col: int) -> bool:
        if not self.is_valid(row, col):
            return False
        return self._cells[row][col]

    def set_walkable(self, row: int, col: int, walkable: bool) -> None:
        if not self.is_valid(row, col):
            raise IndexError(f"Cell ({row}, {col}) is out of grid bounds")
        self._cells[row][col] = walkable

    def block_cell(self, row: int, col: int) -> None:
        self.set_walkable(row, col, False)

    def clear_cell(self, row: int, col: int) -> None:
        self.set_walkable(row, col, True)

    def block_rect(self, row: int, col: int, height: int, width: int) -> None:
        """Block a rectangular region."""
        for r in range(row, row + height):
            for c in range(col, col + width):
                if self.is_valid(r, c):
                    self._cells[r][c] = False

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def world_to_grid(self, pos: Vector2) -> tuple[int, int]:
        """
        Convert a world-space Vector2 to the nearest (row, col) cell index.
        Clamps to valid grid range.
        """
        col = int((pos.x - self.origin.x) / self.cell_size)
        row = int((pos.y - self.origin.y) / self.cell_size)
        row = max(0, min(self.rows - 1, row))
        col = max(0, min(self.cols - 1, col))
        return (row, col)

    def grid_to_world(self, row: int, col: int) -> Vector2:
        """
        Return the world-space center of cell (row, col).
        """
        x = self.origin.x + col * self.cell_size + self.cell_size / 2.0
        y = self.origin.y + row * self.cell_size + self.cell_size / 2.0
        return Vector2(x, y)

    # ------------------------------------------------------------------
    # Neighbor enumeration
    # ------------------------------------------------------------------

    def neighbors(
        self, row: int, col: int, allow_diagonal: bool = True
    ) -> list[tuple[int, int]]:
        """
        Return valid, walkable neighbors of (row, col).

        allow_diagonal — if True, include 8-directional neighbors; else 4.
        """
        cardinal = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        diagonal = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        directions = cardinal + (diagonal if allow_diagonal else [])
        result = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if self.is_walkable(nr, nc):
                result.append((nr, nc))
        return result

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def walkable_count(self) -> int:
        return sum(self._cells[r][c] for r in range(self.rows) for c in range(self.cols))

    def to_dict(self) -> dict:
        return {
            "rows":      self.rows,
            "cols":      self.cols,
            "cell_size": self.cell_size,
            "origin":    self.origin.to_tuple(),
            "walkable_count": self.walkable_count(),
        }
