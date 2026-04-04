from __future__ import annotations

from dataclasses import dataclass, field

from visualization.formatters.result_formatter import FormattedSeries


@dataclass
class TimelineEvent:
    time: float
    event_type: str  # "damage", "buff_applied", "buff_expired", "movement", "kill"
    source: str
    value: float
    metadata: dict = field(default_factory=dict)


@dataclass
class TimelineDataset:
    events: list[TimelineEvent]
    duration: float
    tick_size: float


class TimelineGenerator:
    def __init__(self, tick_size: float = 0.1) -> None:
        self.tick_size = tick_size

    def add_event(self, dataset: TimelineDataset, event: TimelineEvent) -> None:
        dataset.events.append(event)
        dataset.events.sort(key=lambda e: e.time)

    def generate_damage_timeline(self, damage_events: list[dict]) -> TimelineDataset:
        events: list[TimelineEvent] = []
        for ev in damage_events:
            events.append(
                TimelineEvent(
                    time=float(ev["time"]),
                    event_type="damage",
                    source=str(ev["source"]),
                    value=float(ev["amount"]),
                )
            )
        events.sort(key=lambda e: e.time)
        duration = events[-1].time if events else 0.0
        return TimelineDataset(events=events, duration=duration, tick_size=self.tick_size)

    def generate_buff_timeline(self, buff_events: list[dict]) -> TimelineDataset:
        events: list[TimelineEvent] = []
        for ev in buff_events:
            raw_event = str(ev["event"])
            event_type = "buff_applied" if raw_event == "applied" else "buff_expired"
            events.append(
                TimelineEvent(
                    time=float(ev["time"]),
                    event_type=event_type,
                    source=str(ev["buff_name"]),
                    value=float(ev.get("duration", 0.0)),
                    metadata={"buff_name": ev["buff_name"]},
                )
            )
        events.sort(key=lambda e: e.time)
        duration = events[-1].time if events else 0.0
        return TimelineDataset(events=events, duration=duration, tick_size=self.tick_size)

    def generate_movement_timeline(self, movement_events: list[dict]) -> TimelineDataset:
        events: list[TimelineEvent] = []
        for ev in movement_events:
            events.append(
                TimelineEvent(
                    time=float(ev["time"]),
                    event_type="movement",
                    source=str(ev["entity_id"]),
                    value=float(ev["distance_moved"]),
                    metadata={"entity_id": ev["entity_id"]},
                )
            )
        events.sort(key=lambda e: e.time)
        duration = events[-1].time if events else 0.0
        return TimelineDataset(events=events, duration=duration, tick_size=self.tick_size)

    def resample(self, dataset: TimelineDataset, new_tick_size: float) -> TimelineDataset:
        resampled: list[TimelineEvent] = []
        for ev in dataset.events:
            bucket = round(ev.time / new_tick_size) * new_tick_size
            resampled.append(
                TimelineEvent(
                    time=round(bucket, 10),
                    event_type=ev.event_type,
                    source=ev.source,
                    value=ev.value,
                    metadata=dict(ev.metadata),
                )
            )
        resampled.sort(key=lambda e: e.time)
        return TimelineDataset(
            events=resampled,
            duration=dataset.duration,
            tick_size=new_tick_size,
        )

    def to_chart_series(self, dataset: TimelineDataset, event_type: str) -> FormattedSeries:
        tick_totals: dict[float, float] = {}
        for ev in dataset.events:
            if ev.event_type != event_type:
                continue
            bucket = round(round(ev.time / dataset.tick_size) * dataset.tick_size, 10)
            tick_totals[bucket] = tick_totals.get(bucket, 0.0) + ev.value

        x_vals = sorted(tick_totals.keys())
        y_vals = [tick_totals[t] for t in x_vals]

        return FormattedSeries(label=event_type, x=x_vals, y=y_vals)
