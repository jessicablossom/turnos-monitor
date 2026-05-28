from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from tests.helpers import make_settings
from turnos_monitor.check_result import CheckOutcome, CheckResult
from turnos_monitor.window import (
    is_within_daily_window,
    run_window_checks,
    seconds_until_window_start,
)


class TestWindow(unittest.TestCase):
    def test_inside_window_at_midnight(self) -> None:
        settings = make_settings()
        tz = ZoneInfo("Europe/Rome")
        now = datetime(2026, 5, 19, 0, 15, tzinfo=tz)
        self.assertTrue(is_within_daily_window(now, settings))

    def test_window_end_is_exclusive(self) -> None:
        settings = make_settings()
        tz = ZoneInfo("Europe/Rome")
        now = datetime(2026, 5, 19, 1, 0, tzinfo=tz)
        self.assertFalse(is_within_daily_window(now, settings))

    def test_outside_window(self) -> None:
        settings = make_settings()
        tz = ZoneInfo("Europe/Rome")
        now = datetime(2026, 5, 19, 2, 0, tzinfo=tz)
        self.assertFalse(is_within_daily_window(now, settings))

    def test_seconds_until_window_same_day(self) -> None:
        settings = make_settings()
        tz = ZoneInfo("Europe/Rome")
        now = datetime(2026, 5, 19, 23, 0, tzinfo=tz)
        seconds = seconds_until_window_start(now, settings)
        self.assertEqual(seconds, 3600)

    @patch("turnos_monitor.window.send_run_summary_email")
    @patch("turnos_monitor.window.time.sleep")
    @patch("turnos_monitor.window.run_single_check")
    def test_run_window_checks_sends_summary_and_stops_on_success(
        self,
        mock_check: MagicMock,
        mock_sleep: MagicMock,
        mock_summary: MagicMock,
    ) -> None:
        mock_check.side_effect = [
            CheckResult(1, 12, CheckOutcome.UNAVAILABLE, "a"),
            CheckResult(2, 12, CheckOutcome.AVAILABLE, "b"),
        ]
        settings = make_settings()

        results = run_window_checks(settings, stop_on_success=True)

        self.assertEqual(len(results), 2)
        self.assertEqual(mock_check.call_count, 2)
        mock_sleep.assert_called_once()
        mock_summary.assert_called_once_with(settings, results)


if __name__ == "__main__":
    unittest.main()
