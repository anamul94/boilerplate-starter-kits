from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user import create_user, get_user_by_email, get_user_by_username, get_user, update_user, get_users, UserServiceError
from app.core.logging import logger

router = APIRouter()

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create new user
    """
    try:
        user = create_user(db, user_in)
        logger.info(
            f"New user registered",
            extra={
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return user
    except UserServiceError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/me", response_model=UserSchema)
def read_user_me(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user
    """
    logger.info(
        f"User retrieved own profile",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "client_ip": request.client.host if request.client else None,
        }
    )
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update own user
    """
    try:
        # Prevent regular users from changing their role
        if user_in.role is not None and current_user.role != UserRole.ADMIN:
            user_in.role = current_user.role
            logger.warning(
                f"User attempted to change their role",
                extra={
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            
        user = update_user(db, current_user, user_in)
        logger.info(
            f"User updated own profile",
            extra={
                "user_id": user.id,
                "username": user.username,
                "client_ip": request.client.host if request.client else None,
                "fields_updated": list(user_in.dict(exclude_unset=True).keys()),
            }
        )
        return user
    except UserServiceError as e:
        if "already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user",
        )
    except Exception as e:
        logger.error(f"Unexpected error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/all", response_model=List[UserSchema])
def read_all_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Only admins can access this endpoint
):
    """
    Get all users (admin only)
    """
    try:
        users = get_users(db, skip=skip, limit=limit)
        logger.info(
            f"Admin retrieved all users",
            extra={
                "admin_id": current_user.id,
                "admin_username": current_user.username,
                "user_count": len(users),
                "client_ip": request.client.host if request.client else None,
            }
        )
        return users
    except Exception as e:
        logger.error(f"Error retrieving all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users",
        )