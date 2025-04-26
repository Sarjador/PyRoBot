import time
import serial
import ctypes

# Configura tu puerto serie con el Arduino Leonardo
arduino = serial.Serial('COM23', 9600, timeout=1)

def enviar_comando(cmd: str):
    """Envía un comando (MOVE, CLICK o tecla) al Arduino."""
    arduino.write((cmd + '\n').encode())
    print(f"[HID>] {cmd}")
    time.sleep(0.01)

def get_cursor_pos():
    """Devuelve la posición actual del cursor en pantalla."""
    class POINT(ctypes.Structure):
        _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def mover_fragmentado(dx: int, dy: int):
    """
    Desplaza el ratón en fragmentos de máximo ±127 píxeles para que HID los acepte.
    """
    rem_x, rem_y = dx, dy
    while rem_x != 0 or rem_y != 0:
        step_x = max(-127, min(127, rem_x))
        step_y = max(-127, min(127, rem_y))
        enviar_comando(f"MOVE:{step_x},{step_y}")
        rem_x -= step_x
        rem_y -= step_y

def click_izquierdo():
    """Envía el comando de clic izquierdo al Arduino."""
    enviar_comando("CLICK")
    time.sleep(0.01)

def atacar(mobs=None):
    """
    Ataca al primer mob:
    mobs: lista de tuplas (x1, y1, x2, y2) en coordenadas de pantalla.
    """
    if not mobs:
        print("[ACCION] Atacar fallido: no hay mobs")
        return

    # 1) Centro de la caja (ya absolutas)
    x1, y1, x2, y2 = mobs[0]
    target_x = (x1 + x2) // 2
    target_y = (y1 + y2) // 2

    # 2) Delta relativo desde el cursor actual
    cur_x, cur_y = get_cursor_pos()
    dx = target_x - cur_x
    dy = target_y - cur_y

    print(f"Atacar → target=({target_x},{target_y}), cursor=({cur_x},{cur_y}), delta=({dx},{dy})")

    # 3) Mueve fragmentado hasta la posición
    mover_fragmentado(dx, dy)

    # 4) Clic físico
    click_izquierdo()
    print(f"[ACCION] Atacar en ({target_x}, {target_y})")

def usar_pocion():
    enviar_comando('Z')
    print("[ACCION] Usar poción (Z)")

def huir():
    enviar_comando('L')
    print("[ACCION] Huir (L)")

def esperar():
    print("[ACCION] Esperar")

def ejecutar_accion(accion, mobs=None):
    acciones = {
        "atacar": lambda: atacar(mobs),
        #"usar_pocion": usar_pocion,
        #"huir": huir,
        "esperar": esperar
    }
    acciones.get(accion, esperar)()
