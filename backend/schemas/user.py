import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

    @field_validator('password')
    @classmethod
    def password_must_contain_digit(cls, v):
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(UserBase):
    id: uuid.UUID
    reputation_points: int
    faction_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str
