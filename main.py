"""
main.py — Loop principal de PyRoBot.
FASE 0: Logging estructurado, manejo robusto de errores,
        shutdown limpio, y modo simulación.

Uso:
    python main.py                  # Modo normal
    python main.py --simulate       # Simula sin Arduino
    python main.py --simulate -v    # Simula + logs DEBUG en consola
"""
import sys
import time
import signal
import argparse
import logging

# ─── Logging ───────────────────────────────────────────────────────────────────
from core.logging_setup import setup_logging
# Se configura antes de importar el resto para que todo el código use logging
_log_root = setup_logging(level=logging.DEBUG)
log = logging.getLogger("main")

# ─── Argumentos de línea de comandos ───────────────────────────────────────────
parser = argparse.ArgumentParser(description="PyRoBot — Ragnarok AI Bot")
parser.add_argument(
    "--simulate", action="store_true",
    help="Activa modo simulación (sin Arduino, solo logs)."
)
parser.add_argument(
    "-v", "--verbose", action="store_true",
    help="Muestra logs DEBUG en consola."
)
parser.add_argument(
    "--frame-delay", type=float, default=0.2,
    help="Delay entre frames en segundos (default: 0.2)."
)
args = parser.parse_args()

# ─── Modo simulación (pasa a actions.py) ──────────────────────────────────────
if args.simulate:
    # Patchear SIMULATE antes de que cualquier módulo lo importe
    import core.actions as _actions_module
    _actions_module.SIMULATE = True
    log.warning("MODO SIMULACIÓN activo — las acciones se imprimen, no se envían al Arduino.")

# ─── Imports del core (después de logging para capturar todo) ─────────────────
from core.capture       import encontrar_ventana, capturar_client_area, get_client_rect
from core.detection     import detectar_mobs
from core.hud_reader    import leer_hp_sp
from core.actions       import ejecutar_accion, send as hid_send
from core.history_logger import inicializar_log, registrar_decision
from core.agent_rl       import QLearningAgent
from core.rewards        import calcular_recompensa

# ─── Graceful shutdown ─────────────────────────────────────────────────────────
_running = True


def _signal_handler(signum, frame):
    global _running
    log.info(f"Señal {signum} recibida — deteniendo bot.")
    _running = False


