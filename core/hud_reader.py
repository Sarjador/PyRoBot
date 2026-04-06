import cv2
import numpy as np
import pytesseract
import os

# Tesseract path: configurable via environment variable
# On Windows: set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
# On Linux: usually available in PATH, no need to set
_tesseract_cmd = os.environ.get("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


# HUD READER: Para leer HP y SP desde la interfaz fija del juego

# Asegúrate de tener pytesseract instalado y correctamente configurado.
# https://github.com/tesseract-ocr/tesseract/releases

def extraer_region_hp_sp(frame):
    """
    Recorta las regiones donde se muestran los porcentajes de HP y SP (como texto).
    """
    hp_text_region = frame[88:103, 179:211]  # Ajustado al 100% que aparece a la derecha de la barra de HP
    sp_text_region = frame[103:116, 179:211]  # Ajustado al 100% de SP
    return hp_text_region, sp_text_region

def ocr_porcentaje(region):
    """
    Extrae un porcentaje del texto como número entero usando OCR.
    """
    gris = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    _, umbral = cv2.threshold(gris, 180, 255, cv2.THRESH_BINARY)
    texto = pytesseract.image_to_string(umbral, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    try:
        return int(texto.strip())
    except ValueError:
        return 0

def leer_hp_sp(frame):
    """
    Lee el porcentaje de HP y SP desde la pantalla usando OCR.
    """
    hp_region, sp_region = extraer_region_hp_sp(frame)
    hp_leido = ocr_porcentaje(hp_region)
    sp_leido = ocr_porcentaje(sp_region)

    # Debug visual
    cv2.imshow("HP OCR", hp_region)
    cv2.imshow("SP OCR", sp_region)
    cv2.imshow("Vista Previa - Captura de ventana", frame)
    cv2.waitKey(1)

    return hp_leido, sp_leido

# Prueba manual
if __name__ == "__main__":
    from core import capture
    ventana = capture.encontrar_ventana()
    if ventana:
        frame = capture.capturar_client_area(ventana)
        hp, sp = leer_hp_sp(frame)
        print(f"HP: {hp}% | SP: {sp}%")
    else:
        print("No se encontró la ventana del juego.")
