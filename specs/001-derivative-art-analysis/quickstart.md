# Quick Start: Derivative Art Analysis

**Feature**: Derivative Art Analysis  
**Date**: May 13 2026  
**Spec**: [specs/001-derivative-art-analysis/spec.md](../spec.md)

---

## Overview

This document provides step-by-step instructions for setting up and running the Derivative Art Analysis web application.

---

## Prerequisites

### Required Software

- **Python**: 3.8+
- **Node.js**: 16+
- **Conda**: For backend environment management
- **npm**: For frontend dependencies

### System Requirements

- **Memory**: 4GB+ RAM
- **Storage**: 500MB+ for art data files
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+

---

## Installation

### Step 1: Clone Repository

```bash
git clone [repository-url]
cd quortol
```

### Step 2: Setup Backend Environment

```bash
# Create conda environment
conda create -n art-analysis python=3.8 -y
conda activate art-analysis

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Step 3: Setup Frontend Environment

```bash
# Install frontend dependencies
cd frontend
npm install
```

### Step 4: Load Art Data

```bash
# Download historical art data from configured sources
# (Wikipedia, WikiArt.org, supplementary web sources)
python backend/scripts/load_data.py

# Data will be stored in: backend/data/art_records.json
```

---

## Running the Application

### Development Mode

**Terminal 1 - Backend**:
```bash
cd backend
flask run --port=5000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run serve --port=8080
```

### Access the Application

**URL**: `http://localhost:8080`  
**API**: `http://localhost:5000/api`

---

## Testing

### Backend Tests

```bash
cd backend
pytest tests/unit/
pytest tests/integration/
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:unit
npm run test:e2e
```

### Full Test Suite

```bash
# Run all tests (backend + frontend)
./scripts/run-all-tests.sh
```

---

## Development Workflow

### Backend-First Development

1. **Define API contracts** in `contracts/api.md`
2. **Implement backend services** in `backend/src/services/`
3. **Test API endpoints** with pytest
4. **Update frontend** to consume APIs
5. **Test integration** with E2E tests

### Frontend-Second Development

1. **Component structure** in `frontend/src/components/`
2. **API integration** in `frontend/src/services/api.js`
3. **UI components** in `frontend/src/components/`
4. **Chart visualizations** using lets-plot

---

## Key Scripts

### Data Processing

```bash
# Load fresh data from sources
python backend/scripts/load_data.py

# Process influence chains
python backend/scripts/process_influences.py

# Generate derivative metrics
python backend/scripts/calculate_metrics.py
```

### Development

```bash
# Start backend
./scripts/start-backend.sh

# Start frontend  
./scripts/start-frontend.sh

# Run both in dev mode
./scripts/start-dev.sh
```

### Production

```bash
# Build frontend for production
npm run build

# Prepare backend for deployment
python backend/scripts/prepare-deploy.py

# Deploy with Cloudflare Tunnel
./scripts/deploy-tunnel.sh
```

---

## Configuration

### Environment Variables (Backend)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATA_PATH` | Path to art data JSON file | `backend/data/art_records.json` |
| `FLASK_ENV` | Development mode | `development` |
| `FLASK_DEBUG` | Debug mode | `true` |
| `API_PORT` | API server port | `5000` |

### Environment Variables (Frontend)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:5000` |
| `VITE_APP_ENV` | Environment | `development` |

---

## Troubleshooting

### Common Issues

**Issue**: Charts not rendering  
**Solution**: Verify lets-plot version >= 4.9.0

**Issue**: API returns 500 errors  
**Solution**: Check art data file exists and is valid JSON

**Issue**: Filters not working  
**Solution**: Verify data sources have period/movement/medium fields

**Issue**: Performance degradation  
**Solution**: Check influence chain caching and pagination settings

---

## Success Metrics

Verify the application meets success criteria:

- **SC-001**: Dashboard loads within 3 seconds
- **SC-002**: 10,000+ relationships renderable
- **SC-003**: 95% task completion rate (filter + view + compare)
- **SC-004**: Average 3 clicks to navigate influence chains
- **SC-005**: 90% user satisfaction (first-use survey)

---

## Next Steps

1. **Review API contracts** in `contracts/api.md`
2. **Understand data model** in `data-model.md`
3. **Explore user stories** in `../spec.md`
4. **Review tasks** (when generated via `/speckit.tasks`)

---

## Privacy & Data

**No user tracking** is implemented. This application:
- Does not collect cookies
- Does not track user behavior
- Does not send analytics
- Does not store personal data

All data is historical art information from public sources.
