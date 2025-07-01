from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
from datetime import datetime
import re
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str