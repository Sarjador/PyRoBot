"""
hud_reader.py — Lectura de HP/SP desde el HUD del juego mediante OCR.
FASE 0: Sin cv2.imshow, OCR robusto con validación de rango y flag DEBUG.
"""
import os
import logging

# ─── Logging ───────────────────────────────────────────────────────────────────
_log = logging.getLogger("hud_reader")

# ─── Tesseract path (environment variable override) ───────────────────────────
_tesseract_cmd = os.environ.get("TESSERACT_CMD")
if _tesseract_cmd and os.path.exists(_tesseract_cmd):
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd
    _log.info(f"Tesseract configurado desde env: {_tesseract_cmd}")

# Importar pytesseract aquí para que esté disponible globalmente
import pytesseract
import cv2
import numpy as np

# ─── Configuración ──────────────────────────────────────────────────────────────
DEBUG_VISION = os.environ.get("HUD_DEBUG", "0") == "1"

# Regiones del HUD en coordenadas relativas al frame capturado.
# Ajustar si la resolución de pantalla o posición del HUD cambia.
HUD_HP_REGION = (179, 88, 211, 103)   # (x1, y1, x2, y2)
HUD_SP_REGION = (179, 103, 211, 116) # (x1, y1, x2, y2)

# Configuración de OCR: PSM 7 = línea única, whitelist de dígitos
OCR_CONFIG = "--psm 7 -c tessedit_char_whitelist=0123456789"
OCR_CONFIG_DEBUG = "--psm 7"  # Sin whitelist cuando queremos ver qué lee


# ─── Preprocesamiento de imagen para OCR ───────────────────────────────────────

def _preprocess_region(region: np.ndarray) -> np.ndarray:
    """
    Preprocesa una región de imagen para mejorar la precisión del OCR.
    1. Conversión a escala de grises
    2. Binarización invertida (fondo negro, texto blanco)
    3. Dilatación ligera para unir trazos fragmentados
    """
    if region is None or region.size == 0:
        return np.zeros((20, 80), dtype=np.uint8)

    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

    # Binarización con Otsu (umbral automático)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilatación légère para robustez ante texto pequeño/borroso
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)

    return dilated


# ─── OCR ───────────────────────────────────────────────────────────────────────

def ocr_porcentaje(region: np.ndarray, validate: bool = True) -> int:
    """
    Extrae un porcentaje entero desde una región de imagen.

    Args:
        region: imagen recortada del área HP o SP
        validate: si True, fuerza el resultado a rango 0-100

    Returns:
        Entero 0-100 con el porcentaje leído, o 0 si el OCR falla.
    """
    processed = _preprocess_region(region)
    texto = pytesseract.image_to_string(processed, config=OCR_CONFIG)
    limpio = texto.strip()

    try:
        valor = int(limpio)
    except ValueError:
        _log.debug(f"OCR falló → texto='{limpio}', returning 0")
        return 0

    if validate:
        valor = max(0, min(100, valor))  # Clamp a rango válido

    return valor


# ─── Lectura principal ──────────────────────────────────────────────────────────

def extraer_region_hp_sp(frame: np.ndarray):
    """
    Recorta las regiones donde se muestran los porcentajes de HP y SP.
    Args:
        frame: frame completo capturado desde la ventana del juego.
    Returns:
        (hp_region, sp_region) — ambas como imágenes BGR.
    """
    x1_hp, y1_hp, x2_hp, y2_hp = HUD_HP_REGION
    x1_sp, y1_sp, x2_sp, y2_sp = HUD_SP_REGION

    hp_region = frame[y1_hp:y2_hp, x1_hp:x2_hp]
    sp_region = frame[y1_sp:y2_sp, x1_sp:x2_sp]

    return hp_region, sp_region


def leer_hp_sp(frame: np.ndarray):
    """
    Lee el porcentaje de HP y SP desde la pantalla del juego.

    Devuelve (hp, sp) como enteros 0-100.
    Si el OCR falla o el valor está fuera de rango, se devuelve 0.

    NO usa cv2.imshow — la depuración se hace vía logging + flag DEBUG_VISION.
    """
    hp_region, sp_region = extraer_region_hp_sp(frame)

    hp = ocr_porcentaje(hp_region)
    sp = ocr_porcentaje(sp_region)

    _log.debug(f"HP={hp}% | SP={sp}%")

    # ── Debug visual opcional ─────────────────────────────────────────────────
    if DEBUG_VISION:
        _mostrar_debug(hp_region, sp_region, hp, sp)

    return hp, sp


