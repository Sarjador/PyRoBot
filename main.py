from core.game_controller import GameController
from utils.logger import setup_logger
import config.settings as settings


def main():
    # Configurar logger
    logger = setup_logger()

    try:
        logger.info("Iniciando Ragnarök Bot")
        logger.info(f"Configuración CUDA: {settings.Config.USE_CUDA}")

        # Inicializar controlador
        controller = GameController()

        # Iniciar bucle principal
        controller.start()

    except Exception as e:
        logger.error(f"Error crítico: {str(e)}", exc_info=True)
    finally:
        logger.info("Aplicación terminada")


if __name__ == "__main__":
    main()
