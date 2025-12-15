from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# DATABASE_URL = "postgresql://postgres:password@localhost:5432/webhooks"

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