signal.signal(signal.SIGINT,  _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


# ─── Verificación de ventana ──────────────────────────────────────────────────
def _verificar_ventana():
    """Busca la ventana del juego. Reintenta 3 veces con espera."""
    for intento in range(1, 4):
        ventana = encontrar_ventana()
        if ventana:
            left, top, width, height = get_client_rect(ventana._hWnd)
            log.info(f"Ventana encontrada: {width}×{height} en ({left},{top})")
            return ventana
        log.warning(f"Ventana no encontrada (intento {intento}/3)")
        if intento < 3:
            time.sleep(2)
    return None


# ─── Función de frame con manejo de errores ────────────────────────────────────
def _procesar_frame(frame, frame_num: int, hp_anterior: float):
    """
    Procesa un frame: detección → OCR → decisión → acción → aprendizaje.
    Cada paso tiene su propio try/except para que un fallo parcial
    no detenga el loop.

    Returns:
        (next_hp, next_sp) para la siguiente iteración.
    """
    log_debug = logging.getLogger("main.frame")

    # ── 1. Detección de mobs ──────────────────────────────────────────────────
    try:
        mobs = detectar_mobs(frame)
        log_debug.debug(f"Frame {frame_num}: {len(mobs)} mobs detectados")
    except Exception as e:
        log.error(f"Detección falló: {e}")
        mobs = []

    # ── 2. OCR HUD ───────────────────────────────────────────────────────────
    try:
        hp, sp = leer_hp_sp(frame)
        log_debug.debug(f"Frame {frame_num}: HP={hp}% | SP={sp}%")
    except Exception as e:
        log.error(f"OCR HUD falló: {e}")
        hp, sp = hp_anterior, 50  # Fallback: mantener HP anterior, SP neutral

    # ── 3. Estado y decisión ─────────────────────────────────────────────────
    estado = (hp, sp, len(mobs))
    try:
        accion = agente.choose_action(estado)
        log_debug.debug(f"Estado={estado} → Acción={accion}")
    except Exception as e:
        log.error(f"Agente RL falló: {e}")
        accion = "esperar"

    # ── 4. Ejecución de acción ───────────────────────────────────────────────
    try:
        ejecutar_accion(accion, mobs)
    except Exception as e:
        log.error(f"Ejecución de acción '{accion}' falló: {e}")

    # ── 5. Aprendizaje (pequeña pausa para que el juego reaccione) ────────────
    time.sleep(args.frame_delay)

    return hp, sp


# ─── Inicialización ────────────────────────────────────────────────────────────
log.info("=" * 60)
log.info("PyRoBot — Ragnarok AI Bot  (Ctrl+C para detener)")
log.info("=" * 60)

# Ventana del juego
ventana = _verificar_ventana()
if not ventana:
    log.critical("No se pudo encontrar la ventana del juego. Saliendo.")
    sys.exit(1)

# Agente RL — se carga y guarda automáticamente (ver agent_rl.py FASE 0)
agente = QLearningAgent(actions=["atacar", "usar_pocion", "huir", "esperar"])
log.info(f"Agente RL inicializado — acciones: {agente.actions}")
log.info(f"Epsilon actual: {agente.epsilon:.4f}")

# Logger de histórico
inicializar_log()

# ─── Loop principal ───────────────────────────────────────────────────────────
log.info("Iniciando loop principal...")
hp_anterior = 100.0
frame_num = 0
fps_tgt = 1 / args.frame_delay  # FPS objetivo

try:
    while _running:
        frame_num += 1
        t_start = time.time()

        # Captura de frame
        try:
            frame = capturar_client_area(ventana)
        except Exception as e:
            log.error(f"Capture falló: {e}")
            time.sleep(1)
            continue

        # Procesamiento
        try:
            frame_next = capturar_client_area(ventana)
        except Exception:
            frame_next = frame  # Fallback

        try:
            mobs_next = detectar_mobs(frame_next)
        except Exception:
            mobs_next = []

        hp_next, sp_next = _procesar_frame(frame, frame_num, hp_anterior)

        # ── Aprendizaje y registro ──────────────────────────────────────────
        estado      = (hp_anterior, 50, 0)  # Estado anterior (simplificado)
        next_state  = (hp_next, sp_next, len(mobs_next))
        recompensa  = calcular_recompensa(
            hp_next, sp_next, mobs_next,
            agente.last_action, hp_anterior
        )

        try:
            agente.learn(estado, accion, recompensa, next_state)
        except Exception as e:
            log.error(f"Aprendizaje RL falló: {e}")

        try:
            agente.save()
        except Exception as e:
            log.warning(f"No se pudo guardar Q-table: {e}")

        registrar_decision(
            hp_next, sp_next, mobs_next,
            getattr(agente, 'last_action', 'desconocida')
        )

        # Log de resumen por frame
        accion = getattr(agente, 'last_action', 'desconocida')
        log.info(
            f"Frame #{frame_num:05d} | "
            f"HP={hp_next}% SP={sp_next}% | "
            f"Mobs={len(mobs_next)} | "
            f"Acc={accion} | "
            f"Reward={recompensa:+d}"
        )

        hp_anterior = hp_next

        # ── FPS throttling ──────────────────────────────────────────────────
        elapsed = time.time() - t_start
        sleep_time = max(0, args.frame_delay - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            log.warning(f"Frame {frame_num} sobrepasó deadline (+{-elapsed*1000:.0f}ms)")

except KeyboardInterrupt:
    pass  # Ya manejado por signal_handler
finally:
    # ── Cleanup ──────────────────────────────────────────────────────────────
    log.info("Guardando Q-table final...")
    try:
        agente.save()
    except Exception as e:
        log.error(f"Error guardando Q-table al salir: {e}")

    log.info("Cerrando conexiones...")
    try:
        from core.actions import _get_controller
        _get_controller().close()
    except Exception as e:
        log.error(f"Error cerrando HID: {e}")

    log.info("PyRoBot detenido correctamente.")
