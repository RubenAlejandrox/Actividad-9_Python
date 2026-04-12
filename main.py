"""
Aplicación de escritorio Tkinter para gestión universitaria (CRUD vía SQLAlchemy + DAOs).
La sesión de SQLAlchemy se crea aquí y se pasa a cada llamada DAO.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from daos import (
    CourseDAO,
    DepartmentDAO,
    EnrollmentDAO,
    ProfessorDAO,
    StudentDAO,
)
from models import Base

DATABASE_URL = "sqlite:///universidad.db"

# --- Paleta institucional (azul marino) ---
COLOR_NAVY = "#0c2340"  # Azul marino principal (cabecera, acentos)
COLOR_NAVY_DARK = "#08182c"
COLOR_NAVY_MID = "#153a5c"  # Pestaña activa / cabeceras tabla
COLOR_BG_APP = "#e6ecf4"  # Fondo ventana
COLOR_BG_PANEL = "#f4f7fb"  # Paneles y marcos
COLOR_TEXT = "#1a2332"
COLOR_TEXT_MUTED = "#4a5568"
COLOR_WHITE = "#ffffff"
COLOR_BORDER = "#2c5282"
COLOR_ROW_ALT = "#f0f4fa"
COLOR_ROW_SELECT = "#c5d7eb"  # Fila seleccionada en tablas
COLOR_ORANGE = "#f37021"  # Naranja ITTol para efectos hover
COLOR_BTN_HOVER = COLOR_ORANGE
COLOR_TAB_INACTIVE = "#cbd5e1"


def configurar_tema_ttk(root: tk.Tk) -> ttk.Style:
    """Aplica estilos ttk coherentes con la identidad visual (azul marino)."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=COLOR_BG_APP, foreground=COLOR_TEXT, font=("Segoe UI", 10))

    # Marcos interiores alineados con el fondo de panel; el contenedor principal usa App.TFrame
    style.configure("TFrame", background=COLOR_BG_PANEL)
    style.configure("App.TFrame", background=COLOR_BG_APP)
    style.configure("Card.TFrame", background=COLOR_BG_PANEL)

    style.configure(
        "TLabel",
        background=COLOR_BG_PANEL,
        foreground=COLOR_TEXT,
    )
    style.configure(
        "Muted.TLabel",
        background=COLOR_BG_PANEL,
        foreground=COLOR_TEXT_MUTED,
        font=("Segoe UI", 9),
    )

    style.configure(
        "TLabelframe",
        background=COLOR_BG_PANEL,
        foreground=COLOR_NAVY,
        bordercolor=COLOR_BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=COLOR_BG_PANEL,
        foreground=COLOR_NAVY,
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "TNotebook",
        background=COLOR_BG_APP,
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=COLOR_TAB_INACTIVE,
        foreground=COLOR_TEXT,
        padding=(14, 8),
        font=("Segoe UI", 10),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLOR_NAVY_MID), ("active", COLOR_ORANGE)],
        foreground=[("selected", COLOR_WHITE), ("active", COLOR_WHITE)],
    )

    style.configure(
        "TButton",
        background=COLOR_NAVY,
        foreground=COLOR_WHITE,
        bordercolor=COLOR_NAVY_DARK,
        focusthickness=3,
        focuscolor=COLOR_ROW_SELECT,
        padding=(10, 6),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", COLOR_BTN_HOVER), ("pressed", COLOR_NAVY_DARK), ("disabled", COLOR_TAB_INACTIVE)],
        foreground=[("disabled", COLOR_TEXT_MUTED)],
    )

    style.configure(
        "Secondary.TButton",
        background=COLOR_NAVY_MID,
        foreground=COLOR_WHITE,
        padding=(8, 5),
        font=("Segoe UI", 9),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLOR_NAVY), ("pressed", COLOR_NAVY_DARK)],
    )

    style.configure(
        "TEntry",
        fieldbackground=COLOR_WHITE,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_BORDER,
        lightcolor=COLOR_BG_PANEL,
        darkcolor=COLOR_BORDER,
        insertcolor=COLOR_NAVY,
        padding=(6, 4),
    )
    style.map("TEntry", bordercolor=[("focus", COLOR_NAVY)])

    style.configure(
        "TCombobox",
        fieldbackground=COLOR_WHITE,
        background=COLOR_WHITE,
        foreground=COLOR_TEXT,
        arrowcolor=COLOR_NAVY,
        bordercolor=COLOR_BORDER,
        padding=(4, 2),
    )
    style.map("TCombobox", bordercolor=[("focus", COLOR_NAVY)], arrowcolor=[("readonly", COLOR_NAVY)])

    style.configure(
        "Vertical.TScrollbar",
        background=COLOR_NAVY_MID,
        troughcolor=COLOR_BG_PANEL,
        bordercolor=COLOR_BORDER,
        arrowcolor=COLOR_WHITE,
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=COLOR_NAVY_MID,
        troughcolor=COLOR_BG_PANEL,
        bordercolor=COLOR_BORDER,
        arrowcolor=COLOR_WHITE,
    )

    style.configure(
        "Treeview",
        background=COLOR_WHITE,
        fieldbackground=COLOR_WHITE,
        foreground=COLOR_TEXT,
        rowheight=26,
        bordercolor=COLOR_BORDER,
        borderwidth=0,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background=COLOR_NAVY,
        foreground=COLOR_WHITE,
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_ROW_SELECT)],
        foreground=[("selected", COLOR_TEXT)],
    )

    return style

