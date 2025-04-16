import cv2
import numpy as np
import pytesseract
from core.vision.ocr import preprocess_for_ocr


class ResourceManager:
    def __init__(self):
        self.inventory_positions = {
            'potions': [(x, y) for x in range(100, 300, 40) for y in range(200, 400, 40)],
            'equipment': [(x, y) for x in range(400, 600, 40) for y in range(200, 400, 40)]
        }

    def check_inventory(self, frame):
        """Analiza el inventario del personaje"""
        # Extraer región del inventario
        inventory_region = frame[200:600, 100:800]

        # Preprocesar para OCR
        processed = preprocess_for_ocr(inventory_region)

        # Detectar items
        items = {}
        for item_type, positions in self.inventory_positions.items():
            items[item_type] = []
            for x, y in positions:
                item_region = processed[y - 15:y + 15, x - 15:x + 15]
                text = pytesseract.image_to_string(item_region, config='--psm 8')
                if text.strip():
                    items[item_type].append({
                        'position': (x, y),
                        'name': text.strip()
                    })

        return items

    def auto_potion(self, frame, hp_threshold=30, sp_threshold=20):
        """Usa pociones automáticamente"""
        status = self.get_player_status(frame)

        if status['hp_percent'] < hp_threshold:
            self.use_item('hp_potion')
        if status['sp_percent'] < sp_threshold:
            self.use_item('sp_potion')

    def get_player_status(self, frame):
        """Lee las barras de HP/SP"""
        # Implementar lógica para leer barras
        return {
            'hp_percent': 100,
            'sp_percent': 100
        }

    def use_item(self, item_name):
        """Usa un item del inventario"""
        # Implementar lógica para usar items
        pass