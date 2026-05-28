from __future__ import annotations

import logging

import requests

from turnos_monitor.api import fetch_availability
from turnos_monitor.check_result import CheckOutcome, CheckResult
from turnos_monitor.config import Settings
from turnos_monitor.types import PuntoAtencion

logger = logging.getLogger(__name__)


def _format_available_detail(points: list[PuntoAtencion]) -> str:
    names = ", ".join(point.get("nombre", "?") for point in points)
    return f"{len(points)} punto(s): {names}"


def run_single_check(
    settings: Settings,
    *,
    index: int = 1,
    total: int = 1,
) -> CheckResult:
    """
    Ejecuta una consulta a la API y devuelve el resultado estructurado.
    """
    try:
        available = fetch_availability(settings.api_url, settings.api_params)
    except requests.RequestException as error:
        logger.error("Error al consultar la API: %s", error)
        return CheckResult(
            index=index,
            total=total,
            outcome=CheckOutcome.API_ERROR,
            detail=str(error),
        )

    if not available:
        logger.info("Sin turnos disponibles por ahora")
        return CheckResult(
            index=index,
            total=total,
            outcome=CheckOutcome.UNAVAILABLE,
            detail="Ningún punto con disponible=true",
        )

    detail = _format_available_detail(available)
    logger.info("Turnos disponibles: %s", detail)
    return CheckResult(
        index=index,
        total=total,
        outcome=CheckOutcome.AVAILABLE,
        detail=detail,
        available_points=tuple(available),
    )
