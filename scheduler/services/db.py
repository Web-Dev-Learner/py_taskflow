# scheduler/services/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read variables from .env
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")

POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Build DATABASE_URL dynamically
DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Create async SQLAlchemy engine and session factory
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# Dependency to get DB session (used in FastAPI routes)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Create tables on startup
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
