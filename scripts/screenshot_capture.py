import cv2
import numpy as np
import mss
import pygetwindow as gw
import time
import os
import sys
import re

# Directorio de guardado dinámico: "train" o "val" según argumento
SAVE_DIR = "dataset/val/images" if "--val" in sys.argv else "dataset/train/images"
CAPTURE_INTERVAL = 1       # Segundos entre capturas
MAX_CAPTURES = 50

def find_ragnarok_window():
    windows = gw.getWindowsWithTitle('Ragnarok')
    for win in windows:
        if win.visible and win.width > 0 and win.height > 0:
            print(f"Ventana encontrada: {win.title}")
            return win
    print("No se encontro la ventana de Ragnarok.")
    return None


def get_start_index():
    # Crear directorio si no existe y obtener el índice de inicio basado en archivos existentes
    os.makedirs(SAVE_DIR, exist_ok=True)
    archivos = os.listdir(SAVE_DIR)
    nums = []
    for f in archivos:
        m = re.match(r'ragnarok_(\d+)\.jpg', f)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


def capture_frame(window, count):
    with mss.mss() as sct:
        monitor = {
            "top": window.top,
            "left": window.left,
            "width": window.width,
            "height": window.height
        }
        img = sct.grab(monitor)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        filename = os.path.join(SAVE_DIR, f"ragnarok_{count:03}.jpg")
        cv2.imwrite(filename, frame)
        print(f"[✔] Captura guardada: {filename}")

        # Mostrar vista previa
        cv2.imshow("Vista previa", frame)
        cv2.waitKey(1)


def main():
    window = find_ragnarok_window()
    if not window:
        return

    start_index = get_start_index()
    print(f"Iniciando captura desde {start_index} cada {CAPTURE_INTERVAL}s... (Ctrl+C para salir)")
    try:
        for i in range(start_index, start_index + MAX_CAPTURES):
            capture_frame(window, i)
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("Captura cancelada por el usuario.")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
