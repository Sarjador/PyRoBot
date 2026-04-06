"""
actions.py — Envío de acciones al Arduino Leonardo vía HID serie.
FASE 0: Puerto serie seguro con auto-detección y modo simulación.
"""
import time
import serial
import serial.tools.list_ports
import ctypes
import sys

# ─── Flag global para modo simulación ───────────────────────────────────────
SIMULATE = False  # Cambiar a True si no hay Arduino conectado

# ─── Logging ───────────────────────────────────────────────────────────────────
try:
    import logging
    _log = logging.getLogger("actions")
except ImportError:
    import logging
    class _DummyHandler(logging.Handler):
        def emit(self, record): print(f"[{record.levelname}] {record.getMessage()}")
    _log = logging.getLogger("actions")
    _log.addHandler(_DummyHandler())
    _log.setLevel(logging.DEBUG)

_log.info("Módulo actions cargado — serial AUTO-DETECT enabled")


# ─── Auto-detección del puerto serie ─────────────────────────────────────────
def _auto_detect_arduino(baudrate: int = 9600, timeout: float = 2.0):
    """
    Escanea todos los puertos serie y devuelve el primero que responde.
    Retorna (port_device, serial_obj) o (None, None) si no hay Arduino.
    """
    _log.debug("Escanenado puertos serie disponibles...")
    for port_info in serial.tools.list_ports.comports():
        try:
            _log.debug(f"Probando {port_info.device} ({port_info.description})")
            ser = serial.Serial(port_info.device, baudrate, timeout=timeout)
            time.sleep(1.5)  # Arduino Leonardo necesita ~1.2s para responder
            # Prueba de vida: envía un comando nulo y verifica que no falle
            ser.reset_input_buffer()
            ser.write(b"\n")
            ser.flush()
            _log.info(f"Arduino detectado en {port_info.device}")
            return port_info.device, ser
        except serial.SerialException as e:
            _log.debug(f"  {port_info.device} no disponible: {e}")
            continue
        except Exception as e:
            _log.debug(f"  {port_info.device} error inesperado: {e}")
            continue

    _log.warning("No se encontró ningún Arduino. Bot continuará en MODO SIMULACIÓN.")
    return None, None


# ─── Wrapper de conexión lazy ──────────────────────────────────────────────────
class HIDController:
    """
    Controlador HID serie con lazy-init y fallback a modo simulación.
    Usa auto-detección. Si no hay Arduino, simula las acciones.
    """

    def __init__(self, port: str = None, baudrate: int = 9600, simulate: bool = False):
        global SIMULATE
        SIMULATE = simulate  # Override global flag

        self._arduino = None
        self._port = port
        self._baudrate = baudrate
        self._connected = False

        if SIMULATE:
            _log.warning("Modo SIMULACIÓN forzado por argumento (--simulate).")
            return

        if port:
            # Puerto explícito proporcionado
            try:
                self._log_connect(port)
                self._arduino = serial.Serial(port, baudrate, timeout=2.0)
                time.sleep(1.5)
                self._connected = True
                _log.info(f"Conectado al puerto explícito: {port}")
                return
            except serial.SerialException as e:
                _log.error(f"No se pudo abrir {port}: {e}")
                _log.warning("Cayendo a modo simulación.")
        else:
            # Auto-detección
            device, self._arduino = _auto_detect_arduino(baudrate)
            if self._arduino:
                self._port = device
                self._connected = True
                return

        # Fallback: modo simulación silencioso
        SIMULATE = True

    def _log_connect(self, port: str):
        _log.debug(f"Intentando conectar a {port}...")

    @property
    def is_connected(self) -> bool:
        """True si hay un Arduino real conectado y abierto."""
        return self._connected and self._arduino is not None and self._arduino.is_open

    def send(self, cmd: str):
        """
        Envía un comando al Arduino.
        En modo simulación solo lo imprime.
        """
        if SIMULATE or not self.is_connected:
            _log.debug(f"[SIM] {cmd}")
            return

        try:
            self._arduino.write((cmd + "\n").encode())
            self._arduino.flush()
            _log.debug(f"[HID>] {cmd}")
        except serial.SerialException as e:
            _log.error(f"Error al enviar '{cmd}': {e}")
            _log.warning("Arduino desconectado — cayendo a modo simulación.")
            self._connected = False
            SIMULATE = True

    def close(self):
        """Cierra la conexión serie si está abierta."""
        if self._arduino and self._arduino.is_open:
            try:
                self._arduino.close()
                _log.info("Conexión serie cerrada.")
            except Exception as e:
                _log.error(f"Error cerrando puerto serie: {e}")


# ─── Instancia global con lazy-init ───────────────────────────────────────────
# Se crea bajo demanda la primera vez que se llama a _get_controller()
_hid: HIDController = None


def _get_controller() -> HIDController:
    global _hid
    if _hid is None:
        _hid = HIDController()
    return _hid


# ─── Funciones públicas ─────────────────────────────────────────────────────────

def send(cmd: str):
    """Envía un comando al Arduino (o simula si no hay hardware)."""
    _get_controller().send(cmd)


def enviar_comando(cmd: str):
    """Alias de send() para backwards compatibility."""
    send(cmd)


def get_cursor_pos():
    """Devuelve la posición actual del cursor en pantalla (Windows)."""
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def mover_fragmentado(dx: int, dy: int):
    """
    Desplaza el ratón en fragmentos de máximo ±127 píxeles
    para que el HID del Arduino Leonardo los acepte.
    """
    rem_x, rem_y = dx, dy
    while rem_x != 0 or rem_y != 0:
        step_x = max(-127, min(127, rem_x))
        step_y = max(-127, min(127, rem_y))
        send(f"MOVE:{step_x},{step_y}")
        rem_x -= step_x
        rem_y -= step_y


def click_izquierdo():
    """Envía el comando de clic izquierdo al Arduino."""
    send("CLICK")
    time.sleep(0.01)


def atacar(mobs=None):
    """
    Mueve el cursor al centro del primer mob y envía clic izquierdo.
    mobs: lista de tuplas (x1, y1, x2, y2) en coordenadas absolutas de pantalla.
    """
    if not mobs:
        _log.debug("Atacar: no hay mobs visibles")
        return

    x1, y1, x2, y2 = mobs[0]
    target_x = (x1 + x2) // 2
    target_y = (y1 + y2) // 2
    cur_x, cur_y = get_cursor_pos()
    dx = target_x - cur_x
    dy = target_y - cur_y

    _log.debug(f"Atacar → target=({target_x},{target_y}), delta=({dx},{dy})")
    mover_fragmentado(dx, dy)
    click_izquierdo()
    _log.debug(f"Atacar en ({target_x}, {target_y})")


def usar_pocion():
    send("Z")
    _log.debug("Usar poción (Z)")


def huir():
    send("L")
    _log.debug("Huir (L)")


def esperar():
    _log.debug("Esperar")


def ejecutar_accion(accion, mobs=None):
    """Dispacha una acción por nombre."""
    acciones = {
        "atacar":       lambda: atacar(mobs),
        "usar_pocion":  usar_pocion,
        "huir":         huir,
        "esperar":      esperar,
    }
    handler = acciones.get(accion, esperar)
    handler()
    _log.debug(f"Acción ejecutada: {accion}")


# ─── Cleanup al salir ──────────────────────────────────────────────────────────
import atexit as _atexit
_atexit.register(lambda: _get_controller().close())
