from datetime import datetime, timedelta, timezone
from typing import Any, Union, Dict
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.logging import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None, extra_data: Dict = None) -> str:
    """
    Create a JWT access token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    to_encode = {"exp": expire, "sub": str(subject), "iat": datetime.now(timezone.utc)}
    
    # Add any extra data to the token
    if extra_data:
        to_encode.update(extra_data)
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(f"Created token for subject {subject} with expiry {expire}")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return its payload
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Verified token with subject {payload.get('sub')}")
        return payload
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise e

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)