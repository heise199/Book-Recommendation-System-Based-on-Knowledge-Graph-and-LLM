from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db, get_neo4j_session
from app.core.deps import get_current_active_user
from app.models.sql import Book, User, Interaction, Rating, SearchLog, Category
from app.schemas.base import BookResponse, InteractionBase, RatingBase, SearchLogCreate
from app.services.sync_service import SyncService
from neo4j import Session as Neo4jSession

router = APIRouter()

@router.get("/books", response_model=List[BookResponse])
def get_books(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    # Manual map for category_name if needed, or use ORM joinedload
    for b in books:
        if b.category:
            b.category_name = b.category.name
    return books

@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.category:
        book.category_name = book.category.name
    
    # Process ratings to include username
    # This assumes lazy loading works for book.ratings and r.user
    # To optimize, we could use joinedload options in the query
    processed_ratings = []
    for r in book.ratings:
        r_dict = r.__dict__.copy()
        if r.user:
            r_dict['username'] = r.user.username
        processed_ratings.append(r_dict)
    
    # We can assign this list to the Pydantic model's ratings field
    # However, since BookResponse expects object attributes (from_attributes=True),
    # we might need to be careful. 
    # Actually, SQLAlchemy objects are compatible if the structure matches.
    # But `username` is not on the Rating model, it's on Rating.user.
    # So we should probably dynamically attach it or return a dict.
    
    # Let's attach username to the rating objects temporarily for Pydantic serialization
    for r in book.ratings:
        r.username = r.user.username if r.user else "Unknown"
        
    return book

@router.post("/search", response_model=List[BookResponse])
def search_books(
    search: SearchLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    # 1. Log the search
    log = SearchLog(user_id=current_user.id, query=search.query)
    db.add(log)
    db.commit()
    
    # 1.5 Sync search to Neo4j
    try:
        sync = SyncService(neo4j)
        sync.sync_search(current_user.id, search.query)
    except Exception as e:
        print(f"Failed to sync search to Neo4j: {e}")

    # 2. Perform Search (Simple LIKE for now)
    # In a real system, this might use ElasticSearch or FullText search
    query_str = f"%{search.query}%"

    q = db.query(Book)

    # Fuzzy match on title (primary) and author (secondary)
    q = q.filter(
        (Book.title.like(query_str)) |
        (Book.author.like(query_str))
    )

    # Optional category filter
    if search.category_id is not None:
        q = q.filter(Book.category_id == search.category_id)
    elif search.category_name:
        q = q.join(Category).filter(Category.name == search.category_name)

    books = q.limit(20).all()
    
    for b in books:
        if b.category:
            b.category_name = b.category.name
            
    return books

@router.post("/interactions")
def create_interaction(
    interaction: InteractionBase, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    # 1. Save to MySQL
    db_interaction = Interaction(
        user_id=current_user.id,
        book_id=interaction.book_id,
        interaction_type=interaction.interaction_type
    )
    db.add(db_interaction)
    db.commit()
    
    # 2. Sync to Neo4j
    sync = SyncService(neo4j)
    sync.sync_interaction(current_user.id, interaction.book_id, interaction.interaction_type)
    
    return {"status": "success"}

@router.post("/books/{book_id}/rate")
def create_review(
    book_id: int,
    rating: RatingBase,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    if rating.book_id != book_id:
        raise HTTPException(status_code=400, detail="Book ID mismatch")
        
    # Check if book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Save Rating
    db_rating = Rating(
        user_id=current_user.id,
        book_id=book_id,
        rating=rating.rating,
        comment=rating.comment
    )
    db.add(db_rating)
    db.flush() # Ensure ID is generated and it's visible for query
    
    # Update Book Average Rating
    # Re-calculate average from all ratings
    existing_ratings = db.query(Rating).filter(Rating.book_id == book_id).all()
    if existing_ratings:
        count = len(existing_ratings)
        total = sum([r.rating for r in existing_ratings])
        book.average_rating = total / count
        db.add(book) 
    
    db.commit()
    
    # Sync to Neo4j
    sync = SyncService(neo4j)
    sync.sync_rating(current_user.id, book_id, rating.rating)
    
    return {"status": "success"}
