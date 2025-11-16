from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from database import get_db
from models.database import (
    Workout, WorkoutExercise, WorkoutSet, Exercise, PersonalRecord
)
from schemas import (
    WorkoutCreate, WorkoutUpdate, WorkoutResponse, WorkoutSummary,
    WorkoutExerciseCreate, WorkoutSetCreate, WorkoutSetUpdate,
    WorkoutSetResponse, PersonalRecordResponse
)

router = APIRouter()


def check_and_update_prs(db: Session, user_id: int, workout_exercise: WorkoutExercise):
    """Check if any sets in this exercise are new PRs"""
    exercise_id = workout_exercise.exercise_id

    for set_data in workout_exercise.sets:
        if set_data.is_warmup or set_data.weight is None or set_data.reps is None:
            continue

        # Check for max weight PR (for same or more reps)
        current_max_weight = db.query(PersonalRecord).filter(
            PersonalRecord.user_id == user_id,
            PersonalRecord.exercise_id == exercise_id,
            PersonalRecord.record_type == "max_weight"
        ).first()

        if not current_max_weight or set_data.weight > current_max_weight.value:
            if current_max_weight:
                current_max_weight.value = set_data.weight
                current_max_weight.reps = set_data.reps
                current_max_weight.achieved_at = datetime.now(timezone.utc)
                current_max_weight.workout_set_id = set_data.id
            else:
                new_pr = PersonalRecord(
                    user_id=user_id,
                    exercise_id=exercise_id,
                    record_type="max_weight",
                    value=set_data.weight,
                    reps=set_data.reps,
                    workout_set_id=set_data.id
                )
                db.add(new_pr)

        # Check for max volume PR (weight * reps in a single set)
        volume = set_data.weight * set_data.reps
        current_max_volume = db.query(PersonalRecord).filter(
            PersonalRecord.user_id == user_id,
            PersonalRecord.exercise_id == exercise_id,
            PersonalRecord.record_type == "max_volume"
        ).first()

        if not current_max_volume or volume > current_max_volume.value:
            if current_max_volume:
                current_max_volume.value = volume
                current_max_volume.reps = set_data.reps
                current_max_volume.achieved_at = datetime.now(timezone.utc)
                current_max_volume.workout_set_id = set_data.id
            else:
                new_pr = PersonalRecord(
                    user_id=user_id,
                    exercise_id=exercise_id,
                    record_type="max_volume",
                    value=volume,
                    reps=set_data.reps,
                    workout_set_id=set_data.id
                )
                db.add(new_pr)


@router.get("/", response_model=List[WorkoutSummary])
def get_workouts(
    user_id: int = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id
    ).order_by(Workout.started_at.desc()).offset(offset).limit(limit).all()

    summaries = []
    for workout in workouts:
        total_sets = 0
        total_volume = 0.0
        for we in workout.exercises:
            for s in we.sets:
                total_sets += 1
                if s.weight and s.reps:
                    total_volume += s.weight * s.reps

        summaries.append(WorkoutSummary(
            id=workout.id,
            user_id=workout.user_id,
            name=workout.name,
            started_at=workout.started_at,
            completed_at=workout.completed_at,
            duration_seconds=workout.duration_seconds,
            exercise_count=len(workout.exercises),
            total_sets=total_sets,
            total_volume=total_volume
        ))

    return summaries


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).options(
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.exercise),
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.sets)
    ).filter(Workout.id == workout_id).first()

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return workout


@router.post("/", response_model=WorkoutResponse)
def create_workout(
    workout: WorkoutCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    db_workout = Workout(
        user_id=user_id,
        name=workout.name,
        notes=workout.notes,
        started_at=workout.started_at
    )
    db.add(db_workout)
    db.flush()

    # Add exercises and sets
    for ex_data in workout.exercises:
        db_exercise = WorkoutExercise(
            workout_id=db_workout.id,
            exercise_id=ex_data.exercise_id,
            order=ex_data.order,
            notes=ex_data.notes
        )
        db.add(db_exercise)
        db.flush()

        for set_data in ex_data.sets:
            db_set = WorkoutSet(
                workout_exercise_id=db_exercise.id,
                set_number=set_data.set_number,
                reps=set_data.reps,
                weight=set_data.weight,
                duration_seconds=set_data.duration_seconds,
                distance=set_data.distance,
                is_warmup=set_data.is_warmup,
                is_dropset=set_data.is_dropset,
                is_failure=set_data.is_failure,
                rpe=set_data.rpe,
                rest_seconds=set_data.rest_seconds,
                notes=set_data.notes
            )
            db.add(db_set)

        db.flush()
        check_and_update_prs(db, user_id, db_exercise)

    db.commit()

    # Reload with relationships
    workout = db.query(Workout).options(
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.exercise),
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.sets)
    ).filter(Workout.id == db_workout.id).first()

    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout(
    workout_id: int,
    workout_update: WorkoutUpdate,
    db: Session = Depends(get_db)
):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    if workout_update.name is not None:
        workout.name = workout_update.name
    if workout_update.notes is not None:
        workout.notes = workout_update.notes
    if workout_update.completed_at is not None:
        workout.completed_at = workout_update.completed_at
    if workout_update.duration_seconds is not None:
        workout.duration_seconds = workout_update.duration_seconds

    db.commit()

    # Reload with relationships
    workout = db.query(Workout).options(
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.exercise),
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.sets)
    ).filter(Workout.id == workout_id).first()

    return workout


