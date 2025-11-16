from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.database import Exercise
from schemas import ExerciseCreate, ExerciseResponse

router = APIRouter()


@router.get("/", response_model=List[ExerciseResponse])
def get_exercises(
    category: Optional[str] = None,
    muscle_group: Optional[str] = None,
    search: Optional[str] = None,
    include_custom: bool = True,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Exercise)

    # Filter by category
    if category:
        query = query.filter(Exercise.category == category)

    # Filter by muscle group (JSON contains)
    if muscle_group:
        # SQLite JSON support - check if muscle_group is in the list
        query = query.filter(Exercise.muscle_groups.contains(muscle_group))

    # Search by name
    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))

    # Filter custom exercises
    if not include_custom:
        query = query.filter(Exercise.is_custom == False)
    elif user_id:
        # Include only this user's custom exercises plus all non-custom
        query = query.filter(
            (Exercise.is_custom == False) | (Exercise.created_by == user_id)
        )

    exercises = query.order_by(Exercise.name).all()
    return exercises


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Exercise.category).distinct().all()
    return [cat[0] for cat in categories]


@router.get("/muscle-groups")
def get_muscle_groups():
    return [
        "chest", "back", "shoulders", "biceps", "triceps",
        "forearms", "core", "quadriceps", "hamstrings",
        "glutes", "calves", "hip_flexors", "full_body"
    ]


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post("/", response_model=ExerciseResponse)
def create_exercise(
    exercise: ExerciseCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    db_exercise = Exercise(
        name=exercise.name,
        description=exercise.description,
        category=exercise.category,
        muscle_groups=exercise.muscle_groups,
        equipment=exercise.equipment,
        is_custom=True,
        created_by=user_id
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.put("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Only allow updating custom exercises created by this user
    if not exercise.is_custom or exercise.created_by != user_id:
        raise HTTPException(status_code=403, detail="Cannot modify this exercise")

    exercise.name = exercise_update.name
    exercise.description = exercise_update.description
    exercise.category = exercise_update.category
    exercise.muscle_groups = exercise_update.muscle_groups
    exercise.equipment = exercise_update.equipment

    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Only allow deleting custom exercises created by this user
    if not exercise.is_custom or exercise.created_by != user_id:
        raise HTTPException(status_code=403, detail="Cannot delete this exercise")

    db.delete(exercise)
    db.commit()
    return {"message": "Exercise deleted successfully"}
