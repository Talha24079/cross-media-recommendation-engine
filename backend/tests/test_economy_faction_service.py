from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
import uuid

import numpy as np
import pytest
from fastapi import HTTPException

from models.bounty import BountyStatus
from models.media import MediaItem
from models.user import User
from services import economy_service, faction_service


@pytest.mark.asyncio
async def test_balance_points_and_streak_flows(fake_session):
    user = User(username="reader", email="reader@example.com", hashed_password="hash")
    fake_session.seed_user(user)

    balance = await economy_service.get_balance(user.id, fake_session)
    assert balance is user

    with pytest.raises(HTTPException, match="User not found"):
        await economy_service.get_balance(uuid.uuid4(), fake_session)

    await economy_service.award_points(user.id, 15, "BONUS", fake_session, reference_id=uuid.uuid4())
    assert user.reputation_points == 115
    assert fake_session.ledger_entries[-1].amount == 15

    await economy_service.deduct_points(user.id, 20, "SPEND", fake_session)
    assert user.reputation_points == 95
    assert fake_session.ledger_entries[-1].amount == -20

    with pytest.raises(HTTPException, match="Insufficient balance"):
        await economy_service.deduct_points(user.id, 500, "SPEND", fake_session)

    claimed = await economy_service.claim_daily_streak(user.id, fake_session)
    assert claimed.last_streak_date == date.today()
    assert claimed.reputation_points == 105

    with pytest.raises(HTTPException, match="Daily streak already claimed today"):
        await economy_service.claim_daily_streak(user.id, fake_session)


@pytest.mark.asyncio
async def test_economy_user_not_found_branches(fake_session):
    missing_user_id = uuid.uuid4()

    with pytest.raises(HTTPException, match="User not found"):
        await economy_service.deduct_points(missing_user_id, 10, "SPEND", fake_session)

    with pytest.raises(HTTPException, match="User not found"):
        await economy_service.claim_daily_streak(missing_user_id, fake_session)


@pytest.mark.asyncio
async def test_bounty_creation_resolution_and_guards(fake_session):
    creator = User(username="creator", email="creator@example.com", hashed_password="hash")
    winner = User(username="winner", email="winner@example.com", hashed_password="hash")
    other = User(username="other", email="other@example.com", hashed_password="hash")
    fake_session.seed_user(creator)
    fake_session.seed_user(winner)
    fake_session.seed_user(other)

    with pytest.raises(HTTPException, match="Insufficient balance"):
        await economy_service.create_bounty(creator.id, "Impossible", "Too costly", 500, fake_session)

    bounty = await economy_service.create_bounty(creator.id, "Find the book", "Need help", 25, fake_session)
    assert bounty.status == BountyStatus.OPEN
    assert creator.reputation_points == 75
    assert fake_session.ledger_entries[-1].amount == -25

    with pytest.raises(HTTPException, match="Bounty not found"):
        await economy_service.resolve_bounty(uuid.uuid4(), winner.id, creator.id, fake_session)

    with pytest.raises(HTTPException, match="Only the bounty creator can resolve it"):
        await economy_service.resolve_bounty(bounty.id, winner.id, other.id, fake_session)

    bounty.status = BountyStatus.COMPLETED
    with pytest.raises(HTTPException, match="Bounty is not open"):
        await economy_service.resolve_bounty(bounty.id, winner.id, creator.id, fake_session)

    bounty.status = BountyStatus.OPEN
    resolved = await economy_service.resolve_bounty(bounty.id, winner.id, creator.id, fake_session)
    assert resolved.status == BountyStatus.COMPLETED
    assert winner.reputation_points == 125
    assert fake_session.ledger_entries[-1].amount == 25


@pytest.mark.asyncio
async def test_build_taste_profile_and_faction_info(fake_session):
    user = User(username="viewer", email="viewer@example.com", hashed_password="hash")
    other_user = User(username="ally", email="ally@example.com", hashed_password="hash")
    user.faction_id = 2
    other_user.faction_id = 2
    fake_session.seed_user(user)
    fake_session.seed_user(other_user)

    first = MediaItem(title="Dune", type="book", embedding=np.array([1.0, 0.0, 0.0], dtype=np.float32).tolist())
    second = MediaItem(title="Interstellar", type="movie", embedding=np.array([0.0, 1.0, 0.0], dtype=np.float32).tolist())
    fake_session.seed_media(first)
    fake_session.seed_media(second)

    await faction_service.build_taste_profile(user.id, [], fake_session)
    assert user.taste_vector is None

    await faction_service.build_taste_profile(user.id, [first.id, second.id], fake_session)
    assert pytest.approx(user.taste_vector[0], rel=1e-6) == 0.5
    assert pytest.approx(user.taste_vector[1], rel=1e-6) == 0.5

    info = await faction_service.get_faction_info(user.id, fake_session)
    assert info["faction_id"] == 2
    assert info["faction_name"] == "The Architects"
    assert len(info["faction_members"]) == 2

    unassigned_user = User(username="newbie", email="newbie@example.com", hashed_password="hash")
    fake_session.seed_user(unassigned_user)
    unassigned = await faction_service.get_faction_info(unassigned_user.id, fake_session)
    assert unassigned["faction_name"] == "Unassigned"


@pytest.mark.asyncio
async def test_faction_clustering_paths(monkeypatch, fake_session):
    first = User(username="a", email="a@example.com", hashed_password="hash")
    second = User(username="b", email="b@example.com", hashed_password="hash")
    first.taste_vector = [1.0, 0.0, 0.0]
    second.taste_vector = [0.0, 1.0, 0.0]
    fake_session.seed_user(first)
    fake_session.seed_user(second)

    @asynccontextmanager
    async def fake_session_factory():
        yield fake_session

    monkeypatch.setattr(faction_service, "AsyncSessionLocal", fake_session_factory)

    await faction_service.run_faction_clustering()
    assert first.faction_id is not None
    assert second.faction_id is not None
    assert first.faction_id in range(5)
    assert second.faction_id in range(5)

    lone_session = type(fake_session)()
    lone_user = User(username="solo", email="solo@example.com", hashed_password="hash")
    lone_user.taste_vector = [1.0, 0.0, 0.0]
    lone_session.seed_user(lone_user)

    @asynccontextmanager
    async def lone_session_factory():
        yield lone_session

    monkeypatch.setattr(faction_service, "AsyncSessionLocal", lone_session_factory)
    await faction_service.run_faction_clustering()
    assert lone_user.faction_id is None
