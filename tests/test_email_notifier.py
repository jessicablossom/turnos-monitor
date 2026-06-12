from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from tests.helpers import make_settings
from turnos_monitor.check_result import CheckOutcome, CheckResult
from turnos_monitor.email_notifier import (
    SUMMARY_SUBJECT_AVAILABLE,
    SUMMARY_SUBJECT_UNAVAILABLE,
    format_points_html,
    send_availability_email,
    send_run_summary_email,
)


class TestEmailNotifier(unittest.TestCase):
    def test_format_points_html(self) -> None:
        html = format_points_html(
            [
                {
                    "nombre": "Consulado Milán",
                    "direccion": "Via Agnello, 2",
                    "localidad": "Milán",
                }
            ]
        )
        self.assertIn("Consulado Milán", html)
        self.assertIn("Via Agnello", html)
        self.assertIn("<ul>", html)

    @patch("turnos_monitor.email_notifier.smtplib.SMTP")
    def test_send_availability_email(self, mock_smtp_class: MagicMock) -> None:
        mock_server = MagicMock()
        mock_server.sendmail.return_value = {}
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        settings = make_settings(notify_email="jessica@test.com")

        send_availability_email(
            settings,
            [{"nombre": "Milán", "direccion": "Via X", "localidad": "Milán"}],
        )

        mock_smtp_class.assert_called_once_with(
            "smtp.gmail.com",
            587,
            timeout=30,
        )
        mock_server.ehlo.assert_called()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@gmail.com", "secret")
        mock_server.sendmail.assert_called_once()
        recipients = mock_server.sendmail.call_args[0][1]
        self.assertEqual(recipients, ["jessica@test.com"])

    @patch("turnos_monitor.email_notifier._send_email")
    def test_send_run_summary_email_unavailable(
        self,
        mock_send: MagicMock,
    ) -> None:
        settings = make_settings()
        results = [
            CheckResult(1, 2, CheckOutcome.UNAVAILABLE, "sin turnos"),
            CheckResult(2, 2, CheckOutcome.UNAVAILABLE, "sin turnos"),
        ]

        send_run_summary_email(settings, results)

        mock_send.assert_called_once()
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs["subject"], SUMMARY_SUBJECT_UNAVAILABLE)
        self.assertIn("Consulta 1/2", kwargs["body_text"])
        self.assertIn("Resultado negativo", kwargs["body_text"])

    @patch("turnos_monitor.email_notifier._send_email")
    def test_send_run_summary_email_available(
        self,
        mock_send: MagicMock,
    ) -> None:
        settings = make_settings()
        results = [
            CheckResult(
                1,
                1,
                CheckOutcome.AVAILABLE,
                "1 punto(s): Milán",
                available_points=({"nombre": "Milán"},),
            ),
        ]

        send_run_summary_email(settings, results)

        mock_send.assert_called_once()
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs["subject"], SUMMARY_SUBJECT_AVAILABLE)
        self.assertIn("Resultado positivo", kwargs["body_text"])
        self.assertIn("Milán", kwargs["body_html"])


if __name__ == "__main__":
    unittest.main()
