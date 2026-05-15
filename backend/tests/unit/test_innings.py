"""Tests for Innings model — over completion, run rate calculation, all-out detection."""

import sys
from pathlib import Path

import pytest

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from models.innings import Innings
from models.delivery import DeliveryOutcome


class TestInnings:
    """Tests for Innings model."""

    def test_creates_innings(self):
        """Test basic Innings creation."""
        innings = Innings(
            innings_number=1,
            batting_team="Mumbai Indians",
        )
        
        assert innings.innings_number == 1
        assert innings.batting_team == "Mumbai Indians"
        assert innings.total_runs == 0
        assert innings.wickets_lost == 0
        assert len(innings.balls) == 0

    def test_add_delivery(self):
        """Test adding a delivery to innings."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        delivery = DeliveryOutcome(
            ball_number=1,
            runs=4,
            is_wicket=False,
            cumulative_score=4,
            cumulative_wickets=0,
        )
        
        innings.add_delivery(delivery)
        
        assert len(innings.balls) == 1
        assert innings.total_runs == 4

    def test_over_completion(self):
        """Test over completion at 6 balls."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        for i in range(6):
            delivery = DeliveryOutcome(
                ball_number=i + 1,
                runs=1,
                is_wicket=False,
                cumulative_score=i + 1,
                cumulative_wickets=0,
            )
            innings.add_delivery(delivery)
        
        assert innings.overs_completed == 1.0
        assert innings.is_over_complete()

    def test_run_rate_calculation(self):
        """Test run rate calculation."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        # 20 overs, 160 runs
        innings.total_runs = 160
        innings.overs_completed = 20.0
        
        assert abs(innings.run_rate - 8.0) < 0.01

    def test_run_rate_zero_when_no_overs(self):
        """Test run rate is 0 when no overs played."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        assert innings.run_rate == 0.0

    def test_all_out_detection(self):
        """Test all-out detection at 10 wickets."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        # Add 10 wickets
        for i in range(10):
            delivery = DeliveryOutcome(
                ball_number=i + 1,
                runs=0,
                is_wicket=True,
                wicket_type="bowled",
                cumulative_score=0,
                cumulative_wickets=i + 1,
            )
            innings.add_delivery(delivery)
        
        assert innings.is_all_out()
        assert innings.wickets_lost == 10

    def test_innings_not_complete_with_wickets(self):
        """Test innings is not complete with remaining wickets."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        innings.wickets_lost = 5
        innings.total_runs = 150
        
        assert not innings.is_complete()

    def test_innings_complete_at_120_balls(self):
        """Test innings is complete at 120 balls (20 overs)."""
        innings = Innings(innings_number=1, batting_team="Mumbai Indians")
        
        # Simulate 120 balls
        for i in range(120):
            delivery = DeliveryOutcome(
                ball_number=i + 1,
                runs=1 if i % 2 == 0 else 0,
                is_wicket=False,
                cumulative_score=i + 1,
                cumulative_wickets=0,
            )
            innings.add_delivery(delivery)
        
        assert innings.is_complete()
