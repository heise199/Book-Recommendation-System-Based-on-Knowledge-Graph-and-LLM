from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    preferred_categories: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class BookBase(BaseModel):
    title: str
    isbn: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    category_id: Optional[int] = None

class BookCreate(BookBase):
    pass

class InteractionBase(BaseModel):
    book_id: int
    interaction_type: str  # click, collect, cart, purchase

class SearchLogCreate(BaseModel):
    query: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None

class RatingBase(BaseModel):
    book_id: int
    rating: int
    comment: Optional[str] = None

class RatingResponse(RatingBase):
    id: int
    user_id: int
    created_at: datetime
    # Optionally include user info if needed, e.g. username
    username: Optional[str] = None

    class Config:
        from_attributes = True

class BookResponse(BookBase):
    id: int
    average_rating: float
    category_name: Optional[str] = None
    ratings: List[RatingResponse] = []
    
    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    book: BookResponse
    score: float
    reason: str
    tags: List[str] = []

class ColdStartRequest(BaseModel):
    user_id: Optional[int] = None
    categories: List[str] = []  # e.g. ["科幻", "历史"]
    moods: List[str] = []       # e.g. ["轻松", "烧脑", "治愈"]
