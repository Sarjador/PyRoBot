"""
logging_setup.py — Configuración centralizada de logging para todo el bot.
FASE 0: Logging estructurado con rotación de archivos.

Uso:
    from core.logging_setup import setup_logging
    logger = setup_logging("MiModulo")
    logger.info("Mensaje")
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# ─── Directorio de logs ────────────────────────────────────────────────────────
_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

# ─── Configuración global ──────────────────────────────────────────────────────
_FORMAT_LONG  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
_FORMAT_SHORT = "%(asctime)s [%(levelname)s] %(message)s"
_DATE_FORMAT  = "%Y-%m-%d %H:%M:%S"

# Niveles por módulo (permite ajustar sin cambiar código)
_MODULE_LEVELS = {
    "actions":     logging.INFO,   # No spamear DEBUG en prod
    "hud_reader":  logging.INFO,
    "capture":     logging.WARNING,
    "detection":   logging.WARNING,
    "agent_rl":    logging.INFO,
    "main":        logging.INFO,
}


def setup_logging(
    level: int = logging.INFO,
    log_file: str = "bot.log",
    max_bytes: int = 5 * 1024 * 1024,   # 5 MB por archivo
    backup_count: int = 3,
    console: bool = True,
) -> logging.Logger:
    """
    Configura logging global con:
    - Rotación de archivo (logs/bot.log → bot.log.1, .2, .3)
    - Consola con color (opcional)
    - Niveles por módulo ajustables

    Debe llamarse UNA vez al inicio de main.py.
    Retorna el logger raíz para uso directo.
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # Captura todo; los handlers filtran

    # Evita duplicar handlers si se llama dos veces
    if root.hasHandlers():
        root.handlers.clear()

    # ── Handler de archivo con rotación ──────────────────────────────────────
    file_path = os.path.join(_LOG_DIR, log_file)
    file_handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FORMAT_LONG, datefmt=_DATE_FORMAT))
    root.addHandler(file_handler)

    # ── Handler de consola ───────────────────────────────────────────────────
    if console:
        console_handler = _ColorConsoleHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter(_FORMAT_SHORT, datefmt=_DATE_FORMAT)
        )
        root.addHandler(console_handler)

    # ── Niveles por módulo ────────────────────────────────────────────────────
    for module_name, module_level in _MODULE_LEVELS.items():
        mod_logger = logging.getLogger(module_name)
        mod_logger.setLevel(module_level)

    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    root.info("=" * 60)
    root.info("PyRoBot iniciado — logging activo")
    root.info(f"Log file: {file_path}")
    root.info("=" * 60)

    return root


# ─── Handler de consola con color ──────────────────────────────────────────────
class _ColorConsoleHandler(logging.StreamHandler):
    """
    Handler que colorea la salida según nivel:
      DEBUG   → gris
      INFO    → blanco
      WARNING → amarillo
      ERROR   → rojo
      CRITICAL→ rojo brillante (negrita)
    """

    COLORS = {
        logging.DEBUG:    "\033[90m",    # gris
        logging.INFO:    "\033[97m",    # blanco
        logging.WARNING:  "\033[33m",    # amarillo
        logging.ERROR:    "\033[31m",   # rojo
        logging.CRITICAL: "\033[1;31m",  # rojo negrita
    }
    RESET = "\033[0m"

    def emit(self, record):
        try:
            color = self.COLORS.get(record.levelno, self.RESET)
            record.msg = f"{color}{record.msg}{self.RESET}"
            super().emit(record)
        except Exception:
            self.handleError(record)


# ─── Acceso rápido ─────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    """Equivalent to logging.getLogger(name) but consistent pattern."""
    return logging.getLogger(name)
