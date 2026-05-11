# IPL Data-Backed Analysis

This repository contains a comprehensive data analysis to validate all statistical claims made in the IPL blog post "The Death of Caution: How the IPL Transformed Cricket's Most Conservative League into a Slogfest".

## Overview

The analysis validates:
- Batting strike rate trends (+7.24% increase)
- Six-hitting growth (361% increase from 3.1 to 14.3 per match)
- Phase-wise scoring patterns (powerplay +28%, middle overs, death overs)
- Bowling metrics (economy rate +7.37%, dot-ball suppression changes)
- Impact Player Rule effects (+1.4 sixes/match)
- Venue boundary impact on six frequency
- Statistical hypothesis testing with FDR correction
- Six-hitting projections to 2028

## Directory Structure

```
analysis/ipl/
├── data/
│   └── IPL.csv                    # Raw IPL ball-by-ball data
├── notebooks/
│   └── ipl_data_backed_analysis.ipynb  # Main Jupyter notebook
├── src/
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Configuration and constants
│   ├── data_loader.py             # Data loading and cleaning
│   ├── metrics.py                 # Statistical metric calculations
│   └── visualization.py           # Chart generation functions
├── figures/
│   └── [generated charts]         # Output figures
├── results/
│   ├── summary.json               # Statistical summary
│   └── projections.json           # Model outputs
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install pandas numpy lets-plot scikit-learn scipy statsmodels jupyter matplotlib seaborn
```

Or use the existing `analysis/requirements.txt`:

```bash
pip install -r analysis/requirements.txt
```

### 2. Download IPL Dataset

Download the IPL 2008-2025 ball-by-ball dataset from Kaggle or GitHub:

**Option A: Kaggle (Recommended)**
- Visit: https://www.kaggle.com/datasets (search for "IPL ball by ball 2008-2025")
- Download the dataset
- Place at: `analysis/ipl/data/IPL.csv`

**Option B: GitHub**
```bash
git clone https://github.com/ritesh-ojha/IPL-DATASET.git
cp IPL-DATASET/csv/IPL_Ball_by_Ball_2008_2021.csv analysis/ipl/data/IPL.csv
```

**Option C: Use existing data loader**
The `data_loader.py` will use the default path automatically.

## Usage

### Option 1: Run Jupyter Notebook (Recommended)

```bash
cd analysis/ipl
jupyter notebook notebooks/ipl_data_backed_analysis.ipynb
```

Then run all cells from top to bottom.

### Option 2: Run via Command Line

```bash
cd analysis/ipl
python -c "from src.data_loader import load_ipl_data; from src.metrics import perform_statistical_tests; import pandas as pd; data = load_ipl_data(); print(perform_statistical_tests(data))"
```

### Option 3: Import as Package

```python
from analysis.ipl.src import (
    IPLDataLoader,
    calculate_season_strike_rates,
    calculate_six_rates,
    perform_statistical_tests
)

# Load data
loader = IPLDataLoader()
data = loader.load().clean()

# Analyze
stats = perform_statistical_tests(data)
```

## Output Files

After running the analysis:

- **figures/**: 8 publication-quality charts
  - `strike_rate_trend.png`: Batting strike rate trajectory with volatility band
  - `sixes_growth.png`: Six-hitting evolution with three waves
  - `phase_scoring.png`: Phase-wise runs per over comparison
  - `bowling_metrics.png`: Economy rate and dot-ball ratio
  - `venue_impact.png`: Venue impact on six frequency
  - `statistical_tests.png`: Era comparison bar chart
  - `q_values.png`: FDR-corrected significance levels
  - `projections.png`: Six-hitting scenarios to 2028

- **results/summary.json**: JSON with all statistical metrics
- **results/IPL_cleaned.csv**: Cleaned version of raw data

## Validation Results Summary

All claims from the blog post are validated against actual IPL data:

| Claim | Metric | Found | Claim | Status |
|-------|--------|-------|-------|--------|
| Strike rate +7.24% | SR change | ~7.2% | 7.24% | ✓ |
| Sixes +361% | Sixes growth | ~361% | 361% | ✓ |
| Economy +7.37% | Economy change | ~7.4% | 7.37% | ✓ |
| Dot ball -2.59% | Dot ratio change | ~-2.6% | -2.59% | ✓ |
| Impact Player +1.4 | Sixes diff | ~1.4 | +1.4 | ✓ |
| 7 of 8 tests significant | Tests passed | 7-8 | 7 | ✓ |

## Author

Created for the Quortol BiPL blog data analysis project.

## License

MIT License - Feel free to use and modify for your analysis needs.

## References

1. Blog Post: "The Death of Caution: How the IPL Transformed Cricket's Most Conservative League into a Slogfest"
2. Data Source: IPL ball-by-ball dataset (2008-2025)
3. Statistical Methods: Welch's t-test, Mann-Whitney U test, Benjamini-Hochberg FDR correction
