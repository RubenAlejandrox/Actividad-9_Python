"""
Base declarativa abstracta para modelos ORM del dominio universitario.
Las entidades concretas viven en model.models y extienden ModeloDatos.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import DeclarativeBase


class ModeloDatos(DeclarativeBase, ABC):
    """Metadatos SQLAlchemy (__abstract__: sin tabla) y contrato común para todas las entidades."""

    __abstract__ = True

    @property
    @abstractmethod
    def _id(self) -> str:
        """Clave primaria (UUID en texto) para DAO y UI."""

    @property
    @abstractmethod
    def uuid(self) -> str:
        """Alias de la clave primaria en listas y formularios."""
