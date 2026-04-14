"""
Ventana principal Tkinter (capa Vista del MVC).
La sesión SQLAlchemy se crea aquí; los DAO se importan del controlador.
"""
from __future__ import annotations

import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session, sessionmaker

from modelo import Base
from vista.tema import (
    AZUL_MARINO,
    BLANCO,
    FILA_PAR,
    FILA_SELECCIONADA,
    FONDO_VENTANA,
    configurar_estilos_ttk,
)
from controlador.base_datos import crear_motor
from controlador.registro_daos import (
    dao_curso,
    dao_departamento,
    dao_estudiante,
    dao_matricula,
    dao_profesor,
)
from controlador.utilidades import analizar_fecha

_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


class VentanaUniversidad(tk.Tk):
    """Ventana principal con pestañas por entidad y operaciones CRUD."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Universidad — Gestión académica")
        self.geometry("1000x640")
        self.minsize(820, 520)
        self.configure(bg=FONDO_VENTANA)

        configurar_estilos_ttk(self)

        cabecera = tk.Frame(self, bg=AZUL_MARINO, height=64)
        cabecera.pack(fill=tk.X)
        cabecera.pack_propagate(False)

        try:
            self.logo_img = tk.PhotoImage(file=str(_RAIZ_PROYECTO / "assets" / "logo-ittol.png"))
            self.logo_img = self.logo_img.subsample(3)
            self.logo_label = tk.Label(cabecera, image=self.logo_img, bg=AZUL_MARINO)
            self.logo_label.pack(side=tk.LEFT, padx=(20, 0), pady=10)
        except Exception as e:
            print(f"Error cargando logo: {e}")

        tk.Label(
            cabecera,
            text="ITTOL-TECNM",
            font=("Segoe UI", 16, "bold"),
            fg=BLANCO,
            bg=AZUL_MARINO,
        ).pack(side=tk.LEFT, padx=(10, 8), pady=14)
        tk.Label(
            cabecera,
            text="Administración de datos  ·  SQLAlchemy + Tkinter",
            font=("Segoe UI", 10),
            fg="#c5d3e3",
            bg=AZUL_MARINO,
        ).pack(side=tk.LEFT, pady=14)

        cuerpo = ttk.Frame(self, padding=(10, 10), style="App.TFrame")
        cuerpo.pack(fill=tk.BOTH, expand=True)

        self.motor = crear_motor()
        Base.metadata.create_all(self.motor)
        self.fabrica_sesion = sessionmaker(bind=self.motor, expire_on_commit=False, future=True)
        self.sesion: Session = self.fabrica_sesion()

        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        cuaderno = ttk.Notebook(cuerpo)
        cuaderno.pack(fill=tk.BOTH, expand=True)

        self._pestana_departamentos(cuaderno)
        self._pestana_profesores(cuaderno)
        self._pestana_cursos(cuaderno)
        self._pestana_estudiantes(cuaderno)
        self._pestana_matriculas(cuaderno)

    def _al_cerrar(self) -> None:
        try:
            self.sesion.close()
        except Exception:
            pass
        self.destroy()

    def _confirmar_o_error(self, mensaje_exito: str = "Operación realizada correctamente.") -> None:
        try:
            self.sesion.commit()
            messagebox.showinfo("Éxito", mensaje_exito)
        except Exception as exc:
            self.sesion.rollback()
            messagebox.showerror("Error de base de datos", str(exc))

    def _pestana_departamentos(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Departamentos  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar departamento", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)
        e_nombre = ttk.Entry(form, width=40)
        e_nombre.grid(row=0, column=1, padx=4, pady=2)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=8)

        cols = ("uuid", "name")
        tree, tv_frame = self._crear_tabla(frame, cols)

        def cargar_tabla() -> None:
            self._llenar_tabla(
                tree,
                cols,
                [
                    (
                        d._id,
                        d.uuid,
                        d.name,
                    )
                    for d in dao_departamento.get_all(self.sesion)
                ],
            )

        def limpiar() -> None:
            e_nombre.delete(0, tk.END)

        def crear() -> None:
            nombre = e_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Validación", "El nombre es obligatorio.")
                return
            try:
                dao_departamento.create(self.sesion, name=nombre)
                self._confirmar_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[str]:
            return self._id_seleccionado_tabla(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un departamento en la tabla.")
                return
            nombre = e_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Validación", "El nombre es obligatorio.")
                return
            try:
                dao_departamento.update(self.sesion, pk, name=nombre)
                self._confirmar_o_error("Departamento actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.sesion.rollback()
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
                if dao_departamento.delete(self.sesion, pk):
                    self._confirmar_o_error("Departamento eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            d = dao_departamento.get(self.sesion, pk)
            if d:
                limpiar()
                e_nombre.insert(0, d.name)

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _opciones_departamentos(self) -> List[Tuple[str, str]]:
        return [(d._id, f"{d._id[:8]}… — {d.name}") for d in dao_departamento.get_all(self.sesion)]

    def _opciones_profesores(self) -> List[Tuple[str, str]]:
        return [
            (p._id, f"{p._id[:8]}… — {p.name}")
            for p in dao_profesor.get_all(self.sesion)
        ]

    def _opciones_cursos(self) -> List[Tuple[str, str]]:
        return [(c._id, f"{c._id[:8]}… — {c.code} {c.name}") for c in dao_curso.get_all(self.sesion)]

    def _opciones_estudiantes(self) -> List[Tuple[str, str]]:
        return [
            (s._id, f"{s._id[:8]}… — {s.name}")
            for s in dao_estudiante.get_all(self.sesion)
        ]

    def _actualizar_combobox(
        self,
        combo: ttk.Combobox,
        opciones: List[Tuple[str, str]],
        mapa: Dict[str, str],
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

    def _pestana_profesores(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Profesores  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar profesor", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Nombre completo:").grid(row=0, column=0, sticky=tk.W)
        e_nombre = ttk.Entry(form, width=36)
        e_nombre.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky=tk.W)
        e_email = ttk.Entry(form, width=36)
        e_email.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Fecha alta (AAAA-MM-DD):").grid(row=2, column=0, sticky=tk.W)
        e_alta = ttk.Entry(form, width=16)
        e_alta.insert(0, date.today().isoformat())
        e_alta.grid(row=2, column=1, sticky=tk.W, padx=4)

        ttk.Label(form, text="Departamento:").grid(row=3, column=0, sticky=tk.W)
        cb_dept_map: Dict[str, str] = {}
        cb_dept = ttk.Combobox(form, width=50, state="readonly")
        cb_dept.grid(row=3, column=1, padx=4, sticky=tk.W)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)

        cols = ("uuid", "name", "email", "hire_date", "department_id")
        tree, _ = self._crear_tabla(frame, cols)

        def refrescar_combos() -> None:
            self._actualizar_combobox(cb_dept, self._opciones_departamentos(), cb_dept_map)

        def cargar_tabla() -> None:
            refrescar_combos()
            self._llenar_tabla(
                tree,
                cols,
                [
                    (
                        p._id,
                        p.uuid,
                        p.name,
                        p.email,
                        p.hire_date,
                        p.department_id,
                    )
                    for p in dao_profesor.get_all(self.sesion)
                ],
            )

        def limpiar() -> None:
            e_nombre.delete(0, tk.END)
            e_email.delete(0, tk.END)
            e_alta.delete(0, tk.END)
            e_alta.insert(0, date.today().isoformat())
            refrescar_combos()

        def crear() -> None:
            if not self._validar_profesor(e_nombre, e_email, e_alta, cb_dept, cb_dept_map):
                return
            dept_id = cb_dept_map[cb_dept.get()]
            try:
                alta = analizar_fecha(e_alta.get())
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                dao_profesor.create(
                    self.sesion,
                    name=e_nombre.get().strip(),
                    email=e_email.get().strip(),
                    hire_date=alta,
                    department_id=dept_id,
                )
                self._confirmar_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[str]:
            return self._id_seleccionado_tabla(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un profesor en la tabla.")
                return
            if not self._validar_profesor(e_nombre, e_email, e_alta, cb_dept, cb_dept_map):
                return
            dept_id = cb_dept_map[cb_dept.get()]
            try:
                alta = analizar_fecha(e_alta.get())
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                dao_profesor.update(
                    self.sesion,
                    pk,
                    name=e_nombre.get().strip(),
                    email=e_email.get().strip(),
                    hire_date=alta,
                    department_id=dept_id,
                )
                self._confirmar_o_error("Profesor actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un profesor en la tabla.")
                return
            if not messagebox.askyesno("Confirmar", "¿Eliminar este profesor?"):
                return
            try:
                if dao_profesor.delete(self.sesion, pk):
                    self._confirmar_o_error("Profesor eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            p = dao_profesor.get(self.sesion, pk)
            if p:
                limpiar()
                e_nombre.insert(0, p.name)
                e_email.insert(0, p.email)
                e_alta.delete(0, tk.END)
                e_alta.insert(0, p.hire_date.isoformat())
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
        e_email: ttk.Entry,
        e_alta: ttk.Entry,
        cb_dept: ttk.Combobox,
        cb_dept_map: Dict[str, str],
    ) -> bool:
        if not e_nombre.get().strip() or not e_email.get().strip():
            messagebox.showwarning("Validación", "Nombre y email son obligatorios.")
            return False
        if not cb_dept.get() or cb_dept.get() not in cb_dept_map:
            messagebox.showwarning("Validación", "Seleccione un departamento.")
            return False
        return True

    def _pestana_cursos(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Cursos  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar curso", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Código asignatura:").grid(row=0, column=0, sticky=tk.W)
        e_codigo = ttk.Entry(form, width=20)
        e_codigo.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Nombre:").grid(row=1, column=0, sticky=tk.W)
        e_nombre_curso = ttk.Entry(form, width=40)
        e_nombre_curso.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Créditos:").grid(row=2, column=0, sticky=tk.W)
        e_creditos = ttk.Entry(form, width=8)
        e_creditos.insert(0, "3")
        e_creditos.grid(row=2, column=1, sticky=tk.W, padx=4)

        ttk.Label(form, text="Capacidad (plazas):").grid(row=3, column=0, sticky=tk.W)
        e_capacidad = ttk.Entry(form, width=8)
        e_capacidad.insert(0, "30")
        e_capacidad.grid(row=3, column=1, sticky=tk.W, padx=4)

        ttk.Label(form, text="Profesor:").grid(row=4, column=0, sticky=tk.W)
        cb_prof_map: Dict[str, str] = {}
        cb_prof = ttk.Combobox(form, width=50, state="readonly")
        cb_prof.grid(row=4, column=1, padx=4, sticky=tk.W)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=8)

        cols = ("uuid", "code", "name", "credits", "capacity", "professor_id")
        tree, _ = self._crear_tabla(frame, cols)

        def refrescar_combos() -> None:
            self._actualizar_combobox(cb_prof, self._opciones_profesores(), cb_prof_map)

        def cargar_tabla() -> None:
            refrescar_combos()
            self._llenar_tabla(
                tree,
                cols,
                [
                    (
                        c._id,
                        c.uuid,
                        c.code,
                        c.name,
                        c.credits,
                        c.capacity,
                        c.professor_id,
                    )
                    for c in dao_curso.get_all(self.sesion)
                ],
            )

        def limpiar() -> None:
            e_codigo.delete(0, tk.END)
            e_nombre_curso.delete(0, tk.END)
            e_creditos.delete(0, tk.END)
            e_creditos.insert(0, "3")
            e_capacidad.delete(0, tk.END)
            e_capacidad.insert(0, "30")
            refrescar_combos()

        def crear() -> None:
            if not self._validar_curso(e_codigo, e_nombre_curso, e_creditos, e_capacidad, cb_prof, cb_prof_map):
                return
            try:
                cr = int(e_creditos.get().strip())
                cap = int(e_capacidad.get().strip())
            except ValueError:
                messagebox.showwarning("Validación", "Créditos y capacidad deben ser números enteros.")
                return
            prof_id = cb_prof_map[cb_prof.get()]
            try:
                dao_curso.create(
                    self.sesion,
                    code=e_codigo.get().strip(),
                    name=e_nombre_curso.get().strip(),
                    credits=cr,
                    capacity=cap,
                    professor_id=prof_id,
                )
                self._confirmar_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[str]:
            return self._id_seleccionado_tabla(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un curso en la tabla.")
                return
            if not self._validar_curso(e_codigo, e_nombre_curso, e_creditos, e_capacidad, cb_prof, cb_prof_map):
                return
            try:
                cr = int(e_creditos.get().strip())
                cap = int(e_capacidad.get().strip())
            except ValueError:
                messagebox.showwarning("Validación", "Créditos y capacidad deben ser números enteros.")
                return
            prof_id = cb_prof_map[cb_prof.get()]
            try:
                dao_curso.update(
                    self.sesion,
                    pk,
                    code=e_codigo.get().strip(),
                    name=e_nombre_curso.get().strip(),
                    credits=cr,
                    capacity=cap,
                    professor_id=prof_id,
                )
                self._confirmar_o_error("Curso actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.sesion.rollback()
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
                if dao_curso.delete(self.sesion, pk):
                    self._confirmar_o_error("Curso eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            c = dao_curso.get(self.sesion, pk)
            if c:
                limpiar()
                e_codigo.insert(0, c.code)
                e_nombre_curso.insert(0, c.name)
                e_creditos.delete(0, tk.END)
                e_creditos.insert(0, str(c.credits))
                e_capacidad.delete(0, tk.END)
                e_capacidad.insert(0, str(c.capacity))
                refrescar_combos()
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
        e_nombre: ttk.Entry,
        e_creditos: ttk.Entry,
        e_capacidad: ttk.Entry,
        cb_prof: ttk.Combobox,
        cb_prof_map: Dict[str, str],
    ) -> bool:
        if not e_codigo.get().strip() or not e_nombre.get().strip():
            messagebox.showwarning("Validación", "Código y nombre son obligatorios.")
            return False
        if not cb_prof.get() or cb_prof.get() not in cb_prof_map:
            messagebox.showwarning("Validación", "Seleccione un profesor.")
            return False
        try:
            int(e_creditos.get().strip())
            int(e_capacidad.get().strip())
        except ValueError:
            messagebox.showwarning("Validación", "Créditos y capacidad deben ser números enteros.")
            return False
        return True

    def _pestana_estudiantes(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Estudiantes  ")

        form = ttk.LabelFrame(frame, text="Nuevo / editar estudiante", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Nombre completo:").grid(row=0, column=0, sticky=tk.W)
        e_nombre = ttk.Entry(form, width=36)
        e_nombre.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky=tk.W)
        e_email = ttk.Entry(form, width=36)
        e_email.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Fecha nacimiento (AAAA-MM-DD):").grid(row=2, column=0, sticky=tk.W)
        e_nac = ttk.Entry(form, width=16)
        e_nac.grid(row=2, column=1, sticky=tk.W, padx=4)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=8)

        cols = ("uuid", "name", "email", "birth_date")
        tree, _ = self._crear_tabla(frame, cols)

        def cargar_tabla() -> None:
            self._llenar_tabla(
                tree,
                cols,
                [
                    (
                        s._id,
                        s.uuid,
                        s.name,
                        s.email,
                        s.birth_date,
                    )
                    for s in dao_estudiante.get_all(self.sesion)
                ],
            )

        def limpiar() -> None:
            e_nombre.delete(0, tk.END)
            e_email.delete(0, tk.END)
            e_nac.delete(0, tk.END)

        def crear() -> None:
            if not e_nombre.get().strip():
                messagebox.showwarning("Validación", "El nombre es obligatorio.")
                return
            if not e_email.get().strip():
                messagebox.showwarning("Validación", "El email es obligatorio.")
                return
            try:
                nac = analizar_fecha(e_nac.get())
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                dao_estudiante.create(
                    self.sesion,
                    name=e_nombre.get().strip(),
                    email=e_email.get().strip(),
                    birth_date=nac,
                )
                self._confirmar_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[str]:
            return self._id_seleccionado_tabla(tree, "id")

        def editar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione un estudiante en la tabla.")
                return
            if not e_nombre.get().strip():
                messagebox.showwarning("Validación", "El nombre es obligatorio.")
                return
            if not e_email.get().strip():
                messagebox.showwarning("Validación", "El email es obligatorio.")
                return
            try:
                nac = analizar_fecha(e_nac.get())
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                dao_estudiante.update(
                    self.sesion,
                    pk,
                    name=e_nombre.get().strip(),
                    email=e_email.get().strip(),
                    birth_date=nac,
                )
                self._confirmar_o_error("Estudiante actualizado.")
                cargar_tabla()
            except Exception as exc:
                self.sesion.rollback()
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
                if dao_estudiante.delete(self.sesion, pk):
                    self._confirmar_o_error("Estudiante eliminado.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            s = dao_estudiante.get(self.sesion, pk)
            if s:
                limpiar()
                e_nombre.insert(0, s.name)
                e_email.insert(0, s.email)
                e_nac.insert(0, s.birth_date.isoformat())

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _pestana_matriculas(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding=10, style="Card.TFrame")
        notebook.add(frame, text="  Matrículas  ")

        form = ttk.LabelFrame(frame, text="Nueva / editar matrícula", padding=8)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Estudiante:").grid(row=0, column=0, sticky=tk.W)
        cb_stu_map: Dict[str, str] = {}
        cb_stu = ttk.Combobox(form, width=55, state="readonly")
        cb_stu.grid(row=0, column=1, padx=4, sticky=tk.W)

        ttk.Label(form, text="Curso:").grid(row=1, column=0, sticky=tk.W)
        cb_cur_map: Dict[str, str] = {}
        cb_cur = ttk.Combobox(form, width=55, state="readonly")
        cb_cur.grid(row=1, column=1, padx=4, sticky=tk.W)

        ttk.Label(form, text="Fecha matrícula (AAAA-MM-DD):").grid(row=2, column=0, sticky=tk.W)
        e_fecha_mat = ttk.Entry(form, width=16)
        e_fecha_mat.insert(0, date.today().isoformat())
        e_fecha_mat.grid(row=2, column=1, sticky=tk.W, padx=4)

        ttk.Label(form, text="Calificación (entero, opcional):").grid(row=3, column=0, sticky=tk.W)
        e_nota = ttk.Entry(form, width=12)
        e_nota.grid(row=3, column=1, sticky=tk.W, padx=4)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)

        cols = ("uuid", "student_id", "course_id", "enrollment_date", "grade")
        tree, _ = self._crear_tabla(frame, cols)

        def refrescar_combos() -> None:
            self._actualizar_combobox(cb_stu, self._opciones_estudiantes(), cb_stu_map)
            self._actualizar_combobox(cb_cur, self._opciones_cursos(), cb_cur_map)

        def cargar_tabla() -> None:
            refrescar_combos()
            self._llenar_tabla(
                tree,
                cols,
                [
                    (
                        e._id,
                        e.uuid,
                        e.student_id,
                        e.course_id,
                        e.enrollment_date,
                        e.grade if e.grade is not None else "",
                    )
                    for e in dao_matricula.get_all(self.sesion)
                ],
            )

        def limpiar() -> None:
            e_nota.delete(0, tk.END)
            e_fecha_mat.delete(0, tk.END)
            e_fecha_mat.insert(0, date.today().isoformat())
            refrescar_combos()

        def _analizar_nota_entero() -> Optional[int]:
            raw = e_nota.get().strip()
            if not raw:
                return None
            try:
                return int(raw)
            except ValueError:
                raise ValueError("La calificación debe ser un número entero.")

        def crear() -> None:
            if not cb_stu.get() or cb_stu.get() not in cb_stu_map:
                messagebox.showwarning("Validación", "Seleccione un estudiante.")
                return
            if not cb_cur.get() or cb_cur.get() not in cb_cur_map:
                messagebox.showwarning("Validación", "Seleccione un curso.")
                return
            try:
                f_mat = analizar_fecha(e_fecha_mat.get())
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                nota = _analizar_nota_entero()
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                dao_matricula.create(
                    self.sesion,
                    student_id=cb_stu_map[cb_stu.get()],
                    course_id=cb_cur_map[cb_cur.get()],
                    enrollment_date=f_mat,
                    grade=nota,
                )
                self._confirmar_o_error()
                cargar_tabla()
                limpiar()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def seleccionado_id() -> Optional[str]:
            return self._id_seleccionado_tabla(tree, "id")

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
                f_mat = analizar_fecha(e_fecha_mat.get())
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                nota = _analizar_nota_entero()
            except ValueError as ve:
                messagebox.showwarning("Validación", str(ve))
                return
            try:
                dao_matricula.update(
                    self.sesion,
                    pk,
                    student_id=cb_stu_map[cb_stu.get()],
                    course_id=cb_cur_map[cb_cur.get()],
                    enrollment_date=f_mat,
                    grade=nota,
                )
                self._confirmar_o_error("Matrícula actualizada.")
                cargar_tabla()
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def eliminar() -> None:
            pk = seleccionado_id()
            if pk is None:
                messagebox.showinfo("Selección", "Seleccione una matrícula en la tabla.")
                return
            if not messagebox.askyesno("Confirmar", "¿Eliminar esta matrícula?"):
                return
            try:
                if dao_matricula.delete(self.sesion, pk):
                    self._confirmar_o_error("Matrícula eliminada.")
                    cargar_tabla()
                    limpiar()
                else:
                    messagebox.showwarning("Aviso", "No se encontró el registro.")
            except Exception as exc:
                self.sesion.rollback()
                messagebox.showerror("Error", str(exc))

        def al_seleccionar(_evt: Any = None) -> None:
            pk = seleccionado_id()
            if pk is None:
                return
            en = dao_matricula.get(self.sesion, pk)
            if en:
                limpiar()
                refrescar_combos()
                s_et = next((t for t, i in cb_stu_map.items() if i == en.student_id), None)
                c_et = next((t for t, i in cb_cur_map.items() if i == en.course_id), None)
                if s_et:
                    cb_stu.set(s_et)
                if c_et:
                    cb_cur.set(c_et)
                e_fecha_mat.delete(0, tk.END)
                e_fecha_mat.insert(0, en.enrollment_date.isoformat())
                if en.grade is not None:
                    e_nota.insert(0, str(en.grade))

        ttk.Button(btn_frame, text="Crear", command=crear).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Actualizar seleccionado", command=editar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Eliminar seleccionado", command=eliminar).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Refrescar tabla", command=cargar_tabla).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Limpiar formulario", command=limpiar).pack(side=tk.LEFT, padx=4)

        tree.bind("<<TreeviewSelect>>", al_seleccionar)
        cargar_tabla()

    def _crear_tabla(self, parent: ttk.Frame, cols: Tuple[str, ...]) -> Tuple[ttk.Treeview, ttk.Frame]:
        """Crea un Treeview con scrollbars y columnas etiquetadas."""
        wrap = ttk.Frame(parent, style="Card.TFrame")
        wrap.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tree = ttk.Treeview(wrap, columns=cols, show="headings", height=12)
        tree.tag_configure("fila_par", background=BLANCO)
        tree.tag_configure("fila_impar", background=FILA_PAR)
        vsb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(wrap, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        anchos = {
            "uuid": 280,
            "name": 160,
            "code": 90,
            "email": 200,
            "hire_date": 100,
            "department_id": 280,
            "professor_id": 280,
            "credits": 70,
            "capacity": 80,
            "student_id": 280,
            "course_id": 280,
            "birth_date": 100,
            "enrollment_date": 110,
            "grade": 80,
        }
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=anchos.get(c, 100), stretch=True)

        return tree, wrap

    def _llenar_tabla(
        self,
        tree: ttk.Treeview,
        cols: Tuple[str, ...],
        filas: List[Tuple[Any, ...]],
    ) -> None:
        tree.delete(*tree.get_children())
        for indice, fila in enumerate(filas):
            # fila[0] = PK (UUID) solo para iid del Treeview; no se muestra como columna.
            # fila[1:] = valores visibles (uuid + resto), alineados con cols.
            iid = str(fila[0])
            valores = tuple("" if v is None else v for v in fila[1:])
            etiqueta = "fila_par" if indice % 2 == 0 else "fila_impar"
            tree.insert("", tk.END, iid=iid, values=valores, tags=(etiqueta,))

    def _id_seleccionado_tabla(self, tree: ttk.Treeview, col_id: str) -> Optional[str]:
        sel = tree.selection()
        if not sel:
            return None
        return sel[0]

