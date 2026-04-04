"""J2 — Tests for raw_data_loader.py"""

import json
import pytest

from data.loaders.raw_data_loader import RawDataLoader


class TestFileLoading:
    def test_loads_real_enemies_file(self):
        loader = RawDataLoader()
        data = loader.load("entities/enemy_profiles.json")
        assert isinstance(data, list)
        assert len(data) > 0

    def test_loads_real_affixes_file(self):
        loader = RawDataLoader()
        data = loader.load("items/affixes.json")
        assert isinstance(data, list)
        assert len(data) > 0

    def test_loads_valid_json_from_tmpdir(self, tmp_path):
        (tmp_path / "test.json").write_text('{"key": "value"}')
        loader = RawDataLoader(data_dir=tmp_path)
        result = loader.load("test.json")
        assert result == {"key": "value"}


class TestMissingFileDetection:
    def test_missing_file_raises_file_not_found(self):
        loader = RawDataLoader()
        with pytest.raises(FileNotFoundError, match="not found"):
            loader.load("nonexistent/path.json")

    def test_exists_returns_false_for_missing(self):
        loader = RawDataLoader()
        assert loader.exists("no_such_file.json") is False

    def test_exists_returns_true_for_real_file(self):
        loader = RawDataLoader()
        assert loader.exists("entities/enemy_profiles.json") is True


class TestDirectoryScan:
    def test_scan_returns_json_files(self):
        loader = RawDataLoader()
        files = loader.scan("entities")
        assert any("enemy_profiles.json" in f for f in files)

    def test_scan_empty_subdir_returns_empty(self, tmp_path):
        loader = RawDataLoader(data_dir=tmp_path)
        assert loader.scan("nonexistent") == []

    def test_scan_finds_nested_files(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "a.json").write_text("[]")
        (sub / "b.json").write_text("[]")
        loader = RawDataLoader(data_dir=tmp_path)
        files = loader.scan()
        assert len(files) == 2
