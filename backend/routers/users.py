from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import base64

from database import get_db
from models.database import User
from schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.name).all()
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": user.name,
            "created_at": user.created_at,
            "last_active": user.last_active,
            "has_profile_picture": user.profile_picture is not None
        }
        result.append(UserResponse(**user_dict))
    return result


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse(
        id=db_user.id,
        name=db_user.name,
        created_at=db_user.created_at,
        last_active=db_user.last_active,
        has_profile_picture=False
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update last active
    user.last_active = datetime.now(timezone.utc)
    db.commit()

    return UserResponse(
        id=user.id,
        name=user.name,
        created_at=user.created_at,
        last_active=user.last_active,
        has_profile_picture=user.profile_picture is not None
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name:
        user.name = user_update.name

    user.last_active = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        name=user.name,
        created_at=user.created_at,
        last_active=user.last_active,
        has_profile_picture=user.profile_picture is not None
    )


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/profile-picture")
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read and store the image
    image_data = await file.read()

    # Resize image if too large (max 500KB)
    if len(image_data) > 500 * 1024:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_data))
        img.thumbnail((400, 400))

        output = io.BytesIO()
        img_format = "JPEG" if file.content_type == "image/jpeg" else "PNG"
        img.save(output, format=img_format, quality=85)
        image_data = output.getvalue()

    user.profile_picture = image_data
    user.profile_picture_mime = file.content_type
    user.last_active = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Profile picture uploaded successfully"}


@router.get("/{user_id}/profile-picture")
def get_profile_picture(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.profile_picture:
        raise HTTPException(status_code=404, detail="No profile picture found")

    return Response(
        content=user.profile_picture,
        media_type=user.profile_picture_mime or "image/jpeg"
    )


@router.delete("/{user_id}/profile-picture")
def delete_profile_picture(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.profile_picture = None
    user.profile_picture_mime = None
    db.commit()

    return {"message": "Profile picture deleted successfully"}
