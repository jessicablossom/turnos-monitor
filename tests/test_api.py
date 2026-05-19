from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import requests

from tests.helpers import MILAN_API_SAMPLE
from turnos_monitor.api import (
    build_api_url,
    create_http_session,
    fetch_availability,
    fetch_points,
    find_available_points,
    parse_availability,
)


class TestApi(unittest.TestCase):
    def test_create_http_session_ignores_proxy_env(self) -> None:
        session = create_http_session()
        self.assertFalse(session.trust_env)

    def test_build_api_url(self) -> None:
        url = build_api_url(
            "https://example.com/api",
            {"tramiteId": 3354, "provincia": 100, "localidad": 2911},
        )
        self.assertEqual(
            url,
            "https://example.com/api?tramiteId=3354&provincia=100&localidad=2911",
        )

    def test_parse_milan_sample(self) -> None:
        points = parse_availability(MILAN_API_SAMPLE)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0]["id"], 3731)
        self.assertFalse(points[0]["disponible"])

    def test_find_available_points_empty(self) -> None:
        points = parse_availability(MILAN_API_SAMPLE)
        self.assertEqual(find_available_points(points), [])

    def test_find_available_points_when_true(self) -> None:
        points = [
            {"disponible": False},
            {"disponible": True, "nombre": "Milán"},
        ]
        available = find_available_points(points)
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0]["nombre"], "Milán")

    def test_parse_skips_non_dict_items(self) -> None:
        payload = {"metadata": [], "result": [{"disponible": True}, "invalid", None]}
        points = parse_availability(payload)
        self.assertEqual(len(points), 1)

    def test_parse_missing_result_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            parse_availability({"metadata": []})
        self.assertIn("result", str(ctx.exception))

    def test_parse_invalid_root_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_availability([])

    def test_fetch_points_with_mock_session(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = MILAN_API_SAMPLE
        mock_response.raise_for_status = MagicMock()

        session = MagicMock(spec=requests.Session)
        session.get.return_value = mock_response

        points = fetch_points(
            "https://example.com/api",
            {"tramiteId": 3354, "provincia": 100, "localidad": 2911},
            session=session,
        )
        self.assertEqual(len(points), 1)
        session.get.assert_called_once()
        call_kwargs = session.get.call_args
        self.assertIn("tramiteId=3354", call_kwargs[0][0])

    def test_fetch_availability_returns_only_available(self) -> None:
        payload = {
            "metadata": [],
            "result": [
                {"disponible": False},
                {"disponible": True, "nombre": "X"},
            ],
        }
        mock_response = MagicMock()
        mock_response.json.return_value = payload
        mock_response.raise_for_status = MagicMock()
        session = MagicMock(spec=requests.Session)
        session.get.return_value = mock_response

        available = fetch_availability(
            "https://example.com/api",
            {"tramiteId": 1, "provincia": 1, "localidad": 1},
            session=session,
        )
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0]["nombre"], "X")


if __name__ == "__main__":
    unittest.main()
