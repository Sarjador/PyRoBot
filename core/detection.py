import cv2
import numpy as np
from ultralytics import YOLO
from core.capture import encontrar_ventana, get_client_rect

# Ajusta esta ruta a tu modelo real
MODEL_PATH = "F:/GITHUB_REPOS/runs/detect/train2/weights/best.pt"
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
            abs_boxes.append((x1 + left, y1 + top, x2 + left, y2 + top))
    return abs_boxes

if __name__ == "__main__":
    from core.capture import capturar_client_area
    v = encontrar_ventana()
    frame = capturar_client_area(v)
    boxes = detectar_mobs(frame)
    print("ABS boxes:", boxes)
    # Dibuja para verificación:
    for x1,y1,x2,y2 in boxes:
        rx = x1 - left; ry = y1 - top  # relativos al frame
        cv2.rectangle(frame, (rx, ry), (x2-left, y2-top), (0,255,0), 2)
    cv2.imshow("abs detection", frame)
    cv2.waitKey(0)
