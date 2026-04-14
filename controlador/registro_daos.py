"""Instancias singleton de DAO (nombres en inglés según la práctica)."""
from modelo.daos import (
    CourseDAO,
    DepartmentDAO,
    EnrollmentDAO,
    ProfessorDAO,
    StudentDAO,
)

dao_departamento = DepartmentDAO()
dao_profesor = ProfessorDAO()
dao_curso = CourseDAO()
dao_estudiante = StudentDAO()
dao_matricula = EnrollmentDAO()
