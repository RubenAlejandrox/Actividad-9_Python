"""Punto de entrada del controlador: crea la vista principal y el bucle de eventos."""
from view.main_window import UniversidadApp


def main() -> None:
    app = UniversidadApp()
    app.mainloop()


if __name__ == "__main__":
    main()
