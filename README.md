# turnos-monitor

Python app that polls the Argentina consulate appointment API **daily from 00:00 to 01:00** (`Europe/Rome`) **every 5 minutes** and, when the run finishes, sends a **summary email** listing each check and its result (available, unavailable, or API error).

**Default target:** Milan consulate (`tramiteId=3354`, `provincia=100`, `localidad=2911`).

## Deploy (GitHub Actions)

Workflow: [`.github/workflows/turnos-monitor.yml`](.github/workflows/turnos-monitor.yml) — runs at **00:00 Europe/Rome** and executes the 1-hour check window.

**Secrets** (Settings → Environments → **LIVE** → Environment secrets):

| Secret | Description |
|--------|-------------|
| `SMTP_USER` | Sender Gmail address |
| `SMTP_PASSWORD` | [Gmail app password](https://myaccount.google.com/apppasswords) |
| `NOTIFY_EMAIL` | *(optional)* Recipient; defaults to `SMTP_USER` if unset |

**Manual run:** Actions → **Turnos monitor** → **Run workflow** → `pilot` (API only), `once`, or `window`.

## Local setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set SMTP_USER and SMTP_PASSWORD
```

Use `.venv/bin/python` if `python` is not on your PATH.

## Commands

| Command | Description |
|---------|-------------|
| `pilot` | Live API test, no email |
| `once` | Single check + summary email |
| `window` | 12 checks over 1 h (every 5 min) + summary email |
| `daemon` | 24/7 scheduler (local) |

```bash
python -m turnos_monitor pilot
python -m turnos_monitor once
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## API

```
GET .../disponibilidad/puntosatencion?tramiteId=3354&provincia=100&localidad=2911
```

Available when any item in `result` has `"disponible": true`.
