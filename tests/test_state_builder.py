"""tests/test_state_builder.py — Tests para StateBuilder.
FASE 4: Verifica la cuantización de estados.
"""
import pytest
from core.state_builder import StateBuilder


class TestStateBuilder:
    """Suite de tests para StateBuilder."""

    @pytest.fixture
    def sb(self):
        return StateBuilder()

    def test_build_empty_detections(self, sb):
        """Sin mobs → estado包含 'none'."""
        estado = sb.build([], {"hp": 100, "sp": 100})
        assert "none" in estado
        assert "hp_high" in estado
        assert "sp_high" in estado

    def test_build_with_mobs_close(self, sb):
        """Mob muy cerca → estado包含 'close'."""
        detections = [{"distance_to_center": 80, "confidence": 0.9}]
        estado = sb.build(detections, {"hp": 50, "sp": 50})
        assert "close" in estado

    def test_build_hp_bins(self, sb):
        """HP se cuantiza correctamente."""
        assert "hp_critical" in sb.build([], {"hp": 10, "sp": 50})
        assert "hp_low" in sb.build([], {"hp": 25, "sp": 50})
        assert "hp_mid" in sb.build([], {"hp": 50, "sp": 50})
        assert "hp_high" in sb.build([], {"hp": 90, "sp": 50})

    def test_build_sp_bins(self, sb):
        """SP se cuantiza correctamente."""
        assert "sp_empty" in sb.build([], {"hp": 50, "sp": 5})
        assert "sp_low" in sb.build([], {"hp": 50, "sp": 20})
        assert "sp_mid" in sb.build([], {"hp": 50, "sp": 50})
        assert "sp_high" in sb.build([], {"hp": 50, "sp": 80})

    def test_build_mob_count(self, sb):
        """Mob count se cuantiza correctamente."""
        assert "0" in sb.build([], {"hp": 50, "sp": 50})
        assert "1" in sb.build([{"d": 100}], {"hp": 50, "sp": 50})

    def test_hp_clamped_to_100(self, sb):
        """HP > 100 se clamp a 100."""
        estado = sb.build([], {"hp": 150, "sp": 50})
        assert "hp_high" in estado

    def test_state_space_size(self, sb):
        """state_space_size devuelve un entero positivo."""
        size = sb.state_space_size()
        assert isinstance(size, int)
        assert size > 0
        # 4 dist × 4 hp × 4 sp × 4 mob = 256 estados
        assert size == 256
