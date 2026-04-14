"""
Pruebas CRUD (SQLite en memoria, schema autogenerado).
"""
from __future__ import annotations

import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from modelo import Base
from modelo.daos import (
    CourseDAO,
    DepartmentDAO,
    EnrollmentDAO,
    ProfessorDAO,
    StudentDAO,
)


def _crear_sesion() -> Session:
    motor = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(motor)
    return sessionmaker(bind=motor, expire_on_commit=False, future=True)()


class TestDepartamentoCRUD(unittest.TestCase):
    def setUp(self) -> None:
        self.sesion = _crear_sesion()
        self.dao = DepartmentDAO()

    def tearDown(self) -> None:
        self.sesion.close()

    def test_crear_leer_actualizar_borrar(self) -> None:
        d = self.dao.create(self.sesion, name="Ingeniería")
        self.sesion.commit()
        pk = d._id
        self.assertIsNotNone(pk)

        got = self.dao.get(self.sesion, pk)
        self.assertIsNotNone(got)
        assert got is not None
        self.assertEqual(got.name, "Ingeniería")

        todos = self.dao.get_all(self.sesion)
        self.assertEqual(len(todos), 1)

        upd = self.dao.update(self.sesion, pk, name="Sistemas")
        self.sesion.commit()
        assert upd is not None
        self.assertEqual(upd.name, "Sistemas")

        self.assertTrue(self.dao.delete(self.sesion, pk))
        self.sesion.commit()
        self.assertIsNone(self.dao.get(self.sesion, pk))


class TestEsquemaCompletoCRUD(unittest.TestCase):
    def setUp(self) -> None:
        self.sesion = _crear_sesion()
        self.dao_dept = DepartmentDAO()
        self.dao_prof = ProfessorDAO()
        self.dao_curso = CourseDAO()
        self.dao_est = StudentDAO()
        self.dao_mat = EnrollmentDAO()

    def tearDown(self) -> None:
        self.sesion.close()

    def test_cadena_crud(self) -> None:
        dept = self.dao_dept.create(self.sesion, name="Dept Test")
        prof = self.dao_prof.create(
            self.sesion,
            name="Ana López",
            email="ana@uni.test",
            hire_date=date(2020, 1, 15),
            department_id=dept._id,
        )
        curso = self.dao_curso.create(
            self.sesion,
            name="Bases de datos",
            code="BD-101",
            credits=4,
            capacity=25,
            professor_id=prof._id,
        )
        est = self.dao_est.create(
            self.sesion,
            name="Luis Pérez",
            email="luis@alu.test",
            birth_date=date(2002, 3, 10),
        )
        mat = self.dao_mat.create(
            self.sesion,
            student_id=est._id,
            course_id=curso._id,
            enrollment_date=date(2025, 1, 20),
            grade=9,
        )
        self.sesion.commit()

        mid = mat._id
        g = self.dao_mat.get(self.sesion, mid)
        self.assertIsNotNone(g)
        assert g is not None
        self.assertEqual(g.grade, 9)

        self.dao_mat.update(self.sesion, mid, grade=10)
        self.sesion.commit()
        g2 = self.dao_mat.get(self.sesion, mid)
        assert g2 is not None
        self.assertEqual(g2.grade, 10)

        self.assertTrue(self.dao_mat.delete(self.sesion, mid))
        self.sesion.commit()
        self.assertIsNone(self.dao_mat.get(self.sesion, mid))

        self.assertTrue(self.dao_curso.delete(self.sesion, curso._id))
        self.assertTrue(self.dao_est.delete(self.sesion, est._id))
        self.assertTrue(self.dao_prof.delete(self.sesion, prof._id))
        self.assertTrue(self.dao_dept.delete(self.sesion, dept._id))
        self.sesion.commit()


if __name__ == "__main__":
    unittest.main()
