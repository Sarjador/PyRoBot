import cv2
import pytesseract
import torch
import numpy as np


class EnhancedOCREngine:
    def __init__(self):
        self.text_detector = TextDetector().to(torch.device('cuda'))
        self.text_recognizer = TextRecognizer().to(torch.device('cuda'))
        self.font_db = self._load_font_database()

    def process_frame(self, frame):
        """Pipeline completo de OCR para interfaces de juego"""
        # Detección de áreas de texto
        text_boxes = self.detect_text_regions(frame)

        # Procesamiento paralelo usando CUDA
        results = {}
        with torch.cuda.stream(torch.cuda.Stream()):
            for box in text_boxes:
                x, y, w, h = box
                text_roi = frame[y:y + h, x:x + w]

                # Preprocesamiento
                processed = self._preprocess_text(text_roi)

                # Reconocimiento
                text = self.recognize_text(processed)

                # Postprocesamiento
                clean_text = self._postprocess_text(text)
                results[(x, y)] = clean_text

        return results

    def detect_text_regions(self, frame):
        """Detección de áreas con texto usando CNN"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tensor = torch.from_numpy(gray).float().to('cuda') / 255.0
        tensor = tensor.unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            heatmap = self.text_detector(tensor)

        return self._extract_text_boxes(heatmap.squeeze().cpu().numpy())

    def recognize_text(self, text_roi):
        """Reconocimiento de texto usando modelo CRNN"""
        tensor = self._preprocess_for_recognition(text_roi)

        with torch.no_grad():
            output = self.text_recognizer(tensor)

        return self._decode_output(output)

    def _preprocess_text(self, img):
        """Mejora de contraste y limpieza para OCR"""
        # Implementar técnicas como:
        # - Ajuste de gamma
        # - CLAHE
        # - Binarización adaptativa
        # - Corrección de perspectiva
        return img