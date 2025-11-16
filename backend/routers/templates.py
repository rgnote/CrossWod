from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timezone

from database import get_db
from models.database import WorkoutTemplate, TemplateExercise, Workout, WorkoutExercise, WorkoutSet
from schemas import (
    WorkoutTemplateCreate, WorkoutTemplateResponse, WorkoutResponse
)

router = APIRouter()


@router.get("/", response_model=List[WorkoutTemplateResponse])
def get_templates(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    templates = db.query(WorkoutTemplate).options(
        joinedload(WorkoutTemplate.exercises)
        .joinedload(TemplateExercise.exercise)
    ).filter(
        WorkoutTemplate.user_id == user_id
    ).order_by(WorkoutTemplate.last_used.desc().nullslast()).all()
    return templates


@router.get("/{template_id}", response_model=WorkoutTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(WorkoutTemplate).options(
        joinedload(WorkoutTemplate.exercises)
        .joinedload(TemplateExercise.exercise)
    ).filter(WorkoutTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/", response_model=WorkoutTemplateResponse)
def create_template(
    template: WorkoutTemplateCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    db_template = WorkoutTemplate(
        user_id=user_id,
        name=template.name,
        description=template.description,
        category=template.category
    )
    db.add(db_template)
    db.flush()

    for ex_data in template.exercises:
        db_exercise = TemplateExercise(
            template_id=db_template.id,
            exercise_id=ex_data.exercise_id,
            order=ex_data.order,
            target_sets=ex_data.target_sets,
            target_reps=ex_data.target_reps,
            target_weight=ex_data.target_weight,
            rest_seconds=ex_data.rest_seconds,
            notes=ex_data.notes
        )
        db.add(db_exercise)

    db.commit()

    # Reload with relationships
    template = db.query(WorkoutTemplate).options(
        joinedload(WorkoutTemplate.exercises)
        .joinedload(TemplateExercise.exercise)
    ).filter(WorkoutTemplate.id == db_template.id).first()

    return template


@router.put("/{template_id}", response_model=WorkoutTemplateResponse)
def update_template(
    template_id: int,
    template_update: WorkoutTemplateCreate,
    db: Session = Depends(get_db)
):
    template = db.query(WorkoutTemplate).filter(
        WorkoutTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.name = template_update.name
    template.description = template_update.description
    template.category = template_update.category

    # Remove old exercises
    db.query(TemplateExercise).filter(
        TemplateExercise.template_id == template_id
    ).delete()

    # Add new exercises
    for ex_data in template_update.exercises:
        db_exercise = TemplateExercise(
            template_id=template_id,
            exercise_id=ex_data.exercise_id,
            order=ex_data.order,
            target_sets=ex_data.target_sets,
            target_reps=ex_data.target_reps,
            target_weight=ex_data.target_weight,
            rest_seconds=ex_data.rest_seconds,
            notes=ex_data.notes
        )
        db.add(db_exercise)

    db.commit()

    # Reload with relationships
    template = db.query(WorkoutTemplate).options(
        joinedload(WorkoutTemplate.exercises)
        .joinedload(TemplateExercise.exercise)
    ).filter(WorkoutTemplate.id == template_id).first()

    return template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(WorkoutTemplate).filter(
        WorkoutTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/start", response_model=WorkoutResponse)
def start_workout_from_template(
    template_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Create a new workout from a template"""
    template = db.query(WorkoutTemplate).options(
        joinedload(WorkoutTemplate.exercises)
    ).filter(WorkoutTemplate.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create the workout
    db_workout = Workout(
        user_id=user_id,
        name=template.name,
        started_at=datetime.now(timezone.utc)
    )
    db.add(db_workout)
    db.flush()

    # Add exercises from template
    for template_ex in sorted(template.exercises, key=lambda x: x.order):
        db_exercise = WorkoutExercise(
            workout_id=db_workout.id,
            exercise_id=template_ex.exercise_id,
            order=template_ex.order,
            notes=template_ex.notes
        )
        db.add(db_exercise)
        db.flush()

        # Pre-populate sets based on template targets
        if template_ex.target_sets:
            for i in range(template_ex.target_sets):
                db_set = WorkoutSet(
                    workout_exercise_id=db_exercise.id,
                    set_number=i + 1,
                    weight=template_ex.target_weight,
                    rest_seconds=template_ex.rest_seconds
                )
                db.add(db_set)

    # Update template last used
    template.last_used = datetime.now(timezone.utc)

    db.commit()

    # Reload with relationships
    workout = db.query(Workout).options(
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.exercise),
        joinedload(Workout.exercises)
        .joinedload(WorkoutExercise.sets)
    ).filter(Workout.id == db_workout.id).first()

    return workout
