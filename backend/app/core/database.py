"""Database configuration and session management."""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

# Create SQLModel engine with connection pooling
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    pool_pre_ping=True,  # Enable connection health checks
    # Uncomment below for production with connection pool sizing
    # pool_size=5,
    # max_overflow=10,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields a SQLModel Session that automatically commits on success
    or rolls back on exception.
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Initialize database by creating all tables.

    WARNING: This should only be used in development.
    In production, use Alembic migrations instead.
    """
    from sqlmodel import SQLModel

    # Import all models here to ensure they are registered with SQLModel
    from app.models.item import Item  # noqa: F401
    from app.models.user import User  # noqa: F401

    SQLModel.metadata.create_all(engine)
