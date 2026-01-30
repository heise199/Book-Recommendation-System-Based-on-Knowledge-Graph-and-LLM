"""
统一配置管理模块
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # MySQL Configuration
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = "book_rec_sys"
    
    # Neo4j Configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "mfl,.031104"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Cache Configuration
    CACHE_L1_TTL: int = 300  # 5 minutes for L1 (Redis)
    CACHE_L2_TTL: int = 3600  # 1 hour for L2 (MySQL)
    CACHE_L3_TTL: int = 86400  # 24 hours for L3
    
    # Recommendation Configuration
    RECOMMENDATION_LIMIT: int = 10
    CLICK_INVALIDATION_THRESHOLD: int = 3  # Invalidate cache after 3 clicks
    
    # Negative Feedback Configuration
    IMPLICIT_NEGATIVE_EXPOSURE_THRESHOLD: int = 10  # Add to blacklist after 10 exposures without click
    SOFT_PENALTY_FACTOR: float = 0.1  # Score penalty per exposure
    
    # Diversity Configuration
    DIVERSITY_PRIMARY_RATIO: float = 0.4
    DIVERSITY_SECONDARY_RATIO: float = 0.3
    DIVERSITY_EXPLORE_RATIO: float = 0.2
    DIVERSITY_POPULAR_RATIO: float = 0.1
    MMR_LAMBDA: float = 0.5  # Balance between relevance and diversity
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
