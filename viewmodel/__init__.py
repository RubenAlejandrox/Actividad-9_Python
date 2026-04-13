"""Capa ViewModel: sesión/BD, DAOs compartidos y utilidades de dominio para la UI."""
from viewmodel.database import DATABASE_URL, crear_engine
from viewmodel.daos_registry import (
    course_dao,
    department_dao,
    enrollment_dao,
    professor_dao,
    student_dao,
)
from viewmodel.helpers import parse_fecha

__all__ = [
    "DATABASE_URL",
    "course_dao",
    "crear_engine",
    "department_dao",
    "enrollment_dao",
    "parse_fecha",
    "professor_dao",
    "student_dao",
]
