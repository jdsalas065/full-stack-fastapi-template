"""CRUD operations for User model."""

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user.

    Args:
        session: Database session
        user_create: User creation data

    Returns:
        Created user instance
    """
    db_obj = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """
    Update a user.

    Args:
        session: Database session
        db_user: Existing user from database
        user_in: User update data

    Returns:
        Updated user instance
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
        del user_data["password"]

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Get a user by email.

    Args:
        session: Database session
        email: User email address

    Returns:
        User instance if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(*, session: Session, user_id: str) -> User | None:
    """
    Get a user by ID.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User instance if found, None otherwise
    """
    return session.get(User, user_id)


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user.

    Args:
        session: Database session
        email: User email
        password: Plain text password

    Returns:
        User instance if authentication successful, None otherwise
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_users(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[User], int]:
    """
    Get list of users with pagination.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (list of users, total count)
    """
    count_statement = select(User)
    count = len(session.exec(count_statement).all())

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return list(users), count


def delete_user(*, session: Session, user_id: str) -> None:
    """
    Delete a user.

    Args:
        session: Database session
        user_id: User ID to delete
    """
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
