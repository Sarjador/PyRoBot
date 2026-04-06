"""tests/test_agent_rl.py — Tests para el agente Q-Learning.
FASE 4: Verifica persistencia, decay, y lógica de decisión.
"""
import pytest
import os, tempfile, json
from core.agent_rl import QLearningAgent


class TestQLearningAgent:
    """Suite de tests para QLearningAgent."""

    def test_agent_initialization(self):
        """El agente se inicializa con epsilon > 0."""
        agent = QLearningAgent(actions=["atacar", "esperar"])
        assert agent.epsilon > 0
        assert agent.epsilon <= 1.0
        assert "atacar" in agent.actions
        assert "esperar" in agent.actions

    def test_initial_q_table_empty(self, tmp_path):
        """Q-table vacía al inicio si no hay archivo."""
        model_path = tmp_path / "new_q.json"
        agent = QLearningAgent(
            actions=["atacar"],
            model_path=str(model_path)
        )
        assert len(agent.q_table) == 0

    def test_choose_action_exploration(self):
        """Con epsilon=1.0, siempre explora (elige de las acciones disponibles)."""
        agent = QLearningAgent(actions=["a", "b", "c"], epsilon=1.0)
        acciones = {agent.choose_action("test") for _ in range(30)}
        assert len(acciones) > 1  # Debe variar

    def test_choose_action_exploitation(self):
        """Con epsilon=0.0, siempre elige la mejor acción conocida."""
        agent = QLearningAgent(actions=["a", "b"], epsilon=0.0)
        agent.q_table["test"] = {"a": 1.0, "b": 5.0}
        assert agent.choose_action("test") == "b"

    def test_epsilon_decay(self):
        """Epsilon decrementa tras cada elección de acción."""
        agent = QLearningAgent(actions=["a"], epsilon=1.0, epsilon_decay=0.5)
        initial = agent.epsilon
        for _ in range(5):
            agent.choose_action("s")
        assert agent.epsilon < initial
        assert agent.epsilon >= 0

    def test_learn_updates_q_table(self):
        """learn() actualiza los Q-values correctamente."""
        agent = QLearningAgent(actions=["a", "b"], alpha=0.1, gamma=0.9)
        state = "s1"
        agent.learn(state, "a", reward=1.0, next_state="s2")
        assert "s1" in agent.q_table
        assert "a" in agent.q_table["s1"]

    def test_save_and_load(self, tmp_path):
        """save() y load() preservan la Q-table."""
        model_path = tmp_path / "q_test.json"
        agent = QLearningAgent(actions=["x"], model_path=str(model_path))
        agent.q_table["estado1"] = {"x": 99.0}
        agent.save()

        agent2 = QLearningAgent(actions=["x"], model_path=str(model_path))
        assert "estado1" in agent2.q_table
        assert agent2.q_table["estado1"]["x"] == 99.0

    def test_backup_creates_bak_file(self, tmp_path):
        """save() crea un backup antes de sobrescribir."""
        model_path = tmp_path / "q_bak.json"
        agent = QLearningAgent(actions=["a"], model_path=str(model_path))
        agent.q_table["s"] = {"a": 1.0}
        agent.save()
        agent.q_table["s"] = {"a": 2.0}
        agent.save()

        backup_files = list(tmp_path.glob("q_bak.json.bak*"))
        assert len(backup_files) >= 1

    def test_stats_returns_dict(self):
        """stats() devuelve un dict con métricas."""
        agent = QLearningAgent(actions=["a"])
        stats = agent.stats()
        assert isinstance(stats, dict)
        assert "estados" in stats
        assert "epsilon" in stats
