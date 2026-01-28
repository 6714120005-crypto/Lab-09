"""
Application configuration settings.
Loads environment variables with sensible defaults.
Includes security hardening configurations.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings with security-focused defaults.
    All values can be overridden via environment variables.
    """

    # ===========================================
    # Security Settings
    # ===========================================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Token expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Password requirements
    MIN_PASSWORD_LENGTH: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))

    # ===========================================
    # Database Settings
    # ===========================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./auth.db")

    # ===========================================
    # CORS Settings (Security Hardening)
    # ===========================================
    # Allowed origins - be specific in production!
    CORS_ORIGINS: list = json.loads(
        os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173","http://127.0.0.1:3000"]')
    )

    # Allow credentials (cookies, authorization headers)
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

    # Allowed HTTP methods - restrict to what you actually need
    CORS_ALLOW_METHODS: list = json.loads(
        os.getenv("CORS_ALLOW_METHODS", '["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]')
    )

    # Allowed headers
    CORS_ALLOW_HEADERS: list = json.loads(
        os.getenv("CORS_ALLOW_HEADERS", '["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"]')
    )

    # Headers exposed to the browser
    CORS_EXPOSE_HEADERS: list = json.loads(
        os.getenv("CORS_EXPOSE_HEADERS", '["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]')
    )

    # How long the browser should cache preflight results (in seconds)
    CORS_MAX_AGE: int = int(os.getenv("CORS_MAX_AGE", "600"))  # 10 minutes

    # ===========================================
    # Rate Limiting Settings (Security Hardening)
    # ===========================================
    # General rate limits
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    # Default rate limit for all endpoints
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")

    # Stricter limits for auth endpoints (prevent brute-force)
    RATE_LIMIT_LOGIN: str = os.getenv("RATE_LIMIT_LOGIN", "5/minute")
    RATE_LIMIT_REGISTER: str = os.getenv("RATE_LIMIT_REGISTER", "3/minute")
    RATE_LIMIT_REFRESH: str = os.getenv("RATE_LIMIT_REFRESH", "10/minute")
    RATE_LIMIT_PASSWORD_RESET: str = os.getenv("RATE_LIMIT_PASSWORD_RESET", "3/hour")

    # Rate limit storage backend (memory, redis, memcached)
    RATE_LIMIT_STORAGE_URL: str = os.getenv("RATE_LIMIT_STORAGE_URL", "memory://")

    # ===========================================
    # Security Headers Settings
    # ===========================================
    SECURITY_HEADERS_ENABLED: bool = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"

    # Content Security Policy
    CSP_POLICY: str = os.getenv(
        "CSP_POLICY",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'"
    )

    # ===========================================
    # Environment
    # ===========================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


settings = Settings()
