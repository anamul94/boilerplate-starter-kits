from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List, Tuple
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.logging import logger

class UserServiceError(Exception):
    """Base exception for user service errors"""
    pass

def get_user(db: Session, user_id: int) -> Optional[User]:
    try:
        return db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching user by ID {user_id}: {str(e)}")
        raise UserServiceError(f"Error retrieving user: {str(e)}")

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching user by email {email}: {str(e)}")
        raise UserServiceError(f"Error retrieving user by email: {str(e)}")

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    try:
        return db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching user by username {username}: {str(e)}")
        raise UserServiceError(f"Error retrieving user by username: {str(e)}")

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching users list: {str(e)}")
        raise UserServiceError(f"Error retrieving users: {str(e)}")

def create_user(db: Session, user_in: UserCreate) -> User:
    try:
        # Check if user already exists
        if get_user_by_email(db, user_in.email):
            logger.warning(f"Attempted to create user with existing email: {user_in.email}")
            raise UserServiceError("User with this email already exists")
        
        # if get_user_by_username(db, user_in.username):
        #     logger.warning(f"Attempted to create user with existing username: {user_in.username}")
        #     raise UserServiceError("User with this username already exists")
            
        # Create new user
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
            role=user_in.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"New user created: {user_in.username} with role {user_in.role}")
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error when creating user {user_in.username}: {str(e)}")
        raise UserServiceError(f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error when creating user {user_in.username}: {str(e)}")
        raise UserServiceError(f"Error creating user: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when creating user {user_in.username}: {str(e)}")
        raise UserServiceError(f"Unexpected error: {str(e)}")

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    try:
        update_data = user_in.dict(exclude_unset=True)
        
        # Check email uniqueness if being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = get_user_by_email(db, update_data["email"])
            if existing_user:
                logger.warning(f"Attempted to update user with existing email: {update_data['email']}")
                raise UserServiceError("Email already registered")
                
        # Check username uniqueness if being updated
        if "username" in update_data and update_data["username"] != user.username:
            existing_user = get_user_by_username(db, update_data["username"])
            if existing_user:
                logger.warning(f"Attempted to update user with existing username: {update_data['username']}")
                raise UserServiceError("Username already registered")
        
        # Handle password hashing
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Update user attributes
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User updated: {user.username}")
        return user
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error when updating user {user.username}: {str(e)}")
        raise UserServiceError(f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error when updating user {user.username}: {str(e)}")
        raise UserServiceError(f"Error updating user: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when updating user {user.username}: {str(e)}")
        raise UserServiceError(f"Unexpected error: {str(e)}")

def authenticate_user(db: Session, username: str, password: str) -> Tuple[Optional[User], bool]:
    try:
        user = get_user_by_email(db, username)
        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None, False
            
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for user - {username}")
            return None, False
            
        if not user.is_active:
            logger.warning(f"Authentication failed: inactive user - {username}")
            return None, False
            
        logger.info(f"User authenticated successfully: {username}")
        return user, True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during authentication for {username}: {str(e)}")
        raise UserServiceError(f"Authentication error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during authentication for {username}: {str(e)}")
        raise UserServiceError(f"Unexpected authentication error: {str(e)}")

def create_admin_user(db: Session, email: str, username: str, password: str) -> User:
    """
    Create an admin user
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, email)
        if existing_user:
            # If user exists but is not admin, upgrade to admin
            if existing_user.role != UserRole.ADMIN:
                existing_user.role = UserRole.ADMIN
                db.add(existing_user)
                db.commit()
                db.refresh(existing_user)
                logger.info(f"User {username} upgraded to admin role")
                return existing_user
            return existing_user
            
        # Create new admin user
        db_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            role=UserRole.ADMIN
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"New admin user created: {username}")
        return db_user
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error when creating admin user: {str(e)}")
        raise UserServiceError(f"Error creating admin user: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when creating admin user: {str(e)}")
        raise UserServiceError(f"Unexpected error: {str(e)}")