from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import SQLAlchemyError
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import traceback

from app.api.api import api_router
from app.core.config import settings
from app.core.logging import logger
from app.utils.logging_middleware import RequestLoggingMiddleware
from app.utils.debug_middleware import DebugMiddleware
from app.db.base import Base, engine

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except SQLAlchemyError as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Database connection established")
    route_paths = [{"path": route.path, "methods": route.methods if hasattr(route, "methods") else None} for route in app.routes]
    logger.info(f"Available routes: {route_paths}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="API documentation with JWT Bearer auth support",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # OPTIONAL: Apply BearerAuth globally to all endpoints
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)
app.openapi = custom_openapi
# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Set CORS with environment-specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add debug middleware (should be first to catch all exceptions)
app.add_middleware(DebugMiddleware)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    error_detail = exc.errors()
    error_messages = []
    
    for error in error_detail:
        field = error.get("loc", [])[-1] if error.get("loc") else "field"
        msg = error.get("msg", "Invalid input")
        error_messages.append(f"{field}: {msg}")
    
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "validation_errors": len(error_messages)
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "messages": error_messages
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors
    """
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    
    logger.error(
        f"Database error: {error_msg}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "stack_trace": stack_trace
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error": error_msg,
            "stack_trace": stack_trace if app.debug else None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors
    """
    error_msg = str(exc)
    stack_trace = traceback.format_exc()
    
    logger.error(
        f"Unexpected error: {error_msg}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "stack_trace": stack_trace
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": error_msg,
            "stack_trace": stack_trace if app.debug else None
        }
    )

# Add a route to see all available routes for debugging
@app.get("/api/debug/routes", include_in_schema=False)
async def get_routes():
    """
    Get all available routes for debugging
    """
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": route.methods if hasattr(route, "methods") else None
        })
    return {"routes": routes}

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to FastAPI Todo API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

