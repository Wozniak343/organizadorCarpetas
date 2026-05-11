from utils.logging_config import configurar_logging
from ui.app import AplicacionAutoFileOrganizer


def main() -> None:
    configurar_logging()
    aplicacion = AplicacionAutoFileOrganizer()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()