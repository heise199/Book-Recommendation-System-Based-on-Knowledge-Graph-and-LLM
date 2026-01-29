from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import bcrypt

# Monkey patch bcrypt for passlib compatibility (bcrypt >= 4.0.0 removed __about__)
if not hasattr(bcrypt, '__about__'):
    class About:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = About()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Ensure password is bytes and truncate to 72 bytes for bcrypt limitation
    if isinstance(plain_password, str):
        password_bytes = plain_password.encode('utf-8')
    else:
        password_bytes = plain_password
    
    # Passlib's bcrypt backend handles bytes, but the error suggests we should pass string
    # and let passlib handle truncation if we configure it, OR we handle it ourselves
    # BUT passlib might be double-checking.
    
    # Actually, the error "password cannot be longer than 72 bytes" often comes from 
    # newer bcrypt versions being strict.
    # If we pass bytes to passlib's hash/verify, it might be passing them through.
    
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Convert back to string if passlib expects string for 'verify' first argument 
    # (though it usually accepts bytes). 
    # However, if we are monkey patching, maybe we should use bcrypt directly if passlib fails.
    
    try:
        return pwd_context.verify(password_bytes, hashed_password)
    except Exception:
        # Fallback: try using bcrypt directly if passlib is acting up with the monkey patch
        try:
            if isinstance(hashed_password, str):
                hashed_bytes = hashed_password.encode('utf-8')
            else:
                hashed_bytes = hashed_password
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
             return False

def get_password_hash(password: str) -> str:
    # Ensure password is bytes and truncate to 72 bytes for bcrypt limitation
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
        
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Try using bcrypt directly to avoid passlib/bcrypt version mismatch issues completely
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
