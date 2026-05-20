from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

# --- PostgreSQL Setup ---
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False, 
    pool_recycle=3600, 
    pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- MongoDB Setup ---
mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
mongodb = mongodb_client[settings.MONGODB_DB_NAME]

async def get_mongodb():
    yield mongodb
