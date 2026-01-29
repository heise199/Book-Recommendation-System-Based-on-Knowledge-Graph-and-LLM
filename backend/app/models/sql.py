from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # New Demographics
    gender = Column(String(10)) # Male, Female, Other
    age = Column(Integer)
    preferred_categories = Column(Text) # Comma separated string: "科幻,历史"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ratings = relationship("Rating", back_populates="user")
    interactions = relationship("Interaction", back_populates="user")
    search_logs = relationship("SearchLog", back_populates="user")

class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="search_logs")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), unique=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    author = Column(String(255), index=True)
    publisher = Column(String(255))
    publication_year = Column(Integer)
    description = Column(Text)
    cover_url = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    average_rating = Column(Float, default=0.0)
    
    # Relationships
    category = relationship("Category", back_populates="books")
    ratings = relationship("Rating", back_populates="book")
    interactions = relationship("Interaction", back_populates="book")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    books = relationship("Book", back_populates="category")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    interaction_type = Column(String(20), nullable=False)  # click, collect, cart, purchase
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="interactions")
    book = relationship("Book", back_populates="interactions")

class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendations = Column(Text, nullable=False) # JSON string of recommendations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
