from __future__ import annotations

import os
import unittest

from tests.helpers import patch_env, restore_env
from turnos_monitor.env_utils import env_or_default


class TestEnvUtils(unittest.TestCase):
    def test_returns_default_when_missing(self) -> None:
        key = "MISSING_VAR"
        previous_value = os.environ.pop(key, None)
        try:
            self.assertEqual(env_or_default(key, "fallback"), "fallback")
        finally:
            if previous_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous_value

    def test_returns_default_when_empty(self) -> None:
        previous = patch_env(EMPTY_VAR="")
        try:
            self.assertEqual(env_or_default("EMPTY_VAR", "fallback"), "fallback")
        finally:
            restore_env(previous)

    def test_returns_default_when_whitespace(self) -> None:
        previous = patch_env(WHITESPACE_VAR="   ")
        try:
            self.assertEqual(env_or_default("WHITESPACE_VAR", "fallback"), "fallback")
        finally:
            restore_env(previous)

    def test_returns_trimmed_value(self) -> None:
        previous = patch_env(TRIMMED_VAR="  value@example.com  ")
        try:
            self.assertEqual(
                env_or_default("TRIMMED_VAR", "fallback"),
                "value@example.com",
            )
        finally:
            restore_env(previous)


if __name__ == "__main__":
    unittest.main()