def _mostrar_debug(hp_region, sp_region, hp, sp):
    """
    Genera imágenes de debug guardadas en disco (no usa cv2.imshow).
    Útil para verificar la calidad del OCR sin entorno gráfico.
    """
    debug_dir = os.path.join(os.path.dirname(__file__), "..", "debug_vision")
    os.makedirs(debug_dir, exist_ok=True)

    timestamp = int(time.time() * 1000)
    processed_hp = _preprocess_region(hp_region)
    processed_sp = _preprocess_region(sp_region)

    cv2.imwrite(os.path.join(debug_dir, f"hp_raw_{timestamp}.png"), hp_region)
    cv2.imwrite(os.path.join(debug_dir, f"hp_proc_{timestamp}.png"), processed_hp)
    cv2.imwrite(os.path.join(debug_dir, f"sp_raw_{timestamp}.png"), sp_region)
    cv2.imwrite(os.path.join(debug_dir, f"sp_proc_{timestamp}.png"), processed_sp)

    # Anotar con el valor leído
    def _annotate(img, label, value):
        annotated = img.copy()
        cv2.putText(annotated, f"{label}:{value}%", (2, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        return annotated

    hp_ann = _annotate(hp_region, "HP", hp)
    sp_ann = _annotate(sp_region, "SP", sp)
    cv2.imwrite(os.path.join(debug_dir, f"hp_ann_{timestamp}.png"), hp_ann)
    cv2.imwrite(os.path.join(debug_dir, f"sp_ann_{timestamp}.png"), sp_ann)

    _log.debug(f"Debug frames guardados en {debug_dir}/ (timestamp={timestamp})")


# ─── Utilidades de calibración ─────────────────────────────────────────────────

def calibrar_region(frame: np.ndarray, nombre: str = "HP"):
    """
    Utilidad interactiva para calibrar las regiones del HUD.
    Muestra coords al pasar el mouse y permite ajustar las constantes
    HUD_HP_REGION / HUD_SP_REGION.

    Útil durante setup; no debe llamarse en producción.
    """
    _log.warning("Calibración: mueve el mouse sobre la imagen. Presiona ESC para salir.")
    WIN_NAME = f"Calibración {nombre} — ESC sale"

    clone = frame.copy()
    h, w = clone.shape[:2]
    info = {"coords": None}

    def _mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            info["coords"] = (x, y)
            display = clone.copy()
            # Fondo oscuro para el texto
            cv2.rectangle(display, (0, 0), (w - 1, 50), (0, 0, 0), -1)
            cv2.putText(display, f"x={x}, y={y}  |  Ajusta HUD_*_REGION en hud_reader.py",
                        (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            cv2.imshow(WIN_NAME, display)

    cv2.namedWindow(WIN_NAME)
    cv2.setMouseCallback(WIN_NAME, _mouse_callback)

    while True:
        key = cv2.waitKey(50) & 0xFF
        if key == 27:  # ESC
            break
        if info["coords"]:
            x, y = info["coords"]
            # Muestra línea vertical y horizontal en la posición del mouse
            cross = clone.copy()
            cv2.line(cross, (x, 0), (x, h), (0, 255, 0), 1)
            cv2.line(cross, (0, y), (w, y), (0, 255, 0), 1)
            cv2.imshow(WIN_NAME, cross)

    cv2.destroyWindow(WIN_NAME)
    _log.info("Calibración finalizada.")


# ─── Test directo ───────────────────────────────────────────────────────────────
import time

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    from core import capture

    ventana = capture.encontrar_ventana()
    if not ventana:
        print("No se encontró la ventana del juego.")
        exit()

    # Captura 3 frames para validar estabilidad
    hp_validos, sp_validos = [], []
    for i in range(3):
        frame = capture.capturar_client_area(ventana)
        hp, sp = leer_hp_sp(frame)
        hp_validos.append(hp)
        sp_validos.append(sp)
        print(f"  Frame {i+1}: HP={hp}% | SP={sp}%")
        time.sleep(0.3)

    hp_final = int(round(sum(hp_validos) / len(hp_validos)))
    sp_final = int(round(sum(sp_validos) / len(sp_validos)))
    print(f"\nLectura estabilizada: HP={hp_final}% | SP={sp_final}%")

    # Calibración opcional (descomentar para ajustar regiones)
    # frame = capture.capturar_client_area(ventana)
    # calibrar_region(frame, "HP")
