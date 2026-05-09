import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
from core.database import Base

class BountyStatus(str, enum.Enum):
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class Bounty(Base):
    __tablename__ = "bounties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    reward_amount = Column(Integer, default=0, nullable=False)
    status = Column(Enum(BountyStatus), default=BountyStatus.OPEN, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CentralLedger(Base):
    __tablename__ = "central_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False) # Positive for earning, Negative for spending
    transaction_type = Column(String, nullable=False) # e.g. "BOUNTY_REWARD", "BOUNTY_CREATION"
    reference_id = Column(UUID(as_uuid=True), nullable=True) # e.g. Bounty ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
