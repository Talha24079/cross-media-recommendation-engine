import uuid
from pydantic import BaseModel, ConfigDict, Field, model_validator
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
    creator_username: Optional[str] = None
    submission_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class BountySubmissionCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    media_id: Optional[uuid.UUID] = None

class BountySubmissionResponse(BaseModel):
    id: uuid.UUID
    bounty_id: uuid.UUID
    submitter_id: uuid.UUID
    submitter_username: str
    content: str
    media_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BountyResolve(BaseModel):
    winner_id: Optional[uuid.UUID] = None
    submission_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def require_winner_or_submission(self):
        if self.winner_id is None and self.submission_id is None:
            raise ValueError("Either winner_id or submission_id is required")
        return self

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

class BountyCancelResponse(BaseModel):
    id: uuid.UUID
    status: str
    refunded_amount: int
    message: str
