import torch
import numpy as np
from collections import deque
from core.vision.object_detection import ObjectDetector
from core.learning.dqn import DQNAgent
from utils.visual_debugger import VisualDebugger


class CombatSystem:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.object_detector = ObjectDetector()
        self.visual_debug = VisualDebugger()
        self.combat_agent = DQNAgent(state_size=20, action_size=8)  # 8 habilidades
        self.last_states = deque(maxlen=5)
        self.combo_memory = deque(maxlen=3)

        # Cargar modelo de predicción de movimientos enemigos
        self.enemy_movement_predictor = torch.jit.load('data/models/enemy_movement.pt').to(self.device)

    def evaluate_combat_situation(self, frame):
        """Analiza la situación de combate actual"""
        # Detección de objetos con CUDA
        detections = self.object_detector.detect(frame)

        # Procesar información relevante
        monsters = [d for d in detections if d['class'] == 'monster' and d['confidence'] > 0.7]
        players = [d for d in detections if d['class'] == 'player']

        # Predecir movimientos enemigos
        monster_positions = np.array([m['bbox'][:2] for m in monsters])
        if len(monster_positions) > 0:
            with torch.no_grad():
                inputs = torch.FloatTensor(monster_positions).to(self.device)
                predicted_movements = self.enemy_movement_predictor(inputs).cpu().numpy()

        # Crear estado para el agente
        state = self._create_state_vector(detections, predicted_movements)
        self.last_states.append(state)

        # Visualización (debug)
        self.visual_debug.draw_detections(frame, detections)

        return state

    def _create_state_vector(self, detections, predicted_movements):
        """Crea un vector de estado para el agente de RL"""
        # Implementar lógica para crear vector de estado
        return np.zeros(20)  # placeholder

    def execute_combat_action(self, action_id, target=None):
        """Ejecuta una acción de combate"""
        action_map = {
            0: 'attack_primary',
            1: 'cast_skill1',
            2: 'cast_skill2',
            # ... otras acciones
        }

        action = action_map.get(action_id, 'attack_primary')

        if target:
            self._move_to_target(target)

        if action.startswith('cast'):
            self._cast_skill(action.split('_')[1])
        else:
            pyautogui.press(config.keybindings.ATTACK_PRIMARY)

        self.combo_memory.append(action_id)
        self._check_combo()

    def _check_combo(self):
        """Verifica si los últimos movimientos forman un combo"""
        # Implementar lógica de combos
        pass