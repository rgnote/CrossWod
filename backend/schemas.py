from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


# User schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_active: datetime
    has_profile_picture: bool = False

    class Config:
        from_attributes = True


# Exercise schemas
class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str
    muscle_groups: List[str]
    equipment: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: int
    is_custom: bool
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Workout Set schemas
class WorkoutSetBase(BaseModel):
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance: Optional[float] = None
    is_warmup: bool = False
    is_dropset: bool = False
    is_failure: bool = False
    rpe: Optional[float] = Field(None, ge=1, le=10)
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class WorkoutSetCreate(WorkoutSetBase):
    pass


class WorkoutSetUpdate(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance: Optional[float] = None
    is_warmup: Optional[bool] = None
    is_dropset: Optional[bool] = None
    is_failure: Optional[bool] = None
    rpe: Optional[float] = Field(None, ge=1, le=10)
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class WorkoutSetResponse(WorkoutSetBase):
    id: int
    workout_exercise_id: int
    completed_at: datetime

    class Config:
        from_attributes = True


# Workout Exercise schemas
class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    order: int
    notes: Optional[str] = None


class WorkoutExerciseCreate(WorkoutExerciseBase):
    sets: List[WorkoutSetCreate] = []


class WorkoutExerciseResponse(WorkoutExerciseBase):
    id: int
    workout_id: int
    exercise: ExerciseResponse
    sets: List[WorkoutSetResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Workout schemas
class WorkoutBase(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    started_at: datetime
    exercises: List[WorkoutExerciseCreate] = []


class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None


class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    exercises: List[WorkoutExerciseResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutSummary(BaseModel):
    id: int
    user_id: int
    name: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    exercise_count: int
    total_sets: int
    total_volume: float  # weight * reps

    class Config:
        from_attributes = True


# Personal Record schemas
class PersonalRecordResponse(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    exercise_name: str
    record_type: str
    value: float
    reps: Optional[int] = None
    achieved_at: datetime

    class Config:
        from_attributes = True


# Body Metric schemas
class BodyMetricBase(BaseModel):
    date: date
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    measurements: Optional[dict] = None
    notes: Optional[str] = None


class BodyMetricCreate(BodyMetricBase):
    pass


class BodyMetricResponse(BodyMetricBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Progress Photo schemas
class ProgressPhotoBase(BaseModel):
    category: Optional[str] = None
    date: date
    notes: Optional[str] = None


class ProgressPhotoCreate(ProgressPhotoBase):
    pass


class ProgressPhotoResponse(ProgressPhotoBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Template schemas
class TemplateExerciseBase(BaseModel):
    exercise_id: int
    order: int
    target_sets: Optional[int] = None
    target_reps: Optional[str] = None
    target_weight: Optional[float] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None


class TemplateExerciseCreate(TemplateExerciseBase):
    pass


class TemplateExerciseResponse(TemplateExerciseBase):
    id: int
    exercise: ExerciseResponse

    class Config:
        from_attributes = True


class WorkoutTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None


class WorkoutTemplateCreate(WorkoutTemplateBase):
    exercises: List[TemplateExerciseCreate] = []


class WorkoutTemplateResponse(WorkoutTemplateBase):
    id: int
    user_id: int
    created_at: datetime
    last_used: Optional[datetime] = None
    exercises: List[TemplateExerciseResponse] = []

    class Config:
        from_attributes = True


# Analytics schemas
class WeeklySummary(BaseModel):
    week_start: date
    total_workouts: int
    total_duration_minutes: int
    total_volume: float
    total_sets: int
    muscle_groups_worked: dict  # {"chest": 10, "back": 8, etc.}
    new_prs: int


class ProgressData(BaseModel):
    dates: List[str]
    values: List[float]
    exercise_name: str
    metric_type: str  # "weight", "volume", "reps"


class StreakInfo(BaseModel):
    current_streak: int
    longest_streak: int
    total_workouts: int
    last_workout_date: Optional[date] = None
