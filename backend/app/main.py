from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.constants import Environment
from app.core.logging import get_logger, setup_logging
from app.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.middleware import RequestLoggingMiddleware

# Setup logging
setup_logging()
logger = get_logger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API docs: http://localhost:8000{settings.API_V1_STR}/docs")
    
    # Initialize database in local environment (for development only)
    # In production, use Alembic migrations instead
    if settings.ENVIRONMENT == Environment.LOCAL:
        logger.info("Local environment detected - initializing database tables")
        from app.core.database import init_db
        
        try:
            init_db()
            logger.info("Database tables created successfully")
            
            # Create first superuser if not exists
            from app.core.database import get_session
            from app.crud import user as user_crud
            from app.schemas.user import UserCreate
            
            with next(get_session()) as session:
                user = user_crud.get_user_by_email(
                    session=session, email=settings.FIRST_SUPERUSER
                )
                if not user:
                    logger.info("Creating first superuser")
                    user_crud.create_user(
                        session=session,
                        user_create=UserCreate(
                            email=settings.FIRST_SUPERUSER,
                            password=settings.FIRST_SUPERUSER_PASSWORD,
                            is_superuser=True,
                            full_name="Admin User",
                        ),
                    )
                    logger.info("First superuser created successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)

# Add middleware
if settings.ENVIRONMENT == Environment.LOCAL:
    app.add_middleware(RequestLoggingMiddleware)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
