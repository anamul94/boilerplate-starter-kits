from fastapi import Depends, HTTPException, status, Request, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.config import settings
from app.core.logging import logger
from app.db.base import get_db
from app.models.user import User, UserRole
from app.schemas.token import TokenPayload

# Use HTTPBearer for more reliable token extraction
security = HTTPBearer(auto_error=False)

async def get_token_from_header(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> str:
    """
    Extract JWT token from the Authorization header
    """
    if not credentials:
        logger.warning("Missing authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials

def get_current_user(
    request: Request,
    db: Session = Depends(get_db), 
    token: str = Depends(get_token_from_header)
) -> User:
    """
    Validate JWT token and return the current user
    """
    try:
        logger.debug(f"Validating token: {token[:10]}...")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None:
            logger.warning("Token validation failed: missing subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError) as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    
    if not user:
        logger.warning(f"User not found for token sub: {token_data.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Add user info to request state for logging
    request.state.user_id = user.id
    request.state.username = user.username
    request.state.user_role = user.role
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current admin user
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user attempted to access admin-only resource: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user

def check_roles(required_roles: List[UserRole]):
    """
    Dependency factory to check if the current user has one of the required roles
    """
    def _check_roles(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            logger.warning(
                f"User with insufficient role attempted access: {current_user.username}",
                extra={
                    "user_role": current_user.role,
                    "required_roles": required_roles
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required roles: {required_roles}"
            )
        return current_user
    
    return _check_roles