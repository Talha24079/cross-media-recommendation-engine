from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from fastapi import HTTPException, status
from models.user import User
from models.bounty import Bounty, BountyStatus, CentralLedger
from datetime import date


async def get_balance(user_id, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def award_points(user_id, amount: int, transaction_type: str, db: AsyncSession, reference_id=None):
    """Award points to a user and log it in the central ledger. Must be called within a transaction."""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(reputation_points=User.reputation_points + amount)
    )

    ledger_entry = CentralLedger(
        user_id=user_id,
        amount=amount,
        transaction_type=transaction_type,
        reference_id=reference_id
    )
    db.add(ledger_entry)


async def deduct_points(user_id, amount: int, transaction_type: str, db: AsyncSession, reference_id=None):
    """Deduct points from a user. Raises 400 if insufficient balance."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.reputation_points < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Current: {user.reputation_points}, Required: {amount}"
        )

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(reputation_points=User.reputation_points - amount)
    )

    ledger_entry = CentralLedger(
        user_id=user_id,
        amount=-amount,
        transaction_type=transaction_type,
        reference_id=reference_id
    )
    db.add(ledger_entry)


async def create_bounty(creator_id, title: str, description: str, reward_amount: int, db: AsyncSession):
    """Create a bounty by deducting the reward from the creator's balance."""
    # Deduct points from creator (this validates balance)
    await deduct_points(creator_id, reward_amount, "BOUNTY_STAKE", db)

    bounty = Bounty(
        creator_id=creator_id,
        title=title,
        description=description,
        reward_amount=reward_amount,
        status=BountyStatus.OPEN
    )
    db.add(bounty)
    await db.commit()
    await db.refresh(bounty)
    return bounty


async def resolve_bounty(bounty_id, winner_id, creator_id, db: AsyncSession):
    """Resolve a bounty by awarding points to the winner. Only the creator can resolve it."""
    result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = result.scalar_one_or_none()

    if not bounty:
        raise HTTPException(status_code=404, detail="Bounty not found")
    if bounty.creator_id != creator_id:
        raise HTTPException(status_code=403, detail="Only the bounty creator can resolve it")
    if bounty.status != BountyStatus.OPEN:
        raise HTTPException(status_code=400, detail="Bounty is not open")

    # Award points to winner
    await award_points(winner_id, bounty.reward_amount, "BOUNTY_WON", db, reference_id=bounty.id)

    # Update bounty status
    await db.execute(
        update(Bounty)
        .where(Bounty.id == bounty_id)
        .values(status=BountyStatus.COMPLETED)
    )

    await db.commit()
    return bounty


async def claim_daily_streak(user_id, db: AsyncSession):
    """Award 10 points for daily login streak. Can only be claimed once per day."""
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
        .values(last_streak_date=today)
    )

    await db.commit()

    # Refresh to get the updated balance
    await db.refresh(user)
    return user
