from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from turnos_monitor.types import PuntoAtencion

OUTCOME_LABEL_AVAILABLE = "Turnos disponibles"
OUTCOME_LABEL_UNAVAILABLE = "Sin turnos"
OUTCOME_LABEL_API_ERROR = "Error de API"


class CheckOutcome(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    API_ERROR = "api_error"


@dataclass(frozen=True)
class CheckResult:
    index: int
    total: int
    outcome: CheckOutcome
    detail: str
    available_points: tuple[PuntoAtencion, ...] = ()


def outcome_label(outcome: CheckOutcome) -> str:
    if outcome is CheckOutcome.AVAILABLE:
        return OUTCOME_LABEL_AVAILABLE
    if outcome is CheckOutcome.UNAVAILABLE:
        return OUTCOME_LABEL_UNAVAILABLE
    return OUTCOME_LABEL_API_ERROR


def format_check_line(result: CheckResult) -> str:
    label = outcome_label(result.outcome)
    return f"Consulta {result.index}/{result.total}: {label} — {result.detail}"


def format_checks_text(results: list[CheckResult]) -> str:
    return "\n".join(format_check_line(result) for result in results)


def format_checks_html(results: list[CheckResult]) -> str:
    rows = []
    for result in results:
        label = outcome_label(result.outcome)
        css_class = result.outcome.value.replace("_", "-")
        rows.append(
            f'<li class="{css_class}">'
            f"<strong>Consulta {result.index}/{result.total}</strong>: "
            f"{label} — {result.detail}</li>"
        )
    return "<ul>" + "".join(rows) + "</ul>"


def has_available_turnos(results: list[CheckResult]) -> bool:
    return any(result.outcome is CheckOutcome.AVAILABLE for result in results)


def has_api_errors(results: list[CheckResult]) -> bool:
    return any(result.outcome is CheckOutcome.API_ERROR for result in results)
