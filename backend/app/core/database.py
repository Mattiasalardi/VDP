from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=0,
    echo=settings.DEBUG  # Enable SQL query logging in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database dependency for FastAPI
def get_db():
    """
    Database dependency for FastAPI endpoints.
    Creates a new database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to create all tables
def create_tables():
    """Create all tables in the database"""
    from app.models.base import Base
    # Import all models to ensure they're registered with the metadata
    import app.models
    Base.metadata.create_all(bind=engine)

# Helper function to drop all tables
def drop_tables():
    """Drop all tables from the database"""
    from app.models.base import Base
    # Import all models to ensure they're registered with the metadata
    import app.models
    Base.metadata.drop_all(bind=engine)