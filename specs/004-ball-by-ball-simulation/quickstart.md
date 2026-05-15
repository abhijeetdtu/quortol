# Quickstart: Ball-by-Ball Match Simulation

**Feature**: 004-ball-by-ball-simulation  
**Date**: 2026-05-14  
**Purpose**: Get the dashboard running locally in 5 minutes

## Prerequisites

- Python 3.11+ (or 3.8+ per constitution minimum)
- Conda (for backend environment management)
- Node.js 16+ (for frontend dependencies, if applicable)
- IPL.csv in `data/` directory (from features 002/003)

## Installation

### 1. Clone and Navigate

```bash
cd C:\Users\abhij\Code\quortol
git checkout 004-ball-by-ball-simulation
```

### 2. Create Conda Environment

```bash
conda create -n ipl-simulation python=3.11
conda activate ipl-simulation
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

**Required packages**:
- `dash>=2.14.0` — Web app framework
- `plotly>=5.18.0` — Interactive charts
- `flask>=2.3.0` — Backend API
- `pandas>=2.0.0` — Data processing
- `scipy>=1.11.0` — Bayesian inference
- `pytest>=7.4.0` — Testing (per constitution)

### 4. Verify IPL.csv

Ensure `data/IPL.csv` exists and is readable. The dashboard will show an error message if the file is missing or corrupted.

## Running the Dashboard

### Backend (Flask API)

```bash
cd backend
python src/api/routes.py
```

The API will start on `http://localhost:5000`.

### Frontend (Dash App)

```bash
cd frontend
python src/pages/simulation.py
```

The dashboard will open in your browser at `http://localhost:8050`.

## Using the Dashboard

### 1. Select Teams

Use the team selector dropdown to choose two distinct IPL teams. The system prevents selecting the same team twice.

### 2. Adjust Recency Bias

Use the slider to control how much recent data influences the simulation:
- **Left (0.0)**: All seasons weighted equally
- **Right (1.0)**: Recent seasons dominate

### 3. Set Random Seed (Optional)

The seed is pre-populated for reproducibility. Edit it to get different outcomes.

### 4. Simulate Match

Click "Simulate Match". A loading spinner appears during the 1–5 second simulation.

### 5. View Results

- **Ball-by-ball chart**: Cumulative score over overs, with key events highlighted
- **Match summary**: Final scores, result, key statistics
- **Replay**: Step through balls, jump to overs or milestones

## Troubleshooting

### "IPL.csv not found"

Ensure `data/IPL.csv` exists. The file should be in the repository root's `data/` directory.

### "Simulation failed"

Check the browser console for error details. Common causes:
- Invalid team selection
- Corrupted IPL.csv
- Insufficient memory (rare)

### Charts not rendering

Ensure Plotly is installed correctly:
```bash
pip install --upgrade plotly
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

Tests cover:
- **Unit**: Probability model, recency bias, simulation engine
- **Integration**: Full simulation pipeline
- **Contract**: API endpoint validation

## Next Steps

- Read [plan.md](plan.md) for implementation details
- Read [data-model.md](data-model.md) for entity definitions
- Read [contracts/api.md](contracts/api.md) for API specifications
- Run `/speckit.tasks` to generate task decomposition
