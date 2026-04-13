"""Capa Model: entidades ORM, base abstracta y DAOs."""
from model.daos import (
    DAO,
    CourseDAO,
    DepartmentDAO,
    EnrollmentDAO,
    ProfessorDAO,
    StudentDAO,
)
from model.modelo_datos import ModeloDatos
from model.models import (
    Base,
    Course,
    Department,
    Enrollment,
    Professor,
    Student,
    nuevo_uuid,
)

__all__ = [
    "Base",
    "Course",
    "CourseDAO",
    "DAO",
    "Department",
    "DepartmentDAO",
    "Enrollment",
    "EnrollmentDAO",
    "ModeloDatos",
    "Professor",
    "ProfessorDAO",
    "Student",
    "StudentDAO",
    "nuevo_uuid",
]
