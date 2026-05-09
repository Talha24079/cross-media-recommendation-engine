from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.bounty import BountyStatus
from schemas.economy import (
    BountyCreate, BountyResponse, BountyResolve,
    BalanceResponse, DailyStreakResponse
)
from services import economy_service
from sqlalchemy.future import select
from models.bounty import Bounty

router = APIRouter(prefix="/economy", tags=["economy"])


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await economy_service.get_balance(current_user.id, db)
    return BalanceResponse(
        user_id=user.id,
        username=user.username,
        reputation_points=user.reputation_points
    )


@router.post("/daily-streak", response_model=DailyStreakResponse)
async def claim_daily_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await economy_service.claim_daily_streak(current_user.id, db)
    return DailyStreakResponse(
        message="Daily streak claimed!",
        points_awarded=10,
        new_balance=user.reputation_points
    )


@router.post("/bounties", response_model=BountyResponse, status_code=status.HTTP_201_CREATED)
async def create_bounty(
    bounty_data: BountyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    bounty = await economy_service.create_bounty(
        creator_id=current_user.id,
        title=bounty_data.title,
        description=bounty_data.description,
        reward_amount=bounty_data.reward_amount,
        db=db
    )
    return bounty


@router.get("/bounties", response_model=List[BountyResponse])
async def list_open_bounties(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bounty).where(Bounty.status == BountyStatus.OPEN)
    )
    bounties = result.scalars().all()
    return bounties


@router.post("/bounties/{bounty_id}/resolve", response_model=BountyResponse)
async def resolve_bounty(
    bounty_id: uuid.UUID,
    resolve_data: BountyResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    bounty = await economy_service.resolve_bounty(
        bounty_id=bounty_id,
        winner_id=resolve_data.winner_id,
        creator_id=current_user.id,
        db=db
    )
    return bounty
