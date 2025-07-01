from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
import os

from app.api.deps import get_db
from app.core.config import settings
from app.core.logging import logger
from app.core.security import create_access_token
from app.core.rate_limiter import rate_limit_auth
from app.services.user import authenticate_user, UserServiceError, get_user_by_email, create_user
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.models.user import UserRole

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    },
)

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_auth)
):
    """
    JWT token login, get an access token for future requests
    """
    try:
        user, is_authenticated = authenticate_user(db, form_data.username, form_data.password)
        
        if not user or not is_authenticated:
            logger.warning(
                f"Failed login attempt",
                extra={
                    "username": form_data.username,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Include user role in the token
        extra_data = {"role": user.role}
        token = create_access_token(
            user.id, 
            expires_delta=access_token_expires,
            extra_data=extra_data
        )
        
        logger.info(
            f"User successfully logged in",
            extra={
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
        }
        
    except UserServiceError as e:
        logger.error(f"Authentication service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
        
        
@router.get("/google-login")
async def google_login(request: Request, _: None = Depends(rate_limit_auth)):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri, prompt='select_account')

@router.get('/auth/google/callback')
async def auth_google_callback(request: Request, db: Session = Depends(get_db), _: None = Depends(rate_limit_auth)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            user_info = await oauth.google.parse_id_token(request, token)
        
        email = user_info.get('email')
        name = user_info.get('name', '')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists
        user = get_user_by_email(db, email)
        
        if not user:
            # Create new user
            user_create = UserCreate(
                email=email,
                username=name or email.split('@')[0],
                password="google_oauth",  # Placeholder password
                role=UserRole.USER
            )
            user = create_user(db, user_create)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        extra_data = {"role": user.role}
        access_token = create_access_token(
            user.id,
            expires_delta=access_token_expires,
            extra_data=extra_data
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }
        
    except OAuthError as e:
        logger.error(f"OAuth error: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")