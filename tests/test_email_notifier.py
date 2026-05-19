from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from tests.helpers import make_settings
from turnos_monitor.email_notifier import format_points_html, send_availability_email


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
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        settings = make_settings(notify_email="jessica@test.com")

        send_availability_email(
            settings,
            [{"nombre": "Milán", "direccion": "Via X", "localidad": "Milán"}],
        )

        mock_smtp_class.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@gmail.com", "secret")
        mock_server.sendmail.assert_called_once()
        recipients = mock_server.sendmail.call_args[0][1]
        self.assertEqual(recipients, ["jessica@test.com"])


if __name__ == "__main__":
    unittest.main()
