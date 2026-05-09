import uuid
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class BountyCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    reward_amount: int = Field(..., gt=0, le=10000)

class BountyResponse(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    description: Optional[str] = None
    reward_amount: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BountyResolve(BaseModel):
    winner_id: uuid.UUID

class BalanceResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    reputation_points: int

class LedgerEntry(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    amount: int
    transaction_type: str
    reference_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DailyStreakResponse(BaseModel):
    message: str
    points_awarded: int
    new_balance: int
