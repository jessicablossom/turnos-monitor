# turnos-monitor

[![CI](https://github.com/jessicablossom/turnos-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/jessicablossom/turnos-monitor/actions/workflows/ci.yml)

Monitor de turnos del consulado argentino: consulta la API de [turnos.argentina.gob.ar](https://turnos.argentina.gob.ar/), detecta disponibilidad y envía un **email de resumen**. Self-hosted con GitHub Actions o en local.

**Trámite configurado:** Certificado Consular Conversión Licencia Conducir.

**Consulado por defecto:** Milán. En Italia solo hay dos consulados argentinos:

| `CONSULATE` | Ciudad | `tramiteId` | `provincia` | `localidad` |
|-------------|--------|-------------|-------------|-------------|
| `milan` | Milán | `3354` | `100` | `2911` |
| `rome` | Roma | `3219` | `67` | `2875` |

Cada consulado usa un `tramiteId` distinto para el mismo trámite.

> **Disclaimer:** API no oficial ni documentada. Herramienta informativa: no garantiza conseguir turno. Usala con responsabilidad y respetá los límites razonables de consulta.

## Frecuencia

Una sola consulta a la API por ejecución. Dos modos:

| Modo | Cuándo corre |
|------|----------------|
| `daily` | Todos los días a las 00:00 (`Europe/Rome`) |
| `weekly` | Solo los lunes a las 00:00 (`Europe/Rome`) |

## Quick start (5 minutos)

### 1. Probar la API (sin email)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m turnos_monitor pilot
```

### 2. Probar con email (local)

```bash
cp .env.example .env   # completá SMTP_USER y SMTP_PASSWORD
python -m turnos_monitor once
```

### 3. Deploy con GitHub Actions (fork)

1. Hacé **fork** de este repo.
2. Configurá los [secrets de SMTP](#secrets-en-github-actions).
3. Elegí la frecuencia con la [variable `MONITOR_FREQUENCY`](#frecuencia-en-github-actions) (`daily` o `weekly`).
4. **Actions → Turnos monitor → Run workflow** para probar manualmente.

## Comandos

| Comando | Descripción |
|---------|-------------|
| `pilot` | Consulta la API y muestra el resultado (sin email) |
| `once` | Un chequeo + email de resumen |
| `daemon` | Scheduler local 24/7 según `MONITOR_FREQUENCY` |

```bash
python -m turnos_monitor pilot
python -m turnos_monitor once
```

## Configuración local

Copiá `.env.example` a `.env`:

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `SMTP_USER` | Sí | Gmail emisor |
| `SMTP_PASSWORD` | Sí | [Contraseña de aplicación](https://myaccount.google.com/apppasswords) |
| `NOTIFY_EMAIL` | No | Destinatario; por defecto usa `SMTP_USER` |
| `CONSULATE` | No | `milan` o `rome` (default: `milan`) |
| `MONITOR_FREQUENCY` | No | `daily` o `weekly` (default: `daily`) |
| `TRAMITE_ID` | No | Override manual del trámite |
| `PROVINCIA` | No | Override manual de provincia en la API |
| `LOCALIDAD` | No | Override manual de localidad en la API |
| `TIMEZONE` | No | Zona horaria (default: `Europe/Rome`) |

## Secrets en GitHub Actions

### SMTP

**Opción A — Repository secrets** (recomendado para forks):

1. **Settings → Secrets and variables → Actions → New repository secret**
2. Borrá `environment: LIVE` del workflow si usás esta opción

| Secret | Requerido | Descripción |
|--------|-----------|-------------|
| `SMTP_USER` | Sí | Gmail emisor |
| `SMTP_PASSWORD` | Sí | Contraseña de aplicación de Gmail |
| `NOTIFY_EMAIL` | No | Destinatario; si no existe, usa `SMTP_USER` |

**Opción B — Environment secrets** (este repo):

1. **Settings → Environments → LIVE → Environment secrets**
2. Mismos nombres que arriba

### Frecuencia en GitHub Actions

**Settings → Secrets and variables → Actions → Variables → New repository variable**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `MONITOR_FREQUENCY` | `daily` o `weekly` | Default del cron (si no existe, usa `daily`) |
| `CONSULATE` | `milan` o `rome` | Consulado a monitorear (default: `milan`) |

En ejecución manual podés elegir `daily` o `weekly` desde el dropdown del workflow.

> **Gmail:** necesitás verificación en 2 pasos para la contraseña de aplicación.

## Otros países

El catálogo de Italia está completo (`milan`, `rome`). Para otro país:

1. Abrí [turnos.argentina.gob.ar](https://turnos.argentina.gob.ar/) y elegí país, consulado y trámite.
2. Copiá los IDs de la URL o de **DevTools → Network** (`puntosatencion`).
3. Sumalo en `turnos_monitor/consulates.py` y abrí un PR.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Licencia

[MIT](LICENSE) — libre para usar, modificar y distribuir. Sin garantía.
