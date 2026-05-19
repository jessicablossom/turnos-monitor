DEFAULT_API_URL = (
    "https://turnos-api.argentina.gob.ar/api/v1.0/disponibilidad/puntosatencion"
)
DEFAULT_TRAMITE_ID = 3354
DEFAULT_PROVINCIA = 100
DEFAULT_LOCALIDAD = 2911
DEFAULT_TIMEZONE = "Europe/Berlin"
DEFAULT_NOTIFY_EMAIL = "jessica.francavilla86@gmail.com"

# Ventana diaria: 00:00–01:00 hora local, cada 5 minutos
WINDOW_START_HOUR = 0
WINDOW_START_MINUTE = 0
WINDOW_DURATION_MINUTES = 60
CHECK_INTERVAL_MINUTES = 5

REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = "TurnosMonitor/1.0 (personal use; availability check)"
