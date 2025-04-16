import cv2
import torch
import numpy as np
from core.vision.nn_models import RONavigationNet
from core.learning.dqn import DQNAgent


class MapNavigator:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.navigation_net = RONavigationNet().to(self.device)
        self.navigation_net.load_state_dict(torch.load('data/models/navigation_net.pth'))
        self.navigation_net.eval()

        self.rl_agent = DQNAgent(state_size=15, action_size=4)
        self.current_path = []
        self.minimap_template = cv2.imread('data/templates/minimap.png', 0)

    def find_path(self, current_frame, target_position):
        """Encuentra ruta al objetivo usando minimapa"""
        # Procesar minimapa
        minimap = self._extract_minimap(current_frame)

        # Obtener posición actual
        res = cv2.matchTemplate(minimap, self.minimap_template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        current_pos = np.array(max_loc)

        # Predecir mejor ruta con RL
        state = self._create_navigation_state(current_pos, target_position, minimap)
        action = self.rl_agent.act(state)

        # Convertir acción a movimiento
        movements = {
            0: 'move_up',
            1: 'move_right',
            2: 'move_down',
            3: 'move_left'
        }

        return movements[action]

    def _extract_minimap(self, frame):
        """Extrae la región del minimapa"""
        return frame[10:110, -120:-10]  # Ajustar según resolución

    def _create_navigation_state(self, current_pos, target_pos, minimap):
        """Crea vector de estado para navegación"""
        # Implementar lógica para crear estado
        return np.zeros(15)  # placeholder