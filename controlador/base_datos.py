"""Motor SQLAlchemy y URL de la base de datos."""
from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, event

URL_BASE_DATOS = "sqlite:///universidad.db"


def _pragma_sqlite_fk(dbapi_connection: Any, connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def crear_motor():
    motor = create_engine(URL_BASE_DATOS, echo=False, future=True)
    event.listen(motor, "connect", _pragma_sqlite_fk)
    return motor
