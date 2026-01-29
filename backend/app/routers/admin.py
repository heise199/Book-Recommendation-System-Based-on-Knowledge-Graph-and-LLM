from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db, get_neo4j_session
from app.core.deps import get_current_admin_user
from app.models.sql import User, Book, Rating, Interaction
from app.schemas.base import UserResponse, BookCreate, BookResponse
from app.services.sync_service import SyncService
from neo4j import Session as Neo4jSession

router = APIRouter()

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user_count = db.query(User).count()
    book_count = db.query(Book).count()
    interaction_count = db.query(Interaction).count()
    rating_count = db.query(Rating).count()
    
    return {
        "users": user_count,
        "books": book_count,
        "interactions": interaction_count,
        "ratings": rating_count
    }

@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/users/{user_id}/ban")
def ban_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"status": "success", "message": f"User {user.username} has been banned"}

@router.post("/users/{user_id}/unban")
def unban_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    return {"status": "success", "message": f"User {user.username} has been unbanned"}

@router.post("/books", response_model=BookResponse)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    neo4j: Neo4jSession = Depends(get_neo4j_session),
    current_user: User = Depends(get_current_admin_user)
):
    # 1. Save to MySQL
    db_book = Book(**book_in.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # 2. Sync to Neo4j
    sync = SyncService(neo4j)
    # Assuming category name is passed or fetched. For simplicity, just use ID or fetch name.
    # We might need to fetch category name if we want to sync it properly.
    # For now, let's just sync basic info.
    sync.sync_book(db_book, category_name="Unknown") 
    
    return db_book

@router.delete("/reviews/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    review = db.query(Rating).filter(Rating.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    db.delete(review)
    db.commit()
    return {"status": "success"}
