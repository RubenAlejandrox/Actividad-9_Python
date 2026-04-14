"""Arranque de la aplicación (controlador)."""
from vista.ventana_principal import VentanaUniversidad


def main() -> None:
    app = VentanaUniversidad()
    app.mainloop()


if __name__ == "__main__":
    main()
