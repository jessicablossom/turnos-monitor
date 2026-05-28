from __future__ import annotations

import os
from typing import Any

from turnos_monitor.config import Settings

MILAN_API_SAMPLE: dict[str, Any] = {
    "metadata": [],
    "result": [
        {
            "id": 3731,
            "nombre": "Consulado General y Centro de Promoción de la República Argentina en Milán",
            "pais": "Italia",
            "provincia": "Lombardía",
            "localidad": "Milán",
            "direccion": "Via Agnello, 2, 20121 Milano MI, Italia",
            "latitud": 45.465277414728,
            "longitud": 9.1933899,
            "multiturno": 0,
            "disponible": False,
            "hora_uso": "Europe/Rome",
        }
    ],
}


def make_settings(**overrides: Any) -> Settings:
    defaults = {
        "api_url": "https://example.com/api",
        "tramite_id": 3354,
        "provincia": 100,
        "localidad": 2911,
        "timezone": "Europe/Rome",
        "notify_email": "test@example.com",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "user@gmail.com",
        "smtp_password": "secret",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def patch_env(**values: str) -> dict[str, str | None]:
    """Guarda y reemplaza variables de entorno; devuelve el estado anterior."""
    previous: dict[str, str | None] = {}
    for key, value in values.items():
        previous[key] = os.environ.get(key)
        os.environ[key] = value
    return previous


def restore_env(previous: dict[str, str | None]) -> None:
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
