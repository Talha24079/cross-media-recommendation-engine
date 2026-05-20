from fastapi import APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.economy import (
    BountyCreate,
    BountyResponse,
    BountyResolve,
    BountySubmissionCreate,
    BountySubmissionResponse,
    BountyCancelResponse,
    BalanceResponse,
    DailyStreakResponse,
)
from services import economy_service, realtime_broadcast

router = APIRouter(prefix="/economy", tags=["economy"])


def _bounty_response(bounty, creator_username: str | None = None, submission_count: int = 0) -> BountyResponse:
    return BountyResponse(
        id=bounty.id,
        creator_id=bounty.creator_id,
        title=bounty.title,
        description=bounty.description,
        reward_amount=bounty.reward_amount,
        status=bounty.status.value if hasattr(bounty.status, "value") else str(bounty.status),
        created_at=bounty.created_at,
        creator_username=creator_username,
        submission_count=int(submission_count or 0),
    )


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await economy_service.get_balance(current_user.id, db)
    return BalanceResponse(
        user_id=user.id,
        username=user.username,
        reputation_points=user.reputation_points,
    )


@router.post("/daily-streak", response_model=DailyStreakResponse)
async def claim_daily_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await economy_service.claim_daily_streak(current_user.id, db)
    return DailyStreakResponse(
        message="Daily streak claimed!",
        points_awarded=10,
        new_balance=user.reputation_points,
    )


@router.post("/bounties", response_model=BountyResponse, status_code=status.HTTP_201_CREATED)
async def create_bounty(
    bounty_data: BountyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bounty = await economy_service.create_bounty(
        creator_id=current_user.id,
        title=bounty_data.title,
        description=bounty_data.description,
        reward_amount=bounty_data.reward_amount,
        db=db,
    )
    await realtime_broadcast.notify_bounties_list()
    return _bounty_response(bounty, current_user.username, 0)


@router.get("/bounties", response_model=List[BountyResponse])
async def list_open_bounties(db: AsyncSession = Depends(get_db)):
    rows = await economy_service.list_open_bounties(db)
    return [_bounty_response(bounty, username, count) for bounty, username, count in rows]


@router.get("/bounties/{bounty_id}", response_model=BountyResponse)
async def get_bounty(
    bounty_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    bounty, username = await economy_service.get_bounty_detail(bounty_id, db)
    submissions = await economy_service.list_bounty_submissions(bounty_id, db)
    return _bounty_response(bounty, username, len(submissions))


@router.get("/bounties/{bounty_id}/submissions", response_model=List[BountySubmissionResponse])
async def list_submissions(
    bounty_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    rows = await economy_service.list_bounty_submissions(bounty_id, db)
    return [
        BountySubmissionResponse(
            id=row["submission"].id,
            bounty_id=row["submission"].bounty_id,
            submitter_id=row["submission"].submitter_id,
            submitter_username=row["submitter_username"],
            content=row["submission"].content,
            media_id=row["submission"].media_id,
            created_at=row["submission"].created_at,
        )
        for row in rows
    ]


@router.post(
    "/bounties/{bounty_id}/submissions",
    response_model=BountySubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    bounty_id: uuid.UUID,
    body: BountySubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    submission = await economy_service.submit_bounty_answer(
        bounty_id=bounty_id,
        submitter_id=current_user.id,
        content=body.content,
        media_id=body.media_id,
        db=db,
    )
    await realtime_broadcast.notify_bounty(str(bounty_id))
    await realtime_broadcast.notify_bounties_list()
    return BountySubmissionResponse(
        id=submission.id,
        bounty_id=submission.bounty_id,
        submitter_id=submission.submitter_id,
        submitter_username=current_user.username,
        content=submission.content,
        media_id=submission.media_id,
        created_at=submission.created_at,
    )


@router.post("/bounties/{bounty_id}/cancel", response_model=BountyCancelResponse)
async def cancel_bounty(
    bounty_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bounty, refunded = await economy_service.cancel_bounty(
        bounty_id=bounty_id,
        creator_id=current_user.id,
        db=db,
    )
    await realtime_broadcast.notify_bounty(str(bounty_id))
    await realtime_broadcast.notify_bounties_list()
    return BountyCancelResponse(
        id=bounty.id,
        status=bounty.status.value,
        refunded_amount=refunded,
        message="Bounty archived and reward refunded to your balance",
    )


@router.post("/bounties/{bounty_id}/resolve", response_model=BountyResponse)
async def resolve_bounty(
    bounty_id: uuid.UUID,
    resolve_data: BountyResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bounty = await economy_service.resolve_bounty(
        bounty_id=bounty_id,
        creator_id=current_user.id,
        db=db,
        winner_id=resolve_data.winner_id,
        submission_id=resolve_data.submission_id,
    )
    await realtime_broadcast.notify_bounty(str(bounty_id))
    await realtime_broadcast.notify_bounties_list()
    _, username = await economy_service.get_bounty_detail(bounty_id, db)
    submissions = await economy_service.list_bounty_submissions(bounty_id, db)
    return _bounty_response(bounty, username, len(submissions))
