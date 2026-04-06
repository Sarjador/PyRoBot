"""
agent_rl.py — Agente Q-Learning con persistencia y logging.
FASE 0: Auto-load en __init__, save() con backup, last_action tracking.
"""
import os
import random
import json
import logging
import shutil
from datetime import datetime

# ─── Logging ───────────────────────────────────────────────────────────────────
_log = logging.getLogger("agent_rl")

# ─── Paths ─────────────────────────────────────────────────────────────────────
_QTABLE_DIR = os.path.join(os.path.dirname(__file__), "..")
_QTABLE_PATH = os.environ.get("PYROBOT_QTABLE_PATH",
                              os.path.join(_QTABLE_DIR, "q_table.json"))


class QLearningAgent:
    """
    Agente Q-Learning con:
    - Persistencia automática (load en __init__, save en __init__ y periÃ³dico)
    - Backup de q_table.json antes de sobrescribir
    - Tracking de last_action para logging
    - Logging estructurado
    """

    def __init__(
        self,
        actions,
        alpha: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 0.1,
        model_path: str = None,
        save_interval: int = 50,   # Guardar cada N llamadas a learn()
    ):
        self.q_table: dict = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.actions = actions
        self.model_path = model_path or _QTABLE_PATH
        self.save_interval = save_interval
        self._learn_calls = 0
        self.last_action: str = "esperar"  # Tracking para logging

        # Crear directorio del modelo si no existe
        try:
            os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        except Exception as e:
            _log.warning(f"No se pudo crear dir para q_table: {e}")

        # ── Auto-load: cargar Q-table existente si hay disco ────────────────
        if os.path.exists(self.model_path):
            try:
                self.load()
                _log.info(f"Q-table cargada desde {self.model_path}")
                _log.info(f"  Estados conocidos: {len(self.q_table)}")
            except Exception as e:
                _log.warning(f"No se pudo cargar Q-table existente: {e}")
                _log.info("Iniciando con Q-table vacía (aprendizaje desde cero).")
        else:
            _log.info(f"Q-table no encontrada ({self.model_path}) — nueva sesión.")

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _backup(self):
        """Crea un backup numerado de q_table.json antes de sobrescribir."""
        if not os.path.exists(self.model_path):
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.model_path + f".bak{ts}"
        try:
            shutil.copy2(self.model_path, backup_path)
            _log.debug(f"Backup creado: {os.path.basename(backup_path)}")

            # Mantener solo los 3 backups más recientes
            backups = sorted([
                f for f in os.listdir(os.path.dirname(self.model_path) or ".")
                if f.startswith(os.path.basename(self.model_path)) and f.endswith(".bak")
            ])
            while len(backups) > 3:
                oldest = backups.pop(0)
                os.remove(os.path.join(os.path.dirname(self.model_path) or ".", oldest))
                _log.debug(f"Backup antiguo eliminado: {oldest}")
        except Exception as e:
            _log.warning(f"Backup falló: {e}")

    def save(self):
        """Guarda q_table.json con backup automático."""
        self._backup()
        try:
            with open(self.model_path, "w", encoding="utf-8") as f:
                json.dump(self.q_table, f, indent=2, ensure_ascii=False)
            _log.debug(f"Q-table guardada ({len(self.q_table)} estados)")
        except Exception as e:
            _log.error(f"Error guardando Q-table: {e}")

    def load(self):
        """Carga q_table.json."""
        with open(self.model_path, "r", encoding="utf-8") as f:
            self.q_table = json.load(f)

    # ── Estado ────────────────────────────────────────────────────────────────

    def get_state_key(self, state):
        """Convierte cualquier estado iterable en clave hashable."""
        try:
            return str(tuple(float(v) for v in state))
        except (TypeError, ValueError):
            return str(state)

    # ── Decisión ─────────────────────────────────────────────────────────────

    def choose_action(self, state):
        """
        Elige una acción por epsilon-greedy.
        Guarda last_action para logging.
        """
        key = self.get_state_key(state)
        self.q_table.setdefault(key, {a: 0.0 for a in self.actions})

        if random.random() < self.epsilon:
            accion = random.choice(self.actions)
            _log.debug(f"[EPS] Explorando: {accion} (ε={self.epsilon:.3f})")
        else:
            q_vals = self.q_table[key]
            accion = max(q_vals, key=q_vals.__getitem__)
            _log.debug(f"[GRL] Explotando: {accion} (ε={self.epsilon:.3f})")

        self.last_action = accion
        return accion

    # ── Aprendizaje ──────────────────────────────────────────────────────────

    def learn(self, state, action, reward, next_state):
        """
        Actualiza Q-table con TD-learning.
        Auto-save cada save_interval llamadas.
        """
        key      = self.get_state_key(state)
        next_key = self.get_state_key(next_state)

        self.q_table.setdefault(key,      {a: 0.0 for a in self.actions})
        self.q_table.setdefault(next_key, {a: 0.0 for a in self.actions})

        q_predict = self.q_table[key][action]
        q_target  = reward + self.gamma * max(self.q_table[next_key].values())
        self.q_table[key][action] += self.alpha * (q_target - q_predict)

        self._learn_calls += 1
        if self._learn_calls % self.save_interval == 0:
            _log.info(f"Auto-save: {self._learn_calls} learns completados, guardando...")
            self.save()

    # ─── Stats para dashboard ─────────────────────────────────────────────────
    def stats(self) -> dict:
        """Resumen de estadísticas del agente."""
        if not self.q_table:
            return {"estados": 0, "acciones_conocidas": 0}

        total_q = sum(max(v.values()) for v in self.q_table.values())
        return {
            "estados": len(self.q_table),
            "total_q": round(total_q, 3),
            "epsilon": self.epsilon,
            "learn_calls": self._learn_calls,
        }


# ─── Test directo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")

    agent = QLearningAgent(actions=["atacar", "usar_pocion", "huir", "esperar"])
    print("Stats iniciales:", agent.stats())

    estado = (100, 100, 1)
    accion = agent.choose_action(estado)
    print(f"Acción elegida: {accion}")

    agent.learn(estado, accion, reward=1, next_state=(90, 100, 1))
    print("Stats tras learn:", agent.stats())
    agent.save()
    print(f"Q-table guardada en {agent.model_path}")
