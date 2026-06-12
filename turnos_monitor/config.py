from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from turnos_monitor.consulates import DEFAULT_CONSULATE_KEY, resolve_consulate
from turnos_monitor.constants import DEFAULT_API_URL, DEFAULT_TIMEZONE
from turnos_monitor.env_utils import env_or_default
from turnos_monitor.monitor_frequency import (
    DEFAULT_MONITOR_FREQUENCY,
    MonitorFrequency,
    parse_monitor_frequency,
)


@dataclass(frozen=True)
class Settings:
    api_url: str
    consulate_key: str
    consulate_label: str
    tramite_label: str
    tramite_id: int
    provincia: int
    localidad: int
    timezone: str
    monitor_frequency: MonitorFrequency
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


def _smtp_missing_message(smtp_user: str, smtp_password: str) -> str:
    missing: list[str] = []
    if not smtp_user:
        missing.append("SMTP_USER")
    if not smtp_password:
        missing.append("SMTP_PASSWORD")

    if os.environ.get("GITHUB_ACTIONS") == "true":
        return (
            f"Faltan los secrets de GitHub Actions: {', '.join(missing)}. "
            "Configuralos en Settings → Environments → LIVE → Environment secrets "
            "(o como repository secrets). Para Gmail usá una contraseña de aplicación "
            "(no la contraseña normal): https://myaccount.google.com/apppasswords"
        )

    return (
        f"Faltan {', '.join(missing)} en .env "
        "(para Gmail, usá una contraseña de aplicación)"
    )


def _resolve_api_target() -> tuple[str, str, str, int, int, int]:
    consulate = resolve_consulate(
        env_or_default("CONSULATE", DEFAULT_CONSULATE_KEY)
    )
    tramite_id = int(
        env_or_default("TRAMITE_ID", str(consulate.tramite_id))
    )
    provincia = int(
        env_or_default("PROVINCIA", str(consulate.provincia))
    )
    localidad = int(
        env_or_default("LOCALIDAD", str(consulate.localidad))
    )
    return (
        consulate.key,
        consulate.label,
        consulate.tramite_label,
        tramite_id,
        provincia,
        localidad,
    )


def load_settings(env_path: str | None = None) -> Settings:
    load_dotenv(env_path)

    smtp_user = env_or_default("SMTP_USER", "")
    smtp_password = env_or_default("SMTP_PASSWORD", "").replace(" ", "")
    if not smtp_password or not smtp_user:
        raise ValueError(_smtp_missing_message(smtp_user, smtp_password))

    notify_email = env_or_default("NOTIFY_EMAIL", smtp_user)
    if "@" not in notify_email:
        raise ValueError(
            "NOTIFY_EMAIL inválido o vacío. Configurá el secret NOTIFY_EMAIL "
            "o usá SMTP_USER como destinatario."
        )

    (
        consulate_key,
        consulate_label,
        tramite_label,
        tramite_id,
        provincia,
        localidad,
    ) = _resolve_api_target()

    return Settings(
        api_url=env_or_default("API_URL", DEFAULT_API_URL),
        consulate_key=consulate_key,
        consulate_label=consulate_label,
        tramite_label=tramite_label,
        tramite_id=tramite_id,
        provincia=provincia,
        localidad=localidad,
        timezone=env_or_default("TIMEZONE", DEFAULT_TIMEZONE),
        monitor_frequency=parse_monitor_frequency(
            env_or_default("MONITOR_FREQUENCY", DEFAULT_MONITOR_FREQUENCY)
        ),
        notify_email=notify_email,
        smtp_host=env_or_default("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(env_or_default("SMTP_PORT", "587")),
        smtp_user=smtp_user,
        smtp_password=smtp_password,
    )
