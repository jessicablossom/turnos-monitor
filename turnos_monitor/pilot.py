from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import requests

from turnos_monitor.api import (
    build_api_url,
    create_http_session,
    find_available_points,
    parse_availability,
)
from turnos_monitor.constants import (
    DEFAULT_API_URL,
    DEFAULT_LOCALIDAD,
    DEFAULT_PROVINCIA,
    DEFAULT_TRAMITE_ID,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PilotResult:
    url: str
    status_code: int
    points: list[dict[str, object]]
    available_count: int
    raw_json: object

    @property
    def has_availability(self) -> bool:
        return self.available_count > 0


def run_pilot(
    api_url: str = DEFAULT_API_URL,
    tramite_id: int = DEFAULT_TRAMITE_ID,
    provincia: int = DEFAULT_PROVINCIA,
    localidad: int = DEFAULT_LOCALIDAD,
    session: requests.Session | None = None,
) -> PilotResult:
    params = {
        "tramiteId": tramite_id,
        "provincia": provincia,
        "localidad": localidad,
    }
    url = build_api_url(api_url, params)
    http = session or create_http_session()

    logger.info("Prueba piloto: GET %s", url)
    response = http.get(
        url,
        headers={"User-Agent": "TurnosMonitor/1.0", "Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    raw_json = response.json()
    points = parse_availability(raw_json)
    available = find_available_points(points)

    return PilotResult(
        url=url,
        status_code=response.status_code,
        points=[dict(point) for point in points],
        available_count=len(available),
        raw_json=raw_json,
    )


def format_pilot_report(result: PilotResult, indent: int = 2) -> str:
    lines = [
        "=== Prueba piloto – API turnos ===",
        f"URL: {result.url}",
        f"HTTP: {result.status_code}",
        f"Puntos en result: {len(result.points)}",
        f"Disponibles (disponible=true): {result.available_count}",
        "",
    ]

    for point in result.points:
        nombre = point.get("nombre", "?")
        disponible = point.get("disponible")
        direccion = point.get("direccion", "")
        lines.append(f"  • {nombre}")
        lines.append(f"    disponible: {disponible}")
        if direccion:
            lines.append(f"    dirección: {direccion}")

    lines.extend(
        [
            "",
            "--- JSON completo ---",
            json.dumps(result.raw_json, ensure_ascii=False, indent=indent),
        ]
    )
    return "\n".join(lines)
