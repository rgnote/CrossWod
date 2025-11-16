# CrossWod - Workout Tracking PWA

A modern, self-hosted workout tracking Progressive Web App with iPhone liquid glass UI.

## Features

- **Multi-user profiles** - Simple profile selection, no passwords
- **Workout logging** - Track exercises, sets, reps, weights
- **Exercise library** - 100+ pre-built exercises with custom creation
- **Progress tracking** - PRs, charts, volume analysis
- **Offline support** - Full PWA functionality
- **iPhone optimized** - Liquid glass UI, haptic feedback
- **Single database** - All data in one SQLite file for easy backup

## Quick Start (Self-Hosting)

### Option 1: Docker (Recommended)

```bash
# Clone and start
git clone <repo-url>
cd CrossWod
docker-compose up -d
```

Access at `http://localhost:3000`

### Option 2: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Backup

All data is stored in `backend/data/crosswod.db`. Simply copy this file to backup your entire database including:
- User profiles and photos
- All workouts and exercises
- Progress photos
- Personal records

## Tech Stack

- **Frontend**: React + Vite + PWA (Chart.js for analytics)
- **Backend**: Python + FastAPI + SQLite
- **Deployment**: Docker Compose

## Project Structure

```
CrossWod/
├── backend/           # FastAPI Python backend
│   ├── data/         # SQLite database storage
│   ├── routers/      # API route handlers
│   ├── models/       # SQLAlchemy models
│   └── main.py       # Application entry point
├── frontend/         # React + Vite PWA
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Main app pages
│   │   ├── hooks/       # Custom React hooks
│   │   └── utils/       # Helper functions
│   └── public/          # Static assets
└── docker-compose.yml   # One-command deployment
```

## License

MIT
