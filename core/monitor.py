import logging
from queue import Empty, Queue
from threading import Event, Thread
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.organizador import OrganizadorArchivos
from utils.categorias import MAPA_CATEGORIAS, obtener_nombres_carpetas


class ManejadorEventosArchivos(FileSystemEventHandler):
    def __init__(self, cola_rutas: Queue, nombres_carpetas: set[str]) -> None:
        super().__init__()
        self.cola_rutas = cola_rutas
        self.nombres_carpetas = nombres_carpetas

    def on_created(self, evento) -> None:
        if evento.is_directory:
            return
        self._agregar_ruta(evento.src_path)

    def on_moved(self, evento) -> None:
        if evento.is_directory:
            return
        self._agregar_ruta(evento.dest_path)

    def _agregar_ruta(self, ruta_evento: str) -> None:
        ruta = Path(ruta_evento)
        if ruta.parent.name.lower() in self.nombres_carpetas:
            return
        self.cola_rutas.put(ruta)


class MonitorArchivos:
    def __init__(self, ruta_carpeta: Path | str, mapa_categorias: dict[str, set[str]] | None = None, registrar_mensaje=None) -> None:
        self.ruta_carpeta = Path(ruta_carpeta)
        self.mapa_categorias = mapa_categorias or MAPA_CATEGORIAS
        self.logger = logging.getLogger("auto_file_organizer")
        self.registrar_mensaje = registrar_mensaje or self.logger.info
        self.organizador = OrganizadorArchivos(self.mapa_categorias, self.registrar_mensaje)
        self.cola_rutas: Queue = Queue()
        self.detener_evento = Event()
        self.observer: Observer | None = None
        self.hilo_trabajo: Thread | None = None
        self.activo = False
        self.nombres_carpetas = obtener_nombres_carpetas(self.mapa_categorias)

    def iniciar(self) -> bool:
        if self.activo:
            return False

        if not self.ruta_carpeta.exists() or not self.ruta_carpeta.is_dir():
            raise FileNotFoundError("La carpeta seleccionada no existe")

        self.detener_evento.clear()
        self.observer = Observer()
        manejador = ManejadorEventosArchivos(self.cola_rutas, self.nombres_carpetas)
        self.observer.schedule(manejador, str(self.ruta_carpeta), recursive=False)
        self.observer.start()

        self.hilo_trabajo = Thread(target=self._procesar_cola, daemon=True)
        self.hilo_trabajo.start()
        self.activo = True
        self.registrar_mensaje("Monitoreo iniciado")
        return True

    def detener(self) -> None:
        if not self.activo:
            return

        self.detener_evento.set()

        if self.observer is not None:
            self.observer.stop()
            self.observer.join(timeout=2)
            self.observer = None

        if self.hilo_trabajo is not None:
            self.hilo_trabajo.join(timeout=2)
            self.hilo_trabajo = None

        while True:
            try:
                self.cola_rutas.get_nowait()
            except Empty:
                break

        self.activo = False
        self.registrar_mensaje("Monitoreo detenido")

    def _procesar_cola(self) -> None:
        while not self.detener_evento.is_set() or not self.cola_rutas.empty():
            try:
                ruta_archivo = self.cola_rutas.get(timeout=0.2)
            except Empty:
                continue

            try:
                self.organizador.organizar_archivo(ruta_archivo)
            except Exception as error:
                self.logger.exception("Error inesperado al procesar archivo")
                self.registrar_mensaje(f"Error inesperado al procesar {ruta_archivo.name}: {error}")
            self.cola_rutas.task_done()
