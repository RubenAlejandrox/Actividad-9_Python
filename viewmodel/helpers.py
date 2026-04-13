"""Utilidades de presentación / dominio compartidas con la vista."""
from __future__ import annotations

from datetime import date, datetime


def parse_fecha(texto: str) -> date:
    """Interpreta AAAA-MM-DD o DD/MM/AAAA."""
    s = texto.strip()
    if not s:
        raise ValueError("La fecha es obligatoria.")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError("Use el formato AAAA-MM-DD o DD/MM/AAAA.")
