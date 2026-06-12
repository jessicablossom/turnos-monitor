from __future__ import annotations

import argparse
import logging
import sys

from turnos_monitor.checker import run_single_check
from turnos_monitor.config import Settings, load_settings
from turnos_monitor.email_notifier import send_run_summary_email
from turnos_monitor.pilot import format_pilot_report, run_pilot
from turnos_monitor.scheduler_app import start_scheduler


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Monitor de turnos Consulado Argentina en Milán",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("once", help="Un solo chequeo ahora + email de resumen")
    sub.add_parser(
        "pilot",
        help="Prueba piloto: consulta la API y muestra la respuesta (sin email)",
    )
    sub.add_parser(
        "daemon",
        help="Proceso 24/7; un chequeo según MONITOR_FREQUENCY (00:00 Europe/Rome)",
    )

    return parser


def _run_once_with_summary(settings: Settings) -> None:
    result = run_single_check(settings, index=1, total=1)
    send_run_summary_email(settings, [result])


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    if args.command == "pilot":
        try:
            result = run_pilot()
            print(format_pilot_report(result))
            return 0 if result.status_code == 200 else 1
        except Exception as error:
            logging.error("Prueba piloto fallida: %s", error)
            return 1

    try:
        settings = load_settings()
    except ValueError as error:
        logging.error("%s", error)
        return 1

    if args.command == "once":
        _run_once_with_summary(settings)
        return 0

    if args.command == "daemon":
        start_scheduler(settings)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
