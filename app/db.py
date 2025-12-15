from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# DATABASE_URL = "postgresql://postgres:password@localhost:5432/webhooks"

engine = create_engine(
    settings.database_url,
    pool_size=10,          # <= what you asked for
    max_overflow=20,       # burst handling
    pool_timeout=30,       # seconds to wait for a connection
    pool_recycle=1800,     # recycle connections (important in AWS)
    pool_pre_ping=True,    # kill dead connections
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()
