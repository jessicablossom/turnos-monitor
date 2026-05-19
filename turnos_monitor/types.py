from __future__ import annotations

from typing import TypedDict


class PuntoAtencion(TypedDict, total=False):
    id: int
    nombre: str
    pais: str
    provincia: str
    localidad: str
    direccion: str
    disponible: bool
    hora_uso: str


class ApiResponse(TypedDict):
    metadata: list[object]
    result: list[PuntoAtencion]
