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

## Requirements

* [Docker](https://www.docker.com/)
* [uv](https://docs.astral.sh/uv/) for Python package and environment management

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

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── utils.py      # Utility routes (health check)
│   │   └── main.py           # API router setup
│   ├── core/
│   │   └── config.py         # Application configuration
│   ├── main.py               # FastAPI application
│   └── models.py             # Pydantic models
├── tests/                    # Test files
├── pyproject.toml           # Project dependencies
└── Dockerfile               # Docker configuration
```

## API Endpoints

### Health Check
- `GET /api/v1/utils/health-check/` - Returns health status

## Adding Features

To add new features to this base:

1. Create new route files in `app/api/routes/`
2. Add new models in `app/models.py`
3. Register routes in `app/api/main.py`
4. Update configuration in `app/core/config.py` if needed

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
