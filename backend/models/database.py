from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, LargeBinary, JSON, Date
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)  # Stored as BLOB
    profile_picture_mime = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    body_metrics = relationship("BodyMetric", back_populates="user", cascade="all, delete-orphan")
    progress_photos = relationship("ProgressPhoto", back_populates="user", cascade="all, delete-orphan")
    templates = relationship("WorkoutTemplate", back_populates="user", cascade="all, delete-orphan")
    personal_records = relationship("PersonalRecord", back_populates="user", cascade="all, delete-orphan")
    custom_exercises = relationship("Exercise", back_populates="created_by_user", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # push, pull, legs, cardio, etc.
    muscle_groups = Column(JSON, nullable=False)  # ["chest", "triceps", "shoulders"]
    equipment = Column(String(100), nullable=True)  # barbell, dumbbell, bodyweight, etc.
    is_custom = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    created_by_user = relationship("User", back_populates="custom_exercises")
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    personal_records = relationship("PersonalRecord", back_populates="exercise", cascade="all, delete-orphan")
    template_exercises = relationship("TemplateExercise", back_populates="exercise")


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    sets = relationship("WorkoutSet", back_populates="workout_exercise", cascade="all, delete-orphan")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_exercise_id = Column(Integer, ForeignKey("workout_exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # in kg or lbs based on user preference
    duration_seconds = Column(Integer, nullable=True)  # for timed exercises
    distance = Column(Float, nullable=True)  # for cardio (in meters)
    is_warmup = Column(Boolean, default=False)
    is_dropset = Column(Boolean, default=False)
    is_failure = Column(Boolean, default=False)
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion (1-10)
    rest_seconds = Column(Integer, nullable=True)  # Rest after this set
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    workout_exercise = relationship("WorkoutExercise", back_populates="sets")


class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    record_type = Column(String(50), nullable=False)  # max_weight, max_reps, max_volume, etc.
    value = Column(Float, nullable=False)
    reps = Column(Integer, nullable=True)  # for context (e.g., 100kg for 5 reps)
    achieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    workout_set_id = Column(Integer, nullable=True)  # Reference to the actual set

    # Relationships
    user = relationship("User", back_populates="personal_records")
    exercise = relationship("Exercise", back_populates="personal_records")


class BodyMetric(Base):
    __tablename__ = "body_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=True)  # kg or lbs
    body_fat_percentage = Column(Float, nullable=True)
    measurements = Column(JSON, nullable=True)  # {"chest": 100, "waist": 80, "arms": 35, etc.}
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="body_metrics")


class ProgressPhoto(Base):
    __tablename__ = "progress_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_data = Column(LargeBinary, nullable=False)  # Stored as BLOB
    photo_mime = Column(String(50), nullable=False)
    category = Column(String(50), nullable=True)  # front, side, back
    date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="progress_photos")


class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # Push, Pull, Legs, Upper, Lower, Full Body
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="templates")
    exercises = relationship("TemplateExercise", back_populates="template", cascade="all, delete-orphan")


class TemplateExercise(Base):
    __tablename__ = "template_exercises"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workout_templates.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, nullable=False)
    target_sets = Column(Integer, nullable=True)
    target_reps = Column(String(50), nullable=True)  # "8-12" or "5x5"
    target_weight = Column(Float, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    template = relationship("WorkoutTemplate", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="template_exercises")
