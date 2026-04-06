"""core/state_builder.py — Construye estado discretizado para la Q-table.
FASE 1: Convierte detections + HUD en string de estado cuantizado.
"""
import logging

_log = logging.getLogger("state_builder")

# ─── Distancias en píxeles desde el centro de la pantalla ──────────────────
DIST_BINS   = ["far", "medium", "close", "none"]
HP_BINS     = ["hp_critical", "hp_low", "hp_mid", "hp_high"]
SP_BINS     = ["sp_empty", "sp_low", "sp_mid", "sp_high"]
MOB_BINS    = ["0", "1", "2_3", "4plus"]


class StateBuilder:
    """
    Convierte raw detections + HUD data en un string de estado
    que sirve como clave para la Q-table.

    Uso:
        builder = StateBuilder()
        estado = builder.build(detections, hud_data)
        accion = agente.choose_action(estado)
    """

    def build(self, detections: list, hud: dict) -> str:
        """
        Args:
            detections: lista de dicts con al menos 'x_center', 'y_center'
                       y opcionalmente 'distance_to_center'
            hud: dict con 'hp' (0-100) y 'sp' (0-100)

        Returns:
            String de estado: "{dist}_{hp_bin}_{sp_bin}_{mob_count}"
            Ejemplo: "close_hp_mid_sp_high_2_3"
        """
        # ── Distancia al mob más cercano ──────────────────────────────────────
        if detections:
            try:
                dist = min(d.get("distance_to_center", float("inf")) for d in detections)
                dist_bin = self._bin_distance(dist)
                mob_count = len([d for d in detections if d.get("confidence", 1) > 0.6])
                mob_bin = self._bin_mobs(mob_count)
            except Exception:
                dist_bin = "none"
                mob_bin = "0"
        else:
            dist_bin = "none"
            mob_bin = "0"

        hp_bin = self._bin_hp(hud.get("hp", 100))
        sp_bin = self._bin_sp(hud.get("sp", 100))

        estado = f"{dist_bin}_{hp_bin}_{sp_bin}_{mob_bin}"
        _log.debug(f"Estado construido: {estado}")
        return estado

    # ── Bins ────────────────────────────────────────────────────────────────

    def _bin_distance(self, dist: float) -> str:
        """Cuantiza distancia al mob más cercano."""
        if dist < 120:
            return "close"
        if dist < 300:
            return "medium"
        if dist < 600:
            return "far"
        return "none"

    def _bin_hp(self, hp: int) -> str:
        """Cuantiza HP del personaje."""
        hp = max(0, min(100, hp))
        if hp <= 15:
            return "hp_critical"
        if hp <= 35:
            return "hp_low"
        if hp <= 70:
            return "hp_mid"
        return "hp_high"

    def _bin_sp(self, sp: int) -> str:
        """Cuantiza SP del personaje."""
        sp = max(0, min(100, sp))
        if sp <= 10:
            return "sp_empty"
        if sp <= 30:
            return "sp_low"
        if sp <= 65:
            return "sp_mid"
        return "sp_high"

    def _bin_mobs(self, count: int) -> str:
        """Cuantiza número de mobs visibles."""
        if count == 0:
            return "0"
        if count == 1:
            return "1"
        if count <= 3:
            return "2_3"
        return "4plus"

    # ── Stats ──────────────────────────────────────────────────────────────

    def state_space_size(self) -> int:
        """Tamaño teórico del espacio de estados."""
        return len(DIST_BINS) * len(HP_BINS) * len(SP_BINS) * len(MOB_BINS)
