"""
Modelos ORM para la base de datos universitaria (SQLite).
Esquema según diagrama ER: Department, Professor, Course, Student, Enrollment.
Todas las tablas heredan de model.modelo_datos.ModeloDatos; schema con Base.metadata.create_all(engine).
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.modelo_datos import ModeloDatos


def nuevo_uuid() -> str:
    """Genera un UUID v4 como cadena para persistencia en SQLite."""
    return str(uuid.uuid4())


class Department(ModeloDatos):
    """Departamento académico."""

    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    professors: Mapped[List["Professor"]] = relationship(back_populates="department")

    @property
    def _id(self) -> str:
        return self.department_id

    @property
    def uuid(self) -> str:
        return self.department_id

    def __repr__(self) -> str:
        return f"<Department {self.name}>"


class Professor(ModeloDatos):
    """Profesor adscrito a un departamento."""

    __tablename__ = "professors"

    professor_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.department_id"), nullable=False)

    department: Mapped["Department"] = relationship(back_populates="professors")
    courses: Mapped[List["Course"]] = relationship(back_populates="professor")

    @property
    def _id(self) -> str:
        return self.professor_id

    @property
    def uuid(self) -> str:
        return self.professor_id

    def __repr__(self) -> str:
        return f"<Professor {self.name}>"


class Course(ModeloDatos):
    """Asignatura impartida por un profesor."""

    __tablename__ = "courses"

    course_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    professor_id: Mapped[str] = mapped_column(ForeignKey("professors.professor_id"), nullable=False)

    professor: Mapped["Professor"] = relationship(back_populates="courses")
    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="course")

    @property
    def _id(self) -> str:
        return self.course_id

    @property
    def uuid(self) -> str:
        return self.course_id

    def __repr__(self) -> str:
        return f"<Course {self.code}>"


class Student(ModeloDatos):
    """Estudiante matriculado en la universidad."""

    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")

    @property
    def _id(self) -> str:
        return self.student_id

    @property
    def uuid(self) -> str:
        return self.student_id

    def __repr__(self) -> str:
        return f"<Student {self.name}>"


class Enrollment(ModeloDatos):
    """Inscripción de un estudiante en un curso (tabla puente con datos)."""

    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),)

    enrollment_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=nuevo_uuid)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.student_id"), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.course_id"), nullable=False)
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    @property
    def _id(self) -> str:
        return self.enrollment_id

    @property
    def uuid(self) -> str:
        return self.enrollment_id

    def __repr__(self) -> str:
        return f"<Enrollment {self.enrollment_id}>"


Base = ModeloDatos
