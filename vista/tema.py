"""Paleta y estilos ttk (vista)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

AZUL_MARINO = "#0c2340"
AZUL_OSCURO = "#08182c"
AZUL_MEDIO = "#153a5c"
FONDO_VENTANA = "#e6ecf4"
FONDO_PANEL = "#f4f7fb"
TEXTO = "#1a2332"
TEXTO_SECUNDARIO = "#4a5568"
BLANCO = "#ffffff"
BORDE = "#2c5282"
FILA_PAR = "#f0f4fa"
FILA_SELECCIONADA = "#c5d7eb"
NARANJA = "#f37021"
NARANJA_BOTON = NARANJA
PESTANA_INACTIVA = "#cbd5e1"


def configurar_estilos_ttk(raiz: tk.Tk) -> ttk.Style:
    estilo = ttk.Style(raiz)
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    estilo.configure(".", background=FONDO_VENTANA, foreground=TEXTO, font=("Segoe UI", 10))

    estilo.configure("TFrame", background=FONDO_PANEL)
    estilo.configure("App.TFrame", background=FONDO_VENTANA)
    estilo.configure("Card.TFrame", background=FONDO_PANEL)

    estilo.configure(
        "TLabel",
        background=FONDO_PANEL,
        foreground=TEXTO,
    )
    estilo.configure(
        "Muted.TLabel",
        background=FONDO_PANEL,
        foreground=TEXTO_SECUNDARIO,
        font=("Segoe UI", 9),
    )

    estilo.configure(
        "TLabelframe",
        background=FONDO_PANEL,
        foreground=AZUL_MARINO,
        bordercolor=BORDE,
        relief="solid",
        borderwidth=1,
    )
    estilo.configure(
        "TLabelframe.Label",
        background=FONDO_PANEL,
        foreground=AZUL_MARINO,
        font=("Segoe UI", 10, "bold"),
    )

    estilo.configure(
        "TNotebook",
        background=FONDO_VENTANA,
        borderwidth=0,
    )
    estilo.configure(
        "TNotebook.Tab",
        background=PESTANA_INACTIVA,
        foreground=TEXTO,
        padding=(14, 8),
        font=("Segoe UI", 10),
    )
    estilo.map(
        "TNotebook.Tab",
        background=[("selected", AZUL_MEDIO), ("active", NARANJA)],
        foreground=[("selected", BLANCO), ("active", BLANCO)],
    )

    estilo.configure(
        "TButton",
        background=AZUL_MARINO,
        foreground=BLANCO,
        bordercolor=AZUL_OSCURO,
        focusthickness=3,
        focuscolor=FILA_SELECCIONADA,
        padding=(10, 6),
        font=("Segoe UI", 9, "bold"),
    )
    estilo.map(
        "TButton",
        background=[("active", NARANJA_BOTON), ("pressed", AZUL_OSCURO), ("disabled", PESTANA_INACTIVA)],
        foreground=[("disabled", TEXTO_SECUNDARIO)],
    )

    estilo.configure(
        "Secondary.TButton",
        background=AZUL_MEDIO,
        foreground=BLANCO,
        padding=(8, 5),
        font=("Segoe UI", 9),
    )
    estilo.map(
        "Secondary.TButton",
        background=[("active", AZUL_MARINO), ("pressed", AZUL_OSCURO)],
    )

    estilo.configure(
        "TEntry",
        fieldbackground=BLANCO,
        foreground=TEXTO,
        bordercolor=BORDE,
        lightcolor=FONDO_PANEL,
        darkcolor=BORDE,
        insertcolor=AZUL_MARINO,
        padding=(6, 4),
    )
    estilo.map("TEntry", bordercolor=[("focus", AZUL_MARINO)])

    estilo.configure(
        "TCombobox",
        fieldbackground=BLANCO,
        background=BLANCO,
        foreground=TEXTO,
        arrowcolor=AZUL_MARINO,
        bordercolor=BORDE,
        padding=(4, 2),
    )
    estilo.map("TCombobox", bordercolor=[("focus", AZUL_MARINO)], arrowcolor=[("readonly", AZUL_MARINO)])

    estilo.configure(
        "Vertical.TScrollbar",
        background=AZUL_MEDIO,
        troughcolor=FONDO_PANEL,
        bordercolor=BORDE,
        arrowcolor=BLANCO,
    )
    estilo.configure(
        "Horizontal.TScrollbar",
        background=AZUL_MEDIO,
        troughcolor=FONDO_PANEL,
        bordercolor=BORDE,
        arrowcolor=BLANCO,
    )

    estilo.configure(
        "Treeview",
        background=BLANCO,
        fieldbackground=BLANCO,
        foreground=TEXTO,
        rowheight=26,
        bordercolor=BORDE,
        borderwidth=0,
        font=("Segoe UI", 9),
    )
    estilo.configure(
        "Treeview.Heading",
        background=AZUL_MARINO,
        foreground=BLANCO,
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    estilo.map(
        "Treeview",
        background=[("selected", FILA_SELECCIONADA)],
        foreground=[("selected", TEXTO)],
    )

    return estilo
