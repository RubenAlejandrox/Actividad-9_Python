"""Paleta y estilos ttk de la aplicación (identidad visual)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# --- Paleta institucional (azul marino) ---
COLOR_NAVY = "#0c2340"
COLOR_NAVY_DARK = "#08182c"
COLOR_NAVY_MID = "#153a5c"
COLOR_BG_APP = "#e6ecf4"
COLOR_BG_PANEL = "#f4f7fb"
COLOR_TEXT = "#1a2332"
COLOR_TEXT_MUTED = "#4a5568"
COLOR_WHITE = "#ffffff"
COLOR_BORDER = "#2c5282"
COLOR_ROW_ALT = "#f0f4fa"
COLOR_ROW_SELECT = "#c5d7eb"
COLOR_ORANGE = "#f37021"
COLOR_BTN_HOVER = COLOR_ORANGE
COLOR_TAB_INACTIVE = "#cbd5e1"


def configurar_tema_ttk(root: tk.Tk) -> ttk.Style:
    """Aplica estilos ttk coherentes con la identidad visual (azul marino)."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=COLOR_BG_APP, foreground=COLOR_TEXT, font=("Segoe UI", 10))

    style.configure("TFrame", background=COLOR_BG_PANEL)
    style.configure("App.TFrame", background=COLOR_BG_APP)
    style.configure("Card.TFrame", background=COLOR_BG_PANEL)

    style.configure(
        "TLabel",
        background=COLOR_BG_PANEL,
        foreground=COLOR_TEXT,
    )
    style.configure(
        "Muted.TLabel",
        background=COLOR_BG_PANEL,
        foreground=COLOR_TEXT_MUTED,
        font=("Segoe UI", 9),
    )

    style.configure(
        "TLabelframe",
        background=COLOR_BG_PANEL,
        foreground=COLOR_NAVY,
        bordercolor=COLOR_BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=COLOR_BG_PANEL,
        foreground=COLOR_NAVY,
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "TNotebook",
        background=COLOR_BG_APP,
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=COLOR_TAB_INACTIVE,
        foreground=COLOR_TEXT,
        padding=(14, 8),
        font=("Segoe UI", 10),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLOR_NAVY_MID), ("active", COLOR_ORANGE)],
        foreground=[("selected", COLOR_WHITE), ("active", COLOR_WHITE)],
    )

    style.configure(
        "TButton",
        background=COLOR_NAVY,
        foreground=COLOR_WHITE,
        bordercolor=COLOR_NAVY_DARK,
        focusthickness=3,
        focuscolor=COLOR_ROW_SELECT,
        padding=(10, 6),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", COLOR_BTN_HOVER), ("pressed", COLOR_NAVY_DARK), ("disabled", COLOR_TAB_INACTIVE)],
        foreground=[("disabled", COLOR_TEXT_MUTED)],
    )

    style.configure(
        "Secondary.TButton",
        background=COLOR_NAVY_MID,
        foreground=COLOR_WHITE,
        padding=(8, 5),
        font=("Segoe UI", 9),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLOR_NAVY), ("pressed", COLOR_NAVY_DARK)],
    )

    style.configure(
        "TEntry",
        fieldbackground=COLOR_WHITE,
        foreground=COLOR_TEXT,
        bordercolor=COLOR_BORDER,
        lightcolor=COLOR_BG_PANEL,
        darkcolor=COLOR_BORDER,
        insertcolor=COLOR_NAVY,
        padding=(6, 4),
    )
    style.map("TEntry", bordercolor=[("focus", COLOR_NAVY)])

    style.configure(
        "TCombobox",
        fieldbackground=COLOR_WHITE,
        background=COLOR_WHITE,
        foreground=COLOR_TEXT,
        arrowcolor=COLOR_NAVY,
        bordercolor=COLOR_BORDER,
        padding=(4, 2),
    )
    style.map("TCombobox", bordercolor=[("focus", COLOR_NAVY)], arrowcolor=[("readonly", COLOR_NAVY)])

    style.configure(
        "Vertical.TScrollbar",
        background=COLOR_NAVY_MID,
        troughcolor=COLOR_BG_PANEL,
        bordercolor=COLOR_BORDER,
        arrowcolor=COLOR_WHITE,
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=COLOR_NAVY_MID,
        troughcolor=COLOR_BG_PANEL,
        bordercolor=COLOR_BORDER,
        arrowcolor=COLOR_WHITE,
    )

    style.configure(
        "Treeview",
        background=COLOR_WHITE,
        fieldbackground=COLOR_WHITE,
        foreground=COLOR_TEXT,
        rowheight=26,
        bordercolor=COLOR_BORDER,
        borderwidth=0,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background=COLOR_NAVY,
        foreground=COLOR_WHITE,
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_ROW_SELECT)],
        foreground=[("selected", COLOR_TEXT)],
    )

    return style
