from __future__ import annotations

from datetime import timedelta

import pytest
from pydantic import ValidationError

from core.security import create_access_token, get_password_hash, verify_password, verify_token
from schemas.community import CommentCreate, ThreadCreate
from schemas.economy import BountyCreate
from schemas.recommendation import MediaItemCreate, MediaTypeEnum
from schemas.user import UserCreate, UserLogin


def test_user_create_validation_rules():
    with pytest.raises(ValidationError):
        UserCreate(username="bad name", email="user@example.com", password="password1")

    with pytest.raises(ValidationError):
        UserCreate(username="valid_name", email="user@example.com", password="abcdef")

    user = UserCreate(username="valid_name", email="user@example.com", password="password1")
    assert user.username == "valid_name"


def test_login_schema_accepts_credentials():
    login = UserLogin(username="reader_1", password="password1")
    assert login.username == "reader_1"


def test_media_and_economy_schema_limits():
    media = MediaItemCreate(title="Dune", media_type=MediaTypeEnum.book, description="Sci-fi")
    assert media.media_type == MediaTypeEnum.book

    bounty = BountyCreate(title="Find the best book", description="Need a recommendation", reward_amount=50)
    assert bounty.reward_amount == 50

    with pytest.raises(ValidationError):
        BountyCreate(title="Bad bounty", description="Too small reward", reward_amount=0)

    thread = ThreadCreate(title="Discussion", content="Let's talk", media_id=None, tags=["books"])
    assert thread.tags == ["books"]

    comment = CommentCreate(content="I agree")
    assert comment.content == "I agree"


def test_token_and_password_helpers_round_trip():
    password = "password1"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)

    token = create_access_token("user-123", expires_delta=timedelta(minutes=5))
    assert verify_token(token) == "user-123"
