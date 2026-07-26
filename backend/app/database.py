"""
Database setup and session management.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)


def _create_engine_with_fallback():
    database_url = settings.database_url
    connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}

    try:
        return create_engine(database_url, connect_args=connect_args)
    except ModuleNotFoundError as exc:
        # Common local issue: postgres async driver not installed.
        if "postgresql+asyncpg" in database_url and getattr(exc, "name", "") == "asyncpg":
            fallback_url = "sqlite:///./resource_management.db"
            logger.warning(
                "Database driver asyncpg not installed; falling back to %s",
                fallback_url,
            )
            return create_engine(fallback_url, connect_args={"check_same_thread": False})
        raise


engine = _create_engine_with_fallback()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    from app.models import resource, project, allocation  # noqa: F401
    Base.metadata.create_all(bind=engine)
