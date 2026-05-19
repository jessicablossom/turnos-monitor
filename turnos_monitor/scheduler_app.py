from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from turnos_monitor.config import Settings
from turnos_monitor.constants import WINDOW_START_HOUR, WINDOW_START_MINUTE
from turnos_monitor.window import run_window_checks

logger = logging.getLogger(__name__)


def start_scheduler(settings: Settings) -> None:
    """
    Proceso en segundo plano: cada día a las 00:00 (CET/CEST) lanza la ventana de 1 h.
    """
    scheduler = BlockingScheduler(timezone=settings.timezone)

    def daily_job() -> None:
        logger.info("Job diario disparado a las %s", datetime.now())
        run_window_checks(settings, stop_on_success=False)

    scheduler.add_job(
        daily_job,
        CronTrigger(
            hour=WINDOW_START_HOUR,
            minute=WINDOW_START_MINUTE,
            timezone=settings.timezone,
        ),
        id="daily_turnos_window",
        replace_existing=True,
    )

    logger.info(
        "Scheduler activo. Ventana diaria: %02d:%02d %s (duración 1 h, cada 5 min)",
        WINDOW_START_HOUR,
        WINDOW_START_MINUTE,
        settings.timezone,
    )
    scheduler.start()
