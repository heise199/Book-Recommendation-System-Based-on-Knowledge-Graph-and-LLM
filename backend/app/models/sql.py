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
    negative_feedbacks = relationship("NegativeFeedback", back_populates="user")
    recommendation_histories = relationship("RecommendationHistory", back_populates="user")
    exposure_logs = relationship("ExposureLog", back_populates="user")

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
    negative_feedbacks = relationship("NegativeFeedback", back_populates="book")
    exposure_logs = relationship("ExposureLog", back_populates="book")

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
    is_stale = Column(Boolean, default=False)  # 标记缓存是否待更新
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")


class NegativeFeedback(Base):
    """负反馈记录表"""
    __tablename__ = "negative_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False)  # not_interested, wrong_category, wrong_author, seen_before, other
    reason = Column(Text, nullable=True)  # 用户填写的具体原因（可选）
    strength = Column(Integer, default=3)  # 负反馈强度 1-3，3最强
    is_active = Column(Boolean, default=True)  # 是否有效（支持软删除）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    book = relationship("Book")


class RecommendationHistory(Base):
    """推荐历史记录表（用于滑动窗口去重）"""
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recommended_books = Column(Text, nullable=False)  # JSON数组: [book_id1, book_id2, ...]
    window_size = Column(Integer, default=50)  # 窗口大小
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")


class ExposureLog(Base):
    """曝光记录表（用于隐式负反馈）"""
    __tablename__ = "exposure_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    exposure_count = Column(Integer, default=1)  # 曝光次数
    click_count = Column(Integer, default=0)  # 点击次数
    last_exposure_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    book = relationship("Book")
