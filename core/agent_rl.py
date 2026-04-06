import random
import json
import os

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.1, model_path=None):
        self.q_table = {}  # estado -> {accion: valor}
        self.alpha = alpha  # tasa de aprendizaje
        self.gamma = gamma  # descuento de futuro
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay if 'epsilon_decay' in dir() else 0.995  # exploración
        self.actions = actions

        # Model path: configurable via parameter or environment variable
        if model_path is None:
            default_path = os.path.join(os.path.dirname(__file__), "..", "q_table.json")
            model_path = os.environ.get("PYROBOT_QTABLE_PATH", os.path.abspath(default_path))
        self.model_path = model_path
        # Ensure directory exists for model_path to prevent write errors
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        except Exception:
            pass

    def get_state_key(self, state):
        """Convierte un estado complejo en una clave hashable"""
        return str(tuple(state))

    def choose_action(self, state):
        key = self.get_state_key(state)
        self.q_table.setdefault(key, {a: 0.0 for a in self.actions})

        if random.random() < self.epsilon:
            return random.choice(self.actions)  # exploración
        else:
            return max(self.q_table[key], key=self.q_table[key].get)  # explotación

    def learn(self, state, action, reward, next_state):
        key = self.get_state_key(state)
        next_key = self.get_state_key(next_state)

        self.q_table.setdefault(key, {a: 0.0 for a in self.actions})
        self.q_table.setdefault(next_key, {a: 0.0 for a in self.actions})

        q_predict = self.q_table[key][action]
        q_target = reward + self.gamma * max(self.q_table[next_key].values())
        self.q_table[key][action] += self.alpha * (q_target - q_predict)

    def save(self):
        with open(self.model_path, 'w', encoding='utf-8') as f:
            json.dump(self.q_table, f, indent=2)

    def load(self):
        with open(self.model_path, 'r', encoding='utf-8') as f:
            self.q_table = json.load(f)

# Ejemplo de uso manual
if __name__ == "__main__":
    agent = QLearningAgent(actions=["atacar", "usar_pocion", "huir", "esperar"])
    estado = (100, 100, 1)
    accion = agent.choose_action(estado)
    print("Acción elegida:", accion)
    agent.learn(estado, accion, reward=1, next_state=(90, 100, 1))
    agent.save()
