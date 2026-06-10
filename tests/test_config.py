from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from tests.helpers import patch_env, restore_env
from turnos_monitor.config import load_settings


class TestConfig(unittest.TestCase):
    def test_load_settings_reads_env(self) -> None:
        previous = patch_env(
            SMTP_USER="sender@test.com",
            SMTP_PASSWORD="app-pass",
            NOTIFY_EMAIL="dest@test.com",
            TRAMITE_ID="3354",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                settings = load_settings()
        finally:
            restore_env(previous)

        self.assertEqual(settings.smtp_user, "sender@test.com")
        self.assertEqual(settings.notify_email, "dest@test.com")
        self.assertEqual(settings.api_params["tramiteId"], 3354)

    def test_notify_email_defaults_when_secret_empty(self) -> None:
        previous = patch_env(
            SMTP_USER="sender@test.com",
            SMTP_PASSWORD="app-pass",
            NOTIFY_EMAIL="",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                settings = load_settings()
        finally:
            restore_env(previous)

        self.assertEqual(settings.notify_email, "sender@test.com")

    def test_load_settings_strips_spaces_from_app_password(self) -> None:
        previous = patch_env(
            SMTP_USER="sender@test.com",
            SMTP_PASSWORD="abcd efgh ijkl mnop",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                settings = load_settings()
        finally:
            restore_env(previous)

        self.assertEqual(settings.smtp_password, "abcdefghijklmnop")

    def test_load_settings_raises_without_smtp(self) -> None:
        previous = patch_env(SMTP_USER="", SMTP_PASSWORD="")
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                with self.assertRaises(ValueError) as ctx:
                    load_settings()
                self.assertIn("SMTP", str(ctx.exception))
        finally:
            restore_env(previous)
            for key in ("SMTP_USER", "SMTP_PASSWORD"):
                os.environ.pop(key, None)


if __name__ == "__main__":
    unittest.main()
