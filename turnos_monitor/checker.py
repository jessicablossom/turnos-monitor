from __future__ import annotations

import logging
import smtplib

import requests

from turnos_monitor.api import fetch_availability
from turnos_monitor.config import Settings
from turnos_monitor.email_notifier import send_availability_email

logger = logging.getLogger(__name__)


def run_single_check(settings: Settings) -> bool:
    """
    Ejecuta una consulta. Devuelve True si había turnos y se envió email.
    """
    try:
        available = fetch_availability(settings.api_url, settings.api_params)
    except requests.RequestException as error:
        logger.error("Error al consultar la API: %s", error)
        return False

    if not available:
        logger.info("Sin turnos disponibles por ahora")
        return False

    try:
        send_availability_email(settings, available)
    except (smtplib.SMTPException, OSError) as error:
        logger.error("Error al enviar email: %s", error)
        return False

    return True
