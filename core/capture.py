import ctypes
import mss
import numpy as np
import win32gui
import pygetwindow as gw
import cv2

# Asegura que las coordenadas de ventana sean correctas en pantallas con DPI scaling
ctypes.windll.user32.SetProcessDPIAware()


def encontrar_ventana(titulo_parcial="Ragnarok"):
    """
    Busca y devuelve la primera ventana visible cuyo título contiene el texto proporcionado.
    Ajusta por DPI y verifica dimensiones.
    """
    # Enumerar ventanas
    ventanas = gw.getWindowsWithTitle(titulo_parcial)
    for ventanaro in ventanas:
        if ventanaro.visible and ventanaro.width > 0 and ventanaro.height > 0:
            # Asegurarse de que las coordenadas sean enteros y sin escalado
            #ventanaro.left = int(ventanaro.left)
            #ventanaro.top = int(ventanaro.top)
            #ventanaro.width = int(ventanaro.width)
            #ventanaro.height = int(ventanaro.height)
            #print(f"[CAPTURE] Ventana encontrada: {ventana.title} -> ({ventana.left},{ventana.top},{ventana.width},{ventana.height})")
            return ventanaro
    print("[CAPTURE] No se encontró la ventana del juego.")
    return None

def get_client_rect(hwnd):
    # Devuelve (left, top, width, height) del área cliente en coords de pantalla
    x0, y0 = win32gui.ClientToScreen(hwnd, (0, 0))
    l, t, r, b = win32gui.GetClientRect(hwnd)
    return x0, y0, r - l, b - t

def capturar_client_area(ventana):
    """Captura sólo el área cliente del HWND proporcionado."""
    hwnd = ventana._hWnd
    left, top, w, h = get_client_rect(hwnd)
    monitor = {"left": left, "top": top, "width": w, "height": h}
    with mss.mss() as sct:
        img = sct.grab(monitor)
        frame = np.array(img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


# Uso de ejemplo para vista previa en tiempo real
if __name__ == "__main__":
    ventana = encontrar_ventana()
    if not ventana:
        print("No se ha podido capturar la ventana.")
        exit()
    print("Client area:", get_client_rect(ventana._hWnd))
    try:
        while True:
            frame = capturar_client_area(ventana)
            cv2.imshow("Cliente", frame)
            # Pulsa ESC para salir de la vista previa
            if cv2.waitKey(30) == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
