from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.core.config import get_settings

Base = declarative_base()

_settings = get_settings()
engine = create_engine(
    _settings.database_url(),
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for request-scoped usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
# PUBLIC_INTERFACE
def db_session() -> Generator[Session, None, None]:
    """Context manager that provides a DB session with commit/rollback handling."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
