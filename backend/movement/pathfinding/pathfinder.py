"""
L9 — A* Pathfinding Engine

Implements A* search on a NavigationGrid to find the shortest walkable path
between two world-space positions. Returns a list of Vector2 waypoints from
start to goal (exclusive of start, inclusive of goal).

Heuristic: octile distance (accurate for 8-directional grids).
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Optional

from spatial.models.vector2 import Vector2
from movement.pathfinding.navigation_grid import NavigationGrid


# ---------------------------------------------------------------------------
# Internal node type
# ---------------------------------------------------------------------------

@dataclass(order=True)
class _Node:
    f:      float
    g:      float = field(compare=False)
    row:    int   = field(compare=False)
    col:    int   = field(compare=False)
    parent: Optional["_Node"] = field(compare=False, default=None)


# ---------------------------------------------------------------------------
# Heuristics
# ---------------------------------------------------------------------------

def _octile(r1: int, c1: int, r2: int, c2: int) -> float:
    """Octile distance — optimal heuristic for 8-directional grids."""
    dr = abs(r1 - r2)
    dc = abs(c1 - c2)
    return max(dr, dc) + (math.sqrt(2) - 1) * min(dr, dc)


def _manhattan(r1: int, c1: int, r2: int, c2: int) -> float:
    return float(abs(r1 - r2) + abs(c1 - c2))


# ---------------------------------------------------------------------------
# Pathfinder
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PathResult:
    """Result of an A* search."""

    found:     bool
    waypoints: list[Vector2]   # world-space path (start excluded, goal included)
    length:    float           # total path length in world-units
    nodes_explored: int        # number of nodes popped from open list


class Pathfinder:
    """
    A* pathfinder operating on a NavigationGrid.

    find_path(start, goal)  → PathResult
    find_path_grid(start_cell, goal_cell) → PathResult
    """

    def __init__(
        self,
        grid: NavigationGrid,
        allow_diagonal: bool = True,
        heuristic: str = "octile",
    ) -> None:
        self._grid = grid
        self._allow_diagonal = allow_diagonal
        self._h = _octile if heuristic == "octile" else _manhattan

    def find_path(self, start: Vector2, goal: Vector2) -> PathResult:
        """Find a path from world-space *start* to *goal*."""
        start_cell = self._grid.world_to_grid(start)
        goal_cell = self._grid.world_to_grid(goal)
        return self.find_path_grid(start_cell, goal_cell)

    def find_path_grid(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> PathResult:
        """Find a path from grid cell *start* to *goal*."""
        sr, sc = start
        gr, gc = goal

        if not self._grid.is_walkable(sr, sc):
            return PathResult(found=False, waypoints=[], length=0.0, nodes_explored=0)
        if not self._grid.is_walkable(gr, gc):
            return PathResult(found=False, waypoints=[], length=0.0, nodes_explored=0)

        if start == goal:
            return PathResult(
                found=True,
                waypoints=[self._grid.grid_to_world(gr, gc)],
                length=0.0,
                nodes_explored=0,
            )

        open_heap: list[_Node] = []
        open_map: dict[tuple[int, int], float] = {}   # cell → best g
        closed: set[tuple[int, int]] = set()
        nodes_explored = 0

        start_node = _Node(
            f=self._h(sr, sc, gr, gc),
            g=0.0,
            row=sr,
            col=sc,
        )
        heapq.heappush(open_heap, start_node)
        open_map[(sr, sc)] = 0.0

        while open_heap:
            current = heapq.heappop(open_heap)
            cr, cc = current.row, current.col
            cell = (cr, cc)
            nodes_explored += 1

            if cell in closed:
                continue
            closed.add(cell)

            if cell == (gr, gc):
                return self._reconstruct(current, nodes_explored)

            for nr, nc in self._grid.neighbors(cr, cc, self._allow_diagonal):
                if (nr, nc) in closed:
                    continue
                # Step cost: sqrt(2) for diagonal, 1 for cardinal
                step_cost = math.sqrt(2) if (nr != cr and nc != cc) else 1.0
                new_g = current.g + step_cost
                if open_map.get((nr, nc), float("inf")) <= new_g:
                    continue
                h = self._h(nr, nc, gr, gc)
                node = _Node(f=new_g + h, g=new_g, row=nr, col=nc, parent=current)
                heapq.heappush(open_heap, node)
                open_map[(nr, nc)] = new_g

        return PathResult(found=False, waypoints=[], length=0.0, nodes_explored=nodes_explored)

    def _reconstruct(self, goal_node: _Node, nodes_explored: int) -> PathResult:
        """Walk back through parent pointers to build the waypoint list."""
        path: list[_Node] = []
        n: _Node | None = goal_node
        while n is not None:
            path.append(n)
            n = n.parent
        path.reverse()

        waypoints = [self._grid.grid_to_world(n.row, n.col) for n in path[1:]]  # skip start
        # Ensure goal world point is the last waypoint
        if not waypoints:
            waypoints = [self._grid.grid_to_world(goal_node.row, goal_node.col)]

        # Compute total length
        length = sum(
            waypoints[i].distance_to(waypoints[i - 1])
            for i in range(1, len(waypoints))
        )
        if len(waypoints) >= 1:
            # Add distance from start cell center to first waypoint
            start_world = self._grid.grid_to_world(path[0].row, path[0].col)
            if waypoints:
                length += start_world.distance_to(waypoints[0])

        return PathResult(
            found=True,
            waypoints=waypoints,
            length=length,
            nodes_explored=nodes_explored,
        )
