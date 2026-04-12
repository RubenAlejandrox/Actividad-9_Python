"""
Modelos ORM para la base de datos universitaria (SQLite).
Schema autogenerado con Base.metadata.create_all(engine).
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def nuevo_uuid() -> str:
    """Genera un UUID v4 como cadena para persistencia en SQLite."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos."""

    pass


class Department(Base):
    """Departamento académico."""

    __tablename__ = "departments"

    _id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=nuevo_uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    professors: Mapped[List["Professor"]] = relationship(back_populates="department")
    courses: Mapped[List["Course"]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"<Department {self.code}>"


class Professor(Base):
    """Profesor adscrito a un departamento."""

    __tablename__ = "professors"

    _id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=nuevo_uuid, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments._id"), nullable=False)

    department: Mapped["Department"] = relationship(back_populates="professors")
    courses: Mapped[List["Course"]] = relationship(back_populates="professor")

    def __repr__(self) -> str:
        return f"<Professor {self.first_name} {self.last_name}>"


class Course(Base):
    """Asignatura impartida por un profesor en un departamento."""

    __tablename__ = "courses"

    _id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=nuevo_uuid, nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments._id"), nullable=False)
    professor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("professors._id"), nullable=True
    )

    department: Mapped["Department"] = relationship(back_populates="courses")
    professor: Mapped[Optional["Professor"]] = relationship(back_populates="courses")
    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="course")

    def __repr__(self) -> str:
        return f"<Course {self.code}>"


class Student(Base):
    """Estudiante matriculado en la universidad."""

    __tablename__ = "students"

    _id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=nuevo_uuid, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    student_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")

    def __repr__(self) -> str:
        return f"<Student {self.student_number}>"


class Enrollment(Base):
    """Inscripción de un estudiante en un curso (tabla de relación con datos)."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_enrollment_student_course"),
    )

    _id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, default=nuevo_uuid, nullable=False)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students._id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses._id", ondelete="CASCADE"), nullable=False
    )
    grade: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        return f"<Enrollment student={self.student_id} course={self.course_id}>"
