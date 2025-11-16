from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta, timezone

from database import get_db
from models.database import Workout, WorkoutExercise, WorkoutSet, Exercise, BodyMetric
from schemas import WeeklySummary, ProgressData, StreakInfo

router = APIRouter()


@router.get("/weekly-summary", response_model=WeeklySummary)
def get_weekly_summary(
    user_id: int = Query(...),
    week_offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get summary for a specific week (0 = current week, 1 = last week, etc.)"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday() + (week_offset * 7))
    week_end = week_start + timedelta(days=7)

    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        func.date(Workout.started_at) >= week_start,
        func.date(Workout.started_at) < week_end
    ).all()

    total_duration = 0
    total_volume = 0.0
    total_sets = 0
    muscle_groups = {}

    for workout in workouts:
        if workout.duration_seconds:
            total_duration += workout.duration_seconds

        for we in workout.exercises:
            # Get muscle groups for this exercise
            exercise = db.query(Exercise).filter(
                Exercise.id == we.exercise_id
            ).first()
            if exercise:
                for mg in exercise.muscle_groups:
                    muscle_groups[mg] = muscle_groups.get(mg, 0) + len(we.sets)

            for s in we.sets:
                total_sets += 1
                if s.weight and s.reps:
                    total_volume += s.weight * s.reps

    # Count new PRs this week (simplified - would need PR history for accurate count)
    new_prs = 0  # TODO: Implement PR history tracking

    return WeeklySummary(
        week_start=week_start,
        total_workouts=len(workouts),
        total_duration_minutes=total_duration // 60,
        total_volume=total_volume,
        total_sets=total_sets,
        muscle_groups_worked=muscle_groups,
        new_prs=new_prs
    )


@router.get("/exercise-progress", response_model=ProgressData)
def get_exercise_progress(
    user_id: int = Query(...),
    exercise_id: int = Query(...),
    metric_type: str = Query("weight", pattern="^(weight|volume|reps)$"),
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get progress data for a specific exercise"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return ProgressData(
            dates=[],
            values=[],
            exercise_name="Unknown",
            metric_type=metric_type
        )

    # Get all sets for this exercise
    sets = db.query(WorkoutSet).join(
        WorkoutExercise
    ).join(
        Workout
    ).filter(
        Workout.user_id == user_id,
        WorkoutExercise.exercise_id == exercise_id,
        WorkoutSet.completed_at >= cutoff_date,
        WorkoutSet.is_warmup == False
    ).order_by(WorkoutSet.completed_at).all()

    # Group by date and calculate metric
    date_values = {}
    for s in sets:
        if s.weight is None or s.reps is None:
            continue

        set_date = s.completed_at.date().isoformat()

        if metric_type == "weight":
            # Track max weight per day
            if set_date not in date_values or s.weight > date_values[set_date]:
                date_values[set_date] = s.weight
        elif metric_type == "volume":
            # Track total volume per day
            volume = s.weight * s.reps
            date_values[set_date] = date_values.get(set_date, 0) + volume
        elif metric_type == "reps":
            # Track max reps at max weight per day
            if set_date not in date_values or s.reps > date_values[set_date]:
                date_values[set_date] = s.reps

    dates = sorted(date_values.keys())
    values = [date_values[d] for d in dates]

    return ProgressData(
        dates=dates,
        values=values,
        exercise_name=exercise.name,
        metric_type=metric_type
    )


@router.get("/body-weight-progress")
def get_body_weight_progress(
    user_id: int = Query(...),
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get body weight progress over time"""
    cutoff_date = date.today() - timedelta(days=days)

    metrics = db.query(BodyMetric).filter(
        BodyMetric.user_id == user_id,
        BodyMetric.date >= cutoff_date,
        BodyMetric.weight.isnot(None)
    ).order_by(BodyMetric.date).all()

    return {
        "dates": [m.date.isoformat() for m in metrics],
        "weights": [m.weight for m in metrics]
    }


@router.get("/streak", response_model=StreakInfo)
def get_streak_info(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get workout streak information"""
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id
    ).order_by(Workout.started_at.desc()).all()

    if not workouts:
        return StreakInfo(
            current_streak=0,
            longest_streak=0,
            total_workouts=0,
            last_workout_date=None
        )

    # Get unique workout dates
    workout_dates = set()
    for w in workouts:
        workout_dates.add(w.started_at.date())

    sorted_dates = sorted(workout_dates, reverse=True)

    # Calculate current streak
    current_streak = 0
    today = date.today()

    # Check if worked out today or yesterday (streak continues)
    if sorted_dates and (sorted_dates[0] == today or sorted_dates[0] == today - timedelta(days=1)):
        current_streak = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i-1] - timedelta(days=1):
                current_streak += 1
            else:
                break

    # Calculate longest streak
    longest_streak = 1
    current_run = 1
    sorted_dates_asc = sorted(workout_dates)

    for i in range(1, len(sorted_dates_asc)):
        if sorted_dates_asc[i] == sorted_dates_asc[i-1] + timedelta(days=1):
            current_run += 1
            longest_streak = max(longest_streak, current_run)
        else:
            current_run = 1

    if len(sorted_dates_asc) == 1:
        longest_streak = 1

    return StreakInfo(
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_workouts=len(workouts),
        last_workout_date=sorted_dates[0] if sorted_dates else None
    )


@router.get("/muscle-group-balance")
def get_muscle_group_balance(
    user_id: int = Query(...),
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Get muscle group distribution over recent period"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    workout_exercises = db.query(WorkoutExercise).join(
        Workout
    ).filter(
        Workout.user_id == user_id,
        Workout.started_at >= cutoff_date
    ).all()

    muscle_groups = {}
    for we in workout_exercises:
        exercise = db.query(Exercise).filter(
            Exercise.id == we.exercise_id
        ).first()
        if exercise:
            sets_count = len(we.sets)
            for mg in exercise.muscle_groups:
                muscle_groups[mg] = muscle_groups.get(mg, 0) + sets_count

    return {
        "muscle_groups": muscle_groups,
        "period_days": days
    }


@router.get("/workout-frequency")
def get_workout_frequency(
    user_id: int = Query(...),
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Get workout frequency data for calendar view"""
    cutoff_date = date.today() - timedelta(days=days)

    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        func.date(Workout.started_at) >= cutoff_date
    ).all()

    # Group by date
    date_counts = {}
    for w in workouts:
        d = w.started_at.date().isoformat()
        date_counts[d] = date_counts.get(d, 0) + 1

    return {
        "dates": date_counts,
        "period_days": days
    }
