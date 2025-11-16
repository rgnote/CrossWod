from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base
from models.database import *  # Import all models to register them
from routers import users, exercises, workouts, analytics, body_metrics, templates
from utils.seed_exercises import seed_exercises


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    seed_exercises()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="CrossWod API",
    description="Workout tracking API for CrossWod PWA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["Exercises"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])
app.include_router(body_metrics.router, prefix="/api/body-metrics", tags=["Body Metrics"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
