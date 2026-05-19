from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from turnos_monitor.checker import run_single_check
from turnos_monitor.config import load_settings
from turnos_monitor.pilot import format_pilot_report, run_pilot
from turnos_monitor.scheduler_app import start_scheduler
from turnos_monitor.window import is_within_daily_window, run_window_checks


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

    sub.add_parser("once", help="Un solo chequeo ahora")
    sub.add_parser(
        "pilot",
        help="Prueba piloto: consulta la API y muestra la respuesta (sin email)",
    )
    sub.add_parser(
        "window",
        help="Ventana de 1 h con chequeos cada 5 min (para cron)",
    )
    sub.add_parser(
        "daemon",
        help="Proceso 24/7; dispara la ventana cada día a las 00:00 CET/CEST",
    )

    run_if = sub.add_parser(
        "run-if-window",
        help="Ejecuta ventana solo si estamos entre 00:00 y 01:00 hora local",
    )
    run_if.add_argument(
        "--force",
        action="store_true",
        help="Ignorar comprobación horaria (útil para pruebas)",
    )

    return parser


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
        run_single_check(settings)
        return 0

    if args.command == "window":
        run_window_checks(settings)
        return 0

    if args.command == "run-if-window":
        now = datetime.now()
        if args.force or is_within_daily_window(now, settings):
            run_window_checks(settings)
        else:
            logging.info("Fuera de la ventana horaria; no se ejecuta nada")
        return 0

    if args.command == "daemon":
        start_scheduler(settings)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
