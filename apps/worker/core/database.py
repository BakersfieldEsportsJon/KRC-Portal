from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import worker_settings
import logging

logger = logging.getLogger(__name__)

# Database metadata with naming convention for constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

# Create sync engine for worker
engine = create_engine(
    worker_settings.DATABASE_URL,
    echo=worker_settings.is_development,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Create declarative base
Base = declarative_base(metadata=metadata)


def get_db() -> Session:
    """Get database session for worker tasks"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseManager:
    """Database management utilities for workers"""

    @staticmethod
    def get_session() -> Session:
        """Get a database session"""
        return SessionLocal()