"""
IPL Analysis Configuration

Defines eras, metrics, and constants for the IPL data-backed analysis.
"""

# Era definitions as per blog
ERA_SPLIT = {
    'early': {
        'name': 'Early Era',
        'start': 2008,
        'end': 2015,
        'description': 'Traditional cautious approach'
    },
    'late': {
        'name': 'Late Era',
        'start': 2016,
        'end': 2024,
        'description': 'Modern aggressive approach'
    },
    'impact_player': {
        'name': 'Impact Player Era',
        'start': 2023,
        'end': 2025,
        'description': 'Post-impact player rule'
    }
}

# Phase definitions (over ranges)
PHASES = {
    'powerplay': {'start': 0, 'end': 5, 'name': 'Powerplay (1-6)'},
    'middle': {'start': 6, 'end': 13, 'name': 'Middle Overs (7-14)'},
    'death': {'start': 14, 'end': 19, 'name': 'Death Overs (15-20)'}
}

# Position groups
POSITION_GROUPS = {
    'top_order': {'range': (0, 2), 'description': 'Positions 1-3'},
    'middle_order': {'range': (3, 5), 'description': 'Positions 4-6'},
    'finishers': {'range': (5, 7), 'description': 'Positions 6-8'}
}

# Metric definitions
METRICS = {
    'strike_rate': {
        'formula': '(runs * 100) / balls_faced',
        'description': 'Batting strike rate'
    },
    'boundary_rate': {
        'formula': '(fours + sixes) / balls_faced',
        'description': 'Frequency of boundaries'
    },
    'six_rate': {
        'formula': 'sixes / balls_faced',
        'description': 'Six-hitting frequency'
    },
    'dot_ball_ratio': {
        'formula': 'dot_balls / balls_faced',
        'description': 'Percentage of dot balls'
    },
    'economy_rate': {
        'formula': 'runs_conceded / overs_bowled',
        'description': 'Bowling economy'
    },
    'runs_per_over': {
        'formula': 'total_runs / overs',
        'description': 'Scoring rate'
    }
}

# Venue boundary sizes (meters)
VENUE_BOUNDARIES = {
    'Wankhede Stadium': {'square': 65, 'straight': 70, 'average': 67.5},
    'Chinnaswamy Stadium': {'square': 60, 'straight': 65, 'average': 62.5},
    'Eden Gardens': {'square': 70, 'straight': 75, 'average': 72.5},
    'M. Chinnaswamy': {'square': 60, 'straight': 65, 'average': 62.5},
    'Ferozeshah Kotla': {'square': 70, 'straight': 75, 'average': 72.5},
    'Rajiv Gandhi Intl.': {'square': 70, 'straight': 75, 'average': 72.5},
    'Punjab Cricket Assoc.': {'square': 65, 'straight': 70, 'average': 67.5},
    'M. A. Chidambaram': {'square': 70, 'straight': 75, 'average': 72.5},  # Chepauk
    'Sardar Patel Stadium': {'square': 65, 'straight': 70, 'average': 67.5},
    'HPCA Stadium': {'square': 65, 'straight': 70, 'average': 67.5},
    'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium': {'square': 62, 'straight': 66, 'average': 64},  # Lucknow
    'Arun Jaitley Stadium': {'square': 68, 'straight': 72, 'average': 70},
    'Narendra Modi Stadium': {'square': 68, 'straight': 72, 'average': 70},
    'Dr. Y.S. Rajasekhara Reddy Cricket Stadium': {'square': 65, 'straight': 70, 'average': 67.5},
    'Maharashtra Cricket Association Stadium': {'square': 65, 'straight': 70, 'average': 67.5},
    'Kapurthala': {'square': 65, 'straight': 70, 'average': 67.5},
}

# Short boundary threshold
SHORT_BOUNDARY_THRESHOLD = 66  # meters

# Statistical parameters
ALPHA = 0.05  # Significance level for hypothesis testing
FDR_CORRECTION = 'bh'  # Benjamini-Hochberg

# Projection scenarios
PROJECTION_SCENARIOS = {
    'conservative': {'annual_growth': 0.03, 'end_year': 2028, 'description': 'Boundary dims stabilize'},
    'moderate': {'annual_growth': 0.06, 'end_year': 2028, 'description': 'Player development'},
    'acceleration': {'annual_growth': 0.09, 'end_year': 2028, 'description': 'Rule changes'}
}
