"""J15 — Tests for data_integrity_logger.py"""

import pytest
from debug.data_integrity_logger import DataIntegrityLogger, Severity


class TestLogCreation:
    def test_info_recorded(self):
        logger = DataIntegrityLogger()
        logger.info("skill", "fireball", "Loaded successfully")
        records = logger.to_list()
        assert len(records) == 1
        assert records[0]["severity"] == "info"
        assert records[0]["category"] == "skill"

    def test_warning_recorded(self):
        logger = DataIntegrityLogger()
        logger.warning("affix", "fire_res", "Mid-tier value unusual")
        assert logger.warning_count() == 1

    def test_error_recorded(self):
        logger = DataIntegrityLogger()
        logger.error("enemy", "boss_1", "Missing armor field")
        assert logger.has_errors() is True
        assert logger.error_count() == 1


class TestErrorDetection:
    def test_filter_by_severity_errors_only(self):
        logger = DataIntegrityLogger()
        logger.info("s", "x", "ok")
        logger.error("s", "y", "bad")
        errors = logger.to_list(Severity.ERROR)
        assert len(errors) == 1
        assert errors[0]["item_id"] == "y"

    def test_summary_counts(self):
        logger = DataIntegrityLogger()
        logger.info("s", "a", "msg")
        logger.warning("s", "b", "msg")
        logger.error("s", "c", "msg")
        s = logger.summary()
        assert s["total"] == 3
        assert s["errors"] == 1
        assert s["warnings"] == 1
        assert s["infos"] == 1

    def test_max_entries_evicts_oldest(self):
        logger = DataIntegrityLogger(max_entries=3)
        for i in range(5):
            logger.info("s", str(i), "msg")
        assert len(logger.to_list()) == 3

    def test_clear_empties_buffer(self):
        logger = DataIntegrityLogger()
        logger.error("s", "x", "oops")
        logger.clear()
        assert len(logger.to_list()) == 0
