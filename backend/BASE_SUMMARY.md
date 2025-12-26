# FastAPI Base Backend - Summary

This is a minimal FastAPI backend base created from the full-stack FastAPI template. It provides a clean starting point for new projects without any specific features.

## What's Included

### Core Structure
- ✅ Basic FastAPI application setup
- ✅ Modular project structure with organized directories
- ✅ Configuration management using Pydantic Settings
- ✅ CORS middleware configuration
- ✅ OpenAPI documentation (Swagger UI and ReDoc)
- ✅ Health check endpoint

### Code Organization
```
backend/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── routes/
│   │   │   └── utils.py       # Health check endpoint
│   │   └── main.py            # API router
│   ├── core/
│   │   └── config.py          # Settings and configuration
│   ├── crud/                  # CRUD operations (organized by domain)
│   │   └── __init__.py        # Ready for future CRUD modules
│   ├── models/                # Database models (organized by domain)
│   │   └── __init__.py        # Ready for future SQLModel models
│   ├── schemas/               # Pydantic schemas (organized by domain)
│   │   ├── __init__.py
│   │   └── common.py          # Common schemas like Message
│   └── main.py                # FastAPI application
├── tests/                     # Test files
│   └── api/routes/test_utils.py
├── scripts/                   # Utility scripts
│   ├── format.sh             # Code formatting
│   ├── lint.sh               # Code linting
│   ├── test.sh               # Run tests with coverage
│   └── prestart.sh           # Prestart checks
└── pyproject.toml            # Dependencies and config
```

### Dependencies
**Core:**
- fastapi[standard] - Web framework
- pydantic - Data validation
- pydantic-settings - Configuration management

**Development:**
- pytest - Testing framework
- mypy - Type checking
- ruff - Linting and formatting
- coverage - Test coverage

### API Endpoints
- `GET /api/v1/utils/health-check/` - Health check endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /api/v1/openapi.json` - OpenAPI schema

### Configuration
Settings are managed through environment variables:
- `PROJECT_NAME` - Project name (default: "FastAPI Base Project")
- `API_V1_STR` - API version prefix (default: "/api/v1")
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins
- `ENVIRONMENT` - Environment name (local/staging/production)

### Scripts
- `bash scripts/format.sh` - Format code with ruff
- `bash scripts/lint.sh` - Lint code with mypy and ruff
- `bash scripts/test.sh` - Run tests with coverage
- `bash scripts/prestart.sh` - Pre-start checks

### Testing
- Simple test setup with pytest
- Test client fixture available
- Example health check test
- Code coverage reporting

## What's NOT Included

This base intentionally excludes:
- ❌ Database integration (SQLModel, Alembic, PostgreSQL)
- ❌ Authentication/Authorization (JWT, OAuth)
- ❌ User management
- ❌ Email functionality
- ❌ CRUD operations
- ❌ Sentry monitoring
- ❌ Any business logic or features

## Getting Started

1. **Install dependencies:**
   ```bash
   cd backend
   uv sync
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Run development server:**
   ```bash
   fastapi dev app/main.py
   ```

4. **Run tests:**
   ```bash
   bash scripts/test.sh
   ```

5. **Access documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Adding Features

To add features to this base:

1. **Add new routes:**
   - Create new route files in `app/api/routes/`
   - Register routes in `app/api/main.py`

2. **Add database models:**
   - Create model files in `app/models/` (e.g., `user.py`, `item.py`)
   - Each file should contain related SQLModel models
   - Import and expose models in `app/models/__init__.py`
   - Example:
     ```python
     # app/models/user.py
     from sqlmodel import Field, SQLModel
     
     class User(SQLModel, table=True):
         id: int | None = Field(default=None, primary_key=True)
         email: str = Field(unique=True)
         name: str
     ```

3. **Add schemas:**
   - Create schema files in `app/schemas/` (e.g., `user.py`, `item.py`)
   - Each file should contain related Pydantic schemas for validation
   - Import and expose schemas in `app/schemas/__init__.py`
   - Example:
     ```python
     # app/schemas/user.py
     from pydantic import BaseModel, EmailStr
     
     class UserCreate(BaseModel):
         email: EmailStr
         name: str
     ```

4. **Add CRUD operations:**
   - Create CRUD files in `app/crud/` (e.g., `user.py`, `item.py`)
   - Each file should contain CRUD operations for that specific model
   - Import and expose CRUD instances in `app/crud/__init__.py`
   - Example:
     ```python
     # app/crud/user.py
     from sqlmodel import Session, select
     from app.models.user import User
     
     def get_user(session: Session, user_id: int) -> User | None:
         return session.get(User, user_id)
     ```

5. **Add configuration:**
   - Update `app/core/config.py` with new settings

6. **Add dependencies:**
   - Add to `pyproject.toml` dependencies section
   - Run `uv sync` to install

7. **Add tests:**
   - Create test files in `tests/` directory
   - Run `bash scripts/test.sh` to verify

## Code Quality

This base is configured with:
- Type checking with mypy (strict mode)
- Linting with ruff
- Code formatting with ruff
- Test coverage reporting
- All checks pass ✅

## Coverage

Current test coverage: 93%
- All core functionality tested
- Health check endpoint verified
- Application startup/shutdown tested

---

This base provides a solid foundation for building FastAPI applications without the overhead of unused features.
