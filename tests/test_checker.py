from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import requests

from tests.helpers import make_settings
from turnos_monitor.checker import run_single_check


class TestChecker(unittest.TestCase):
    @patch("turnos_monitor.checker.send_availability_email")
    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_false_when_no_availability(
        self,
        mock_fetch: MagicMock,
        mock_email: MagicMock,
    ) -> None:
        mock_fetch.return_value = []
        settings = make_settings()

        result = run_single_check(settings)

        self.assertFalse(result)
        mock_email.assert_not_called()

    @patch("turnos_monitor.checker.send_availability_email")
    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_true_and_sends_email_when_available(
        self,
        mock_fetch: MagicMock,
        mock_email: MagicMock,
    ) -> None:
        available = [{"disponible": True, "nombre": "Milán"}]
        mock_fetch.return_value = available
        settings = make_settings()

        result = run_single_check(settings)

        self.assertTrue(result)
        mock_email.assert_called_once_with(settings, available)

    @patch("turnos_monitor.checker.send_availability_email")
    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_false_on_api_error(
        self,
        mock_fetch: MagicMock,
        mock_email: MagicMock,
    ) -> None:
        mock_fetch.side_effect = requests.HTTPError("503")
        settings = make_settings()

        result = run_single_check(settings)

        self.assertFalse(result)
        mock_email.assert_not_called()

    @patch("turnos_monitor.checker.send_availability_email")
    @patch("turnos_monitor.checker.fetch_availability")
    def test_returns_false_on_smtp_error(
        self,
        mock_fetch: MagicMock,
        mock_email: MagicMock,
    ) -> None:
        mock_fetch.return_value = [{"disponible": True}]
        mock_email.side_effect = OSError("SMTP down")
        settings = make_settings()

        result = run_single_check(settings)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
