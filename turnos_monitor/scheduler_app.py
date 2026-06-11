from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from turnos_monitor.checker import run_single_check
from turnos_monitor.config import Settings
from turnos_monitor.constants import WINDOW_START_HOUR, WINDOW_START_MINUTE
from turnos_monitor.email_notifier import send_run_summary_email

logger = logging.getLogger(__name__)


def start_scheduler(settings: Settings) -> None:
    scheduler = BlockingScheduler(timezone=settings.timezone)

    def weekly_job() -> None:
        logger.info("Job semanal disparado a las %s", datetime.now())
        result = run_single_check(settings, index=1, total=1)
        send_run_summary_email(settings, [result])

    scheduler.add_job(
        weekly_job,
        CronTrigger(
            day_of_week="mon",
            hour=WINDOW_START_HOUR,
            minute=WINDOW_START_MINUTE,
            timezone=settings.timezone,
        ),
        id="weekly_turnos_check",
        replace_existing=True,
    )

    logger.info(
        "Scheduler activo. Chequeo semanal: lunes %02d:%02d %s",
        WINDOW_START_HOUR,
        WINDOW_START_MINUTE,
        settings.timezone,
    )
    scheduler.start()
