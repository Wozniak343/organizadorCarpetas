import logging
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from core.monitor import MonitorArchivos
from core.organizador import OrganizadorArchivos
from utils.categorias import MAPA_CATEGORIAS
from utils.configuracion import cargar_configuracion, guardar_configuracion


class AplicacionAutoFileOrganizer(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Auto File Organizer")
        self.geometry("980x640")
        self.minsize(940, 620)

        self.configuracion = cargar_configuracion()
        self.monitor: MonitorArchivos | None = None
        self.carpeta_actual: Path | None = None
        self.ruta_seleccionada: Path | None = None
        self.logger = logging.getLogger("auto_file_organizer")

        self._construir_interfaz()
        self._cargar_carpeta_reciente()
        self.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)

    def _construir_interfaz(self) -> None:
        self.fondo_principal = ctk.CTkFrame(self, corner_radius=16, fg_color="#111317")
        self.fondo_principal.pack(fill="both", expand=True, padx=14, pady=14)

        encabezado = ctk.CTkFrame(self.fondo_principal, corner_radius=12, fg_color="#171a20")
        encabezado.pack(fill="x", padx=12, pady=(12, 8))

        titulo = ctk.CTkLabel(
            encabezado,
            text="Auto File Organizer",
            font=("Segoe UI", 26, "bold"),
            text_color="#f5f7fb",
        )
        titulo.pack(anchor="w", padx=16, pady=(14, 2))

        subtitulo = ctk.CTkLabel(
            encabezado,
            text="Organiza y renombra archivos de forma simple",
            font=("Segoe UI", 12),
            text_color="#9aa4b2",
        )
        subtitulo.pack(anchor="w", padx=16, pady=(0, 14))

        self.panel_estado = ctk.CTkFrame(self.fondo_principal, corner_radius=12, fg_color="#171a20")
        self.panel_estado.pack(fill="x", padx=12, pady=(0, 8))

        fila_estado = ctk.CTkFrame(self.panel_estado, fg_color="transparent")
        fila_estado.pack(fill="x", padx=14, pady=(12, 8))

        self.indicador_estado = ctk.CTkLabel(fila_estado, text="●", font=("Segoe UI", 24, "bold"), text_color="#ef4444")
        self.indicador_estado.pack(side="left")

        self.etiqueta_estado = ctk.CTkLabel(
            fila_estado,
            text="Detenido",
            font=("Segoe UI", 16, "bold"),
            text_color="#f5f7fb",
        )
        self.etiqueta_estado.pack(side="left", padx=(10, 0))

        self.etiqueta_carpeta = ctk.CTkLabel(
            self.panel_estado,
            text="Carpeta seleccionada: Ninguna",
            font=("Segoe UI", 12),
            text_color="#9aa4b2",
            wraplength=900,
            justify="left",
        )
        self.etiqueta_carpeta.pack(anchor="w", padx=14, pady=(0, 12))

        controles = ctk.CTkFrame(self.fondo_principal, corner_radius=12, fg_color="#171a20")
        controles.pack(fill="x", padx=12, pady=(0, 8))

        boton_fila = ctk.CTkFrame(controles, fg_color="transparent")
        boton_fila.pack(fill="x", padx=14, pady=(12, 6))

        self.boton_seleccionar = ctk.CTkButton(
            boton_fila,
            text="Seleccionar carpeta",
            command=self._seleccionar_carpeta,
            height=32,
            corner_radius=10,
        )
        self.boton_seleccionar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_recargar = ctk.CTkButton(
            boton_fila,
            text="Recargar",
            command=self._recargar_explorador,
            height=32,
            corner_radius=10,
            fg_color="#3f4654",
            hover_color="#2f3542",
        )
        self.boton_recargar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_organizar = ctk.CTkButton(
            boton_fila,
            text="Organizar ahora",
            command=self._organizar_ahora,
            height=32,
            corner_radius=10,
            fg_color="#2d7dd2",
            hover_color="#2360a8",
        )
        self.boton_organizar.pack(side="left", fill="x", expand=True)

        acciones = ctk.CTkFrame(controles, fg_color="transparent")
        acciones.pack(fill="x", padx=14, pady=(0, 12))

        self.boton_iniciar = ctk.CTkButton(
            acciones,
            text="Iniciar",
            command=self._iniciar_monitoreo,
            height=32,
            corner_radius=10,
            fg_color="#2d7dd2",
            hover_color="#2360a8",
        )
        self.boton_iniciar.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.boton_detener = ctk.CTkButton(
            acciones,
            text="Detener",
            command=self._detener_monitoreo,
            height=32,
            corner_radius=10,
            fg_color="#3f4654",
            hover_color="#2f3542",
        )
        self.boton_detener.pack(side="left", padx=(0, 10), fill="x", expand=True)

        contenido = ctk.CTkFrame(self.fondo_principal, corner_radius=12, fg_color="#171a20")
        contenido.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        explorador_panel = ctk.CTkFrame(contenido, corner_radius=12, fg_color="#0f1115")
        explorador_panel.pack(side="left", fill="both", expand=True, padx=(12, 8), pady=12)
        explorador_panel.configure(width=560)

        titulo_explorador = ctk.CTkLabel(
            explorador_panel,
            text="Archivos y carpetas",
            font=("Segoe UI", 15, "bold"),
            text_color="#f5f7fb",
        )
        titulo_explorador.pack(anchor="w", padx=12, pady=(12, 6))

        fila_arbol_botones = ctk.CTkFrame(explorador_panel, fg_color="transparent")
        fila_arbol_botones.pack(fill="x", padx=12, pady=(0, 8))

        self.boton_expandir = ctk.CTkButton(
            fila_arbol_botones,
            text="Expandir",
            command=self._expandir_todo,
            height=28,
            corner_radius=8,
            fg_color="#3f4654",
            hover_color="#2f3542",
        )
        self.boton_expandir.pack(side="left", padx=(0, 8), fill="x", expand=True)

        self.boton_contraer = ctk.CTkButton(
            fila_arbol_botones,
            text="Contraer",
            command=self._contraer_todo,
            height=28,
            corner_radius=8,
            fg_color="#3f4654",
            hover_color="#2f3542",
        )
        self.boton_contraer.pack(side="left", fill="x", expand=True)

        self.frame_arbol = ctk.CTkFrame(explorador_panel, fg_color="#0f1115")
        self.frame_arbol.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#111827",
            fieldbackground="#111827",
            foreground="#f3f4f6",
            rowheight=28,
            borderwidth=0,
            relief="flat",
        )
        estilo.configure(
            "Treeview.Heading",
            background="#1f2937",
            foreground="#e5e7eb",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

        self.arbol = ttk.Treeview(
            self.frame_arbol,
            columns=("ruta", "tipo"),
            displaycolumns=("tipo",),
            show="tree headings",
        )
        self.arbol.heading("#0", text="Nombre")
        self.arbol.column("#0", width=235, minwidth=180, stretch=True)
        self.arbol.heading("tipo", text="Tipo")
        self.arbol.column("tipo", width=75, minwidth=70, stretch=False, anchor="center")
        self.arbol.column("ruta", width=0, stretch=False)
        barra_arbol = ttk.Scrollbar(self.frame_arbol, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=barra_arbol.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        barra_arbol.pack(side="right", fill="y")
        self.arbol.bind("<<TreeviewOpen>>", self._al_expandir_nodo)
        self.arbol.bind("<<TreeviewSelect>>", self._al_seleccionar_elemento)
        self.arbol.bind("<Double-1>", self._al_doble_click)

        editor_panel = ctk.CTkFrame(contenido, corner_radius=12, fg_color="#0f1115")
        editor_panel.pack(side="right", fill="y", expand=False, padx=(8, 12), pady=12)
        editor_panel.configure(width=300)

        self.etiqueta_archivo = ctk.CTkLabel(
            editor_panel,
            text="Ningun archivo seleccionado",
            font=("Segoe UI", 14, "bold"),
            text_color="#f5f7fb",
            wraplength=260,
            justify="left",
        )
        self.etiqueta_archivo.pack(anchor="w", padx=12, pady=(12, 4))

        self.etiqueta_tipo = ctk.CTkLabel(
            editor_panel,
            text="Selecciona un archivo o carpeta para renombrarlo",
            font=("Segoe UI", 11),
            text_color="#9aa4b2",
            wraplength=260,
            justify="left",
        )
        self.etiqueta_tipo.pack(anchor="w", padx=12, pady=(0, 8))

        self.panel_renombrado = ctk.CTkFrame(
            editor_panel,
            corner_radius=10,
            fg_color="#111827",
            border_width=1,
            border_color="#243244",
        )
        self.panel_renombrado.pack(fill="x", expand=False, padx=12, pady=(0, 12))

        self.entrada_nombre = ctk.CTkEntry(
            self.panel_renombrado,
            height=36,
            corner_radius=8,
            placeholder_text="Nuevo nombre",
        )
        self.entrada_nombre.pack(fill="x", padx=14, pady=(14, 8))

        self.boton_aplicar_nombre = ctk.CTkButton(
            self.panel_renombrado,
            text="Aplicar nombre",
            command=self._renombrar_elemento,
            height=32,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        self.boton_aplicar_nombre.pack(fill="x", padx=14, pady=(0, 8))

        self.etiqueta_ayuda = ctk.CTkLabel(
            self.panel_renombrado,
            text="No se muestra contenido del archivo. Solo renombrado.",
            font=("Segoe UI", 11),
            text_color="#9aa4b2",
            wraplength=250,
            justify="left",
        )
        self.etiqueta_ayuda.pack(anchor="w", padx=14, pady=(0, 14))

        barra_estado = ctk.CTkFrame(self.fondo_principal, corner_radius=10, fg_color="#171a20")
        barra_estado.pack(fill="x", padx=12, pady=(0, 12))

        self.etiqueta_actividad = ctk.CTkLabel(
            barra_estado,
            text="Listo",
            font=("Segoe UI", 11),
            text_color="#9aa4b2",
        )
        self.etiqueta_actividad.pack(anchor="w", padx=12, pady=8)

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
        self.ruta_seleccionada = None
        self._mostrar_detalle(None)

        if self.carpeta_actual is None or not self.carpeta_actual.exists():
            self.etiqueta_actividad.configure(text="Selecciona una carpeta para comenzar")
            return

        self._cargar_raiz()
        self.etiqueta_actividad.configure(text=f"Explorando: {self.carpeta_actual}")

    def _cargar_raiz(self) -> None:
        if self.carpeta_actual is None:
            return

        self.nodo_raiz = self.arbol.insert(
            "",
            "end",
            text=self.carpeta_actual.name,
            open=True,
            values=(str(self.carpeta_actual), "Carpeta"),
        )
        self._cargar_nodos(self.nodo_raiz, self.carpeta_actual)
        self.arbol.item(self.nodo_raiz, open=True)
        self.arbol.selection_set(self.nodo_raiz)
        self.arbol.focus(self.nodo_raiz)

    def _cargar_nodos(self, nodo_padre: str, ruta_padre: Path) -> None:
        for ruta_hija in self._obtener_elementos(ruta_padre):
            tipo = "Carpeta" if ruta_hija.is_dir() else "Archivo"
            nodo_hijo = self.arbol.insert(nodo_padre, "end", text=ruta_hija.name, values=(str(ruta_hija), tipo))
            if ruta_hija.is_dir() and self._tiene_hijos(ruta_hija):
                self.arbol.insert(nodo_hijo, "end", text="Cargando...", values=("", ""))

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

    def _expandir_todo(self) -> None:
        for nodo in self.arbol.get_children(""):
            self._establecer_expansion_recursiva(nodo, True)

    def _contraer_todo(self) -> None:
        for nodo in self.arbol.get_children(""):
            self._establecer_expansion_recursiva(nodo, False)

    def _establecer_expansion_recursiva(self, nodo: str, abierto: bool) -> None:
        if abierto:
            self.arbol.item(nodo, open=True)
            self.arbol.focus(nodo)
            self._al_expandir_nodo()

        for hijo in self.arbol.get_children(nodo):
            self._establecer_expansion_recursiva(hijo, abierto)

        if not abierto:
            self.arbol.item(nodo, open=False)

    def _al_seleccionar_elemento(self, _evento=None) -> None:
        seleccion = self.arbol.selection()
        if not seleccion:
            return

        ruta = self._ruta_desde_nodo(seleccion[0])
        if ruta is None:
            return

        self.ruta_seleccionada = ruta
        self._mostrar_detalle(ruta)

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

        self.ruta_seleccionada = ruta
        self._mostrar_detalle(ruta)

    def _ruta_desde_nodo(self, nodo: str) -> Path | None:
        valores = self.arbol.item(nodo, "values")
        if not valores:
            return self.carpeta_actual

        ruta = valores[0]
        if not ruta:
            return None

        return Path(ruta)

    def _mostrar_detalle(self, ruta: Path | None) -> None:
        if ruta is None:
            self.etiqueta_archivo.configure(text="Ningun archivo seleccionado")
            self.etiqueta_tipo.configure(text="Selecciona un archivo o carpeta para renombrarlo")
            self.entrada_nombre.configure(state="normal")
            self.entrada_nombre.delete(0, "end")
            self.entrada_nombre.insert(0, "")
            self.entrada_nombre.configure(state="disabled")
            return

        if ruta.is_dir():
            self.etiqueta_archivo.configure(text=f"Carpeta: {ruta.name}")
            self.etiqueta_tipo.configure(text="Carpeta seleccionada en el explorador")
        else:
            self.etiqueta_archivo.configure(text=f"Archivo: {ruta.name}")
            self.etiqueta_tipo.configure(text=f"Ruta completa: {ruta}")

        self.entrada_nombre.configure(state="normal")
        self.entrada_nombre.delete(0, "end")
        self.entrada_nombre.insert(0, ruta.name)

    def _renombrar_elemento(self) -> None:
        if self.ruta_seleccionada is None:
            messagebox.showwarning("Auto File Organizer", "Selecciona un archivo o carpeta para renombrar")
            return

        if self.carpeta_actual is not None and self.ruta_seleccionada.resolve() == self.carpeta_actual.resolve():
            messagebox.showwarning("Auto File Organizer", "No se puede renombrar la carpeta raiz desde esta vista")
            return

        nuevo_nombre = self.entrada_nombre.get().strip()
        if not nuevo_nombre:
            messagebox.showwarning("Auto File Organizer", "Escribe un nombre valido")
            return

        if "/" in nuevo_nombre or "\\" in nuevo_nombre:
            messagebox.showwarning("Auto File Organizer", "El nombre no puede contener separadores de ruta")
            return

        destino = self.ruta_seleccionada.with_name(nuevo_nombre)
        if destino == self.ruta_seleccionada:
            return

        if destino.exists():
            messagebox.showwarning("Auto File Organizer", "Ya existe un archivo o carpeta con ese nombre")
            return

        try:
            self.ruta_seleccionada.rename(destino)
        except OSError as error:
            messagebox.showerror("Auto File Organizer", f"No se pudo renombrar: {error}")
            return

        self.ruta_seleccionada = destino
        self._actualizar_actividad(f"Renombrado: {destino.name}")
        self._recargar_explorador()

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
