"""
Database configuration and session management

Task 2.0: Database Integration
Phase 5: PostgreSQL Support Added

Author: TANGO
Last Updated: June 6, 2026
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# Database URL (SQLite for development, PostgreSQL for production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./preto.db")

# PostgreSQL connection pool settings (Phase 5)
POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", "10"))
POSTGRES_MAX_OVERFLOW = int(os.getenv("POSTGRES_MAX_OVERFLOW", "20"))
POSTGRES_POOL_PRE_PING = os.getenv("POSTGRES_POOL_PRE_PING", "true").lower() == "true"

# Create engine with appropriate settings
if "postgresql" in DATABASE_URL:
    # PostgreSQL production configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=POSTGRES_POOL_SIZE,
        max_overflow=POSTGRES_MAX_OVERFLOW,
        pool_pre_ping=POSTGRES_POOL_PRE_PING,
        echo=False
    )
    logger.info("Using PostgreSQL database")
else:
    # SQLite development configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        echo=False  # Set to True for SQL logging
    )
    logger.info("Using SQLite database")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency for getting database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    try:
        logger.info(f"Initializing database: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


# Database URL helper for display (masks password)
def get_db_url_safe() -> str:
    """Return database URL with password masked."""
    if "@" in DATABASE_URL:
        # Format: protocol://user:password@host/db
        parts = DATABASE_URL.split("@")
        credentials = parts[0].split("://")
        if ":" in credentials[1]:
            user, _ = credentials[1].split(":", 1)
            return f"{credentials[0]}://{user}:****@{parts[1]}"
    return DATABASE_URL
