from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from turnos_monitor.checker import run_single_check
from turnos_monitor.config import Settings
from turnos_monitor.constants import (
    CHECK_INTERVAL_MINUTES,
    WINDOW_DURATION_MINUTES,
    WINDOW_START_HOUR,
    WINDOW_START_MINUTE,
)

logger = logging.getLogger(__name__)


def is_within_daily_window(now: datetime, settings: Settings) -> bool:
    tz = ZoneInfo(settings.timezone)
    local = now.astimezone(tz)
    start = local.replace(
        hour=WINDOW_START_HOUR,
        minute=WINDOW_START_MINUTE,
        second=0,
        microsecond=0,
    )
    end = start + timedelta(minutes=WINDOW_DURATION_MINUTES)
    return start <= local < end


def seconds_until_window_start(now: datetime, settings: Settings) -> float:
    tz = ZoneInfo(settings.timezone)
    local = now.astimezone(tz)
    start_today = local.replace(
        hour=WINDOW_START_HOUR,
        minute=WINDOW_START_MINUTE,
        second=0,
        microsecond=0,
    )
    if local < start_today:
        target = start_today
    else:
        target = start_today + timedelta(days=1)
    return (target - local).total_seconds()


def run_window_checks(settings: Settings, stop_on_success: bool = False) -> int:
    """
    Ejecuta consultas cada 5 minutos durante 1 hora (12 chequeos).
    Devuelve la cantidad de emails enviados.
    """
    interval_seconds = CHECK_INTERVAL_MINUTES * 60
    checks_count = WINDOW_DURATION_MINUTES // CHECK_INTERVAL_MINUTES
    emails_sent = 0

    logger.info(
        "Iniciando ventana: %d chequeos cada %d min",
        checks_count,
        CHECK_INTERVAL_MINUTES,
    )

    for index in range(checks_count):
        logger.info("Chequeo %d/%d", index + 1, checks_count)
        if run_single_check(settings):
            emails_sent += 1
            if stop_on_success:
                logger.info("Turnos encontrados; deteniendo ventana")
                break

        if index < checks_count - 1:
            time.sleep(interval_seconds)

    return emails_sent
