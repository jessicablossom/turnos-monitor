from __future__ import annotations

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

from turnos_monitor.check_result import (
    CheckOutcome,
    CheckResult,
    format_checks_html,
    format_checks_text,
    has_api_errors,
    has_available_turnos,
)
from turnos_monitor.config import Settings
from turnos_monitor.types import PuntoAtencion

logger = logging.getLogger(__name__)

SUMMARY_SUBJECT_AVAILABLE = "Turnos monitor – Turnos disponibles"
SUMMARY_SUBJECT_UNAVAILABLE = "Turnos monitor – Sin turnos"
SUMMARY_SUBJECT_ERRORS = "Turnos monitor – Completado con errores"


def format_points_html(points: list[PuntoAtencion]) -> str:
    rows = []
    for point in points:
        nombre = point.get("nombre", "Sin nombre")
        direccion = point.get("direccion", "")
        localidad = point.get("localidad", "")
        rows.append(
            f"<li><strong>{nombre}</strong><br>"
            f"{direccion}<br>{localidad}</li>"
        )
    return "<ul>" + "".join(rows) + "</ul>"


def _build_summary_subject(results: list[CheckResult]) -> str:
    if has_available_turnos(results):
        return SUMMARY_SUBJECT_AVAILABLE
    if has_api_errors(results):
        return SUMMARY_SUBJECT_ERRORS
    return SUMMARY_SUBJECT_UNAVAILABLE


def _build_summary_intro(results: list[CheckResult], settings: Settings) -> str:
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    checks = len(results)
    if has_available_turnos(results):
        status = "Resultado positivo: se encontraron turnos disponibles."
    elif has_api_errors(results):
        status = (
            "Resultado con incidencias: hubo errores en al menos una consulta."
        )
    else:
        status = "Resultado negativo: no hay turnos disponibles."
    return (
        f"{status}\n\n"
        f"Zona horaria: {settings.timezone}\n"
        f"Finalizado: {now}\n"
        f"Consultas realizadas: {checks}\n\n"
    )


def _send_email(
    settings: Settings,
    *,
    subject: str,
    body_text: str,
    body_html: str,
) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.smtp_user
    message["To"] = settings.notify_email
    message.attach(MIMEText(body_text, "plain", "utf-8"))
    message.attach(MIMEText(body_html, "html", "utf-8"))

    logger.info("Enviando email a %s", settings.notify_email)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(
            settings.smtp_user,
            [settings.notify_email],
            message.as_string(),
        )
    logger.info("Email enviado correctamente")


def send_availability_email(
    settings: Settings,
    available_points: list[PuntoAtencion],
) -> None:
    subject = "Turnos disponibles – Consulado Milán"
    body_text = (
        "Hay turnos disponibles en al menos un punto de atención.\n\n"
        + "\n".join(
            f"- {p.get('nombre', '?')} ({p.get('direccion', '')})"
            for p in available_points
        )
        + "\n\nReservá en: https://turnos.argentina.gob.ar/\n"
    )
    body_html = (
        "<p><strong>Hay turnos disponibles</strong> en:</p>"
        + format_points_html(available_points)
        + '<p><a href="https://turnos.argentina.gob.ar/">Ir a reservar turno</a></p>'
    )
    _send_email(settings, subject=subject, body_text=body_text, body_html=body_html)


def send_run_summary_email(
    settings: Settings,
    results: list[CheckResult],
) -> None:
    if not results:
        raise ValueError("No hay resultados para incluir en el resumen")

    subject = _build_summary_subject(results)
    intro = _build_summary_intro(results, settings)
    checks_text = format_checks_text(results)
    body_text = intro + "Detalle por consulta:\n" + checks_text + "\n"

    available_blocks = []
    for result in results:
        if result.outcome is CheckOutcome.AVAILABLE and result.available_points:
            available_blocks.append(
                "<h3>Consulta "
                f"{result.index}/{result.total}</h3>"
                + format_points_html(list(result.available_points))
            )

    body_html = (
        f"<p>{intro.replace(chr(10), '<br>')}</p>"
        "<h2>Detalle por consulta</h2>"
        + format_checks_html(results)
    )
    if available_blocks:
        body_html += "<h2>Puntos disponibles</h2>" + "".join(available_blocks)
    body_html += (
        '<p><a href="https://turnos.argentina.gob.ar/">Ir a reservar turno</a></p>'
    )

    _send_email(settings, subject=subject, body_text=body_text, body_html=body_html)
