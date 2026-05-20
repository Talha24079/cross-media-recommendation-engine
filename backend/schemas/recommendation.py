import uuid
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from enum import Enum

class MediaTypeEnum(str, Enum):
    movie = "movie"
    book = "book"
    game = "game"
    music = "music"
    podcast = "podcast"
    anime = "anime"

class MediaItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    media_type: MediaTypeEnum
    description: Optional[str] = None
    genre: Optional[str] = None

class MediaItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    media_type: str
    description: Optional[str] = None
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    rating: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class MetadataPreviewResponse(BaseModel):
    title: str
    media_type: str
    poster_url: Optional[str] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    source: Optional[str] = None

class RecommendationResponse(BaseModel):
    id: uuid.UUID
    title: str
    media_type: str
    score: float
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    rating: Optional[float] = None
    recommended_because: Optional[str] = None
