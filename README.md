# Quortol

A full-stack application with Vue 3 frontend and Flask backend.

## Prerequisites

- Node.js (v16+)
- Python (v3.8+)

## Getting Started

### Backend

1. Create environment from environment.yml (requires Conda):
   ```
   conda env create -f backend/environment.yml
   conda activate quortol
   ```

2. Start the backend server from the project root:
   ```
   python -m backend.app
   ```

The backend will run on `http://localhost:5000`

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

The frontend will run on `http://localhost:8050`

## Notes

- Start the backend first, then the frontend
- Both must be running simultaneously for the application to work
- The router fix (importing `useAuthStore`) resolves the navigation guard errors
