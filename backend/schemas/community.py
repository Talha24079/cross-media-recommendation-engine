import uuid
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# Common fields for MongoDB responses
class MongoBaseModel(BaseModel):
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)

class ThreadCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)
    media_id: Optional[uuid.UUID] = None
    tags: List[str] = []

class ThreadResponse(MongoBaseModel):
    title: str
    content: str
    author_id: str
    author_username: Optional[str] = None
    author_avatar_url: Optional[str] = None
    media_id: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[str] = None

class CommentResponse(MongoBaseModel):
    thread_id: str
    parent_id: Optional[str] = None
    author_id: str
    author_username: Optional[str] = None
    author_avatar_url: Optional[str] = None
    content: str
    created_at: datetime
    updated_at: datetime
