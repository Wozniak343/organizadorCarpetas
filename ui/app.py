import logging
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from core.monitor import MonitorArchivos
from core.organizador import OrganizadorArchivos
from utils.categorias import MAPA_CATEGORIAS
from utils.configuracion import cargar_configuracion, guardar_configuracion


EXTENSIONES_TEXTO = {
    ".txt",
    ".md",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".log",
    ".ini",
    ".cfg",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".sh",
    ".bat",
    ".cmd",
}


class AplicacionAutoFileOrganizer(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Auto File Organizer")
        self.geometry("1020x700")
        self.minsize(1020, 700)

        self.configuracion = cargar_configuracion()
        self.monitor: MonitorArchivos | None = None
        self.carpeta_actual: Path | None = None
        self.archivo_actual: Path | None = None
        self.logger = logging.getLogger("auto_file_organizer")

        self._construir_interfaz()
        self._cargar_carpeta_reciente()
        self.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)

    def _construir_interfaz(self) -> None:
        self.fondo_principal = ctk.CTkFrame(self, corner_radius=20, fg_color="#111317")
        self.fondo_principal.pack(fill="both", expand=True, padx=18, pady=18)

        encabezado = ctk.CTkFrame(self.fondo_principal, corner_radius=16, fg_color="#171a20")
        encabezado.pack(fill="x", padx=18, pady=(18, 12))

        titulo = ctk.CTkLabel(
            encabezado,
            text="Auto File Organizer",
            font=("Segoe UI", 24, "bold"),
            text_color="#f5f7fb",
        )
        titulo.pack(anchor="w", padx=18, pady=(16, 2))

        subtitulo = ctk.CTkLabel(
            encabezado,
            text="Explora, edita y organiza archivos desde una sola ventana",
            font=("Segoe UI", 13),
            text_color="#9aa4b2",
        )
        subtitulo.pack(anchor="w", padx=18, pady=(0, 16))

        self.panel_estado = ctk.CTkFrame(self.fondo_principal, corner_radius=16, fg_color="#171a20")
        self.panel_estado.pack(fill="x", padx=18, pady=(0, 12))

        fila_estado = ctk.CTkFrame(self.panel_estado, fg_color="transparent")
        fila_estado.pack(fill="x", padx=18, pady=(16, 10))

        self.indicador_estado = ctk.CTkLabel(fila_estado, text="●", font=("Segoe UI", 24, "bold"), text_color="#ef4444")
        self.indicador_estado.pack(side="left")

        self.etiqueta_estado = ctk.CTkLabel(
            fila_estado,
            text="Detenido",
            font=("Segoe UI", 18, "bold"),
            text_color="#f5f7fb",
        )
        self.etiqueta_estado.pack(side="left", padx=(10, 0))

        self.etiqueta_carpeta = ctk.CTkLabel(
            self.panel_estado,
            text="Carpeta seleccionada: Ninguna",
            font=("Segoe UI", 13),
            text_color="#9aa4b2",
            wraplength=940,
            justify="left",
        )
        self.etiqueta_carpeta.pack(anchor="w", padx=18, pady=(0, 16))

        controles = ctk.CTkFrame(self.fondo_principal, corner_radius=16, fg_color="#171a20")
        controles.pack(fill="x", padx=18, pady=(0, 12))

        boton_fila = ctk.CTkFrame(controles, fg_color="transparent")
        boton_fila.pack(fill="x", padx=18, pady=18)

        self.boton_seleccionar = ctk.CTkButton(
            boton_fila,
            text="Seleccionar carpeta",
            command=self._seleccionar_carpeta,
            height=42,
            corner_radius=12,
        )
        self.boton_seleccionar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_iniciar = ctk.CTkButton(
            boton_fila,
            text="Iniciar monitoreo",
            command=self._iniciar_monitoreo,
            height=42,
            corner_radius=12,
        )
        self.boton_iniciar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_detener = ctk.CTkButton(
            boton_fila,
            text="Detener monitoreo",
            command=self._detener_monitoreo,
            height=42,
            corner_radius=12,
            fg_color="#3f4654",
            hover_color="#2f3542",
        )
        self.boton_detener.pack(side="left", fill="x", expand=True)

        acciones = ctk.CTkFrame(controles, fg_color="transparent")
        acciones.pack(fill="x", padx=18, pady=(0, 18))

        self.boton_organizar = ctk.CTkButton(
            acciones,
            text="Organizar ahora",
            command=self._organizar_ahora,
            height=38,
            corner_radius=12,
            fg_color="#2d7dd2",
            hover_color="#2360a8",
        )
        self.boton_organizar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_recargar = ctk.CTkButton(
            acciones,
            text="Recargar vista",
            command=self._recargar_explorador,
            height=38,
            corner_radius=12,
            fg_color="#3f4654",
            hover_color="#2f3542",
        )
        self.boton_recargar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_guardar = ctk.CTkButton(
            acciones,
            text="Guardar archivo",
            command=self._guardar_archivo_actual,
            height=38,
            corner_radius=12,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        self.boton_guardar.pack(side="left", fill="x", expand=True)

        contenido = ctk.CTkFrame(self.fondo_principal, corner_radius=16, fg_color="#171a20")
        contenido.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        explorador_panel = ctk.CTkFrame(contenido, corner_radius=14, fg_color="#0f1115")
        explorador_panel.pack(side="left", fill="both", expand=False, padx=(16, 8), pady=16)
        explorador_panel.configure(width=320)

        titulo_explorador = ctk.CTkLabel(
            explorador_panel,
            text="Archivos y carpetas",
            font=("Segoe UI", 15, "bold"),
            text_color="#f5f7fb",
        )
        titulo_explorador.pack(anchor="w", padx=14, pady=(14, 8))

        self.frame_arbol = ctk.CTkFrame(explorador_panel, fg_color="#0f1115")
        self.frame_arbol.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#0f1115",
            fieldbackground="#0f1115",
            foreground="#e5e7eb",
            rowheight=26,
            borderwidth=0,
            relief="flat",
        )
        estilo.map("Treeview", background=[("selected", "#1f2937")], foreground=[("selected", "#ffffff")])

        self.arbol = ttk.Treeview(self.frame_arbol, show="tree")
        barra_arbol = ttk.Scrollbar(self.frame_arbol, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=barra_arbol.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        barra_arbol.pack(side="right", fill="y")
        self.arbol.bind("<<TreeviewOpen>>", self._al_expandir_nodo)
        self.arbol.bind("<<TreeviewSelect>>", self._al_seleccionar_elemento)
        self.arbol.bind("<Double-1>", self._al_doble_click)

        editor_panel = ctk.CTkFrame(contenido, corner_radius=14, fg_color="#0f1115")
        editor_panel.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        self.etiqueta_archivo = ctk.CTkLabel(
            editor_panel,
            text="Ningun archivo seleccionado",
            font=("Segoe UI", 15, "bold"),
            text_color="#f5f7fb",
            wraplength=520,
            justify="left",
        )
        self.etiqueta_archivo.pack(anchor="w", padx=14, pady=(14, 6))

        self.etiqueta_tipo = ctk.CTkLabel(
            editor_panel,
            text="Selecciona un archivo de texto para editarlo",
            font=("Segoe UI", 12),
            text_color="#9aa4b2",
            wraplength=520,
            justify="left",
        )
        self.etiqueta_tipo.pack(anchor="w", padx=14, pady=(0, 10))

        self.editor_texto = ctk.CTkTextbox(
            editor_panel,
            corner_radius=12,
            fg_color="#111827",
            border_width=1,
            border_color="#243244",
            font=("Consolas", 12),
        )
        self.editor_texto.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.editor_texto.insert("end", "Selecciona una carpeta para explorar sus archivos.\n")
        self.editor_texto.configure(state="disabled")

        barra_estado = ctk.CTkFrame(self.fondo_principal, corner_radius=14, fg_color="#171a20")
        barra_estado.pack(fill="x", padx=18, pady=(0, 18))

        self.etiqueta_actividad = ctk.CTkLabel(
            barra_estado,
            text="Listo",
            font=("Segoe UI", 12),
            text_color="#9aa4b2",
        )
        self.etiqueta_actividad.pack(anchor="w", padx=16, pady=12)

    def _cargar_carpeta_reciente(self) -> None:
        carpeta = self.configuracion.get("ultima_carpeta", "")
        if not carpeta:
            return

        ruta = Path(carpeta)
        if ruta.exists() and ruta.is_dir():
            self.carpeta_actual = ruta
            self.etiqueta_carpeta.configure(text=f"Carpeta seleccionada: {ruta}")
            self._recargar_explorador()

    def _seleccionar_carpeta(self) -> None:
        carpeta = filedialog.askdirectory(title="Selecciona una carpeta")
        if not carpeta:
            return

        ruta = Path(carpeta)
        self.carpeta_actual = ruta
        self.etiqueta_carpeta.configure(text=f"Carpeta seleccionada: {ruta}")
        guardar_configuracion(str(ruta))
        self.configuracion["ultima_carpeta"] = str(ruta)
        self._actualizar_actividad(f"Carpeta seleccionada: {ruta}")
        self._recargar_explorador()

    def _iniciar_monitoreo(self) -> None:
        if self.carpeta_actual is None:
            messagebox.showwarning("Auto File Organizer", "Selecciona una carpeta primero")
            return

        if self.monitor and self.monitor.activo:
            return

        self.monitor = MonitorArchivos(self.carpeta_actual, MAPA_CATEGORIAS, self._registrar_mensaje)

        try:
            self.monitor.iniciar()
        except FileNotFoundError:
            self.logger.warning("La carpeta seleccionada no existe")
            messagebox.showerror("Auto File Organizer", "La carpeta seleccionada no existe")
            return
        except OSError as error:
            self.logger.exception("No se pudo iniciar el monitoreo")
            messagebox.showerror("Auto File Organizer", f"No se pudo iniciar el monitoreo: {error}")
            return

        self._actualizar_estado(True)
        self._actualizar_actividad("Monitoreo activo")

    def _detener_monitoreo(self) -> None:
        if self.monitor is not None:
            self.monitor.detener()
        self._actualizar_estado(False)
        self._actualizar_actividad("Monitoreo detenido")

    def _organizar_ahora(self) -> None:
        if self.carpeta_actual is None:
            messagebox.showwarning("Auto File Organizer", "Selecciona una carpeta primero")
            return

        organizador = self.monitor.organizador if self.monitor is not None else OrganizadorArchivos(
            MAPA_CATEGORIAS,
            self._registrar_mensaje,
        )

        cantidad = organizador.organizar_carpeta(self.carpeta_actual)
        self._actualizar_actividad(f"Organizacion manual completada: {cantidad} archivo(s)")
        self._recargar_explorador()

    def _recargar_explorador(self) -> None:
        self.arbol.delete(*self.arbol.get_children())
        self.archivo_actual = None
        self._mostrar_archivo(None)

        if self.carpeta_actual is None or not self.carpeta_actual.exists():
            self.etiqueta_actividad.configure(text="Selecciona una carpeta para comenzar")
            return

        self._cargar_raiz()
        self.etiqueta_actividad.configure(text=f"Explorando: {self.carpeta_actual}")

    def _cargar_raiz(self) -> None:
        if self.carpeta_actual is None:
            return

        self.nodo_raiz = self.arbol.insert("", "end", text=self.carpeta_actual.name, open=True, values=(str(self.carpeta_actual),))
        self._cargar_nodos(self.nodo_raiz, self.carpeta_actual)
        self.arbol.item(self.nodo_raiz, open=True)
        self.arbol.selection_set(self.nodo_raiz)
        self.arbol.focus(self.nodo_raiz)

    def _cargar_nodos(self, nodo_padre: str, ruta_padre: Path) -> None:
        for ruta_hija in self._obtener_elementos(ruta_padre):
            texto = ruta_hija.name + ("/" if ruta_hija.is_dir() else "")
            nodo_hijo = self.arbol.insert(nodo_padre, "end", text=texto, values=(str(ruta_hija),))
            if ruta_hija.is_dir() and self._tiene_hijos(ruta_hija):
                self.arbol.insert(nodo_hijo, "end", text="Cargando...", values=("",))

    def _obtener_elementos(self, ruta: Path) -> list[Path]:
        try:
            return sorted(ruta.iterdir(), key=lambda elemento: (not elemento.is_dir(), elemento.name.lower()))
        except OSError:
            return []

    def _tiene_hijos(self, ruta: Path) -> bool:
        try:
            next(ruta.iterdir())
            return True
        except (OSError, StopIteration):
            return False

    def _al_expandir_nodo(self, _evento=None) -> None:
        nodo = self.arbol.focus()
        if not nodo:
            return

        ruta = self._ruta_desde_nodo(nodo)
        if ruta is None or not ruta.is_dir():
            return

        hijos = self.arbol.get_children(nodo)
        if len(hijos) == 1 and self.arbol.item(hijos[0], "text") == "Cargando...":
            self.arbol.delete(hijos[0])
            self._cargar_nodos(nodo, ruta)

    def _al_seleccionar_elemento(self, _evento=None) -> None:
        seleccion = self.arbol.selection()
        if not seleccion:
            return

        ruta = self._ruta_desde_nodo(seleccion[0])
        if ruta is None:
            return

        if ruta.is_dir():
            self.archivo_actual = None
            self._mostrar_archivo(ruta)
            return

        self.archivo_actual = ruta
        self._mostrar_archivo(ruta)

    def _al_doble_click(self, _evento=None) -> None:
        seleccion = self.arbol.selection()
        if not seleccion:
            return

        ruta = self._ruta_desde_nodo(seleccion[0])
        if ruta is None:
            return

        if ruta.is_dir():
            estado = self.arbol.item(seleccion[0], "open")
            self.arbol.item(seleccion[0], open=not estado)
            if not estado:
                self._al_expandir_nodo()
            return

        self._abrir_archivo(ruta)

    def _ruta_desde_nodo(self, nodo: str) -> Path | None:
        valores = self.arbol.item(nodo, "values")
        if not valores:
            return self.carpeta_actual

        ruta = valores[0]
        if not ruta:
            return None

        return Path(ruta)

    def _abrir_archivo(self, ruta: Path) -> None:
        if not ruta.exists() or not ruta.is_file():
            return

        if ruta.suffix.lower() not in EXTENSIONES_TEXTO:
            self._mostrar_archivo(ruta, "Este archivo no se puede editar directamente desde la app.\n", editable=False)
            messagebox.showinfo("Auto File Organizer", "Este archivo no se puede editar directamente desde la app")
            return

        try:
            contenido = ruta.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                contenido = ruta.read_text(encoding="latin-1")
            except OSError as error:
                messagebox.showerror("Auto File Organizer", f"No se pudo abrir el archivo: {error}")
                return
        except OSError as error:
            messagebox.showerror("Auto File Organizer", f"No se pudo abrir el archivo: {error}")
            return

        self.archivo_actual = ruta
        self._mostrar_archivo(ruta, contenido)

    def _mostrar_archivo(self, ruta: Path | None, contenido: str | None = None, editable: bool = True) -> None:
        self.editor_texto.configure(state="normal")
        self.editor_texto.delete("1.0", "end")

        if ruta is None:
            self.etiqueta_archivo.configure(text="Ningun archivo seleccionado")
            self.etiqueta_tipo.configure(text="Selecciona un archivo de texto para editarlo")
            self.editor_texto.insert("end", "Selecciona una carpeta para explorar sus archivos.\n")
            self.editor_texto.configure(state="disabled")
            return

        if ruta.is_dir():
            self.etiqueta_archivo.configure(text=f"Carpeta: {ruta.name}")
            self.etiqueta_tipo.configure(text="Carpeta seleccionada en el explorador")
            self.editor_texto.insert("end", f"Carpeta seleccionada:\n{ruta}\n")
            self.editor_texto.configure(state="disabled")
            return

        self.etiqueta_archivo.configure(text=f"Archivo: {ruta.name}")
        self.etiqueta_tipo.configure(text=f"Ruta completa: {ruta}")

        if contenido is None:
            try:
                contenido = ruta.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    contenido = ruta.read_text(encoding="latin-1")
                except OSError:
                    contenido = ""
            except OSError:
                contenido = ""

        self.editor_texto.insert("end", contenido or "")
        self.editor_texto.edit_modified(False)
        self.editor_texto.configure(state="normal" if editable else "disabled")

    def _guardar_archivo_actual(self) -> None:
        if self.archivo_actual is None or not self.archivo_actual.is_file():
            messagebox.showwarning("Auto File Organizer", "Selecciona un archivo de texto para guardarlo")
            return

        if self.archivo_actual.suffix.lower() not in EXTENSIONES_TEXTO:
            messagebox.showwarning("Auto File Organizer", "Solo se pueden editar archivos de texto")
            return

        contenido = self.editor_texto.get("1.0", "end-1c")

        try:
            self.archivo_actual.write_text(contenido, encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Auto File Organizer", f"No se pudo guardar el archivo: {error}")
            return

        self._actualizar_actividad(f"Archivo guardado: {self.archivo_actual.name}")
        self._mostrar_archivo(self.archivo_actual, contenido)

    def _actualizar_estado(self, activo: bool) -> None:
        if activo:
            self.indicador_estado.configure(text_color="#22c55e")
            self.etiqueta_estado.configure(text="Monitoreando...")
        else:
            self.indicador_estado.configure(text_color="#ef4444")
            self.etiqueta_estado.configure(text="Detenido")

    def _registrar_mensaje(self, mensaje: str) -> None:
        self.logger.info(mensaje)
        self._actualizar_actividad(mensaje)

    def _actualizar_actividad(self, mensaje: str) -> None:
        self.etiqueta_actividad.configure(text=mensaje)

    def _cerrar_aplicacion(self) -> None:
        if self.monitor is not None:
            self.monitor.detener()
        self.destroy()
