from __future__ import annotations

import unittest

from turnos_monitor.check_result import (
    CheckOutcome,
    CheckResult,
    format_check_line,
    format_checks_html,
    format_checks_text,
    has_api_errors,
    has_available_turnos,
    outcome_label,
)


class TestCheckResult(unittest.TestCase):
    def test_outcome_labels(self) -> None:
        self.assertEqual(outcome_label(CheckOutcome.AVAILABLE), "Turnos disponibles")
        self.assertEqual(outcome_label(CheckOutcome.UNAVAILABLE), "Sin turnos")
        self.assertEqual(outcome_label(CheckOutcome.API_ERROR), "Error de API")

    def test_format_check_line(self) -> None:
        result = CheckResult(
            index=2,
            total=12,
            outcome=CheckOutcome.UNAVAILABLE,
            detail="Ningún punto con disponible=true",
        )
        line = format_check_line(result)
        self.assertIn("Consulta 2/12", line)
        self.assertIn("Sin turnos", line)

    def test_format_checks_text_and_html(self) -> None:
        results = [
            CheckResult(1, 2, CheckOutcome.UNAVAILABLE, "ok"),
            CheckResult(2, 2, CheckOutcome.API_ERROR, "timeout"),
        ]
        text = format_checks_text(results)
        self.assertIn("Consulta 1/2", text)
        self.assertIn("Consulta 2/2", text)
        html = format_checks_html(results)
        self.assertIn("<ul>", html)
        self.assertIn("api-error", html)

    def test_has_available_and_errors(self) -> None:
        available = CheckResult(1, 1, CheckOutcome.AVAILABLE, "x")
        unavailable = CheckResult(1, 1, CheckOutcome.UNAVAILABLE, "x")
        error = CheckResult(1, 1, CheckOutcome.API_ERROR, "x")

        self.assertTrue(has_available_turnos([available]))
        self.assertFalse(has_available_turnos([unavailable]))
        self.assertTrue(has_api_errors([error]))
        self.assertFalse(has_api_errors([unavailable]))


if __name__ == "__main__":
    unittest.main()
