from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db, get_neo4j_session
from app.core.security import create_access_token, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.sql import User
from app.schemas.base import Token, UserCreate, UserResponse
from app.services.sync_service import SyncService
from neo4j import Session as Neo4jSession

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate, 
    db: Session = Depends(get_db),
    neo4j: Neo4jSession = Depends(get_neo4j_session)
):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            gender=user.gender,
            age=user.age,
            preferred_categories=user.preferred_categories
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Sync User to Neo4j
        try:
            sync = SyncService(neo4j)
            sync.sync_user(new_user)
        except Exception as e:
            print(f"Failed to sync user to Neo4j: {e}")
            # Optional: Decide if we should rollback MySQL transaction or just log error
            # For now, we log but keep the user created in MySQL
            
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # Passlib verify might fail with "password too long" if not handled, 
        # but our custom verify_password in security.py handles it.
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
