import random
import pickle
import os

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.1, model_path="q_table.pkl"):
        self.q_table = {}  # estado -> {accion: valor}
        self.alpha = alpha  # tasa de aprendizaje
        self.gamma = gamma  # descuento de futuro
        self.epsilon = epsilon  # exploración
        self.actions = actions
        self.model_path = model_path

        if os.path.exists(self.model_path):
            self.load()

    def get_state_key(self, state):
        """Convierte un estado complejo en una clave hashable"""
        return tuple(state)

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
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self):
        with open(self.model_path, 'rb') as f:
            self.q_table = pickle.load(f)

# Ejemplo de uso manual
if __name__ == "__main__":
    agent = QLearningAgent(actions=["atacar", "usar_pocion", "huir", "esperar"])
    estado = (100, 100, "coco")
    accion = agent.choose_action(estado)
    print("Acción elegida:", accion)
    agent.learn(estado, accion, reward=1, next_state=(90, 100, "coco"))
    agent.save()
