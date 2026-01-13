# FastAPI Backend - Standalone Project

A standalone FastAPI backend that can run independently without dependencies on parent directories.

## Features

This backend includes:
- ✅ Basic FastAPI application setup
- ✅ Project structure with modular organization
- ✅ Health check endpoint
- ✅ CORS middleware configuration
- ✅ OpenAPI documentation
- ✅ Configuration management with Pydantic Settings
- ✅ Development and testing setup
- ✅ SQLModel database integration with PostgreSQL
- ✅ Alembic database migrations
- ✅ User authentication with JWT tokens
- ✅ Password hashing with bcrypt
- ✅ User and Item management APIs
- ✅ File storage with MinIO
- ✅ Document processing and OCR

## Requirements

* [Docker](https://www.docker.com/) and Docker Compose
* [uv](https://docs.astral.sh/uv/) for Python package and environment management (for local development without Docker)
* PostgreSQL database (included in Docker Compose)

## Quick Start

### 1. Setup Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration values. Minimum required variables:
- `PROJECT_NAME`
- `POSTGRES_PASSWORD`
- `POSTGRES_USER`
- `POSTGRES_DB`
- `SECRET_KEY`
- `FIRST_SUPERUSER`
- `FIRST_SUPERUSER_PASSWORD`

### 2. Run with Docker Compose

Start all services (database, MinIO, backend):

```bash
docker compose up -d
```

The backend will be available at http://localhost:8000

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

### 3. Development Mode with Hot Reload

For development with auto-reload:

```bash
docker compose up
```

This uses `docker-compose.override.yml` which enables:
- Hot reload on code changes
- Exposed ports for all services
- Development-friendly settings

## Local Development (without Docker)

### Using uv

From the `backend/` directory, install dependencies:

```console
$ uv sync
```

Activate the virtual environment:

```console
# On Windows
$ .venv\Scripts\activate

# On Unix/MacOS
$ source .venv/bin/activate
```

Run the development server:

```console
$ fastapi dev app/main.py
```

Make sure your editor is using the correct Python virtual environment at `backend/.venv/bin/python`.

**Note:** When running without Docker, you'll need to:
- Set up PostgreSQL separately
- Set up MinIO separately
- Update `.env` to point to your local services (e.g., `POSTGRES_SERVER=localhost`)

## Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# Project Configuration
PROJECT_NAME=FastAPI Backend
DOMAIN=localhost
ENVIRONMENT=local

# Frontend Configuration
FRONTEND_HOST=http://localhost:5173
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Security
SECRET_KEY=changethis
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Database Configuration
POSTGRES_SERVER=db  # Use 'localhost' if running without Docker
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis

# First Superuser
FIRST_SUPERUSER=admin@localhost
FIRST_SUPERUSER_PASSWORD=changethis

# MinIO Configuration
MINIO_ENDPOINT=minio:9000  # Use 'localhost:9000' if running without Docker
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=documents

# OpenAI Configuration (for LLM OCR)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o

# Sentry (optional)
SENTRY_DSN=

# Docker Configuration
DOCKER_IMAGE_BACKEND=backend
TAG=latest
```

## Database Setup

### Database Migrations with Alembic

**IMPORTANT**: In production, always use Alembic migrations. Never use `init_db()` or `create_all()`.

#### Create a new migration

After making changes to your models:

```console
$ cd backend
$ alembic revision --autogenerate -m "Add new table"
```

#### Apply migrations

To apply all pending migrations:

```console
$ cd backend
$ alembic upgrade head
```

Or with Docker:

```console
$ docker compose exec backend alembic upgrade head
```

#### Rollback migrations

To rollback the last migration:

```console
$ cd backend
$ alembic downgrade -1
```

#### View migration history

```console
$ cd backend
$ alembic history
$ alembic current
```

### Initial Superuser

The first superuser is automatically created on startup in local environment. Configure in `.env`:

```bash
FIRST_SUPERUSER=admin@localhost
FIRST_SUPERUSER_PASSWORD=changethis
```

**Note**: In local development, the database tables are automatically created. In production, you must run migrations manually.

## Project Structure

```
backend/
├── app/
│   ├── alembic/               # Database migrations
│   │   ├── versions/          # Migration scripts
│   │   ├── env.py             # Alembic environment
│   │   ├── script.py.mako     # Migration template
│   │   └── README.md          # Migration instructions
│   ├── api/
│   │   ├── routes/
│   │   │   ├── login.py       # Authentication routes
│   │   │   ├── users.py       # User management routes
│   │   │   ├── items.py       # Item management routes
│   │   │   ├── files.py       # File management routes
│   │   │   ├── submissions.py # Submission routes
│   │   │   ├── document.py    # Document processing routes
│   │   │   └── utils.py       # Utility routes (health check)
│   │   ├── dependencies.py    # Shared dependencies
│   │   └── main.py            # API router setup
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   ├── constants.py       # Application constants
│   │   ├── database.py        # Database session management
│   │   ├── logging.py          # Logging configuration
│   │   └── security.py         # Password hashing and JWT
│   ├── crud/                  # CRUD operations
│   │   ├── user.py            # User CRUD
│   │   ├── item.py            # Item CRUD
│   │   └── file.py            # File CRUD
│   ├── models/                # SQLModel database models
│   │   ├── user.py            # User model
│   │   ├── item.py            # Item model
│   │   ├── file.py            # File model
│   │   └── submission.py      # Submission model
│   ├── schemas/               # Pydantic schemas
│   │   ├── common.py          # Common schemas
│   │   ├── user.py            # User schemas
│   │   ├── item.py            # Item schemas
│   │   ├── file.py            # File schemas
│   │   ├── submission.py      # Submission schemas
│   │   └── document.py        # Document schemas
│   ├── services/              # Business logic services
│   │   ├── storage_service.py # MinIO storage service
│   │   ├── document_processor.py # Document processing
│   │   ├── llm_ocr_service.py # LLM-based OCR
│   │   └── field_comparison_service.py # Field comparison
│   ├── utils/
│   │   └── email.py           # Email utilities
│   └── main.py                # FastAPI application
├── tests/                     # Test files
├── scripts/                   # Utility scripts
│   ├── prestart.sh           # Pre-startup script
│   ├── init_minio.py         # MinIO initialization
│   └── tests-start.sh        # Test runner
├── alembic.ini                # Alembic configuration
├── pyproject.toml            # Project dependencies
├── docker-compose.yml         # Docker Compose configuration
├── docker-compose.override.yml # Development overrides
├── Dockerfile                 # Docker configuration
└── .env                       # Environment variables (create from .env.example)
```

## API Endpoints

### Authentication
- `POST /api/v1/login/access-token` - Login with email and password
- `POST /api/v1/login/test-token` - Test access token
- `POST /api/v1/password-recovery/{email}` - Request password reset
- `POST /api/v1/reset-password/` - Reset password with token

### Users
- `GET /api/v1/users/` - List all users (superuser only)
- `POST /api/v1/users/` - Create user (superuser only)
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete current user
- `PATCH /api/v1/users/me/password` - Update password
- `POST /api/v1/users/signup` - Register new user
- `GET /api/v1/users/{user_id}` - Get user by ID (superuser only)
- `PATCH /api/v1/users/{user_id}` - Update user (superuser only)
- `DELETE /api/v1/users/{user_id}` - Delete user (superuser only)

### Items
- `GET /api/v1/items/` - List items (own items or all for superuser)
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/{id}` - Get item by ID
- `PUT /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item

### Files
- `POST /api/v1/files/` - Upload file
- `GET /api/v1/files/{file_id}` - Get file metadata
- `DELETE /api/v1/files/{file_id}` - Delete file
- `GET /api/v1/files/{file_id}/download` - Download file

### Submissions
- `POST /api/v1/submissions/` - Create submission
- `GET /api/v1/submissions/` - List submissions
- `GET /api/v1/submissions/{submission_id}` - Get submission
- `PATCH /api/v1/submissions/{submission_id}` - Update submission
- `DELETE /api/v1/submissions/{submission_id}` - Delete submission

### Documents
- `POST /api/v1/documents/process` - Process document
- `GET /api/v1/documents/{document_id}` - Get document data

### Health Check
- `GET /api/v1/utils/health-check/` - Returns health status

## Adding Features

To add new features to this base:

1. **Add new routes:**
   - Create new route files in `app/api/routes/`
   - Register routes in `app/api/main.py`

2. **Add database models:**
   - Create model files in `app/models/` (e.g., `user.py`, `item.py`)
   - Each file should contain related SQLModel models
   - Import and expose models in `app/models/__init__.py`

3. **Add schemas:**
   - Create schema files in `app/schemas/` (e.g., `user.py`, `item.py`)
   - Each file should contain related Pydantic schemas for validation
   - Import and expose schemas in `app/schemas/__init__.py`

4. **Add CRUD operations:**
   - Create CRUD files in `app/crud/` (e.g., `user.py`, `item.py`)
   - Each file should contain CRUD operations for that specific model
   - Import and expose CRUD instances in `app/crud/__init__.py`

5. **Update configuration:**
   - Add new settings to `app/core/config.py` as needed

## Testing

Run tests with Docker:

```console
$ docker compose exec backend bash scripts/tests-start.sh
```

Or locally (without Docker):

```console
$ pytest
```

## Docker Commands

### Start services
```bash
docker compose up -d
```

### Stop services
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f backend
```

### Execute commands in container
```bash
docker compose exec backend bash
```

### Rebuild and restart
```bash
docker compose up -d --build
```

## Standalone Operation

This backend is designed to run completely independently:

- ✅ All configuration in `backend/.env`
- ✅ Docker Compose includes all dependencies (PostgreSQL, MinIO)
- ✅ No references to parent directory
- ✅ Can be deployed separately from frontend
- ✅ All scripts are self-contained

## Troubleshooting

### Database connection issues
- Ensure PostgreSQL is running: `docker compose ps`
- Check `.env` has correct `POSTGRES_SERVER` (use `db` for Docker, `localhost` for local)
- Verify database credentials in `.env`

### MinIO connection issues
- Ensure MinIO is running: `docker compose ps`
- Check `.env` has correct `MINIO_ENDPOINT` (use `minio:9000` for Docker, `localhost:9000` for local)
- Access MinIO console at http://localhost:9001

### Port conflicts
- Change ports in `docker-compose.yml` if 8000, 5432, 9000, or 9001 are in use
- Update `.env` accordingly
