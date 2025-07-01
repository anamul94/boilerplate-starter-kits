import time
import traceback
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.logging import logger

class DebugMiddleware(BaseHTTPMiddleware):
    """
    Middleware for debugging requests and catching exceptions
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # For 404 errors, log the path to help debug routing issues
            if response.status_code == 404:
                logger.warning(
                    f"404 Not Found: {request.method} {request.url.path}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "query_params": str(request.query_params),
                        "client_ip": request.client.host if request.client else None,
                    }
                )
                
                # If it's an API route, return detailed information
                if request.url.path.startswith("/api"):
                    return JSONResponse(
                        status_code=404,
                        content={
                            "detail": "Not Found",
                            "path": request.url.path,
                            "method": request.method,
                            "message": f"The requested endpoint {request.method} {request.url.path} does not exist."
                        }
                    )
            
            return response
            
        except Exception as e:
            # Get full traceback
            error_traceback = traceback.format_exc()
            
            logger.error(
                f"Unhandled exception in request: {str(e)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else None,
                    "traceback": error_traceback
                },
                exc_info=True
            )
            
            # Return detailed error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "error": str(e),
                    "traceback": error_traceback,
                    "path": request.url.path,
                    "method": request.method
                }
            )