from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from typing import List, Optional

from app.core.database import get_db, get_neo4j_session
from app.services.recommendation import RecommendationService
from app.schemas.base import RecommendationResponse, BookResponse, ColdStartRequest, RecommendationRequest

router = APIRouter()


@router.post("/recommend/cold-start", response_model=List[RecommendationResponse])
def cold_start_recommend_books(
    request: ColdStartRequest,
    db: Session = Depends(get_db), 
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    """冷启动推荐（基于用户问卷）"""
    service = RecommendationService(db, neo4j)
    try:
        recommendations = service.get_cold_start_recommendations(
            request.categories, 
            request.moods,
            limit=10
        )
        return recommendations
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/{user_id}", response_model=List[RecommendationResponse])
def recommend_books(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="推荐数量"),
    enable_diversity: bool = Query(default=True, description="是否启用多样性控制"),
    diversity_mode: str = Query(default="quota", description="多样性模式: quota, mmr, none"),
    force_refresh: bool = Query(default=False, description="是否强制刷新缓存"),
    db: Session = Depends(get_db), 
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    """
    获取个性化推荐
    
    支持参数：
    - limit: 推荐数量 (1-50)
    - enable_diversity: 是否启用多样性控制
    - diversity_mode: 多样性模式
        - quota: 类别配额算法（默认）
        - mmr: MMR算法
        - none: 不控制多样性
    - force_refresh: 是否强制刷新缓存
    """
    service = RecommendationService(db, neo4j)
    try:
        recommendations = service.get_recommendations(
            user_id=user_id,
            limit=limit,
            enable_diversity=enable_diversity,
            diversity_mode=diversity_mode,
            force_refresh=force_refresh
        )
        return recommendations
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/{user_id}", response_model=List[RecommendationResponse])
def recommend_books_post(
    user_id: int,
    request: RecommendationRequest,
    db: Session = Depends(get_db), 
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    """
    获取个性化推荐（POST方式，支持更多参数）
    """
    service = RecommendationService(db, neo4j)
    try:
        recommendations = service.get_recommendations(
            user_id=user_id,
            limit=request.limit,
            enable_diversity=request.enable_diversity,
            diversity_mode=request.diversity_mode,
            force_refresh=False
        )
        return recommendations
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
