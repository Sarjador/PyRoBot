import cv2
import numpy as np
import torch
from .nn_models import ROObjectDetector


class ObjectDetector:
    def __init__(self):
        self.model = ROObjectDetector()
        self.model.load_state_dict(torch.load('data/models/object_detector.pth'))
        self.model.eval()
        self.classes = ['monster', 'npc', 'item', 'player', 'portal', 'skill', 'buff', 'debuff', 'hp_bar', 'sp_bar']

    def detect(self, frame):
        # Preprocesamiento para la red neuronal
        input_tensor = self._preprocess(frame)

        with torch.no_grad():
            outputs = self.model(input_tensor)

        return self._postprocess(outputs, frame.shape)

    def _preprocess(self, frame):
        # Convertir a tensor y normalizar
        frame = cv2.resize(frame, (224, 224))
        frame = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
        frame = frame.unsqueeze(0).to(self.model.device)
        return frame

    def _postprocess(self, outputs, frame_shape):
        # Procesar salidas de la red
        probs = torch.softmax(outputs, dim=1)
        conf, class_id = torch.max(probs, 1)

        # Escalar coordenadas al tamaño original
        # (Implementar lógica específica según tu modelo)
        return {
            'class': self.classes[class_id.item()],
            'confidence': conf.item(),
            'bbox': self._scale_bbox(...)  # Implementar según necesidad
        }