"""core/rewards.py — Función de recompensa avanzada para el agente RL.
FASE 1: Recompensas diferenciadas, tracking de eventos, múltiples fuentes.
"""
import time
import logging

_log = logging.getLogger("rewards")


class RewardCalculator:
    """
    Calcula recompensas diferenciadas para Q-Learning.

    Diseño de recompensas:
    - Recompensas POSITIVAS por outcomes buenos (matar mob, heal inteligente)
    - Penalizaciones FUERTES por HP crítico (urgencia)
    - Penalizaciones LIGERAS por inacción prolongada (evita stuck)
    - Sesgo hacia mob Killing para que el agente aprenda a farmear
    """

    def __init__(self):
        # Tracking de estado entre frames
        self._last_hp = 100
        self._last_sp = 100
        self._mob_kills = 0
        self._last_action_time = time.time()
        self._episode_start = time.time()

        # Configuración de umbrales
        self.HP_CRITICAL   = 20
        self.HP_LOW        = 40
        self.SP_EMPTY      = 15
        self.IDLE_PENALTY  = -3.0      # por cada 20s sin kills
        self.IDLE_THRESHOLD = 20.0     # segundos

        # Pesos de recompensa
        self.W_DAMAGE      = -0.6      # por punto de HP perdido
        self.W_KILL        = +10.0     # por mob matado
        self.W_POTION_SMART= +5.0      # poción cuando HP < 40
        self.W_POTION_WASTE = -3.0     # poción con HP > 70
        self.W_ATTACK      = +1.0      # atacar con mobs presentes
        self.W_ATTACK_WASTE= -2.0      # atacar sin mobs
        self.W_FLEE_SMART  = +5.0      # huir con HP crítico
        self.W_FLEE_WASTE  = -1.0      # huir con HP alto
        self.W_WAIT_MOBS   = -4.0      # esperar con mobs visibles
        self.W_SURVIVE     = +0.1      # frame sobrevivido sin penalizaciones

    def calculate(
        self,
        hp: int,
        sp: int,
        mob_count: int,
        action: str,
        hp_anterior: int = None
    ) -> float:
        """
        Calcula la recompensa para un frame.

        Args:
            hp: HP actual del personaje (0-100)
            sp: SP actual del personaje (0-100)
            mob_count: número de mobs detectados en este frame
            action: acción elegida por el agente
            hp_anterior: HP en el frame anterior (para calcular daño recibido)

        Returns:
            float: recompensa (puede ser negativa)
        """
        reward = 0.0
        hp = max(0, min(100, hp))
        sp = max(0, min(100, sp))
        hp_prev = hp_anterior if hp_anterior is not None else self._last_hp

        idle_time = time.time() - self._last_action_time

        # ── 1. Daño recibido ────────────────────────────────────────────────
        dmg = hp_prev - hp
        if dmg > 0:
            reward += dmg * self.W_DAMAGE
            if hp <= self.HP_CRITICAL:
                reward -= 8.0  # Penalización extra por HP crítico
            _log.debug(f"Daño recibido: -{dmg} HP → reward={reward:.1f}")

        # ── 2. Acción: atacar ────────────────────────────────────────────────
        if action == "atacar":
            if mob_count > 0 and sp > self.SP_EMPTY:
                reward += self.W_ATTACK
            elif mob_count == 0:
                reward += self.W_ATTACK_WASTE  # Penalizar atacar al aire

        # ── 3. Acción: usar poción ─────────────────────────────────────────
        elif action == "usar_pocion":
            if hp < self.HP_LOW:
                reward += self.W_POTION_SMART
                _log.debug(f"Poción inteligente: HP={hp}%")
            elif hp > 70:
                reward += self.W_POTION_WASTE  # Penalizar desperdiciar poción

        # ── 4. Acción: huir ────────────────────────────────────────────────
        elif action == "huir":
            if hp <= self.HP_CRITICAL:
                reward += self.W_FLEE_SMART
                _log.debug(f"Huir con HP crítico: +{self.W_FLEE_SMART}")
            elif hp > 60:
                reward += self.W_FLEE_WASTE

        # ── 5. Acción: esperar ─────────────────────────────────────────────
        elif action == "esperar":
            if mob_count > 0:
                reward += self.W_WAIT_MOBS  # Penalizar inacción con mobs

        # ── 6. Idle penalty ────────────────────────────────────────────────
        if idle_time > self.IDLE_THRESHOLD:
            reward += self.IDLE_PENALTY
            _log.debug(f"Idle penalty: {self.IDLE_PENALTY} (idle={idle_time:.0f}s)")

        # ── 7. Reward por sobrevivir ────────────────────────────────────────
        if reward == 0.0:
            reward += self.W_SURVIVE  # Pequeño reward por frame sin problemas

        # ── Actualizar tracking ─────────────────────────────────────────────
        self._last_hp = hp
        self._last_sp = sp

        return round(reward, 2)

    # ── Eventos especiales ──────────────────────────────────────────────────

    def on_mob_killed(self) -> float:
        """Llamar cuando se detecta que un mob fue derrotado."""
        reward = self.W_KILL
        self._mob_kills += 1
        self._last_action_time = time.time()
        _log.debug(f"Mob matado #{self._mob_kills} → +{reward}")
        return reward

    def episode_stats(self) -> dict:
        """Estadísticas del episodio para logging."""
        elapsed = time.time() - self._episode_start
        kpm = (self._mob_kills / elapsed * 60) if elapsed > 0 else 0
        return {
            "kills":       self._mob_kills,
            "elapsed_sec": round(elapsed, 1),
            "kills_per_min": round(kpm, 2),
            "final_hp":    self._last_hp,
            "final_sp":    self._last_sp,
        }

    def reset(self):
        """Reinicia el tracking para un nuevo episodio."""
        self._last_hp = 100
        self._last_sp = 100
        self._mob_kills = 0
        self._last_action_time = time.time()
        self._episode_start = time.time()
