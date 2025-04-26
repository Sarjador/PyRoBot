import cv2
import numpy as np
import mss
import pygetwindow as gw
from ultralytics import YOLO
import time

# yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=500 imgsz=800 device=0

MODEL_PATH = "F:/GITHUB_REPOS/runs/detect/train/weights/best.pt"
CONFIDENCE_THRESHOLD = 0.5

# Inicializa el modelo YOLOv8
model = YOLO(MODEL_PATH)

def find_ragnarok_window():
    windows = gw.getWindowsWithTitle('Ragnarok')
    for win in windows:
        if win.visible and win.width > 0 and win.height > 0:
            print(f"Ventana encontrada: {win.title}")
            return win
    print("No se encontro la ventana de Ragnarok.")
    return None

def capture_with_mss(window):
    with mss.mss() as sct:
        monitor = {
            "top": window.top,
            "left": window.left,
            "width": window.width,
            "height": window.height
        }
        img = sct.grab(monitor)
        frame = np.array(img)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def main():
    window = find_ragnarok_window()
    if not window:
        return

    print("Iniciando detección con YOLOv8... (ESC para salir)")
    try:
        while True:
            frame = capture_with_mss(window)
            results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, verbose=True)

            for result in results:
                for box in result.boxes.xyxy.cpu().numpy():
                    x1, y1, x2, y2 = box[:4].astype(int)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("YOLOv8 - Deteccion de Mobs", frame)
            if cv2.waitKey(1) == 27:  # ESC
                break
    except KeyboardInterrupt:
        print("Detección interrumpida por el usuario.")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
