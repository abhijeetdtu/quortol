"""Tests for RecencyBiasWeight model — linear decay formula, edge cases."""

import sys
from pathlib import Path

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from models.recency_bias import RecencyBiasWeight


class TestRecencyBiasWeight:
    """Tests for RecencyBiasWeight model."""

    def test_calculate_weights_default(self):
        """Test weight calculation with default decay_slope=0.5."""
        weights = RecencyBiasWeight.calculate_weights(decay_slope=0.5)
        
        assert isinstance(weights, dict)
        assert len(weights) > 0
        
        # Weights should decrease with age (older seasons have lower weights)
        seasons = sorted(weights.keys())
        for i in range(len(seasons) - 1):
            assert weights[seasons[i]] <= weights[seasons[i + 1]]

    def test_calculate_weights_zero_decay(self):
        """Test that decay_slope=0 gives equal weights."""
        weights = RecencyBiasWeight.calculate_weights(decay_slope=0.0)
        
        # All weights should be 1.0 (no decay)
        for weight in weights.values():
            assert abs(weight - 1.0) < 0.01

    def test_calculate_weights_max_decay(self):
        """Test that decay_slope=1.0 gives maximum decay."""
        weights = RecencyBiasWeight.calculate_weights(decay_slope=1.0)
        
        # Weights should decrease significantly with age
        seasons = sorted(weights.keys())
        oldest_weight = weights[seasons[0]]
        newest_weight = weights[seasons[-1]]
        
        assert oldest_weight < newest_weight
        assert oldest_weight >= 0.0

    def test_weight_formula(self):
        """Test the linear decay formula: weight = 1.0 - (decay_slope * age / years_range)."""
        # Create a minimal case
        weights = RecencyBiasWeight.calculate_weights(
            decay_slope=1.0,
            base_year=2020,
            years_range=2,
        )
        
        # Should have 3 seasons: 2020, 2021, 2022
        assert len(weights) == 3
        
        # 2020 (age=2): weight = 1.0 - (1.0 * 2 / 2) = 0.0
        assert weights[2020] == 0.0
        
        # 2021 (age=1): weight = 1.0 - (1.0 * 1 / 2) = 0.5
        assert weights[2021] == 0.5
        
        # 2022 (age=0): weight = 1.0 - (1.0 * 0 / 2) = 1.0
        assert weights[2022] == 1.0

    def test_negative_decay_slope_raises_error(self):
        """Test that negative decay_slope raises ValueError."""
        with pytest.raises(ValueError, match="decay_slope must be between 0 and 1"):
            RecencyBiasWeight.calculate_weights(decay_slope=-0.1)

    def test_decay_slope_above_one_raises_error(self):
        """Test that decay_slope > 1 raises ValueError."""
        with pytest.raises(ValueError, match="decay_slope must be between 0 and 1"):
            RecencyBiasWeight.calculate_weights(decay_slope=1.5)

    def test_weights_sum_reasonable(self):
        """Test that total weights sum to a reasonable value."""
        weights = RecencyBiasWeight.calculate_weights(decay_slope=0.5)
        
        total = sum(weights.values())
        
        # Total should be positive and reasonable
        assert total > 0
        assert total <= len(weights)
