from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FormattedSeries:
    label: str
    x: list[float]
    y: list[float]
    unit: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class FormattedDataset:
    title: str
    series: list[FormattedSeries]
    x_label: str = "Time (s)"
    y_label: str = "Value"


class ResultFormatter:
    def normalize(self, data: list[float]) -> list[float]:
        if not data:
            return []
        lo = min(data)
        hi = max(data)
        if hi == lo:
            return list(data)
        span = hi - lo
        return [(v - lo) / span for v in data]

    def format_time_series(
        self,
        timestamps: list[float],
        values: list[float],
        label: str,
        unit: str = "",
    ) -> FormattedSeries:
        return FormattedSeries(label=label, x=list(timestamps), y=list(values), unit=unit)

    def format_multi_series(
        self,
        data: dict[str, tuple[list[float], list[float]]],
        title: str,
    ) -> FormattedDataset:
        series = [
            FormattedSeries(label=label, x=list(x_list), y=list(y_list))
            for label, (x_list, y_list) in data.items()
        ]
        return FormattedDataset(title=title, series=series)

    def aggregate_by_bucket(
        self,
        timestamps: list[float],
        values: list[float],
        bucket_size: float,
    ) -> tuple[list[float], list[float]]:
        if not timestamps or bucket_size <= 0:
            return [], []

        buckets: dict[int, list[float]] = {}
        for t, v in zip(timestamps, values):
            key = int(t / bucket_size)
            buckets.setdefault(key, []).append(v)

        bucket_centers: list[float] = []
        averages: list[float] = []
        for key in sorted(buckets):
            center = (key + 0.5) * bucket_size
            avg = sum(buckets[key]) / len(buckets[key])
            bucket_centers.append(center)
            averages.append(avg)

        return bucket_centers, averages

    def to_dict(self, dataset: FormattedDataset) -> dict:
        return {
            "title": dataset.title,
            "x_label": dataset.x_label,
            "y_label": dataset.y_label,
            "series": [
                {
                    "label": s.label,
                    "x": s.x,
                    "y": s.y,
                    "unit": s.unit,
                    "metadata": s.metadata,
                }
                for s in dataset.series
            ],
        }
