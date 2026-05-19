from __future__ import annotations

import logging
from typing import cast

import requests

from turnos_monitor.constants import REQUEST_TIMEOUT_SECONDS, USER_AGENT
from turnos_monitor.types import ApiResponse, PuntoAtencion

logger = logging.getLogger(__name__)


def build_api_url(base_url: str, params: dict[str, int]) -> str:
    query = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{base_url}?{query}"


def parse_availability(payload: object) -> list[PuntoAtencion]:
    if not isinstance(payload, dict):
        raise ValueError("La respuesta de la API no es un objeto JSON")

    data = cast(ApiResponse, payload)
    result = data.get("result")
    if not isinstance(result, list):
        raise ValueError("La respuesta no contiene 'result' como lista")

    return [cast(PuntoAtencion, item) for item in result if isinstance(item, dict)]


def find_available_points(points: list[PuntoAtencion]) -> list[PuntoAtencion]:
    return [point for point in points if point.get("disponible") is True]


def create_http_session() -> requests.Session:
    session = requests.Session()
    # Evita que un proxy del sistema bloquee la API de turnos
    session.trust_env = False
    return session


def fetch_points(
    api_url: str,
    params: dict[str, int],
    session: requests.Session | None = None,
) -> list[PuntoAtencion]:
    http = session or create_http_session()
    url = build_api_url(api_url, params)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    logger.info("Consultando API: %s", url)
    response = http.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return parse_availability(response.json())


def fetch_availability(
    api_url: str,
    params: dict[str, int],
    session: requests.Session | None = None,
) -> list[PuntoAtencion]:
    points = fetch_points(api_url, params, session=session)
    available = find_available_points(points)

    logger.info(
        "Puntos totales: %d | Disponibles: %d",
        len(points),
        len(available),
    )
    return available
