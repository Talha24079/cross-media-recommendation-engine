import uuid
from sqlalchemy import Column, String, DateTime, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, DateTime, JSON, Float, UniqueConstraint
from core.database import Base

class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    type = Column(String, index=True, nullable=False) # e.g. "movie", "book", "game"
    description = Column(String) # the text used to generate the embedding
    genre = Column(String) # e.g. "Action, Sci-Fi"
    poster_url = Column(String) # image URL from the API
    rating = Column(Float) # e.g. 8.5
    external_id = Column(String) # the ID from TMDB/RAWG/OpenLibrary for deduplication
    source = Column(String) # either 'tmdb', 'rawg', or 'openlibrary'
    metadata_json = Column(JSON, default={})
    embedding = Column(Vector(384)) # For sentence-transformers/all-MiniLM-L6-v2
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('external_id', 'source', name='uq_external_id_source'),
    )
