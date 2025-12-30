# FastAPI Base Project - Backend

A minimal FastAPI backend base for project initialization. This is a clean starting point without any specific features - just the essential structure.

## Features

This base includes:
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

## Requirements

* [Docker](https://www.docker.com/)
* [uv](https://docs.astral.sh/uv/) for Python package and environment management
* PostgreSQL database

## Local Development

### Using Docker Compose

Start the local development environment with Docker Compose:

```console
$ docker compose watch
```

The backend will be available at http://localhost:8000

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Using uv (without Docker)

From `./backend/` directory, install dependencies:

```console
$ uv sync
```

Activate the virtual environment:

```console
$ source .venv/bin/activate
```

Run the development server:

```console
$ fastapi dev app/main.py
```

Make sure your editor is using the correct Python virtual environment at `backend/.venv/bin/python`.

## Database Setup

### Environment Variables

Configure the database connection in the `.env` file:

```bash
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
```

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
│   │   │   └── utils.py       # Utility routes (health check)
│   │   ├── dependencies.py    # Shared dependencies
│   │   └── main.py            # API router setup
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database session management
│   │   └── security.py        # Password hashing and JWT
│   ├── crud/                  # CRUD operations
│   │   ├── user.py            # User CRUD
│   │   └── item.py            # Item CRUD
│   ├── models/                # SQLModel database models
│   │   ├── user.py            # User model
│   │   └── item.py            # Item model
│   ├── schemas/               # Pydantic schemas
│   │   ├── common.py          # Common schemas
│   │   ├── user.py            # User schemas
│   │   └── item.py            # Item schemas
│   ├── utils/
│   │   └── email.py           # Email utilities
│   └── main.py                # FastAPI application
├── tests/                     # Test files
├── alembic.ini                # Alembic configuration
├── pyproject.toml            # Project dependencies
└── Dockerfile                # Docker configuration
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

Run tests with:

```console
$ bash ./scripts/test.sh
```

Or if using Docker:

```console
$ docker compose exec backend bash scripts/tests-start.sh
```

## Configuration

Configuration is managed through environment variables. See the `.env` file in the project root.

Key settings:
- `PROJECT_NAME`: Project name
- `API_V1_STR`: API version prefix (default: `/api/v1`)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins
- `ENVIRONMENT`: Environment name (local/staging/production)
