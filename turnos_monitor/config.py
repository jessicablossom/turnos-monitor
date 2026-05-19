from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from turnos_monitor.constants import (
    DEFAULT_API_URL,
    DEFAULT_LOCALIDAD,
    DEFAULT_NOTIFY_EMAIL,
    DEFAULT_PROVINCIA,
    DEFAULT_TIMEZONE,
    DEFAULT_TRAMITE_ID,
)


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

    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    smtp_user = os.environ.get("SMTP_USER", "")
    if not smtp_password or not smtp_user:
        raise ValueError(
            "Faltan SMTP_USER y SMTP_PASSWORD en .env "
            "(para Gmail, usá una contraseña de aplicación)"
        )

    return Settings(
        api_url=os.environ.get("API_URL", DEFAULT_API_URL),
        tramite_id=int(os.environ.get("TRAMITE_ID", DEFAULT_TRAMITE_ID)),
        provincia=int(os.environ.get("PROVINCIA", DEFAULT_PROVINCIA)),
        localidad=int(os.environ.get("LOCALIDAD", DEFAULT_LOCALIDAD)),
        timezone=os.environ.get("TIMEZONE", DEFAULT_TIMEZONE),
        notify_email=os.environ.get("NOTIFY_EMAIL", DEFAULT_NOTIFY_EMAIL),
        smtp_host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.environ.get("SMTP_PORT", "587")),
        smtp_user=smtp_user,
        smtp_password=smtp_password,
    )
