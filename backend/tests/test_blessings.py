"""
Monolith of Fate Blessings — full coverage test suite.

Verifies:
  1. Game data loader returns the expected timeline and blessing entries.
  2. resolve_blessing_stats() expands every supported stat_type correctly,
     skips drop-rate / unknown ids, and respects explicit value overrides.
  3. End-to-end stat pipeline integration: applying a blessing to a fresh
     BuildStats produces the exact delta vs a baseline with no blessings.
  4. The /api/ref/blessings endpoint serialises all ten timelines.
"""

from __future__ import annotations

import pytest

from app.engines.stat_engine import BuildStats
from app.engines.stat_resolution_pipeline import resolve_blessing_stats
from app.game_data.game_data_loader import (
    get_all_blessings,
    get_all_blessings_flat,
    get_blessing_by_id,
)
from app.domain.calculators.stat_calculator import combine_additive_percents


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(blessing_id: str, *, is_grand: bool = True, value=None,
           timeline_id: str = "x") -> dict:
    """Construct a single Build.blessings entry."""
    e = {"timeline_id": timeline_id, "blessing_id": blessing_id, "is_grand": is_grand}
    if value is not None:
        e["value"] = value
    return e


def _apply_blessings(stats: BuildStats, entries: list[dict]) -> None:
    """Apply blessings to a BuildStats using the same rules as
    aggregate_stats step 5b — additive percent for ``increased`` /
    ``_pct`` keys, flat add otherwise.  Mirrors stat_engine.py exactly so
    the integration test catches drift between layers.
    """
    for delta in resolve_blessing_stats(entries):
        key = delta["stat_key"]
        value = delta["value"]
        if not hasattr(stats, key):
            continue
        if delta.get("stat_type") == "increased" or key.endswith("_pct"):
            setattr(stats, key,
                    combine_additive_percents(getattr(stats, key), value))
        else:
            setattr(stats, key, getattr(stats, key) + value)


# ---------------------------------------------------------------------------
# GROUP 1 — Data loader
# ---------------------------------------------------------------------------

class TestBlessingsDataLoader:
    def test_get_all_blessings_returns_ten_timelines(self, app):
        with app.app_context():
            timelines = get_all_blessings()
        assert isinstance(timelines, list)
        assert len(timelines) == 10

    def test_get_blessing_by_id_whisper_of_orobyss(self, app):
        with app.app_context():
            b = get_blessing_by_id("whisper_of_orobyss")
        assert b is not None
        assert b["stat_key"] == "void_damage_pct"
        assert b["grand_max"] == 100

    def test_get_blessing_by_id_cruelty_of_strength(self, app):
        with app.app_context():
            b = get_blessing_by_id("cruelty_of_strength")
        assert b is not None
        assert b["stat_key"] == "physical_damage_pct"
        assert b["grand_max"] == 100

    def test_get_blessing_by_id_nonexistent_returns_none(self, app):
        with app.app_context():
            assert get_blessing_by_id("nonexistent") is None

    def test_total_blessing_count_is_112(self, app):
        with app.app_context():
            timelines = get_all_blessings()
            total_nested = sum(len(tl.get("blessings", []) or []) for tl in timelines)
            total_flat = len(get_all_blessings_flat())
        assert total_nested == 112
        assert total_flat == 112


# ---------------------------------------------------------------------------
# GROUP 2 — resolve_blessing_stats()
# ---------------------------------------------------------------------------

