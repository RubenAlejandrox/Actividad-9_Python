"""Instancias singleton de DAO usadas por la ventana principal (inyección ligera)."""
from model.daos import (
    CourseDAO,
    DepartmentDAO,
    EnrollmentDAO,
    ProfessorDAO,
    StudentDAO,
)

department_dao = DepartmentDAO()
professor_dao = ProfessorDAO()
course_dao = CourseDAO()
student_dao = StudentDAO()
enrollment_dao = EnrollmentDAO()
