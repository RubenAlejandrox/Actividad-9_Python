"""
Capa DAO (convención en inglés: DAO, create, get, update, delete).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelo.entidades import Curso, Departamento, Estudiante, Matricula, Profesor

T = TypeVar("T")


class DAO(ABC, Generic[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    @abstractmethod
    def create(self, session: Session, **kwargs: Any) -> T:
        pass

    @abstractmethod
    def get(self, session: Session, id: Union[str, int]) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, session: Session) -> List[T]:
        pass

    @abstractmethod
    def update(self, session: Session, id: Union[str, int], **kwargs: Any) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, session: Session, id: Union[str, int]) -> bool:
        pass


class _BaseDAO(DAO[T]):
    def __init__(self, model_class: Type[T], pk_attr: str):
        super().__init__(model_class)
        self._pk_attr = pk_attr

    def create(self, session: Session, **kwargs: Any) -> T:
        obj = self.model_class(**kwargs)
        session.add(obj)
        session.flush()
        return obj

    def get(self, session: Session, id: Union[str, int]) -> Optional[T]:
        return session.get(self.model_class, id)

    def get_all(self, session: Session) -> List[T]:
        return list(session.scalars(select(self.model_class)).all())

    def update(self, session: Session, id: Union[str, int], **kwargs: Any) -> Optional[T]:
        obj = self.get(session, id)
        if obj is None:
            return None
        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        session.flush()
        return obj

    def delete(self, session: Session, id: Union[str, int]) -> bool:
        obj = self.get(session, id)
        if obj is None:
            return False
        session.delete(obj)
        session.flush()
        return True


class DepartmentDAO(_BaseDAO[Departamento]):
    def __init__(self) -> None:
        super().__init__(Departamento, "_id")


class ProfessorDAO(_BaseDAO[Profesor]):
    def __init__(self) -> None:
        super().__init__(Profesor, "_id")


class CourseDAO(_BaseDAO[Curso]):
    def __init__(self) -> None:
        super().__init__(Curso, "_id")


class StudentDAO(_BaseDAO[Estudiante]):
    def __init__(self) -> None:
        super().__init__(Estudiante, "_id")


class EnrollmentDAO(_BaseDAO[Matricula]):
    def __init__(self) -> None:
        super().__init__(Matricula, "_id")
