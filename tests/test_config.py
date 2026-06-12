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

    def test_consulate_rome_resolves_api_params(self) -> None:
        previous = patch_env(
            SMTP_USER="sender@test.com",
            SMTP_PASSWORD="app-pass",
            CONSULATE="rome",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                settings = load_settings()
        finally:
            restore_env(previous)

        self.assertEqual(settings.consulate_key, "rome")
        self.assertEqual(settings.consulate_label, "Consulado General en Roma")
        self.assertIn("Licencia Conducir", settings.tramite_label)
        self.assertEqual(settings.api_params["tramiteId"], 3219)
        self.assertEqual(settings.api_params["provincia"], 67)
        self.assertEqual(settings.api_params["localidad"], 2875)

    def test_monitor_frequency_defaults_to_daily(self) -> None:
        previous = patch_env(
            SMTP_USER="sender@test.com",
            SMTP_PASSWORD="app-pass",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                settings = load_settings()
        finally:
            restore_env(previous)

        self.assertEqual(settings.monitor_frequency, "daily")

    def test_monitor_frequency_accepts_weekly(self) -> None:
        previous = patch_env(
            SMTP_USER="sender@test.com",
            SMTP_PASSWORD="app-pass",
            MONITOR_FREQUENCY="weekly",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                settings = load_settings()
        finally:
            restore_env(previous)

        self.assertEqual(settings.monitor_frequency, "weekly")

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
                self.assertIn("SMTP_USER", str(ctx.exception))
                self.assertIn("SMTP_PASSWORD", str(ctx.exception))
        finally:
            restore_env(previous)
            for key in ("SMTP_USER", "SMTP_PASSWORD"):
                os.environ.pop(key, None)

    def test_load_settings_raises_with_github_actions_hint(self) -> None:
        previous = patch_env(
            SMTP_USER="",
            SMTP_PASSWORD="",
            GITHUB_ACTIONS="true",
        )
        try:
            with patch("turnos_monitor.config.load_dotenv"):
                with self.assertRaises(ValueError) as ctx:
                    load_settings()
                self.assertIn("GitHub Actions", str(ctx.exception))
                self.assertIn("LIVE", str(ctx.exception))
        finally:
            restore_env(previous)
            for key in ("SMTP_USER", "SMTP_PASSWORD", "GITHUB_ACTIONS"):
                os.environ.pop(key, None)


if __name__ == "__main__":
    unittest.main()
