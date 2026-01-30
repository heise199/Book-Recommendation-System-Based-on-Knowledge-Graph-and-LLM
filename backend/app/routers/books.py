from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db, get_neo4j_session
from app.core.deps import get_current_active_user
from app.models.sql import Book, User, Interaction, Rating, SearchLog, Category, NegativeFeedback
from app.schemas.base import (
    BookResponse, InteractionBase, RatingBase, SearchLogCreate,
    NegativeFeedbackCreate, NegativeFeedbackResponse
)
from app.services.sync_service import SyncService
from app.services.event_service import event_service, EventType
from app.services.cache_service import CacheService
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
    
    # 1.6 触发缓存失效事件（搜索行为，部分失效）
    event_service.publish_cache_invalidation(
        user_id=current_user.id,
        event_type=EventType.SEARCH,
        priority=1,  # 普通优先级
        extra_data={"query": search.query}
    )

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
    
    # 3. 触发缓存失效事件
    event_type = EventType.CLICK if interaction.interaction_type == "click" else EventType.COLLECT
    priority = 3 if interaction.interaction_type == "collect" else 1  # 收藏行为高优先级
    event_service.publish_cache_invalidation(
        user_id=current_user.id,
        event_type=event_type,
        book_id=interaction.book_id,
        priority=priority
    )
    
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
    
    # 触发缓存失效事件（评分是高价值行为，立即失效）
    event_service.publish_cache_invalidation(
        user_id=current_user.id,
        event_type=EventType.RATING,
        book_id=book_id,
        priority=3  # 高优先级
    )
    
    return {"status": "success"}


# ==================== 负反馈API ====================

@router.post("/books/{book_id}/negative-feedback", response_model=NegativeFeedbackResponse)
def create_negative_feedback(
    book_id: int,
    feedback: NegativeFeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    """
    提交负反馈（不感兴趣）
    """
    if feedback.book_id != book_id:
        raise HTTPException(status_code=400, detail="Book ID mismatch")
    
    # 检查书籍是否存在
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 检查是否已存在负反馈
    existing = db.query(NegativeFeedback).filter(
        NegativeFeedback.user_id == current_user.id,
        NegativeFeedback.book_id == book_id,
        NegativeFeedback.is_active == True
    ).first()
    
    if existing:
        # 更新现有负反馈
        existing.feedback_type = feedback.feedback_type
        existing.reason = feedback.reason
        existing.strength = feedback.strength
        db_feedback = existing
    else:
        # 创建新负反馈
        db_feedback = NegativeFeedback(
            user_id=current_user.id,
            book_id=book_id,
            feedback_type=feedback.feedback_type,
            reason=feedback.reason,
            strength=feedback.strength
        )
        db.add(db_feedback)
    
    db.commit()
    db.refresh(db_feedback)
    
    # 同步到Neo4j（创建负关系）
    try:
        sync = SyncService(neo4j)
        sync.sync_negative_feedback(
            current_user.id, 
            book_id, 
            feedback.feedback_type,
            book.category.name if book.category else None,
            book.author
        )
    except Exception as e:
        print(f"Failed to sync negative feedback to Neo4j: {e}")
    
    # 触发缓存失效事件
    event_service.publish_cache_invalidation(
        user_id=current_user.id,
        event_type=EventType.NEGATIVE_FEEDBACK,
        book_id=book_id,
        priority=3  # 高优先级
    )
    
    # 添加书籍标题到响应
    db_feedback.book_title = book.title
    
    return db_feedback


@router.get("/users/me/negative-feedback", response_model=List[NegativeFeedbackResponse])
def get_my_negative_feedback(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的负反馈列表
    """
    feedbacks = db.query(NegativeFeedback).filter(
        NegativeFeedback.user_id == current_user.id,
        NegativeFeedback.is_active == True
    ).offset(skip).limit(limit).all()
    
    # 添加书籍标题
    for f in feedbacks:
        if f.book:
            f.book_title = f.book.title
    
    return feedbacks


@router.delete("/books/{book_id}/negative-feedback")
def delete_negative_feedback(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除负反馈（软删除）
    """
    feedback = db.query(NegativeFeedback).filter(
        NegativeFeedback.user_id == current_user.id,
        NegativeFeedback.book_id == book_id,
        NegativeFeedback.is_active == True
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Negative feedback not found")
    
    # 软删除
    feedback.is_active = False
    db.commit()
    
    # 触发缓存失效（因为可能需要重新推荐这本书）
    event_service.publish_cache_invalidation(
        user_id=current_user.id,
        event_type=EventType.NEGATIVE_FEEDBACK,
        book_id=book_id,
        priority=2
    )
    
    return {"status": "success", "message": "Negative feedback removed"}
