from app.db.base import Base
from app.db.session import engine
from app.core.logging import logger


def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in SQLAlchemy models.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
