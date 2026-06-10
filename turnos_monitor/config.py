from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from turnos_monitor.constants import (
    DEFAULT_API_URL,
    DEFAULT_LOCALIDAD,
    DEFAULT_PROVINCIA,
    DEFAULT_TIMEZONE,
    DEFAULT_TRAMITE_ID,
)
from turnos_monitor.env_utils import env_or_default


@dataclass(frozen=True)
class Settings:
    api_url: str
    tramite_id: int
    provincia: int
    localidad: int
    timezone: str
    notify_email: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str

    @property
    def api_params(self) -> dict[str, int]:
        return {
            "tramiteId": self.tramite_id,
            "provincia": self.provincia,
            "localidad": self.localidad,
        }


def load_settings(env_path: str | None = None) -> Settings:
    load_dotenv(env_path)

    smtp_user = env_or_default("SMTP_USER", "")
    smtp_password = env_or_default("SMTP_PASSWORD", "").replace(" ", "")
    if not smtp_password or not smtp_user:
        raise ValueError(
            "Faltan SMTP_USER y SMTP_PASSWORD en .env "
            "(para Gmail, usá una contraseña de aplicación)"
        )

    notify_email = env_or_default("NOTIFY_EMAIL", smtp_user)
    if "@" not in notify_email:
        raise ValueError(
            "NOTIFY_EMAIL inválido o vacío. Configurá el secret NOTIFY_EMAIL "
            "o usá SMTP_USER como destinatario."
        )

    return Settings(
        api_url=env_or_default("API_URL", DEFAULT_API_URL),
        tramite_id=int(env_or_default("TRAMITE_ID", str(DEFAULT_TRAMITE_ID))),
        provincia=int(env_or_default("PROVINCIA", str(DEFAULT_PROVINCIA))),
        localidad=int(env_or_default("LOCALIDAD", str(DEFAULT_LOCALIDAD))),
        timezone=env_or_default("TIMEZONE", DEFAULT_TIMEZONE),
        notify_email=notify_email,
        smtp_host=env_or_default("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(env_or_default("SMTP_PORT", "587")),
        smtp_user=smtp_user,
        smtp_password=smtp_password,
    )
