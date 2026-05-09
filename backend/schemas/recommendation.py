import uuid
from pydantic import BaseModel
from typing import Optional

class MediaItemCreate(BaseModel):
    title: str
    media_type: str
    description: Optional[str] = None

class MediaItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    media_type: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: uuid.UUID
    title: str
    media_type: str
    score: float
