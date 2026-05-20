import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
from core.database import Base

class BountyStatus(str, enum.Enum):
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"

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

class BountySubmission(Base):
    __tablename__ = "bounty_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bounty_id = Column(UUID(as_uuid=True), ForeignKey("bounties.id"), nullable=False, index=True)
    submitter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(String, nullable=False)
    media_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("bounty_id", "submitter_id", name="uq_bounty_submitter"),
    )

class CentralLedger(Base):
    __tablename__ = "central_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
