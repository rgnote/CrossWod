from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models.database import BodyMetric, ProgressPhoto
from schemas import (
    BodyMetricCreate, BodyMetricResponse,
    ProgressPhotoCreate, ProgressPhotoResponse
)

router = APIRouter()


# Body Metrics
@router.get("/", response_model=List[BodyMetricResponse])
def get_body_metrics(
    user_id: int = Query(...),
    limit: int = Query(100, ge=1, le=365),
    db: Session = Depends(get_db)
):
    metrics = db.query(BodyMetric).filter(
        BodyMetric.user_id == user_id
    ).order_by(BodyMetric.date.desc()).limit(limit).all()
    return metrics


@router.post("/", response_model=BodyMetricResponse)
def create_body_metric(
    metric: BodyMetricCreate,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    # Check if metric for this date already exists
    existing = db.query(BodyMetric).filter(
        BodyMetric.user_id == user_id,
        BodyMetric.date == metric.date
    ).first()

    if existing:
        # Update existing metric
        if metric.weight is not None:
            existing.weight = metric.weight
        if metric.body_fat_percentage is not None:
            existing.body_fat_percentage = metric.body_fat_percentage
        if metric.measurements is not None:
            existing.measurements = metric.measurements
        if metric.notes is not None:
            existing.notes = metric.notes
        db.commit()
        db.refresh(existing)
        return existing

    db_metric = BodyMetric(
        user_id=user_id,
        date=metric.date,
        weight=metric.weight,
        body_fat_percentage=metric.body_fat_percentage,
        measurements=metric.measurements,
        notes=metric.notes
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.delete("/{metric_id}")
def delete_body_metric(metric_id: int, db: Session = Depends(get_db)):
    metric = db.query(BodyMetric).filter(BodyMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Body metric not found")
    db.delete(metric)
    db.commit()
    return {"message": "Body metric deleted successfully"}


# Progress Photos
@router.get("/photos", response_model=List[ProgressPhotoResponse])
def get_progress_photos(
    user_id: int = Query(...),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    photos = db.query(ProgressPhoto).filter(
        ProgressPhoto.user_id == user_id
    ).order_by(ProgressPhoto.date.desc()).limit(limit).all()
    return photos


@router.post("/photos", response_model=ProgressPhotoResponse)
async def upload_progress_photo(
    user_id: int = Query(...),
    category: str = Query(None),
    photo_date: date = Query(...),
    notes: str = Query(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_data = await file.read()

    # Resize if too large (max 2MB for progress photos)
    if len(image_data) > 2 * 1024 * 1024:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_data))
        img.thumbnail((1200, 1200))

        output = io.BytesIO()
        img_format = "JPEG" if file.content_type == "image/jpeg" else "PNG"
        img.save(output, format=img_format, quality=85)
        image_data = output.getvalue()

    db_photo = ProgressPhoto(
        user_id=user_id,
        photo_data=image_data,
        photo_mime=file.content_type,
        category=category,
        date=photo_date,
        notes=notes
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


@router.get("/photos/{photo_id}/image")
def get_progress_photo_image(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(ProgressPhoto).filter(ProgressPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return Response(
        content=photo.photo_data,
        media_type=photo.photo_mime
    )


@router.delete("/photos/{photo_id}")
def delete_progress_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(ProgressPhoto).filter(ProgressPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.delete(photo)
    db.commit()
    return {"message": "Progress photo deleted successfully"}
