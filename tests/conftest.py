# tests/conftest.py — Fixtures compartidas para pytest
import pytest
import sys, os

# Añadir la raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def mock_frame():
    """Frame sintético de 800x600 para tests de OCR."""
    import numpy as np
    import cv2
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    cv2.putText(frame, "HP: 75%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return frame


@pytest.fixture
def mock_detections():
    """Detections sintéticas para tests del agente."""
    return [
        {"x_center": 400, "y_center": 300, "distance_to_center": 150, "confidence": 0.9},
        {"x_center": 450, "y_center": 320, "distance_to_center": 200, "confidence": 0.8},
    ]


@pytest.fixture
def agent():
    """QLearningAgent limpio para cada test."""
    from core.agent_rl import QLearningAgent
    return QLearningAgent(actions=["atacar", "usar_pocion", "huir", "esperar"])
