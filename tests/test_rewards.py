"""tests/test_rewards.py — Tests para RewardCalculator.
FASE 4: Verifica la lógica de recompensas.
"""
import pytest
from core.rewards import RewardCalculator


class TestRewardCalculator:
    """Suite de tests para RewardCalculator."""

    @pytest.fixture
    def rc(self):
        return RewardCalculator()

    def test_initial_state(self, rc):
        """Calculator inicializa con valores por defecto."""
        assert rc._last_hp == 100
        assert rc._last_sp == 100
        assert rc._mob_kills == 0

    def test_damage_negative_reward(self, rc):
        """Recibir daño devuelve recompensa negativa."""
        r = rc.calculate(hp=90, sp=100, mob_count=0, action="esperar", hp_anterior=100)
        assert r < 0

    def test_attack_with_mobs_positive(self, rc):
        """Atacar con mobs visibles devuelve recompensa positiva."""
        r = rc.calculate(hp=100, sp=50, mob_count=2, action="atacar", hp_anterior=100)
        assert r >= 0

    def test_attack_without_mobs_negative(self, rc):
        """Atacar sin mobs devuelve recompensa negativa."""
        r = rc.calculate(hp=100, sp=50, mob_count=0, action="atacar", hp_anterior=100)
        assert r < 0

    def test_potion_smart_reward(self, rc):
        """Usar poción con HP bajo es inteligente."""
        r = rc.calculate(hp=30, sp=100, mob_count=0, action="usar_pocion", hp_anterior=30)
        assert r > 0

    def test_potion_waste_negative(self, rc):
        """Usar poción con HP alto es desperdicio."""
        r = rc.calculate(hp=90, sp=100, mob_count=0, action="usar_pocion", hp_anterior=90)
        assert r < 0

    def test_flee_critical_hp(self, rc):
        """Huir con HP crítico devuelve recompensa positiva."""
        r = rc.calculate(hp=15, sp=100, mob_count=3, action="huir", hp_anterior=15)
        assert r > 0

    def test_flee_no_danger_negative(self, rc):
        """Huir con HP alto devuelve recompensa negativa."""
        r = rc.calculate(hp=90, sp=100, mob_count=0, action="huir", hp_anterior=90)
        assert r < 0

    def test_wait_with_mobs_negative(self, rc):
        """Esperar con mobs visibles devuelve recompensa negativa."""
        r = rc.calculate(hp=100, sp=100, mob_count=3, action="esperar", hp_anterior=100)
        assert r < 0

    def test_on_mob_killed(self, rc):
        """on_mob_killed devuelve reward positivo y actualiza contador."""
        r = rc.on_mob_killed()
        assert r > 0
        assert rc._mob_kills == 1
        r2 = rc.on_mob_killed()
        assert rc._mob_kills == 2

    def test_episode_stats(self, rc):
        """episode_stats devuelve un dict con métricas."""
        rc._mob_kills = 5
        stats = rc.episode_stats()
        assert isinstance(stats, dict)
        assert stats["kills"] == 5
        assert "elapsed_sec" in stats
        assert "kills_per_min" in stats

    def test_reset(self, rc):
        """reset() reinicia el estado."""
        rc._mob_kills = 10
        rc._last_hp = 50
        rc.reset()
        assert rc._mob_kills == 0
        assert rc._last_hp == 100
