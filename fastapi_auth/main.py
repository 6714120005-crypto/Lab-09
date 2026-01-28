"""
FastAPI Authentication Server
Main application entry point with comprehensive security hardening.

Security Features:
- CORS configuration with strict origin control
- Rate limiting with IP blocking
- Security headers (XSS, Clickjacking, MIME sniffing protection)
- Secure cookie settings
- Request validation
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import init_db
from routes import auth, users
from middleware import SecurityHeadersMiddleware, RateLimitMiddleware


# Initialize rate limiter (slowapi - for decorator-based limiting)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database tables on startup.
    """
    # Startup
    print("=" * 60)
    print("🚀 Starting FastAPI Authentication Server...")
    print("=" * 60)
    await init_db()
    print("✅ Database initialized")
    print(f"🔒 Security Headers: {'Enabled' if settings.SECURITY_HEADERS_ENABLED else 'Disabled'}")
    print(f"⏱️  Rate Limiting: {'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    print(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")
    print(f"🔑 Environment: {settings.ENVIRONMENT}")
    print("-" * 60)
    print(f"📝 API Docs: http://localhost:8000/docs")
    print(f"🎨 Frontend: http://localhost:3000 (run separately)")
    print("=" * 60)
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="FastAPI Authentication API",
    description="""
    A secure authentication API with JWT tokens, built with security best practices.

    ## Features
    - **User Registration** with password strength validation
    - **JWT Authentication** with access and refresh tokens
    - **Rate Limiting** to prevent brute-force attacks
    - **Password Hashing** using bcrypt (12 rounds)
    - **CORS** with strict origin control
    - **Security Headers** (XSS, Clickjacking, MIME protection)

    ## Security Hardening
    - Bcrypt password hashing with automatic salting
    - Short-lived access tokens (15 minutes)
    - Long-lived refresh tokens (7 days) stored in database
    - Token revocation for logout
    - Per-endpoint rate limiting with IP blocking
    - Comprehensive security headers
    - HTTPS enforcement (in production)

    ## Rate Limits
    - Login: 5 requests/minute
    - Register: 3 requests/minute
    - Token Refresh: 10 requests/minute
    - Other endpoints: 100 requests/minute
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ===========================================
# Middleware Stack (order matters!)
# ===========================================

# 1. Security Headers Middleware (first - adds headers to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Custom Rate Limiting Middleware (second - blocks before processing)
app.add_middleware(RateLimitMiddleware)

# 3. CORS Middleware (handles preflight requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS,
    max_age=settings.CORS_MAX_AGE,
)

# Add slowapi rate limiter to app state (for decorator-based limiting)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ===========================================
# Request Validation Middleware
# ===========================================

@app.middleware("http")
async def validate_content_type(request: Request, call_next):
    """
    Validate Content-Type header for POST/PUT/PATCH requests.
    Prevents content-type confusion attacks.
    """
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        # Allow JSON and form data
        allowed_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        if content_type and not any(ct in content_type for ct in allowed_types):
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={
                    "error": "Unsupported Media Type",
                    "detail": f"Content-Type must be one of: {', '.join(allowed_types)}",
                },
            )

    response = await call_next(request)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests for security monitoring.
    In production, send to centralized logging.
    """
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Get client IP
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0] if forwarded else (
        request.client.host if request.client else "unknown"
    )

    # Log format
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "ip": client_ip,
        "duration_ms": round(process_time * 1000, 2),
    }

    # In debug mode, print to console
    if settings.DEBUG:
        status_emoji = "✅" if response.status_code < 400 else "❌"
        print(f"{status_emoji} {log_data['method']} {log_data['path']} - {log_data['status']} ({log_data['duration_ms']}ms) [{client_ip}]")

    return response


# ===========================================
# Include Routers
# ===========================================

app.include_router(auth.router)
app.include_router(users.router)


# ===========================================
# Health & Info Endpoints
# ===========================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check endpoint",
)
async def health_check():
    """
    Check if the API is running and healthy.
    """
    return {
        "status": "healthy",
        "message": "FastAPI Authentication Server is running",
        "security": {
            "headers": settings.SECURITY_HEADERS_ENABLED,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "cors_enabled": True,
        },
    }


@app.get(
    "/",
    tags=["Root"],
    summary="API information",
)
async def root():
    """
    Get basic API information and available endpoints.
    """
    return {
        "name": "FastAPI Authentication API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "redoc": "/redoc" if settings.DEBUG else "Disabled in production",
        "health": "/health",
        "security": "/security-info",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "refresh": "POST /auth/refresh",
                "logout": "POST /auth/logout",
                "logout_all": "POST /auth/logout-all",
            },
            "users": {
                "me": "GET /users/me",
                "update": "PATCH /users/me",
                "deactivate": "DELETE /users/me",
            },
        },
    }


@app.get(
    "/security-info",
    tags=["Security"],
    summary="Security configuration info",
)
async def security_info():
    """
    Get current security configuration (public info only).
    Useful for debugging and security audits.
    """
    return {
        "cors": {
            "allowed_origins": settings.CORS_ORIGINS,
            "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
            "allowed_methods": settings.CORS_ALLOW_METHODS,
            "max_age_seconds": settings.CORS_MAX_AGE,
        },
        "rate_limiting": {
            "enabled": settings.RATE_LIMIT_ENABLED,
            "login_limit": settings.RATE_LIMIT_LOGIN,
            "register_limit": settings.RATE_LIMIT_REGISTER,
            "default_limit": settings.RATE_LIMIT_DEFAULT,
        },
        "security_headers": {
            "enabled": settings.SECURITY_HEADERS_ENABLED,
            "headers": [
                "X-XSS-Protection",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "Referrer-Policy",
                "Content-Security-Policy",
                "Permissions-Policy",
            ] if settings.SECURITY_HEADERS_ENABLED else [],
        },
        "authentication": {
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
            "bcrypt_rounds": settings.BCRYPT_ROUNDS,
        },
    }


# ===========================================
# Global Exception Handler
# ===========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions gracefully.
    In production, log the error and return a generic message.
    """
    # In development, show more details
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )

    # In production, don't leak internal details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# ===========================================
# Main Entry Point
# ===========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Enable auto-reload in development
    )
