import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Common fields for MongoDB responses
class MongoBaseModel(BaseModel):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True

class ThreadCreate(BaseModel):
    title: str
    content: str
    media_id: Optional[uuid.UUID] = None
    tags: List[str] = []

class ThreadResponse(MongoBaseModel):
    title: str
    content: str
    author_id: str
    media_id: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None

class CommentResponse(MongoBaseModel):
    thread_id: str
    parent_id: Optional[str] = None
    author_id: str
    content: str
    created_at: datetime
    updated_at: datetime
