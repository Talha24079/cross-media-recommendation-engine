import uuid
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from core.database import Base

class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    type = Column(String, index=True, nullable=False) # e.g. "movie", "book", "game"
    description = Column(String)
    metadata_json = Column(JSON, default={})
    embedding = Column(Vector(384)) # For sentence-transformers/all-MiniLM-L6-v2
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
