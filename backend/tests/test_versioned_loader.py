"""J10 — Tests for versioned_loader.py"""

import json
import pytest

from data.versioning.versioned_loader import VersionedLoader, VersionInfo


class TestVersionDetection:
    def test_detects_unknown_when_no_version_field(self, tmp_path):
        (tmp_path / "items").mkdir()
        (tmp_path / "items" / "affixes.json").write_text("[]")
        vl = VersionedLoader(data_dir=tmp_path)
        info = vl.detect_version()
        assert info.version == "unknown"

    def test_detects_version_from_meta(self, tmp_path):
        (tmp_path / "items").mkdir()
        data = {"_meta": {"version": "1.2.3"}, "affixes": []}
        (tmp_path / "items" / "affixes.json").write_text(json.dumps(data))
        vl = VersionedLoader(data_dir=tmp_path)
        info = vl.detect_version()
        assert info.version == "1.2.3"

    def test_detects_version_from_direct_field(self, tmp_path):
        (tmp_path / "items").mkdir()
        data = {"_version": "2.0", "affixes": []}
        (tmp_path / "items" / "affixes.json").write_text(json.dumps(data))
        vl = VersionedLoader(data_dir=tmp_path)
        assert vl.detect_version().version == "2.0"


class TestFallbackBehavior:
    def test_load_falls_back_to_unversioned(self, tmp_path):
        (tmp_path / "items").mkdir()
        (tmp_path / "items" / "affixes.json").write_text('["real"]')
        vl = VersionedLoader(data_dir=tmp_path)
        data = vl.load("items/affixes.json", version="v99")
        assert data == ["real"]

    def test_load_uses_versioned_when_present(self, tmp_path):
        v_dir = tmp_path / "v1" / "items"
        v_dir.mkdir(parents=True)
        (tmp_path / "items").mkdir()
        (tmp_path / "items" / "affixes.json").write_text('"base"')
        (v_dir / "affixes.json").write_text('"versioned"')
        vl = VersionedLoader(data_dir=tmp_path)
        data = vl.load("items/affixes.json", version="v1")
        assert data == "versioned"

    def test_validate_compatibility_false(self, tmp_path):
        (tmp_path / "items").mkdir()
        (tmp_path / "items" / "affixes.json").write_text('{}')
        vl = VersionedLoader(data_dir=tmp_path)
        assert vl.validate_compatibility("1.0.0") is False
