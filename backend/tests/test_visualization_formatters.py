"""
Unit tests for ResultFormatter and TimelineGenerator.

Run with:
    python -m pytest tests/test_visualization_formatters.py -v --tb=short
"""
from __future__ import annotations

import pytest

from visualization.formatters.result_formatter import (
    FormattedDataset,
    FormattedSeries,
    ResultFormatter,
)
from visualization.timeline.timeline_generator import (
    TimelineDataset,
    TimelineEvent,
    TimelineGenerator,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def formatter():
    return ResultFormatter()


@pytest.fixture
def generator():
    return TimelineGenerator(tick_size=0.1)


# ---------------------------------------------------------------------------
# ResultFormatter.normalize
# ---------------------------------------------------------------------------


class TestResultFormatterNormalize:
    def test_empty_list_returns_empty(self, formatter):
        assert formatter.normalize([]) == []

    def test_all_same_values_returns_as_is(self, formatter):
        data = [5.0, 5.0, 5.0]
        result = formatter.normalize(data)
        assert result == [5.0, 5.0, 5.0]

    def test_all_same_single_value_returns_as_is(self, formatter):
        assert formatter.normalize([3.0]) == [3.0]

    def test_min_is_zero(self, formatter):
        result = formatter.normalize([0.0, 5.0, 10.0])
        assert result[0] == pytest.approx(0.0)

    def test_max_is_one(self, formatter):
        result = formatter.normalize([0.0, 5.0, 10.0])
        assert result[-1] == pytest.approx(1.0)

    def test_midpoint_is_half(self, formatter):
        result = formatter.normalize([0.0, 5.0, 10.0])
        assert result[1] == pytest.approx(0.5)

    def test_negative_range(self, formatter):
        result = formatter.normalize([-10.0, 0.0, 10.0])
        assert result == pytest.approx([0.0, 0.5, 1.0])

    def test_single_value_returns_as_is(self, formatter):
        assert formatter.normalize([42.0]) == [42.0]

    def test_output_length_matches_input(self, formatter):
        data = [1.0, 2.0, 3.0, 4.0]
        assert len(formatter.normalize(data)) == len(data)

    def test_does_not_mutate_input(self, formatter):
        data = [1.0, 2.0, 3.0]
        original = list(data)
        formatter.normalize(data)
        assert data == original


# ---------------------------------------------------------------------------
# ResultFormatter.format_time_series
# ---------------------------------------------------------------------------


class TestResultFormatterFormatTimeSeries:
    def test_returns_formatted_series(self, formatter):
        ts = [0.0, 1.0, 2.0]
        vs = [10.0, 20.0, 30.0]
        series = formatter.format_time_series(ts, vs, label="DPS", unit="dmg/s")
        assert isinstance(series, FormattedSeries)

    def test_correct_label(self, formatter):
        s = formatter.format_time_series([0.0], [1.0], label="MyLabel")
        assert s.label == "MyLabel"

    def test_correct_unit(self, formatter):
        s = formatter.format_time_series([0.0], [1.0], label="L", unit="dmg/s")
        assert s.unit == "dmg/s"

    def test_default_unit_empty_string(self, formatter):
        s = formatter.format_time_series([0.0], [1.0], label="L")
        assert s.unit == ""

    def test_x_matches_timestamps(self, formatter):
        ts = [1.0, 2.0, 3.0]
        s = formatter.format_time_series(ts, [0.0, 0.0, 0.0], label="L")
        assert s.x == ts

    def test_y_matches_values(self, formatter):
        vs = [100.0, 200.0, 300.0]
        s = formatter.format_time_series([0.0, 1.0, 2.0], vs, label="L")
        assert s.y == vs

    def test_returns_copies_not_same_reference(self, formatter):
        ts = [0.0, 1.0]
        vs = [5.0, 6.0]
        s = formatter.format_time_series(ts, vs, label="L")
        ts.append(2.0)
        assert len(s.x) == 2  # was not mutated


# ---------------------------------------------------------------------------
# ResultFormatter.format_multi_series
# ---------------------------------------------------------------------------


class TestResultFormatterFormatMultiSeries:
    def test_returns_formatted_dataset(self, formatter):
        data = {"A": ([0.0, 1.0], [10.0, 20.0])}
        ds = formatter.format_multi_series(data, title="Combat Stats")
        assert isinstance(ds, FormattedDataset)

    def test_correct_title(self, formatter):
        ds = formatter.format_multi_series({}, title="My Chart")
        assert ds.title == "My Chart"

    def test_correct_number_of_series(self, formatter):
        data = {
            "A": ([0.0], [1.0]),
            "B": ([0.0], [2.0]),
            "C": ([0.0], [3.0]),
        }
        ds = formatter.format_multi_series(data, title="T")
        assert len(ds.series) == 3

    def test_series_labels_match_keys(self, formatter):
        data = {"Alpha": ([0.0], [1.0]), "Beta": ([1.0], [2.0])}
        ds = formatter.format_multi_series(data, title="T")
        labels = {s.label for s in ds.series}
        assert labels == {"Alpha", "Beta"}

    def test_empty_data_produces_no_series(self, formatter):
        ds = formatter.format_multi_series({}, title="Empty")
        assert ds.series == []


# ---------------------------------------------------------------------------
# ResultFormatter.aggregate_by_bucket
# ---------------------------------------------------------------------------


class TestResultFormatterAggregateByBucket:
    def test_empty_timestamps_returns_empty(self, formatter):
        centers, avgs = formatter.aggregate_by_bucket([], [], bucket_size=1.0)
        assert centers == [] and avgs == []

    def test_zero_bucket_size_returns_empty(self, formatter):
        centers, avgs = formatter.aggregate_by_bucket([1.0, 2.0], [10.0, 20.0], bucket_size=0)
        assert centers == [] and avgs == []

    def test_single_bucket_center(self, formatter):
        centers, avgs = formatter.aggregate_by_bucket([0.5], [10.0], bucket_size=1.0)
        # key=0, center=0.5*1.0=0.5
        assert centers == pytest.approx([0.5])

    def test_single_bucket_average(self, formatter):
        _, avgs = formatter.aggregate_by_bucket([0.1, 0.9], [10.0, 20.0], bucket_size=1.0)
        assert avgs == pytest.approx([15.0])

    def test_multiple_buckets_count(self, formatter):
        ts = [0.5, 1.5, 2.5]
        vs = [10.0, 20.0, 30.0]
        centers, avgs = formatter.aggregate_by_bucket(ts, vs, bucket_size=1.0)
        assert len(centers) == 3

    def test_multiple_buckets_centers(self, formatter):
        ts = [0.5, 1.5, 2.5]
        vs = [10.0, 20.0, 30.0]
        centers, _ = formatter.aggregate_by_bucket(ts, vs, bucket_size=1.0)
        # keys 0,1,2 -> centers 0.5, 1.5, 2.5
        assert centers == pytest.approx([0.5, 1.5, 2.5])

    def test_multiple_buckets_averages(self, formatter):
        ts = [0.5, 1.5, 2.5]
        vs = [10.0, 20.0, 30.0]
        _, avgs = formatter.aggregate_by_bucket(ts, vs, bucket_size=1.0)
        assert avgs == pytest.approx([10.0, 20.0, 30.0])

    def test_bucket_merges_nearby_timestamps(self, formatter):
        ts = [0.1, 0.2, 0.3, 1.1]
        vs = [10.0, 20.0, 30.0, 40.0]
        centers, avgs = formatter.aggregate_by_bucket(ts, vs, bucket_size=1.0)
        assert len(centers) == 2
        assert avgs[0] == pytest.approx(20.0)  # mean of 10, 20, 30


# ---------------------------------------------------------------------------
# ResultFormatter.to_dict
# ---------------------------------------------------------------------------


class TestResultFormatterToDict:
    def test_has_title_key(self, formatter):
        ds = formatter.format_multi_series({"A": ([0.0], [1.0])}, title="T")
        d = formatter.to_dict(ds)
        assert "title" in d

    def test_has_series_key(self, formatter):
        ds = formatter.format_multi_series({"A": ([0.0], [1.0])}, title="T")
        d = formatter.to_dict(ds)
        assert "series" in d

    def test_title_value(self, formatter):
        ds = formatter.format_multi_series({}, title="My Title")
        d = formatter.to_dict(ds)
        assert d["title"] == "My Title"

    def test_series_entries_have_label(self, formatter):
        ds = formatter.format_multi_series({"DPS": ([0.0], [1.0])}, title="T")
        d = formatter.to_dict(ds)
        assert d["series"][0]["label"] == "DPS"

    def test_series_entries_have_x(self, formatter):
        ds = formatter.format_multi_series({"A": ([1.0, 2.0], [3.0, 4.0])}, title="T")
        d = formatter.to_dict(ds)
        assert d["series"][0]["x"] == [1.0, 2.0]

    def test_series_entries_have_y(self, formatter):
        ds = formatter.format_multi_series({"A": ([1.0], [99.0])}, title="T")
        d = formatter.to_dict(ds)
        assert d["series"][0]["y"] == [99.0]

    def test_has_x_label_and_y_label(self, formatter):
        ds = formatter.format_multi_series({}, title="T")
        d = formatter.to_dict(ds)
        assert "x_label" in d and "y_label" in d


# ---------------------------------------------------------------------------
# TimelineGenerator.generate_damage_timeline
# ---------------------------------------------------------------------------


class TestTimelineGeneratorDamageTimeline:
    def test_returns_timeline_dataset(self, generator):
        events = [{"time": 1.0, "source": "player", "amount": 100.0}]
        ds = generator.generate_damage_timeline(events)
        assert isinstance(ds, TimelineDataset)

    def test_event_type_is_damage(self, generator):
        events = [{"time": 1.0, "source": "player", "amount": 50.0}]
        ds = generator.generate_damage_timeline(events)
        assert all(e.event_type == "damage" for e in ds.events)

    def test_value_equals_amount(self, generator):
        events = [{"time": 1.0, "source": "player", "amount": 250.0}]
        ds = generator.generate_damage_timeline(events)
        assert ds.events[0].value == 250.0

    def test_source_is_preserved(self, generator):
        events = [{"time": 1.0, "source": "fireball", "amount": 50.0}]
        ds = generator.generate_damage_timeline(events)
        assert ds.events[0].source == "fireball"

    def test_multiple_events_count(self, generator):
        events = [
            {"time": 0.5, "source": "A", "amount": 10.0},
            {"time": 1.5, "source": "B", "amount": 20.0},
        ]
        ds = generator.generate_damage_timeline(events)
        assert len(ds.events) == 2

    def test_events_sorted_by_time(self, generator):
        events = [
            {"time": 2.0, "source": "A", "amount": 10.0},
            {"time": 0.5, "source": "B", "amount": 20.0},
        ]
        ds = generator.generate_damage_timeline(events)
        assert ds.events[0].time < ds.events[1].time

    def test_duration_is_last_event_time(self, generator):
        events = [
            {"time": 0.5, "source": "A", "amount": 10.0},
            {"time": 3.0, "source": "B", "amount": 20.0},
        ]
        ds = generator.generate_damage_timeline(events)
        assert ds.duration == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# TimelineGenerator.generate_buff_timeline
# ---------------------------------------------------------------------------


class TestTimelineGeneratorBuffTimeline:
    def test_applied_event_type(self, generator):
        events = [{"time": 1.0, "buff_name": "Haste", "event": "applied", "duration": 5.0}]
        ds = generator.generate_buff_timeline(events)
        assert ds.events[0].event_type == "buff_applied"

    def test_expired_event_type(self, generator):
        events = [{"time": 6.0, "buff_name": "Haste", "event": "expired", "duration": 0.0}]
        ds = generator.generate_buff_timeline(events)
        assert ds.events[0].event_type == "buff_expired"

    def test_source_is_buff_name(self, generator):
        events = [{"time": 1.0, "buff_name": "Haste", "event": "applied"}]
        ds = generator.generate_buff_timeline(events)
        assert ds.events[0].source == "Haste"

    def test_buff_name_in_metadata(self, generator):
        events = [{"time": 1.0, "buff_name": "Haste", "event": "applied"}]
        ds = generator.generate_buff_timeline(events)
        assert ds.events[0].metadata.get("buff_name") == "Haste"

    def test_multiple_events_preserved(self, generator):
        events = [
            {"time": 1.0, "buff_name": "Haste", "event": "applied"},
            {"time": 6.0, "buff_name": "Haste", "event": "expired"},
        ]
        ds = generator.generate_buff_timeline(events)
        assert len(ds.events) == 2

    def test_duration_from_last_event(self, generator):
        events = [
            {"time": 0.0, "buff_name": "X", "event": "applied"},
            {"time": 5.0, "buff_name": "X", "event": "expired"},
        ]
        ds = generator.generate_buff_timeline(events)
        assert ds.duration == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# TimelineGenerator.generate_movement_timeline
# ---------------------------------------------------------------------------


class TestTimelineGeneratorMovementTimeline:
    def test_event_type_is_movement(self, generator):
        events = [{"time": 0.5, "entity_id": "hero", "distance_moved": 1.5}]
        ds = generator.generate_movement_timeline(events)
        assert ds.events[0].event_type == "movement"

    def test_source_is_entity_id(self, generator):
        events = [{"time": 0.5, "entity_id": "hero", "distance_moved": 1.5}]
        ds = generator.generate_movement_timeline(events)
        assert ds.events[0].source == "hero"

    def test_value_is_distance_moved(self, generator):
        events = [{"time": 0.5, "entity_id": "hero", "distance_moved": 3.7}]
        ds = generator.generate_movement_timeline(events)
        assert ds.events[0].value == pytest.approx(3.7)

    def test_multiple_entities(self, generator):
        events = [
            {"time": 0.0, "entity_id": "A", "distance_moved": 1.0},
            {"time": 0.5, "entity_id": "B", "distance_moved": 2.0},
        ]
        ds = generator.generate_movement_timeline(events)
        assert len(ds.events) == 2

    def test_metadata_contains_entity_id(self, generator):
        events = [{"time": 0.5, "entity_id": "hero", "distance_moved": 1.0}]
        ds = generator.generate_movement_timeline(events)
        assert ds.events[0].metadata.get("entity_id") == "hero"


# ---------------------------------------------------------------------------
# TimelineGenerator.resample
# ---------------------------------------------------------------------------


class TestTimelineGeneratorResample:
    def _make_dataset(self, generator, events_raw):
        return generator.generate_damage_timeline(events_raw)

    def test_resampled_tick_size_updated(self, generator):
        ds = self._make_dataset(generator, [
            {"time": 0.15, "source": "A", "amount": 10.0},
        ])
        new_ds = generator.resample(ds, new_tick_size=0.5)
        assert new_ds.tick_size == pytest.approx(0.5)

    def test_same_number_of_events(self, generator):
        ds = self._make_dataset(generator, [
            {"time": 0.15, "source": "A", "amount": 10.0},
            {"time": 0.35, "source": "B", "amount": 20.0},
        ])
        new_ds = generator.resample(ds, new_tick_size=0.5)
        assert len(new_ds.events) == 2

    def test_events_snapped_to_new_buckets(self, generator):
        ds = self._make_dataset(generator, [
            {"time": 0.14, "source": "A", "amount": 10.0},
        ])
        # round(0.14 / 0.5) * 0.5 = 0.0
        new_ds = generator.resample(ds, new_tick_size=0.5)
        assert new_ds.events[0].time == pytest.approx(0.0)

    def test_duration_preserved(self, generator):
        ds = self._make_dataset(generator, [
            {"time": 1.0, "source": "A", "amount": 10.0},
        ])
        new_ds = generator.resample(ds, new_tick_size=0.5)
        assert new_ds.duration == pytest.approx(ds.duration)

    def test_event_values_preserved(self, generator):
        ds = self._make_dataset(generator, [
            {"time": 0.15, "source": "A", "amount": 42.0},
        ])
        new_ds = generator.resample(ds, new_tick_size=0.5)
        assert new_ds.events[0].value == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# TimelineGenerator.to_chart_series
# ---------------------------------------------------------------------------


class TestTimelineGeneratorToChartSeries:
    def _damage_dataset(self, generator, damage_events):
        return generator.generate_damage_timeline(damage_events)

    def test_filters_by_event_type(self, generator):
        raw = [
            {"time": 0.1, "source": "A", "amount": 10.0},
        ]
        ds = self._damage_dataset(generator, raw)
        series = generator.to_chart_series(ds, event_type="damage")
        assert len(series.x) == 1

    def test_empty_when_event_type_mismatch(self, generator):
        raw = [{"time": 0.1, "source": "A", "amount": 10.0}]
        ds = self._damage_dataset(generator, raw)
        series = generator.to_chart_series(ds, event_type="movement")
        assert series.x == [] and series.y == []

    def test_sums_values_per_tick(self, generator):
        # Two events that fall in the same tick bucket (both round to bucket 0.0)
        # round(0.01/0.1)*0.1 = round(0.1)*0.1 = 0.0
        # round(0.04/0.1)*0.1 = round(0.4)*0.1 = 0.0
        raw = [
            {"time": 0.01, "source": "A", "amount": 10.0},
            {"time": 0.04, "source": "B", "amount": 20.0},
        ]
        ds = self._damage_dataset(generator, raw)
        series = generator.to_chart_series(ds, event_type="damage")
        # Both events snap to tick 0.0 and are summed
        assert series.y[0] == pytest.approx(30.0)

    def test_label_is_event_type(self, generator):
        raw = [{"time": 0.1, "source": "A", "amount": 10.0}]
        ds = self._damage_dataset(generator, raw)
        series = generator.to_chart_series(ds, event_type="damage")
        assert series.label == "damage"

    def test_x_values_sorted(self, generator):
        raw = [
            {"time": 1.0, "source": "A", "amount": 10.0},
            {"time": 0.1, "source": "B", "amount": 5.0},
        ]
        ds = self._damage_dataset(generator, raw)
        series = generator.to_chart_series(ds, event_type="damage")
        assert series.x == sorted(series.x)


# ---------------------------------------------------------------------------
# TimelineGenerator.add_event
# ---------------------------------------------------------------------------


class TestTimelineGeneratorAddEvent:
    def test_event_appended(self, generator):
        ds = TimelineDataset(events=[], duration=10.0, tick_size=0.1)
        ev = TimelineEvent(time=1.0, event_type="damage", source="A", value=50.0)
        generator.add_event(ds, ev)
        assert len(ds.events) == 1

    def test_event_is_the_appended_event(self, generator):
        ds = TimelineDataset(events=[], duration=10.0, tick_size=0.1)
        ev = TimelineEvent(time=2.0, event_type="kill", source="B", value=0.0)
        generator.add_event(ds, ev)
        assert ds.events[0] is ev

    def test_events_remain_sorted_after_add(self, generator):
        ds = TimelineDataset(events=[], duration=10.0, tick_size=0.1)
        generator.add_event(ds, TimelineEvent(time=3.0, event_type="damage", source="A", value=10.0))
        generator.add_event(ds, TimelineEvent(time=1.0, event_type="damage", source="B", value=5.0))
        generator.add_event(ds, TimelineEvent(time=2.0, event_type="damage", source="C", value=8.0))
        times = [e.time for e in ds.events]
        assert times == sorted(times)

    def test_multiple_events_accumulated(self, generator):
        ds = TimelineDataset(events=[], duration=10.0, tick_size=0.1)
        for i in range(5):
            generator.add_event(
                ds, TimelineEvent(time=float(i), event_type="damage", source="S", value=1.0)
            )
        assert len(ds.events) == 5
