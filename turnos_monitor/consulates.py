from __future__ import annotations

from dataclasses import dataclass

DEFAULT_CONSULATE_KEY = "milan"
TRAMITE_DRIVER_LICENSE_CONVERSION = (
    "Certificado Consular Conversión Licencia Conducir"
)


@dataclass(frozen=True)
class ConsulateTarget:
    key: str
    label: str
    city: str
    tramite_label: str
    tramite_id: int
    provincia: int
    localidad: int
    turnos_url: str


# Italia tiene solo dos consulados argentinos: Milán y Roma.
CONSULATES_ITALY: dict[str, ConsulateTarget] = {
    "milan": ConsulateTarget(
        key="milan",
        label="Consulado General en Milán",
        city="Milán",
        tramite_label=TRAMITE_DRIVER_LICENSE_CONVERSION,
        tramite_id=3354,
        provincia=100,
        localidad=2911,
        turnos_url=(
            "https://turnos.argentina.gob.ar/turnos/seleccionTurno/"
            "3354/pais/37/prov/100/loc/2911"
        ),
    ),
    "rome": ConsulateTarget(
        key="rome",
        label="Consulado General en Roma",
        city="Roma",
        tramite_label=TRAMITE_DRIVER_LICENSE_CONVERSION,
        tramite_id=3219,
        provincia=67,
        localidad=2875,
        turnos_url=(
            "https://turnos.argentina.gob.ar/turnos/seleccionTurno/"
            "3219/pais/37/prov/67/loc/2875/pda/3616"
        ),
    ),
}


def resolve_consulate(key: str) -> ConsulateTarget:
    normalized = key.strip().lower()
    consulate = CONSULATES_ITALY.get(normalized)
    if consulate is None:
        valid = ", ".join(sorted(CONSULATES_ITALY))
        raise ValueError(
            f"CONSULATE inválido: {key!r}. Valores permitidos: {valid}"
        )
    return consulate
