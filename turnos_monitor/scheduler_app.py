from __future__ import annotations

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from turnos_monitor.checker import run_single_check
from turnos_monitor.config import Settings
from turnos_monitor.constants import SCHEDULE_HOUR, SCHEDULE_MINUTE
from turnos_monitor.email_notifier import send_run_summary_email

logger = logging.getLogger(__name__)


def start_scheduler(settings: Settings) -> None:
    scheduler = BlockingScheduler(timezone=settings.timezone)

    def scheduled_job() -> None:
        logger.info("Chequeo programado disparado a las %s", datetime.now())
        result = run_single_check(settings, index=1, total=1)
        send_run_summary_email(settings, [result])

    if settings.monitor_frequency == "weekly":
        trigger = CronTrigger(
            day_of_week="mon",
            hour=SCHEDULE_HOUR,
            minute=SCHEDULE_MINUTE,
            timezone=settings.timezone,
        )
        schedule_label = f"semanal (lunes {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d})"
        job_id = "weekly_turnos_check"
    else:
        trigger = CronTrigger(
            hour=SCHEDULE_HOUR,
            minute=SCHEDULE_MINUTE,
            timezone=settings.timezone,
        )
        schedule_label = f"diario ({SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d})"
        job_id = "daily_turnos_check"

    scheduler.add_job(
        scheduled_job,
        trigger,
        id=job_id,
        replace_existing=True,
    )

    logger.info(
        "Scheduler activo. Chequeo %s %s",
        schedule_label,
        settings.timezone,
    )
    scheduler.start()
