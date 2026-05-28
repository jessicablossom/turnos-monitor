from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import requests

from tests.helpers import make_settings
from turnos_monitor.check_result import CheckOutcome
from turnos_monitor.checker import run_single_check


class TestChecker(unittest.TestCase):
    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_unavailable_when_empty(
        self,
        mock_fetch: MagicMock,
    ) -> None:
        mock_fetch.return_value = []
        settings = make_settings()

        result = run_single_check(settings, index=3, total=12)

        self.assertEqual(result.outcome, CheckOutcome.UNAVAILABLE)
        self.assertEqual(result.index, 3)
        self.assertEqual(result.total, 12)

    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_available_with_points(
        self,
        mock_fetch: MagicMock,
    ) -> None:
        available = [{"disponible": True, "nombre": "Milán"}]
        mock_fetch.return_value = available
        settings = make_settings()

        result = run_single_check(settings)

        self.assertEqual(result.outcome, CheckOutcome.AVAILABLE)
        self.assertEqual(len(result.available_points), 1)
        self.assertIn("Milán", result.detail)

    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_api_error(
        self,
        mock_fetch: MagicMock,
    ) -> None:
        mock_fetch.side_effect = requests.HTTPError("503")
        settings = make_settings()

        result = run_single_check(settings)

        self.assertEqual(result.outcome, CheckOutcome.API_ERROR)
        self.assertIn("503", result.detail)


if __name__ == "__main__":
    unittest.main()