@router.delete("/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()
    return {"message": "Workout deleted successfully"}


# Exercise management within workouts
@router.post("/{workout_id}/exercises", response_model=WorkoutResponse)
def add_exercise_to_workout(
    workout_id: int,
    exercise_data: WorkoutExerciseCreate,
    db: Session = Depends(get_db)
):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_data.exercise_id,
        order=exercise_data.order,
        notes=exercise_data.notes
    )
    db.add(db_exercise)
    db.flush()

    for set_data in exercise_data.sets:
        db_set = WorkoutSet(
            workout_exercise_id=db_exercise.id,
            set_number=set_data.set_number,
            reps=set_data.reps,
            weight=set_data.weight,
            duration_seconds=set_data.duration_seconds,
            distance=set_data.distance,
            is_warmup=set_data.is_warmup,
            is_dropset=set_data.is_dropset,
            is_failure=set_data.is_failure,
            rpe=set_data.rpe,
            rest_seconds=set_data.rest_seconds,
            notes=set_data.notes
        )
        db.add(db_set)

    db.flush()
    check_and_update_prs(db, workout.user_id, db_exercise)
    db.commit()

    # Reload with relationships
    workout = db.query(Workout).options(
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.exercise),
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.sets)
    ).filter(Workout.id == workout_id).first()

    return workout


# Set management
@router.post("/exercises/{workout_exercise_id}/sets", response_model=WorkoutSetResponse)
def add_set(
    workout_exercise_id: int,
    set_data: WorkoutSetCreate,
    db: Session = Depends(get_db)
):
    we = db.query(WorkoutExercise).filter(
        WorkoutExercise.id == workout_exercise_id
    ).first()
    if not we:
        raise HTTPException(status_code=404, detail="Workout exercise not found")

    db_set = WorkoutSet(
        workout_exercise_id=workout_exercise_id,
        set_number=set_data.set_number,
        reps=set_data.reps,
        weight=set_data.weight,
        duration_seconds=set_data.duration_seconds,
        distance=set_data.distance,
        is_warmup=set_data.is_warmup,
        is_dropset=set_data.is_dropset,
        is_failure=set_data.is_failure,
        rpe=set_data.rpe,
        rest_seconds=set_data.rest_seconds,
        notes=set_data.notes
    )
    db.add(db_set)
    db.flush()

    # Check for PRs
    workout = db.query(Workout).filter(Workout.id == we.workout_id).first()
    we_full = db.query(WorkoutExercise).options(
        joinedload(WorkoutExercise.sets)
    ).filter(WorkoutExercise.id == workout_exercise_id).first()
    check_and_update_prs(db, workout.user_id, we_full)

    db.commit()
    db.refresh(db_set)
    return db_set


@router.put("/sets/{set_id}", response_model=WorkoutSetResponse)
def update_set(
    set_id: int,
    set_update: WorkoutSetUpdate,
    db: Session = Depends(get_db)
):
    db_set = db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")

    for field, value in set_update.model_dump(exclude_unset=True).items():
        setattr(db_set, field, value)

    db.commit()
    db.refresh(db_set)

    # Re-check PRs after update
    we = db.query(WorkoutExercise).options(
        joinedload(WorkoutExercise.sets)
    ).filter(WorkoutExercise.id == db_set.workout_exercise_id).first()
    workout = db.query(Workout).filter(Workout.id == we.workout_id).first()
    check_and_update_prs(db, workout.user_id, we)
    db.commit()

    return db_set


@router.delete("/sets/{set_id}")
def delete_set(set_id: int, db: Session = Depends(get_db)):
    db_set = db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")

    db.delete(db_set)
    db.commit()
    return {"message": "Set deleted successfully"}


# Personal Records
@router.get("/prs/{user_id}", response_model=List[PersonalRecordResponse])
def get_personal_records(
    user_id: int,
    exercise_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PersonalRecord).filter(PersonalRecord.user_id == user_id)

    if exercise_id:
        query = query.filter(PersonalRecord.exercise_id == exercise_id)

    prs = query.all()

    result = []
    for pr in prs:
        exercise = db.query(Exercise).filter(Exercise.id == pr.exercise_id).first()
        result.append(PersonalRecordResponse(
            id=pr.id,
            user_id=pr.user_id,
            exercise_id=pr.exercise_id,
            exercise_name=exercise.name if exercise else "Unknown",
            record_type=pr.record_type,
            value=pr.value,
            reps=pr.reps,
            achieved_at=pr.achieved_at
        ))

    return result
