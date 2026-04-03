"""J17 — Data Loading Performance Benchmarks"""

import time
import pytest

from data.loaders.raw_data_loader import RawDataLoader
from data.mappers.data_mapper import DataMapper


pytestmark = pytest.mark.slow


class TestFullDatasetLoadTime:
    def test_enemy_load_under_1s(self):
        loader = RawDataLoader()
        start = time.perf_counter()
        bundle = loader.load("entities/enemy_profiles.json")
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Enemy load took {elapsed:.3f}s"
        assert len(bundle) > 0

    def test_affix_load_under_2s(self):
        loader = RawDataLoader()
        start = time.perf_counter()
        bundle = loader.load("items/affixes.json")
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"Affix load took {elapsed:.3f}s"
        assert len(bundle) > 0

    def test_passive_load_under_2s(self):
        loader = RawDataLoader()
        start = time.perf_counter()
        bundle = loader.load("classes/passives.json")
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"Passive load took {elapsed:.3f}s"


class TestMappingThroughput:
    def test_affix_mapping_throughput(self):
        loader = RawDataLoader()
        bundle = loader.load("items/affixes.json")
        start = time.perf_counter()
        affixes = DataMapper.affixes_from_bundle(bundle)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"Affix mapping took {elapsed:.3f}s"
        assert len(affixes) > 1000

    def test_passive_mapping_throughput(self):
        loader = RawDataLoader()
        bundle = loader.load("classes/passives.json")
        start = time.perf_counter()
        passives = DataMapper.passives_from_bundle(bundle)
        elapsed = time.perf_counter() - start
        assert elapsed < 3.0, f"Passive mapping took {elapsed:.3f}s"
        assert len(passives) > 100
