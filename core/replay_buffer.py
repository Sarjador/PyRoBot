"""core/replay_buffer.py — Experience Replay para Q-Learning.
FASE 3: Buffer circular de transiciones para batch learning estable.

Paper original: "Playing Atari with Deep Reinforcement Learning" (Mnih et al., 2013)
"""
import random
import logging
from collections import deque
from typing import Tuple, Any, List

_log = logging.getLogger("replay_buffer")


class ReplayBuffer:
    """
    Buffer circular de experiencias con muestreo aleatorio.

    Uso:
        buffer = ReplayBuffer(capacity=10000, batch_size=32)

        # Almacenar experiencia
        buffer.push(state, action, reward, next_state, done)

        # Muestrear minibatch para aprender
        if len(buffer) >= batch_size:
            batch = buffer.sample()
            for s, a, r, ns, d in batch:
                agent.learn(s, a, r, ns)
    """

    def __init__(self, capacity: int = 10000, batch_size: int = 32):
        self.capacity = capacity
        self.batch_size = batch_size
        self.buffer = deque(maxlen=capacity)
        self.total_pushes = 0

    def push(
        self,
        state: Any,
        action: Any,
        reward: float,
        next_state: Any,
        done: bool = False,
    ):
        """
        Almacena una transición en el buffer.
        Si el buffer está lleno, descarta la experiencia más antigua.
        """
        self.buffer.append((state, action, reward, next_state, done))
        self.total_pushes += 1

        if self.total_pushes % 1000 == 0:
            _log.debug(f"Buffer: {len(self)}/{self.capacity} ({self.total_pushes} pushes)")

    def sample(self, batch_size: int = None) -> List[Tuple]:
        """
        Devuelve un minibatch muestreado aleatoriamente.
        Si hay menos experiencias que batch_size, devuelve todas las disponibles.
        """
        size = batch_size or self.batch_size
        size = min(size, len(self.buffer))
        return random.sample(self.buffer, size)

    def __len__(self) -> int:
        return len(self.buffer)

    def is_ready(self, batch_size: int = None) -> bool:
        """True si hay suficientes experiencias para un batch."""
        return len(self.buffer) >= (batch_size or self.batch_size)

    def clear(self):
        """Vacía el buffer."""
        self.buffer.clear()
        _log.info("Replay buffer limpiado")

    def stats(self) -> dict:
        return {
            "size": len(self.buffer),
            "capacity": self.capacity,
            "utilization_pct": round(len(self.buffer) / self.capacity * 100, 1),
            "total_pushes": self.total_pushes,
        }
