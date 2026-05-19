# Monitor de turnos – Consulado Milán

Mini app en Python que, **cada día de 00:00 a 01:00** (hora de Europa Central, `Europe/Berlin` — incluye CET y CEST), consulta la API de turnos **cada 5 minutos** y te envía un email si algún punto tiene `"disponible": true`.

## Requisitos

- Python 3.9+
- Cuenta Gmail con [contraseña de aplicación](https://myaccount.google.com/apppasswords) (o otro SMTP)

## Instalación

```bash
cd ~/turnos-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editá .env con SMTP_USER y SMTP_PASSWORD
```

## Uso

| Comando | Descripción |
|---------|-------------|
| `python -m turnos_monitor once` | Un chequeo ahora (prueba) |
| `python -m turnos_monitor window` | 12 chequeos en 1 h (para lanzar a las 00:00) |
| `python -m turnos_monitor daemon` | Proceso 24/7; ventana automática cada medianoche |
| `python -m turnos_monitor run-if-window` | Solo corre si es entre 00:00 y 01:00 |

### Opción A: Daemon (Mac siempre encendida)

```bash
source .venv/bin/activate
python -m turnos_monitor daemon
```

Dejalo corriendo con `tmux`, `screen`, o como servicio de macOS.

### Opción B: Cron (sin proceso 24/7)

A las 00:00 lanza la ventana de 1 hora:

```bash
crontab -e
```

Añadí (ajustá la ruta):

```cron
0 0 * * * cd /Users/jessica/turnos-monitor && .venv/bin/python -m turnos_monitor window >> /tmp/turnos-monitor.log 2>&1
```

**Nota:** `cron` en macOS usa la zona horaria del sistema. Configurá macOS en `Europe/Berlin` o usá `daemon` para manejar CET/CEST con precisión.

### Opción C: Cron cada 5 min (solo en la hora correcta)

```cron
*/5 0 * * * cd /Users/jessica/turnos-monitor && .venv/bin/python -m turnos_monitor run-if-window >> /tmp/turnos-monitor.log 2>&1
```

Esto ejecuta un chequeo cada 5 minutos solo durante la hora 00:xx (según la TZ del sistema).

## Prueba piloto (API en vivo, sin email)

```bash
python -m turnos_monitor pilot
```

Muestra estado HTTP, cada punto de atención y el JSON completo.

## Tests

```bash
python -m unittest discover -s tests -v
```

24 tests unitarios (API, checker, config, email, ventana horaria, piloto).

## Variables de entorno

Ver `.env.example`. Lo mínimo:

- `SMTP_USER` – email desde el que se envía (ej. tu Gmail)
- `SMTP_PASSWORD` – contraseña de aplicación
- `NOTIFY_EMAIL` – destino (por defecto: jessica.francavilla86@gmail.com)

## API monitoreada

```
https://turnos-api.argentina.gob.ar/api/v1.0/disponibilidad/puntosatencion?tramiteId=3354&provincia=100&localidad=2911
```

Se considera disponible cuando **cualquier** elemento en `result` tiene `"disponible": true`.
