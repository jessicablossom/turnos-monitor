from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from turnos_monitor.monitor_frequency import (
    parse_monitor_frequency,
    should_run_scheduled_check,
)


class TestMonitorFrequency(unittest.TestCase):
    def test_parse_monitor_frequency_accepts_daily(self) -> None:
        self.assertEqual(parse_monitor_frequency("daily"), "daily")

    def test_parse_monitor_frequency_accepts_weekly_trimmed(self) -> None:
        self.assertEqual(parse_monitor_frequency("  WEEKLY "), "weekly")

    def test_parse_monitor_frequency_rejects_invalid(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            parse_monitor_frequency("hourly")
        self.assertIn("hourly", str(ctx.exception))

    def test_should_run_daily_on_any_day(self) -> None:
        tz = ZoneInfo("Europe/Rome")
        wednesday = datetime(2026, 6, 10, 0, 0, tzinfo=tz)
        self.assertTrue(
            should_run_scheduled_check(
                "daily",
                wednesday,
                "Europe/Rome",
                is_manual_run=False,
            )
        )

    def test_should_run_weekly_only_on_monday(self) -> None:
        tz = ZoneInfo("Europe/Rome")
        monday = datetime(2026, 6, 8, 0, 0, tzinfo=tz)
        wednesday = datetime(2026, 6, 10, 0, 0, tzinfo=tz)

        self.assertTrue(
            should_run_scheduled_check(
                "weekly",
                monday,
                "Europe/Rome",
                is_manual_run=False,
            )
        )
        self.assertFalse(
            should_run_scheduled_check(
                "weekly",
                wednesday,
                "Europe/Rome",
                is_manual_run=False,
            )
        )

    def test_should_run_weekly_on_manual_even_if_not_monday(self) -> None:
        tz = ZoneInfo("Europe/Rome")
        wednesday = datetime(2026, 6, 10, 0, 0, tzinfo=tz)
        self.assertTrue(
            should_run_scheduled_check(
                "weekly",
                wednesday,
                "Europe/Rome",
                is_manual_run=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
