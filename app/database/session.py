"""
Database Session Management
Stock Intelligence System
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator

from app.config import settings
from app.utils.logger import db_logger


# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions

    Usage:
        with get_db_context() as db:
            items = db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        db_logger.error(f"Database error: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        db_logger.info("Database tables created successfully")
    except Exception as e:
        db_logger.error(f"Failed to create database tables: {str(e)}", exc_info=True)
        raise


def drop_db():
    """Drop all database tables (use with caution!)"""
    if settings.APP_ENV == "production":
        raise RuntimeError("Cannot drop database in production!")

    try:
        Base.metadata.drop_all(bind=engine)
        db_logger.warning("All database tables dropped")
    except Exception as e:
        db_logger.error(f"Failed to drop database tables: {str(e)}", exc_info=True)
        raise
