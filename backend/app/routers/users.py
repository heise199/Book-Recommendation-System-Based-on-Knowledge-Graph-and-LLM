from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.sql import User, Interaction, Rating
from app.schemas.base import UserResponse, BookResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/me/collections", response_model=List[BookResponse])
def read_my_collections(
    skip: int = 0, 
    limit: int = 20, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Fetch interactions of type 'collect'
    interactions = db.query(Interaction).filter(
        Interaction.user_id == current_user.id,
        Interaction.interaction_type == "collect"
    ).order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()
    
    books = [i.book for i in interactions]
    return books

@router.get("/me/reviews") # Return type needs a schema for Rating with Book info
def read_my_reviews(
    skip: int = 0, 
    limit: int = 20, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ratings = db.query(Rating).filter(
        Rating.user_id == current_user.id
    ).order_by(Rating.created_at.desc()).offset(skip).limit(limit).all()
    
    return ratings
