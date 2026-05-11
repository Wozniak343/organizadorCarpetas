import json
from pathlib import Path

RUTA_CONFIGURACION = Path.home() / ".auto_file_organizer" / "configuracion.json"


def cargar_configuracion() -> dict:
    if not RUTA_CONFIGURACION.exists():
        return {"ultima_carpeta": ""}

    try:
        datos = json.loads(RUTA_CONFIGURACION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ultima_carpeta": ""}

    return {
        "ultima_carpeta": str(datos.get("ultima_carpeta", "")),
    }


def guardar_configuracion(ultima_carpeta: str) -> None:
    RUTA_CONFIGURACION.parent.mkdir(parents=True, exist_ok=True)
    contenido = {"ultima_carpeta": ultima_carpeta}
    RUTA_CONFIGURACION.write_text(json.dumps(contenido, indent=2, ensure_ascii=True), encoding="utf-8")
