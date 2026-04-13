"""Motor SQLAlchemy y configuración de la base de datos."""
from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, event

DATABASE_URL = "sqlite:///universidad.db"


def _sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
    """Activa integridad referencial en SQLite (necesario para ON DELETE CASCADE)."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def crear_engine():
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    event.listen(engine, "connect", _sqlite_pragma)
    return engine
