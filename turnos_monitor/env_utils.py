from __future__ import annotations

import os


def env_or_default(key: str, default: str) -> str:
    """
    Lee una variable de entorno; si falta o está vacía (solo espacios),
    devuelve el valor por defecto.

    GitHub Actions inyecta secrets inexistentes como cadena vacía, no como
    variable ausente — por eso no alcanza con os.environ.get(key, default).
    """
    value = os.environ.get(key, "").strip()
    return value if value else default
