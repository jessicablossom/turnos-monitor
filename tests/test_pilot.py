from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import requests

from tests.helpers import MILAN_API_SAMPLE
from turnos_monitor.pilot import format_pilot_report, run_pilot


class TestPilot(unittest.TestCase):
    def test_run_pilot_with_mock(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MILAN_API_SAMPLE
        mock_response.raise_for_status = MagicMock()

        session = MagicMock(spec=requests.Session)
        session.get.return_value = mock_response

        result = run_pilot(session=session)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.points), 1)
        self.assertEqual(result.available_count, 0)
        self.assertFalse(result.has_availability)

    def test_format_pilot_report_contains_key_fields(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MILAN_API_SAMPLE
        mock_response.raise_for_status = MagicMock()
        session = MagicMock(spec=requests.Session)
        session.get.return_value = mock_response

        result = run_pilot(session=session)
        report = format_pilot_report(result)

        self.assertIn("Prueba piloto", report)
        self.assertIn("disponible: False", report)
        self.assertIn("Consulado", report)
        self.assertIn("JSON completo", report)


if __name__ == "__main__":
    unittest.main()
