"""Tests for DeliveryOutcome model — ball outcome validation, cumulative score calculation."""

import sys
from pathlib import Path

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from models.delivery import DeliveryOutcome


class TestDeliveryOutcome:
    """Tests for DeliveryOutcome model."""

    def test_creates_delivery_outcome(self):
        """Test basic DeliveryOutcome creation."""
        delivery = DeliveryOutcome(
            ball_number=5,
            runs=4,
            is_wicket=False,
            wicket_type=None,
            is_extra=False,
            extra_type=None,
            cumulative_score=28,
            cumulative_wickets=1,
            probability=0.15,
        )
        
        assert delivery.ball_number == 5
        assert delivery.runs == 4
        assert not delivery.is_wicket
        assert not delivery.is_extra
        assert delivery.cumulative_score == 28

    def test_creates_wicket_delivery(self):
        """Test creating a wicket delivery."""
        delivery = DeliveryOutcome(
            ball_number=12,
            runs=0,
            is_wicket=True,
            wicket_type="caught",
            is_extra=False,
            extra_type=None,
            cumulative_score=45,
            cumulative_wickets=2,
            probability=0.08,
        )
        
        assert delivery.is_wicket
        assert delivery.wicket_type == "caught"
        assert delivery.runs == 0

    def test_creates_extra_delivery(self):
        """Test creating an extra delivery."""
        delivery = DeliveryOutcome(
            ball_number=8,
            runs=1,
            is_wicket=False,
            wicket_type=None,
            is_extra=True,
            extra_type="wide",
            cumulative_score=32,
            cumulative_wickets=1,
            probability=0.05,
        )
        
        assert delivery.is_extra
        assert delivery.extra_type == "wide"

    def test_cumulative_score_increments(self):
        """Test that cumulative score increments correctly."""
        delivery1 = DeliveryOutcome(
            ball_number=1,
            runs=0,
            is_wicket=False,
            cumulative_score=0,
            cumulative_wickets=0,
        )
        
        delivery2 = DeliveryOutcome(
            ball_number=2,
            runs=4,
            is_wicket=False,
            cumulative_score=4,
            cumulative_wickets=0,
        )
        
        assert delivery2.cumulative_score == delivery1.cumulative_score + 4

    def test_cumulative_wickets_increments(self):
        """Test that cumulative wickets increments on wicket."""
        delivery1 = DeliveryOutcome(
            ball_number=5,
            runs=0,
            is_wicket=False,
            cumulative_score=20,
            cumulative_wickets=1,
        )
        
        delivery2 = DeliveryOutcome(
            ball_number=6,
            runs=0,
            is_wicket=True,
            wicket_type="bowled",
            cumulative_score=20,
            cumulative_wickets=2,
        )
        
        assert delivery2.cumulative_wickets == delivery1.cumulative_wickets + 1

    def test_boundary_detection(self):
        """Test boundary detection (4 or 6 runs)."""
        four = DeliveryOutcome(ball_number=1, runs=4, is_wicket=False)
        six = DeliveryOutcome(ball_number=2, runs=6, is_wicket=False)
        
        assert not four.is_boundary
        assert six.is_boundary

    def test_is_scoring_delivery(self):
        """Test scoring delivery detection."""
        scoring = DeliveryOutcome(ball_number=1, runs=2, is_wicket=False)
        non_scoring = DeliveryOutcome(ball_number=2, runs=0, is_wicket=True)
        
        assert scoring.is_scoring_delivery
        assert not non_scoring.is_scoring_delivery
