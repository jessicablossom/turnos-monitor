from __future__ import annotations

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

MonitorFrequency = Literal["daily", "weekly"]

DEFAULT_MONITOR_FREQUENCY: MonitorFrequency = "daily"
VALID_MONITOR_FREQUENCIES: frozenset[MonitorFrequency] = frozenset({"daily", "weekly"})
MONDAY_WEEKDAY = 0


def parse_monitor_frequency(raw: str) -> MonitorFrequency:
    value = raw.strip().lower()
    if value not in VALID_MONITOR_FREQUENCIES:
        valid = ", ".join(sorted(VALID_MONITOR_FREQUENCIES))
        raise ValueError(
            f"MONITOR_FREQUENCY inválido: {raw!r}. Valores permitidos: {valid}"
        )
    return value


def should_run_scheduled_check(
    frequency: MonitorFrequency,
    now: datetime,
    timezone: str,
    *,
    is_manual_run: bool,
) -> bool:
    """En cron semanal solo corre los lunes; en ejecución manual siempre corre."""
    if is_manual_run or frequency == "daily":
        return True

    local = now.astimezone(ZoneInfo(timezone))
    return local.weekday() == MONDAY_WEEKDAY
