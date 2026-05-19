from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from turnos_monitor.config import Settings
from turnos_monitor.types import PuntoAtencion

logger = logging.getLogger(__name__)


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
