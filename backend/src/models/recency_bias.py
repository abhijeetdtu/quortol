"""RecencyBiasWeight model for season-level linear decay weighting."""

import logging
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger(__name__)

DEFAULT_SEASON_RANGE = (2008, 2025)


@dataclass
class RecencyBiasWeight:
    """Season-level weight for recency bias application.

    Attributes:
        season: IPL season year (2008-2025).
        weight: Weight for this season (calculated from decay_slope).
        decay_slope: Slope parameter for linear decay (0.0-1.0).
    """

    season: int
    weight: float
    decay_slope: float = 0.5

    def __post_init__(self) -> None:
        """Validate field constraints after initialization."""
        if not (2008 <= self.season <= 2025):
            raise ValueError(f"Season must be between 2008 and 2025, got {self.season}")
        if self.weight <= 0:
            raise ValueError(f"Weight must be > 0, got {self.weight}")
        if not (0.0 <= self.decay_slope <= 1.0):
            raise ValueError(f"decay_slope must be between 0.0 and 1.0, got {self.decay_slope}")

    @classmethod
    def calculate_weights(
        cls,
        decay_slope: float = 0.5,
        season_range: tuple = DEFAULT_SEASON_RANGE,
    ) -> Dict[int, float]:
        """Calculate linear decay weights for all seasons.

        Formula: weight = 1.0 - (decay_slope * (current_year - season) / years_range)

        Args:
            decay_slope: Bias control value (0.0 = no bias, 1.0 = max bias).
            season_range: Tuple of (min_year, max_year).

        Returns:
            Dictionary mapping season year to weight.
        """
        min_year, max_year = season_range
        years_range = max_year - min_year

        weights = {}
        for season in range(min_year, max_year + 1):
            weight = 1.0 - (decay_slope * (max_year - season) / years_range)
            weight = max(0.01, weight)  # Ensure minimum weight > 0
            weights[season] = round(weight, 4)

        logger.info("Calculated recency weights with slope=%.2f: %s", decay_slope, weights)
        return weights

    @classmethod
    def from_dict(cls, data: Dict[int, float], decay_slope: float = 0.5) -> Dict[int, "RecencyBiasWeight"]:
        """Create RecencyBiasWeight instances from dictionary.

        Args:
            data: Dictionary mapping season year to weight.
            decay_slope: Slope parameter.

        Returns:
            Dictionary mapping season year to RecencyBiasWeight instance.
        """
        return {
            season: cls(season=season, weight=weight, decay_slope=decay_slope)
            for season, weight in data.items()
        }
