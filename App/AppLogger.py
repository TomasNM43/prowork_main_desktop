"""
AppLogger — Logging centralizado para ProWork.
Escribe en ~/prowork.log y captura:
  - Excepciones Python no capturadas (sys.excepthook)
  - Excepciones en hilos secundarios (threading.excepthook)
  - Notificaciones explícitas de cada módulo

Uso en cualquier módulo:
    from AppLogger import get_logger
    log = get_logger(__name__)
    log.info("mensaje")
    log.error("error", exc_info=True)
"""

import os
import sys
import logging
import threading
import traceback

# Ruta del archivo de log (carpeta personal del usuario)
LOG_PATH = os.path.join(os.path.expanduser('~'), 'prowork.log')

def setup_logging() -> None:
    """Inicializa el sistema de logging. Llamar UNA sola vez desde main.py."""
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d — %(message)s',
        encoding='utf-8',
        force=True,
    )

    root = logging.getLogger()

    # --- Excepciones Python no capturadas en el hilo principal ---
    def _excepthook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        root.critical(
            "Excepción no capturada en hilo principal",
            exc_info=(exc_type, exc_value, exc_tb),
        )

    sys.excepthook = _excepthook

    # --- Excepciones no capturadas en hilos secundarios (Python ≥ 3.8) ---
    def _threading_excepthook(args):
        if args.exc_type is SystemExit:
            return
        root.critical(
            f"Excepción no capturada en hilo '{args.thread.name}'",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    threading.excepthook = _threading_excepthook

    root.info(f"=== ProWork iniciado — log en {LOG_PATH} ===")


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger con el nombre dado (usar __name__ del módulo)."""
    return logging.getLogger(name)