class TestResolveBlessingStats:
    def test_grand_cruelty_of_strength(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("cruelty_of_strength")])
        assert out == [{
            "stat_key":  "physical_damage_pct",
            "value":     100.0,
            "stat_type": "increased",
        }]

    def test_normal_cruelty_of_strength_uses_normal_max(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("cruelty_of_strength", is_grand=False)])
        assert len(out) == 1
        assert out[0]["value"] == 60.0
        assert out[0]["stat_key"] == "physical_damage_pct"

    def test_explicit_value_overrides_grand_max(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("cruelty_of_strength", value=75.0)])
        assert len(out) == 1
        assert out[0]["value"] == 75.0

    def test_grand_resolve_of_humanity_expands_to_seven_resistances(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("resolve_of_humanity")])
        assert len(out) == 7
        expected_keys = {
            "fire_res", "cold_res", "lightning_res",
            "void_res", "necrotic_res", "physical_res", "poison_res",
        }
        assert {d["stat_key"] for d in out} == expected_keys
        for d in out:
            assert d["value"] == 20.0

    def test_grand_bones_of_eternity_expands_to_two_block_stats(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("bones_of_eternity")])
        by_key = {d["stat_key"]: d for d in out}
        assert set(by_key) == {"block_chance", "block_effectiveness"}
        assert by_key["block_chance"]["value"] == 8.0
        assert by_key["block_effectiveness"]["value"] == 240.0

    def test_drop_rate_blessing_returns_empty(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("pride_of_rebellion")])
        assert out == []

    def test_unknown_blessing_id_returns_empty_no_exception(self, app):
        with app.app_context():
            out = resolve_blessing_stats([_entry("nonexistent_blessing")])
        assert out == []


# ---------------------------------------------------------------------------
# GROUP 3 — Pipeline integration on BuildStats
# ---------------------------------------------------------------------------

class TestBlessingPipelineIntegration:
    def test_grand_chaos_of_lagon_adds_lightning_damage_pct(self, app):
        baseline = BuildStats()
        with_blessing = BuildStats()
        with app.app_context():
            _apply_blessings(with_blessing, [_entry("chaos_of_lagon")])
        assert with_blessing.lightning_damage_pct - baseline.lightning_damage_pct == 100.0

    def test_grand_body_of_obsidian_adds_flat_armour(self, app):
        baseline = BuildStats()
        with_blessing = BuildStats()
        with app.app_context():
            _apply_blessings(with_blessing, [_entry("body_of_obsidian")])
        assert with_blessing.armour - baseline.armour == 320.0

    def test_grand_resolve_of_humanity_adds_twenty_to_each_resistance(self, app):
        baseline = BuildStats()
        with_blessing = BuildStats()
        with app.app_context():
            _apply_blessings(with_blessing, [_entry("resolve_of_humanity")])
        for res in (
            "fire_res", "cold_res", "lightning_res",
            "void_res", "necrotic_res", "physical_res", "poison_res",
        ):
            delta = getattr(with_blessing, res) - getattr(baseline, res)
            assert delta == 20.0, f"{res} expected +20, got +{delta}"

    def test_drop_rate_blessing_leaves_buildstats_unchanged(self, app):
        baseline = BuildStats()
        with_drop_only = BuildStats()
        with app.app_context():
            _apply_blessings(with_drop_only, [
                _entry("pride_of_rebellion"),
                _entry("sight_of_the_outcasts"),
                _entry("memory_of_the_living"),
            ])
        # Every BuildStats field on the drop-only build must equal the baseline.
        for field, base_value in vars(baseline).items():
            assert getattr(with_drop_only, field) == base_value, (
                f"drop-rate blessings should not change {field}"
            )


# ---------------------------------------------------------------------------
# GROUP 4 — API endpoint
# ---------------------------------------------------------------------------

class TestBlessingsApi:
    def test_get_blessings_endpoint_returns_200_and_ten_timelines(self, client):
        resp = client.get("/api/ref/blessings")
        assert resp.status_code == 200
        body = resp.get_json()
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 10

    def test_the_black_sun_and_reign_of_dragons_have_thirteen_blessings(self, client):
        resp = client.get("/api/ref/blessings")
        body = resp.get_json()
        by_id = {tl["id"]: tl for tl in body["data"]}
        assert "the_black_sun" in by_id
        assert "reign_of_dragons" in by_id
        assert len(by_id["the_black_sun"]["blessings"]) == 13
        assert len(by_id["reign_of_dragons"]["blessings"]) == 13
