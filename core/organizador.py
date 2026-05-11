import logging
import shutil
import time
from pathlib import Path

from utils.categorias import MAPA_CATEGORIAS, obtener_categoria, obtener_nombres_carpetas


class OrganizadorArchivos:
    def __init__(self, mapa_categorias: dict[str, set[str]] | None = None, registrar_mensaje=None) -> None:
        self.mapa_categorias = mapa_categorias or MAPA_CATEGORIAS
        self.nombres_carpetas = obtener_nombres_carpetas(self.mapa_categorias)
        self.logger = logging.getLogger("auto_file_organizer")
        self.registrar_mensaje = registrar_mensaje or self.logger.info

    def organizar_carpeta(self, ruta_carpeta: Path | str) -> int:
        carpeta = Path(ruta_carpeta)
        if not carpeta.exists() or not carpeta.is_dir():
            return 0

        cantidad = 0
        for elemento in carpeta.iterdir():
            if elemento.is_file():
                if self.organizar_archivo(elemento):
                    cantidad += 1

        return cantidad

    def organizar_archivo(self, ruta_archivo: Path | str) -> Path | None:
        archivo = Path(ruta_archivo)

        if not archivo.exists() or not archivo.is_file():
            return None

        if archivo.parent.name.lower() in self.nombres_carpetas:
            return None

        if not self._esperar_estabilidad(archivo):
            self.registrar_mensaje(f"No se pudo organizar: {archivo.name}")
            return None

        categoria = obtener_categoria(archivo.name, self.mapa_categorias)
        carpeta_destino = archivo.parent / categoria
        carpeta_destino.mkdir(parents=True, exist_ok=True)

        destino = self._resolver_conflicto(carpeta_destino / archivo.name)

        try:
            shutil.move(str(archivo), str(destino))
        except OSError as error:
            self.logger.exception("Error al mover archivo")
            self.registrar_mensaje(f"Error al mover {archivo.name}: {error}")
            return None

        self.registrar_mensaje(f"Archivo movido: {archivo.name} -> {categoria}")
        return destino

    def _resolver_conflicto(self, destino: Path) -> Path:
        if not destino.exists():
            return destino

        contador = 1
        while True:
            candidato = destino.with_name(f"{destino.stem}_{contador}{destino.suffix}")
            if not candidato.exists():
                return candidato
            contador += 1

    def _esperar_estabilidad(self, archivo: Path) -> bool:
        tamaño_anterior = -1

        for _ in range(5):
            try:
                tamaño_actual = archivo.stat().st_size
            except OSError:
                return False

            if tamaño_actual == tamaño_anterior:
                return True

            tamaño_anterior = tamaño_actual
            time.sleep(0.15)

        return True
