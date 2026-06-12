from __future__ import annotations

import unittest

from turnos_monitor.consulates import (
    CONSULATES_ITALY,
    resolve_consulate,
)


class TestConsulates(unittest.TestCase):
    def test_catalog_includes_milan_and_rome(self) -> None:
        self.assertIn("milan", CONSULATES_ITALY)
        self.assertIn("rome", CONSULATES_ITALY)

    def test_resolve_rome(self) -> None:
        rome = resolve_consulate("rome")
        self.assertEqual(rome.city, "Roma")
        self.assertEqual(rome.tramite_id, 3219)
        self.assertEqual(rome.provincia, 67)
        self.assertEqual(rome.localidad, 2875)

    def test_resolve_milan_case_insensitive(self) -> None:
        milan = resolve_consulate(" Milan ")
        self.assertEqual(milan.tramite_id, 3354)
        self.assertEqual(milan.provincia, 100)
        self.assertEqual(milan.localidad, 2911)

    def test_resolve_consulate_rejects_unknown(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            resolve_consulate("naples")
        self.assertIn("naples", str(ctx.exception))
        self.assertIn("milan", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
