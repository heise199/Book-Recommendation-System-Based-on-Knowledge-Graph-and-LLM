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


# ==================== 负反馈相关 ====================

class NegativeFeedbackCreate(BaseModel):
    """创建负反馈请求"""
    book_id: int
    feedback_type: str  # not_interested, wrong_category, wrong_author, seen_before, other
    reason: Optional[str] = None  # 用户填写的具体原因
    strength: int = 3  # 负反馈强度 1-3

class NegativeFeedbackResponse(BaseModel):
    """负反馈响应"""
    id: int
    user_id: int
    book_id: int
    feedback_type: str
    reason: Optional[str] = None
    strength: int
    is_active: bool
    created_at: datetime
    book_title: Optional[str] = None  # 书籍标题（方便前端显示）
    
    class Config:
        from_attributes = True

class NegativeFeedbackTypeEnum:
    """负反馈类型枚举"""
    NOT_INTERESTED = "not_interested"  # 不感兴趣
    WRONG_CATEGORY = "wrong_category"  # 不喜欢这个类别
    WRONG_AUTHOR = "wrong_author"      # 不喜欢这个作者
    SEEN_BEFORE = "seen_before"        # 看过了/不想看
    LOW_QUALITY = "low_quality"        # 质量不好
    OTHER = "other"                    # 其他原因


# ==================== 推荐请求相关 ====================

class RecommendationRequest(BaseModel):
    """推荐请求（支持多样性参数）"""
    limit: int = 10
    enable_diversity: bool = True  # 是否启用多样性控制
    diversity_mode: str = "quota"  # quota: 类别配额, mmr: MMR算法, none: 不控制
    mmr_lambda: float = 0.5       # MMR算法的λ参数（相关性和多样性的平衡）
    exclude_seen: bool = True     # 是否排除已看过的书籍
    include_explore: bool = True  # 是否包含探索类别


# ==================== 曝光记录相关 ====================

class ExposureLogCreate(BaseModel):
    """记录曝光"""
    book_ids: List[int]  # 曝光的书籍ID列表

class ExposureLogResponse(BaseModel):
    """曝光记录响应"""
    id: int
    user_id: int
    book_id: int
    exposure_count: int
    click_count: int
    last_exposure_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 缓存失效事件相关 ====================

class CacheInvalidationEvent(BaseModel):
    """缓存失效事件"""
    user_id: int
    event_type: str  # rating, collect, click, search
    book_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    priority: int = 1  # 优先级 1-3，3最高


# ==================== 多样性分析相关 ====================

class CategoryDistribution(BaseModel):
    """类别分布"""
    category_name: str
    count: int
    ratio: float

class UserInterestProfile(BaseModel):
    """用户兴趣画像"""
    user_id: int
    primary_categories: List[str] = []    # 主类别（40%）
    secondary_categories: List[str] = []  # 次类别（30%）
    explore_categories: List[str] = []    # 探索类别（20%）
    category_distribution: List[CategoryDistribution] = []
    total_interactions: int = 0