# Instancias DAO (singletons ligeros)
department_dao = DepartmentDAO()
professor_dao = ProfessorDAO()
course_dao = CourseDAO()
student_dao = StudentDAO()
enrollment_dao = EnrollmentDAO()


def _sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Activa integridad referencial en SQLite (necesario para ON DELETE CASCADE)."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def crear_engine():
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    event.listen(engine, "connect", _sqlite_pragma)
    return engine


class UniversidadApp(tk.Tk):
    """Ventana principal con pestañas por entidad y operaciones CRUD."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Universidad — Gestión académica")
        self.geometry("1000x640")
        self.minsize(820, 520)
        self.configure(bg=COLOR_BG_APP)

        configurar_tema_ttk(self)

        # Logo y Cabecera
        header = tk.Frame(self, bg=COLOR_NAVY, height=64)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Cargar logo
        try:
            self.logo_img = tk.PhotoImage(file="assets/logo-ittol.png")
            # Redimensionar si es necesario (el logo es 120x120, subsample 3 -> 40x40)
            self.logo_img = self.logo_img.subsample(3)
            self.logo_label = tk.Label(header, image=self.logo_img, bg=COLOR_NAVY)
            self.logo_label.pack(side=tk.LEFT, padx=(20, 0), pady=10)
        except Exception as e:
            print(f"Error cargando logo: {e}")

        tk.Label(
            header,
            text="ITTOL-TECNM",
            font=("Segoe UI", 16, "bold"),
            fg=COLOR_WHITE,
            bg=COLOR_NAVY,
        ).pack(side=tk.LEFT, padx=(10, 8), pady=14)
        tk.Label(
            header,
            text="Administración de datos  ·  SQLAlchemy + Tkinter",
            font=("Segoe UI", 10),
            fg="#c5d3e3",
            bg=COLOR_NAVY,
        ).pack(side=tk.LEFT, pady=14)

        body = ttk.Frame(self, padding=(10, 10), style="App.TFrame")
        body.pack(fill=tk.BOTH, expand=True)

        self.engine = crear_engine()
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)
        self.session: Session = self.SessionLocal()

        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        nb = ttk.Notebook(body)
        nb.pack(fill=tk.BOTH, expand=True)

        self._pestaña_departamentos(nb)
        self._pestaña_profesores(nb)
        self._pestaña_cursos(nb)
        self._pestaña_estudiantes(nb)
        self._pestaña_matriculas(nb)

    def _al_cerrar(self) -> None:
        try:
            self.session.close()
        except Exception:
            pass
        self.destroy()

    def _commit_o_error(self, mensaje_exito: str = "Operación realizada correctamente.") -> None:
        try:
            self.session.commit()
            messagebox.showinfo("Éxito", mensaje_exito)
        except Exception as exc:
            self.session.rollback()
            messagebox.showerror("Error de base de datos", str(exc))

    def _pestaña_departamentos(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Departamentos  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar departamento", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)
        e_nombre = ttk.Entry(form, width=40)
        e_nombre.grid(row=0, column=1, padx=4, pady=2)

        ttk.Label(form, text="Código:").grid(row=1, column=0, sticky=tk.W, pady=2)
        e_codigo = ttk.Entry(form, width=20)
        e_codigo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=2)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=8)

        cols = ("id", "uuid", "name", "code")
        tree, tv_frame = self._crear_treeview(frame, cols)

        def cargar_tabla() -> None:
            self._llenar_tree(
                tree,
                cols,
                [
                    (
                        d._id,
                        d.uuid,
                        d.name,
                        d.code,
                    )
                    for d in department_dao.get_all(self.session)
                ],
            )

        def limpiar() -> None:
            e_nombre.delete(0, tk.END)
            e_codigo.delete(0, tk.END)

        def crear() -> None:
            nombre = e_nombre.get().strip()
            codigo = e_codigo.get().strip()
            if not nombre or not codigo:
                messagebox.showwarning("Validación", "Nombre y código son obligatorios.")
                return
            try:
                department_dao.create(self.session, name=nombre, code=codigo)
                self._commit_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[int]:
            return self._id_seleccionado_tree(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un departamento en la tabla.")
                return
            nombre = e_nombre.get().strip()
            codigo = e_codigo.get().strip()
            if not nombre or not codigo:
                messagebox.showwarning("Validación", "Nombre y código son obligatorios.")
                return
            try:
                department_dao.update(self.session, pk, name=nombre, code=codigo)
                self._commit_o_error("Departamento actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un departamento en la tabla.")
                return
            if not messagebox.askyesno(
                "Confirmar",
                "¿Eliminar este departamento? Puede fallar si hay profesores o cursos asociados.",
            ):
                return
            try:
                if department_dao.delete(self.session, pk):
                    self._commit_o_error("Departamento eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            d = department_dao.get(self.session, pk)
            if d:
                limpiar()
                e_nombre.insert(0, d.name)
                e_codigo.insert(0, d.code)

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _opciones_departamentos(self) -> List[Tuple[int, str]]:
        return [(d._id, f"{d._id} — {d.name} ({d.code})") for d in department_dao.get_all(self.session)]

    def _opciones_profesores(self) -> List[Tuple[int, str]]:
        return [
            (p._id, f"{p._id} — {p.first_name} {p.last_name}")
            for p in professor_dao.get_all(self.session)
        ]

    def _opciones_cursos(self) -> List[Tuple[int, str]]:
        return [(c._id, f"{c._id} — {c.code} {c.title}") for c in course_dao.get_all(self.session)]

    def _opciones_estudiantes(self) -> List[Tuple[int, str]]:
        return [
            (s._id, f"{s._id} — {s.student_number} {s.first_name} {s.last_name}")
            for s in student_dao.get_all(self.session)
        ]

    def _actualizar_combobox(
        self,
        combo: ttk.Combobox,
        opciones: List[Tuple[int, str]],
        mapa: Dict[str, int],
    ) -> None:
        mapa.clear()
        etiquetas: List[str] = []
        for pk, texto in opciones:
            etiquetas.append(texto)
            mapa[texto] = pk
        combo["values"] = etiquetas
        if etiquetas:
            combo.current(0)
        else:
            combo.set("")

    def _pestaña_profesores(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Profesores  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar profesor", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky=tk.W)
        e_nombre = ttk.Entry(form, width=28)
        e_nombre.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Apellidos:").grid(row=1, column=0, sticky=tk.W)
        e_apellidos = ttk.Entry(form, width=28)
        e_apellidos.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Email:").grid(row=2, column=0, sticky=tk.W)
        e_email = ttk.Entry(form, width=36)
        e_email.grid(row=2, column=1, padx=4)

        ttk.Label(form, text="Departamento:").grid(row=3, column=0, sticky=tk.W)
        cb_dept_map: Dict[str, int] = {}
        cb_dept = ttk.Combobox(form, width=50, state="readonly")
        cb_dept.grid(row=3, column=1, padx=4, sticky=tk.W)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)

        cols = ("id", "uuid", "first_name", "last_name", "email", "department_id")
        tree, _ = self._crear_treeview(frame, cols)

        def refrescar_combos() -> None:
            self._actualizar_combobox(cb_dept, self._opciones_departamentos(), cb_dept_map)

        def cargar_tabla() -> None:
            refrescar_combos()
            self._llenar_tree(
                tree,
                cols,
                [
                    (
                        p._id,
                        p.uuid,
                        p.first_name,
                        p.last_name,
                        p.email,
                        p.department_id,
                    )
                    for p in professor_dao.get_all(self.session)
                ],
            )

        def limpiar() -> None:
            e_nombre.delete(0, tk.END)
            e_apellidos.delete(0, tk.END)
            e_email.delete(0, tk.END)
            refrescar_combos()

        def crear() -> None:
            if not self._validar_profesor(e_nombre, e_apellidos, e_email, cb_dept, cb_dept_map):
                return
            dept_id = cb_dept_map[cb_dept.get()]
            try:
                professor_dao.create(
                    self.session,
                    first_name=e_nombre.get().strip(),
                    last_name=e_apellidos.get().strip(),
                    email=e_email.get().strip(),
                    department_id=dept_id,
                )
                self._commit_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[int]:
            return self._id_seleccionado_tree(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un profesor en la tabla.")
                return
            if not self._validar_profesor(e_nombre, e_apellidos, e_email, cb_dept, cb_dept_map):
                return
            dept_id = cb_dept_map[cb_dept.get()]
            try:
                professor_dao.update(
                    self.session,
                    pk,
                    first_name=e_nombre.get().strip(),
                    last_name=e_apellidos.get().strip(),
                    email=e_email.get().strip(),
                    department_id=dept_id,
                )
                self._commit_o_error("Profesor actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un profesor en la tabla.")
                return
            if not messagebox.askyesno("Confirmar", "¿Eliminar este profesor?"):
                return
            try:
                if professor_dao.delete(self.session, pk):
                    self._commit_o_error("Profesor eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            p = professor_dao.get(self.session, pk)
            if p:
                limpiar()
                e_nombre.insert(0, p.first_name)
                e_apellidos.insert(0, p.last_name)
                e_email.insert(0, p.email)
                refrescar_combos()
                etiqueta = next((t for t, i in cb_dept_map.items() if i == p.department_id), None)
                if etiqueta:
                    cb_dept.set(etiqueta)

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _validar_profesor(
        self,
        e_nombre: ttk.Entry,
        e_apellidos: ttk.Entry,
        e_email: ttk.Entry,
        cb_dept: ttk.Combobox,
        cb_dept_map: Dict[str, int],
    ) -> bool:
        if not e_nombre.get().strip() or not e_apellidos.get().strip() or not e_email.get().strip():
            messagebox.showwarning("Validación", "Nombre, apellidos y email son obligatorios.")
            return False
        if not cb_dept.get() or cb_dept.get() not in cb_dept_map:
            messagebox.showwarning("Validación", "Seleccione un departamento.")
            return False
        return True

    def _pestaña_cursos(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Cursos  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar curso", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Código asignatura:").grid(row=0, column=0, sticky=tk.W)
        e_codigo = ttk.Entry(form, width=20)
        e_codigo.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Título:").grid(row=1, column=0, sticky=tk.W)
        e_titulo = ttk.Entry(form, width=40)
        e_titulo.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Créditos:").grid(row=2, column=0, sticky=tk.W)
        e_creditos = ttk.Entry(form, width=8)
        e_creditos.insert(0, "3")
        e_creditos.grid(row=2, column=1, sticky=tk.W, padx=4)

        ttk.Label(form, text="Departamento:").grid(row=3, column=0, sticky=tk.W)
        cb_dept_map: Dict[str, int] = {}
        cb_dept = ttk.Combobox(form, width=50, state="readonly")
        cb_dept.grid(row=3, column=1, padx=4, sticky=tk.W)

        ttk.Label(form, text="Profesor (opcional):").grid(row=4, column=0, sticky=tk.W)
        cb_prof_map: Dict[str, Optional[int]] = {}
        cb_prof = ttk.Combobox(form, width=50, state="readonly")
        cb_prof.grid(row=4, column=1, padx=4, sticky=tk.W)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=8)

        cols = ("id", "uuid", "code", "title", "credits", "department_id", "professor_id")
        tree, _ = self._crear_treeview(frame, cols)

        def refrescar_combos() -> None:
            self._actualizar_combobox(cb_dept, self._opciones_departamentos(), cb_dept_map)
            # Profesor: primera opción "— Ninguno —" con None
            prof_ops = self._opciones_profesores()
            cb_prof_map.clear()
            etiquetas: List[str] = ["— Ninguno —"]
            cb_prof_map["— Ninguno —"] = None
            for pk, texto in prof_ops:
                etiquetas.append(texto)
                cb_prof_map[texto] = pk
            cb_prof["values"] = etiquetas
            cb_prof.current(0)

        def cargar_tabla() -> None:
            refrescar_combos()
            self._llenar_tree(
                tree,
                cols,
                [
                    (
                        c._id,
                        c.uuid,
                        c.code,
                        c.title,
                        c.credits,
                        c.department_id,
                        c.professor_id if c.professor_id is not None else "",
                    )
                    for c in course_dao.get_all(self.session)
                ],
            )

        def limpiar() -> None:
            e_codigo.delete(0, tk.END)
            e_titulo.delete(0, tk.END)
            e_creditos.delete(0, tk.END)
            e_creditos.insert(0, "3")
            refrescar_combos()

        def crear() -> None:
            if not self._validar_curso(e_codigo, e_titulo, e_creditos, cb_dept, cb_dept_map):
                return
            try:
                cr = int(e_creditos.get().strip())
            except ValueError:
                messagebox.showwarning("Validación", "Créditos debe ser un número entero.")
                return
            dept_id = cb_dept_map[cb_dept.get()]
            prof_id = cb_prof_map.get(cb_prof.get())
            try:
                course_dao.create(
                    self.session,
                    code=e_codigo.get().strip(),
                    title=e_titulo.get().strip(),
                    credits=cr,
                    department_id=dept_id,
                    professor_id=prof_id,
                )
                self._commit_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[int]:
            return self._id_seleccionado_tree(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un curso en la tabla.")
                return
            if not self._validar_curso(e_codigo, e_titulo, e_creditos, cb_dept, cb_dept_map):
                return
            try:
                cr = int(e_creditos.get().strip())
            except ValueError:
                messagebox.showwarning("Validación", "Créditos debe ser un número entero.")
                return
            dept_id = cb_dept_map[cb_dept.get()]
            prof_id = cb_prof_map.get(cb_prof.get())
            try:
                course_dao.update(
                    self.session,
                    pk,
                    code=e_codigo.get().strip(),
                    title=e_titulo.get().strip(),
                    credits=cr,
                    department_id=dept_id,
                    professor_id=prof_id,
                )
                self._commit_o_error("Curso actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un curso en la tabla.")
                return
            if not messagebox.askyesno(
                "Confirmar",
                "¿Eliminar este curso? Se borrarán también las matrículas asociadas.",
            ):
                return
            try:
                if course_dao.delete(self.session, pk):
                    self._commit_o_error("Curso eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            c = course_dao.get(self.session, pk)
            if c:
                limpiar()
                e_codigo.insert(0, c.code)
                e_titulo.insert(0, c.title)
                e_creditos.delete(0, tk.END)
                e_creditos.insert(0, str(c.credits))
                refrescar_combos()
                d_et = next((t for t, i in cb_dept_map.items() if i == c.department_id), None)
                if d_et:
                    cb_dept.set(d_et)
                if c.professor_id is None:
                    cb_prof.set("— Ninguno —")
                else:
                    p_et = next((t for t, i in cb_prof_map.items() if i == c.professor_id), None)
                    if p_et:
                        cb_prof.set(p_et)

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _validar_curso(
        self,
        e_codigo: ttk.Entry,
        e_titulo: ttk.Entry,
        e_creditos: ttk.Entry,
        cb_dept: ttk.Combobox,
        cb_dept_map: Dict[str, int],
    ) -> bool:
        if not e_codigo.get().strip() or not e_titulo.get().strip():
            messagebox.showwarning("Validación", "Código y título son obligatorios.")
            return False
        if not cb_dept.get() or cb_dept.get() not in cb_dept_map:
            messagebox.showwarning("Validación", "Seleccione un departamento.")
            return False
        try:
            int(e_creditos.get().strip())
        except ValueError:
            messagebox.showwarning("Validación", "Créditos debe ser un número entero.")
            return False
        return True

    def _pestaña_estudiantes(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Estudiantes  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar estudiante", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky=tk.W)
        e_nombre = ttk.Entry(form, width=28)
        e_nombre.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Apellidos:").grid(row=1, column=0, sticky=tk.W)
        e_apellidos = ttk.Entry(form, width=28)
        e_apellidos.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Email:").grid(row=2, column=0, sticky=tk.W)
        e_email = ttk.Entry(form, width=36)
        e_email.grid(row=2, column=1, padx=4)

        ttk.Label(form, text="Nº expediente:").grid(row=3, column=0, sticky=tk.W)
        e_exp = ttk.Entry(form, width=20)
        e_exp.grid(row=3, column=1, sticky=tk.W, padx=4)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)

        cols = ("id", "uuid", "first_name", "last_name", "email", "student_number")
        tree, _ = self._crear_treeview(frame, cols)

        def cargar_tabla() -> None:
            self._llenar_tree(
                tree,
                cols,
                [
                    (
                        s._id,
                        s.uuid,
                        s.first_name,
                        s.last_name,
                        s.email,
                        s.student_number,
                    )
                    for s in student_dao.get_all(self.session)
                ],
            )

        def limpiar() -> None:
            e_nombre.delete(0, tk.END)
            e_apellidos.delete(0, tk.END)
            e_email.delete(0, tk.END)
            e_exp.delete(0, tk.END)

        def crear() -> None:
            if not e_nombre.get().strip() or not e_apellidos.get().strip():
                messagebox.showwarning("Validación", "Nombre y apellidos son obligatorios.")
                return
            if not e_email.get().strip() or not e_exp.get().strip():
                messagebox.showwarning("Validación", "Email y número de expediente son obligatorios.")
                return
            try:
                student_dao.create(
                    self.session,
                    first_name=e_nombre.get().strip(),
                    last_name=e_apellidos.get().strip(),
                    email=e_email.get().strip(),
                    student_number=e_exp.get().strip(),
                )
                self._commit_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[int]:
            return self._id_seleccionado_tree(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un estudiante en la tabla.")
                return
            if not e_nombre.get().strip() or not e_apellidos.get().strip():
                messagebox.showwarning("Validación", "Nombre y apellidos son obligatorios.")
                return
            if not e_email.get().strip() or not e_exp.get().strip():
                messagebox.showwarning("Validación", "Email y número de expediente son obligatorios.")
                return
            try:
                student_dao.update(
                    self.session,
                    pk,
                    first_name=e_nombre.get().strip(),
                    last_name=e_apellidos.get().strip(),
                    email=e_email.get().strip(),
                    student_number=e_exp.get().strip(),
                )
                self._commit_o_error("Estudiante actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un estudiante en la tabla.")
                return
            if not messagebox.askyesno(
                "Confirmar",
                "¿Eliminar este estudiante? Se borrarán también sus matrículas.",
            ):
                return
            try:
                if student_dao.delete(self.session, pk):
                    self._commit_o_error("Estudiante eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            s = student_dao.get(self.session, pk)
            if s:
                limpiar()
                e_nombre.insert(0, s.first_name)
                e_apellidos.insert(0, s.last_name)
                e_email.insert(0, s.email)
                e_exp.insert(0, s.student_number)

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _pestaña_matriculas(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Matrículas  ")

        form = ttk.LabelFrame(frame, text="Nueva / editar matrícula", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Estudiante:").grid(row=0, column=0, sticky=tk.W)
        cb_stu_map: Dict[str, int] = {}
        cb_stu = ttk.Combobox(form, width=55, state="readonly")
        cb_stu.grid(row=0, column=1, padx=4, sticky=tk.W)

        ttk.Label(form, text="Curso:").grid(row=1, column=0, sticky=tk.W)
        cb_cur_map: Dict[str, int] = {}
        cb_cur = ttk.Combobox(form, width=55, state="readonly")
        cb_cur.grid(row=1, column=1, padx=4, sticky=tk.W)

        ttk.Label(form, text="Calificación (opcional):").grid(row=2, column=0, sticky=tk.W)
        e_nota = ttk.Entry(form, width=12)
        e_nota.grid(row=2, column=1, sticky=tk.W, padx=4)

        ttk.Label(form, text="Notas (texto libre):").grid(row=3, column=0, sticky=tk.NW)
        txt_notas = tk.Text(
            form,
            width=50,
            height=3,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            insertbackground=COLOR_NAVY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_NAVY,
            font=("Segoe UI", 10),
            padx=6,
            pady=4,
        )
        txt_notas.grid(row=3, column=1, padx=4, sticky=tk.W)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)

        cols = ("id", "uuid", "student_id", "course_id", "grade", "notes")
        tree, _ = self._crear_treeview(frame, cols)

        def refrescar_combos() -> None:
            self._actualizar_combobox(cb_stu, self._opciones_estudiantes(), cb_stu_map)
            self._actualizar_combobox(cb_cur, self._opciones_cursos(), cb_cur_map)

        def cargar_tabla() -> None:
            refrescar_combos()
            self._llenar_tree(
                tree,
                cols,
                [
                    (
                        e._id,
                        e.uuid,
                        e.student_id,
                        e.course_id,
                        e.grade if e.grade is not None else "",
                        (e.notes or "")[:80],
                    )
                    for e in enrollment_dao.get_all(self.session)
                ],
            )

        def limpiar() -> None:
            e_nota.delete(0, tk.END)
            txt_notas.delete("1.0", tk.END)
            refrescar_combos()

        def _parse_nota() -> Optional[float]:
            raw = e_nota.get().strip()
            if not raw:
                return None
            try:
                return float(raw.replace(",", "."))
            except ValueError:
                raise ValueError("La calificación debe ser un número.")

        def crear() -> None:
            if not cb_stu.get() or cb_stu.get() not in cb_stu_map:
                messagebox.showwarning("Validación", "Seleccione un estudiante.")
                return
            if not cb_cur.get() or cb_cur.get() not in cb_cur_map:
                messagebox.showwarning("Validación", "Seleccione un curso.")
                return
            try:
                nota = _parse_nota()
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            notas_txt = txt_notas.get("1.0", tk.END).strip() or None
            try:
                enrollment_dao.create(
                    self.session,
                    student_id=cb_stu_map[cb_stu.get()],
                    course_id=cb_cur_map[cb_cur.get()],
                    grade=nota,
                    notes=notas_txt,
                )
                self._commit_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[int]:
            return self._id_seleccionado_tree(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione una matrícula en la tabla.")
                return
            if not cb_stu.get() or cb_stu.get() not in cb_stu_map:
                messagebox.showwarning("Validación", "Seleccione un estudiante.")
                return
            if not cb_cur.get() or cb_cur.get() not in cb_cur_map:
                messagebox.showwarning("Validación", "Seleccione un curso.")
                return
            try:
                nota = _parse_nota()
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            notas_txt = txt_notas.get("1.0", tk.END).strip() or None
            try:
                enrollment_dao.update(
                    self.session,
                    pk,
                    student_id=cb_stu_map[cb_stu.get()],
                    course_id=cb_cur_map[cb_cur.get()],
                    grade=nota,
                    notes=notas_txt,
                )
                self._commit_o_error("Matrícula actualizada.")
                cargar_tabla()
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione una matrícula en la tabla.")
                return
            if not messagebox.askyesno("Confirmar", "¿Eliminar esta matrícula?"):
                return
            try:
                if enrollment_dao.delete(self.session, pk):
                    self._commit_o_error("Matrícula eliminada.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.session.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            en = enrollment_dao.get(self.session, pk)
            if en:
                limpiar()
                refrescar_combos()
                s_et = next((t for t, i in cb_stu_map.items() if i == en.student_id), None)
                c_et = next((t for t, i in cb_cur_map.items() if i == en.course_id), None)
                if s_et:
                    cb_stu.set(s_et)
                if c_et:
                    cb_cur.set(c_et)
                if en.grade is not None:
                    e_nota.insert(0, str(en.grade))
                if en.notes:
                    txt_notas.insert("1.0", en.notes)

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _crear_treeview(self, parent: ttk.Frame, cols: Tuple[str, ...]) -> Tuple[ttk.Treeview, ttk.Frame]:
        """Crea un Treeview con scrollbars y columnas etiquetadas."""
        wrap = ttk.Frame(parent, style="Card.TFrame")
        wrap.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tree = ttk.Treeview(wrap, columns=cols, show="headings", height=12)
        tree.tag_configure("fila_par", background=COLOR_WHITE)
        tree.tag_configure("fila_impar", background=COLOR_ROW_ALT)
        vsb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(wrap, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        anchos = {
            "id": 50,
            "uuid": 280,
            "name": 160,
            "code": 90,
            "first_name": 100,
            "last_name": 120,
            "email": 200,
            "department_id": 100,
            "professor_id": 100,
            "title": 200,
            "credits": 70,
            "student_number": 120,
            "student_id": 80,
            "course_id": 80,
            "grade": 80,
            "notes": 200,
        }
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=anchos.get(c, 100), stretch=True)

        return tree, wrap

    def _llenar_tree(
        self,
        tree: ttk.Treeview,
        cols: Tuple[str, ...],
        filas: List[Tuple[Any, ...]],
    ) -> None:
        tree.delete(*tree.get_children())
        for indice, fila in enumerate(filas):
            # Primera columna = id para iid estable
            iid = str(fila[0])
            valores = tuple("" if v is None else v for v in fila)
            etiqueta = "fila_par" if indice % 2 == 0 else "fila_impar"
            tree.insert("", tk.END, iid=iid, values=valores, tags=(etiqueta,))

    def _id_seleccionado_tree(self, tree: ttk.Treeview, col_id: str) -> Optional[int]:
        sel = tree.selection()
        if not sel:
            return None
        iid = sel[0]
        try:
            return int(iid)
        except ValueError:
            return None


def main() -> None:
    app = UniversidadApp()
    app.mainloop()


if __name__ == "__main__":
    main()
