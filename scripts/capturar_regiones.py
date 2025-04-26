import cv2
from core.capture import encontrar_ventana, capturar_client_area, get_client_rect
from core.hud_reader import extraer_region_hp_sp

ventana = encontrar_ventana()
if not ventana:
    print("No se encontró la ventana del juego.")
    exit()

while True:
    frame = capturar_client_area(ventana)

    # Extraer regiones según las coordenadas actuales
    hp_img, sp_img = extraer_region_hp_sp(frame)

    # Dibujar rectángulos sobre el frame
    # (frame, (largo_inicial, ancho_inicial), (largo_final, ancho_final), (R, G, B), grosor_rectangulo)
    cv2.rectangle(frame, (179, 88), (211, 103), (0, 255, 0), 1)  # HP
    cv2.rectangle(frame, (179, 103), (211, 116), (255, 0, 0), 1)  # SP

    # Mostrar preview
    cv2.imshow("Calibracion HUD", frame)
    cv2.imshow("HP Region", hp_img)
    cv2.imshow("SP Region", sp_img)

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break

cv2.destroyAllWindows()
