from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from typing import List

from app.core.database import get_db, get_neo4j_session
from app.services.recommendation import RecommendationService
from app.schemas.base import RecommendationResponse, BookResponse, ColdStartRequest

router = APIRouter()

@router.post("/recommend/cold-start", response_model=List[RecommendationResponse])
def cold_start_recommend_books(
    request: ColdStartRequest,
    db: Session = Depends(get_db), 
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    service = RecommendationService(db, neo4j)
    try:
        recommendations = service.get_cold_start_recommendations(request.categories, request.moods)
        return recommendations
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend/{user_id}", response_model=List[RecommendationResponse])
def recommend_books(
    user_id: int, 
    db: Session = Depends(get_db), 
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    service = RecommendationService(db, neo4j)
    try:
        recommendations = service.get_recommendations(user_id)
        return recommendations
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
