from core.controller import GameController
from utils.logger import setup_logger
import config.settings as settings


def main():
    logger = setup_logger()
    logger.info("Iniciando Ragnarök Bot con CUDA")

    try:
        controller = GameController()
        controller.run()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()