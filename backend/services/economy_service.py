from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func
from fastapi import HTTPException, status
from models.user import User
from models.bounty import Bounty, BountyStatus, BountySubmission, CentralLedger
from datetime import date


async def get_balance(user_id, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def award_points(user_id, amount: int, transaction_type: str, db: AsyncSession, reference_id=None):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(reputation_points=User.reputation_points + amount)
    )

    ledger_entry = CentralLedger(
        user_id=user_id,
        amount=amount,
        transaction_type=transaction_type,
        reference_id=reference_id,
    )
    db.add(ledger_entry)


async def deduct_points(user_id, amount: int, transaction_type: str, db: AsyncSession, reference_id=None):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.reputation_points < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Current: {user.reputation_points}, Required: {amount}",
        )

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(reputation_points=User.reputation_points - amount),
    )

    ledger_entry = CentralLedger(
        user_id=user_id,
        amount=-amount,
        transaction_type=transaction_type,
        reference_id=reference_id,
    )
    db.add(ledger_entry)


async def _get_open_bounty(bounty_id, db: AsyncSession) -> Bounty:
    result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = result.scalar_one_or_none()
    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")
    if bounty.status != BountyStatus.OPEN:
        raise HTTPException(status_code=400, detail="Bounty is not open")
    return bounty


async def create_bounty(creator_id, title: str, description: str, reward_amount: int, db: AsyncSession):
    await deduct_points(creator_id, reward_amount, "BOUNTY_STAKE", db)

    bounty = Bounty(
        creator_id=creator_id,
        title=title,
        description=description,
        reward_amount=reward_amount,
        status=BountyStatus.OPEN,
    )
    db.add(bounty)
    await db.commit()
    await db.refresh(bounty)
    return bounty


async def submit_bounty_answer(
    bounty_id,
    submitter_id,
    content: str,
    db: AsyncSession,
    media_id=None,
):
    bounty = await _get_open_bounty(bounty_id, db)

    if bounty.creator_id == submitter_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bounty creator cannot submit an answer to their own bounty",
        )

    existing = await db.execute(
        select(BountySubmission).where(
            BountySubmission.bounty_id == bounty_id,
            BountySubmission.submitter_id == submitter_id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted an answer for this bounty",
        )

    submission = BountySubmission(
        bounty_id=bounty_id,
        submitter_id=submitter_id,
        content=content,
        media_id=media_id,
    )
    db.add(submission)
    await award_points(submitter_id, 1, "BOUNTY_ANSWER", db, reference_id=bounty_id)
    await db.commit()
    await db.refresh(submission)
    return submission


async def list_bounty_submissions(bounty_id, db: AsyncSession):
    result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Bounty not found")

    submissions_result = await db.execute(
        select(BountySubmission, User.username)
        .join(User, User.id == BountySubmission.submitter_id)
        .where(BountySubmission.bounty_id == bounty_id)
        .order_by(BountySubmission.created_at.asc())
    )
    rows = submissions_result.all()
    return [
        {
            "submission": row[0],
            "submitter_username": row[1],
        }
        for row in rows
    ]


async def cancel_bounty(bounty_id, creator_id, db: AsyncSession):
    result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = result.scalar_one_or_none()

    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")
    if bounty.creator_id != creator_id:
        raise HTTPException(status_code=403, detail="Only the bounty creator can archive it")
    if bounty.status != BountyStatus.OPEN:
        raise HTTPException(status_code=400, detail="Bounty is not open")

    refund_amount = bounty.reward_amount
    await award_points(creator_id, refund_amount, "BOUNTY_REFUND", db, reference_id=bounty.id)

    await db.execute(
        update(Bounty)
        .where(Bounty.id == bounty_id)
        .values(status=BountyStatus.ARCHIVED),
    )
    await db.commit()
    reload = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = reload.scalar_one()
    return bounty, refund_amount


async def resolve_bounty(
    bounty_id,
    creator_id,
    db: AsyncSession,
    winner_id=None,
    submission_id=None,
):
    result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = result.scalar_one_or_none()

    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")
    if bounty.creator_id != creator_id:
        raise HTTPException(status_code=403, detail="Only the bounty creator can resolve it")
    if bounty.status != BountyStatus.OPEN:
        raise HTTPException(status_code=400, detail="Bounty is not open")

    resolved_winner_id = winner_id
    if submission_id is not None:
        submission_result = await db.execute(
            select(BountySubmission).where(
                BountySubmission.id == submission_id,
                BountySubmission.bounty_id == bounty_id,
            )
        )
        submission = submission_result.scalars().first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found for this bounty")
        resolved_winner_id = submission.submitter_id

    if resolved_winner_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either winner_id or submission_id is required",
        )

    if resolved_winner_id == creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creator cannot be selected as the bounty winner",
        )

    await award_points(
        resolved_winner_id,
        bounty.reward_amount,
        "BOUNTY_WON",
        db,
        reference_id=bounty.id,
    )

    await db.execute(
        update(Bounty)
        .where(Bounty.id == bounty_id)
        .values(status=BountyStatus.COMPLETED),
    )
    await db.commit()
    reload = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = reload.scalar_one()
    return bounty


async def get_bounty_detail(bounty_id, db: AsyncSession):
    result = await db.execute(
        select(Bounty, User.username)
        .join(User, User.id == Bounty.creator_id)
        .where(Bounty.id == bounty_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Bounty not found")
    return row[0], row[1]


async def list_open_bounties(db: AsyncSession):
    count_subquery = (
        select(
            BountySubmission.bounty_id,
            func.count(BountySubmission.id).label("submission_count"),
        )
        .group_by(BountySubmission.bounty_id)
        .subquery()
    )

    result = await db.execute(
        select(
            Bounty,
            User.username,
            func.coalesce(count_subquery.c.submission_count, 0),
        )
        .join(User, User.id == Bounty.creator_id)
        .outerjoin(count_subquery, count_subquery.c.bounty_id == Bounty.id)
        .where(Bounty.status == BountyStatus.OPEN)
        .order_by(Bounty.created_at.desc())
    )
    return result.all()


async def claim_daily_streak(user_id, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()
    if user.last_streak_date == today:
        raise HTTPException(status_code=400, detail="Daily streak already claimed today")

    await award_points(user_id, 10, "DAILY_STREAK", db)

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(last_streak_date=today),
    )

    await db.commit()
    await db.refresh(user)
    return user
