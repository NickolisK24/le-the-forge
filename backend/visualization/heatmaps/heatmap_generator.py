from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HeatmapCell:
    row: int
    col: int
    value: float       # raw accumulated value
    normalized: float  # 0.0–1.0 relative to max


@dataclass
class HeatmapData:
    grid: list[list[float]]   # rows x cols raw values
    cells: list[HeatmapCell]  # flat list for chart rendering
    rows: int
    cols: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    max_value: float


class HeatmapGenerator:
    def __init__(self, rows: int = 20, cols: int = 20) -> None:
        self.rows = rows
        self.cols = cols

    def _world_to_cell(
        self,
        x: float,
        y: float,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> tuple[int, int]:
        x_range = x_max - x_min
        y_range = y_max - y_min

        if x_range == 0:
            col = 0
        else:
            col = int((x - x_min) / x_range * self.cols)

        if y_range == 0:
            row = 0
        else:
            row = int((y - y_min) / y_range * self.rows)

        col = max(0, min(self.cols - 1, col))
        row = max(0, min(self.rows - 1, row))
        return row, col

    def generate(
        self,
        points: list[tuple[float, float]],
        weights: list[float] | None = None,
    ) -> HeatmapData:
        if not points:
            empty_grid = [[0.0] * self.cols for _ in range(self.rows)]
            cells = [
                HeatmapCell(row=r, col=c, value=0.0, normalized=0.0)
                for r in range(self.rows)
                for c in range(self.cols)
            ]
            return HeatmapData(
                grid=empty_grid,
                cells=cells,
                rows=self.rows,
                cols=self.cols,
                x_min=0.0,
                x_max=0.0,
                y_min=0.0,
                y_max=0.0,
                max_value=0.0,
            )

        if weights is None:
            weights = [1.0] * len(points)

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        grid = [[0.0] * self.cols for _ in range(self.rows)]
        for (px, py), w in zip(points, weights):
            row, col = self._world_to_cell(px, py, x_min, x_max, y_min, y_max)
            grid[row][col] += w

        max_value = max(grid[r][c] for r in range(self.rows) for c in range(self.cols))

        cells: list[HeatmapCell] = []
        for r in range(self.rows):
            for c in range(self.cols):
                raw = grid[r][c]
                normalized = raw / max_value if max_value > 0 else 0.0
                cells.append(HeatmapCell(row=r, col=c, value=raw, normalized=normalized))

        return HeatmapData(
            grid=grid,
            cells=cells,
            rows=self.rows,
            cols=self.cols,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            max_value=max_value,
        )

    def generate_damage_density(
        self,
        hit_positions: list[tuple[float, float]],
        damages: list[float],
    ) -> HeatmapData:
        return self.generate(hit_positions, damages)

    def generate_target_clustering(
        self,
        target_positions: list[tuple[float, float]],
    ) -> HeatmapData:
        return self.generate(target_positions, weights=None)

    def apply_gaussian_blur(self, data: HeatmapData, sigma: float = 1.0) -> HeatmapData:
        # Simple 3x3 gaussian kernel (sigma parameter reserved for future extension)
        kernel = [
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1],
        ]
        kernel_sum = 16

        blurred = [[0.0] * data.cols for _ in range(data.rows)]
        for r in range(data.rows):
            for c in range(data.cols):
                total = 0.0
                weight_total = 0.0
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < data.rows and 0 <= nc < data.cols:
                            kw = kernel[dr + 1][dc + 1]
                            total += data.grid[nr][nc] * kw
                            weight_total += kw
                blurred[r][c] = total / weight_total if weight_total > 0 else 0.0

        max_value = max(
            blurred[r][c] for r in range(data.rows) for c in range(data.cols)
        )

        cells: list[HeatmapCell] = []
        for r in range(data.rows):
            for c in range(data.cols):
                raw = blurred[r][c]
                normalized = raw / max_value if max_value > 0 else 0.0
                cells.append(HeatmapCell(row=r, col=c, value=raw, normalized=normalized))

        return HeatmapData(
            grid=blurred,
            cells=cells,
            rows=data.rows,
            cols=data.cols,
            x_min=data.x_min,
            x_max=data.x_max,
            y_min=data.y_min,
            y_max=data.y_max,
            max_value=max_value,
        )
