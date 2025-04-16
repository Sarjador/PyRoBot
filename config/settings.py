import json
import os

class Config:
    def __init__(self):
        # Rendimiento
        self.USE_CUDA = True
        self.TORCH_PRECISION = 'mixed'  # 'float32' or 'mixed'
        self.INFERENCE_BATCH_SIZE = 8
        
        # Control
        self.ACTION_DELAY = (0.1, 0.3)  # Random delay entre acciones
        self.HUMANIZE_MOVEMENT = True
        self.MAX_ACTION_PER_SECOND = 5
        
        # Rutas
        self.MODEL_DIR = 'data/models/'
        self.TEMPLATE_DIR = 'data/templates/'
        
        self._load_keybindings()
    
    def _load_keybindings(self):
        with open('config/hotkeys.json') as f:
            self.keybindings = json.load(f)
    
    def get_delay(self):
        if self.HUMANIZE_MOVEMENT:
            return random.uniform(*self.ACTION_DELAY)
        return 0.1

config = Config()