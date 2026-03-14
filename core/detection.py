import cv2
import numpy as np
from ultralytics import YOLO
from core.capture import encontrar_ventana, get_client_rect
import os

# Load model path from environment or default to repository model
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "yolov8n.pt")
MODEL_PATH = os.environ.get("PYROBOT_MODEL_PATH", os.path.abspath(os.path.normpath(DEFAULT_MODEL_PATH)))
model = YOLO(MODEL_PATH)

def detectar_mobs(frame, conf=0.25):
    """
    Devuelve cajas en coords ABSOLUTAS de pantalla:
      [(x1_abs, y1_abs, x2_abs, y2_abs), ...]
    """
    ventana = encontrar_ventana()
    if not ventana:
        raise RuntimeError("Ventana de juego no encontrada")
    left, top, _, _ = get_client_rect(ventana._hWnd)

    resultados = model.predict(source=frame, conf=conf, verbose=False)
    abs_boxes = []
    for res in resultados:
        for b in res.boxes.xyxy.cpu().numpy().astype(int):
            x1, y1, x2, y2 = b
            abs_boxes.append((int(x1) + int(left), int(y1) + int(top), int(x2) + int(left), int(y2) + int(top)))
    return abs_boxes

if __name__ == "__main__":
    from core.capture import capturar_client_area
    v = encontrar_ventana()
    frame = capturar_client_area(v)
    boxes = detectar_mobs(frame)
    print("ABS boxes:", boxes)
