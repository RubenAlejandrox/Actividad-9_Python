"""
Base declarativa abstracta para modelos ORM del dominio universitario.
Las entidades concretas están en modelo.entidades.
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class ModeloDatos(DeclarativeBase):
    """Metadatos SQLAlchemy (__abstract__: sin tabla). Las entidades definen _id y uuid."""

    __abstract__ = True
