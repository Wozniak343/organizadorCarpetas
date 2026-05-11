from __future__ import annotations

import logging
from pathlib import Path


NOMBRE_LOGGER = "auto_file_organizer"


def configurar_logging() -> logging.Logger:
    logger = logging.getLogger(NOMBRE_LOGGER)
    if logger.handlers:
        return logger

    raiz_proyecto = Path(__file__).resolve().parents[1]
    directorio_logs = raiz_proyecto / "data"
    directorio_logs.mkdir(parents=True, exist_ok=True)
    ruta_log = directorio_logs / "auto_file_organizer.log"

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formato = logging.Formatter(
        "%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s",
        datefmt="%I:%M:%S %p",
    )

    manejador_archivo = logging.FileHandler(ruta_log, encoding="utf-8")
    manejador_archivo.setLevel(logging.INFO)
    manejador_archivo.setFormatter(formato)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.INFO)
    manejador_consola.setFormatter(formato)

    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)

    return logger