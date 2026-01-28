# FastAPI Authentication Prototype

A secure authentication API with JWT tokens, built with security best practices.

## Features

- ✅ User registration with password strength validation
- ✅ JWT authentication (access + refresh tokens)
- ✅ Password hashing with bcrypt
- ✅ Rate limiting on auth endpoints
- ✅ CORS configuration
- ✅ SQLite database with async SQLAlchemy
- ✅ Token revocation for logout
- ✅ Automatic API documentation

## Quick Start

### 1. Install Dependencies

```bash
cd fastapi_auth
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and customize:

```bash
cp .env.example .env
```

**Important**: Change `SECRET_KEY` in production! Generate one with:
```bash
openssl rand -hex 32
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Get new access token |
| POST | `/auth/logout` | Invalidate refresh token |
| POST | `/auth/logout-all` | Logout from all devices |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| PATCH | `/users/me` | Update profile |
| DELETE | `/users/me` | Deactivate account |

## Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Access Protected Route

```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Access Token

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## Security Best Practices Implemented

1. **Password Hashing**: Uses bcrypt with automatic salting
2. **JWT Tokens**: Short-lived access tokens (15 min), longer refresh tokens (7 days)
3. **Token Rotation**: Refresh tokens stored in DB for revocation
4. **Rate Limiting**: Prevents brute-force attacks
5. **Input Validation**: Pydantic schemas validate all inputs
6. **Password Requirements**: Minimum 8 chars, uppercase, lowercase, digit, special char
7. **CORS**: Configurable allowed origins
8. **Async Database**: Non-blocking I/O with aiosqlite

## Project Structure

```
fastapi_auth/
├── main.py           # FastAPI app, middleware, routes
├── auth.py           # JWT utilities, password hashing
├── config.py         # Application settings
├── database.py       # Database connection
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── routes/
│   ├── __init__.py
│   ├── auth.py       # Auth endpoints
│   └── users.py      # User endpoints
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev-secret | JWT signing key (CHANGE IN PRODUCTION) |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15 | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token lifetime |
| `DATABASE_URL` | sqlite+aiosqlite:///./auth.db | Database connection |
| `CORS_ORIGINS` | ["http://localhost:3000"] | Allowed CORS origins |
| `RATE_LIMIT_PER_MINUTE` | 5 | Auth endpoint rate limit |

## License

MIT
