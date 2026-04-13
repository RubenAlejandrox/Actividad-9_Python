"""
Capa de acceso a datos (DAO) genérica y especializada por entidad.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from model.models import Course, Department, Enrollment, Professor, Student

T = TypeVar("T")


class DAO(ABC, Generic[T]):
    """Clase abstracta genérica para operaciones CRUD sobre un modelo SQLAlchemy."""

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
    """Implementación común usando el nombre del atributo de clave primaria del modelo."""

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


class DepartmentDAO(_BaseDAO[Department]):
    def __init__(self) -> None:
        super().__init__(Department, "_id")


class ProfessorDAO(_BaseDAO[Professor]):
    def __init__(self) -> None:
        super().__init__(Professor, "_id")


class CourseDAO(_BaseDAO[Course]):
    def __init__(self) -> None:
        super().__init__(Course, "_id")


class StudentDAO(_BaseDAO[Student]):
    def __init__(self) -> None:
        super().__init__(Student, "_id")


class EnrollmentDAO(_BaseDAO[Enrollment]):
    def __init__(self) -> None:
        super().__init__(Enrollment, "_id")
