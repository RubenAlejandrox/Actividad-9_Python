"""
Entidades ORM (SQLite). Nombres de tablas y columnas en BD sin cambiar el esquema existente.
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelo.modelo_datos import ModeloDatos


def nuevo_uuid() -> str:
    return str(uuid.uuid4())


class Departamento(ModeloDatos):
    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    profesores: Mapped[List["Profesor"]] = relationship(back_populates="departamento")

    @property
    def _id(self) -> str:
        return self.department_id

    @property
    def uuid(self) -> str:
        return self.department_id

    def __repr__(self) -> str:
        return f"<Departamento {self.name}>"


class Profesor(ModeloDatos):
    __tablename__ = "professors"

    professor_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"), nullable=False)

    departamento: Mapped["Departamento"] = relationship(back_populates="profesores")
    cursos: Mapped[List["Curso"]] = relationship(back_populates="profesor")

    @property
    def _id(self) -> str:
        return self.professor_id

    @property
    def uuid(self) -> str:
        return self.professor_id

    def __repr__(self) -> str:
        return f"<Profesor {self.name}>"


class Curso(ModeloDatos):
    __tablename__ = "courses"

    course_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    professor_id: Mapped[str] = mapped_column(ForeignKey("professors.professor_id"), nullable=False)

    profesor: Mapped["Profesor"] = relationship(back_populates="cursos")
    matriculas: Mapped[List["Matricula"]] = relationship(back_populates="curso")

    @property
    def _id(self) -> str:
        return self.course_id

    @property
    def uuid(self) -> str:
        return self.course_id

    def __repr__(self) -> str:
        return f"<Curso {self.code}>"


class Estudiante(ModeloDatos):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)

    matriculas: Mapped[List["Matricula"]] = relationship(back_populates="estudiante")

    @property
    def _id(self) -> str:
        return self.student_id

    @property
    def uuid(self) -> str:
        return self.student_id

    def __repr__(self) -> str:
        return f"<Estudiante {self.name}>"


class Matricula(ModeloDatos):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),)

    enrollment_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.student_id"), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.course_id"), nullable=False)
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    estudiante: Mapped["Estudiante"] = relationship(back_populates="matriculas")
    curso: Mapped["Curso"] = relationship(back_populates="matriculas")

    @property
    def _id(self) -> str:
        return self.enrollment_id

    @property
    def uuid(self) -> str:
        return self.enrollment_id

    def __repr__(self) -> str:
        return f"<Matricula {self.enrollment_id}>"


Base = ModeloDatos
