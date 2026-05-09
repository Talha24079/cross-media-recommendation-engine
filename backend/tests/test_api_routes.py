from __future__ import annotations

import numpy as np
import pytest

from models.bounty import CentralLedger
from models.media import MediaItem
from services import economy_service, recommendation_service, faction_service


def _register(client, username: str, email: str, password: str):
    return client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )


def _login(client, username: str, password: str):
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
def test_health_auth_and_profile(api):
    client = api.client

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    weak = _register(client, "user_1", "user_1@example.com", "123")
    assert weak.status_code == 422

    bad_username = _register(client, "bad name", "user_2@example.com", "password1")
    assert bad_username.status_code == 422

    register = _register(client, "reader_1", "reader_1@example.com", "password1")
    assert register.status_code == 201

    duplicate = _register(client, "reader_1", "reader_1@example.com", "password1")
    assert duplicate.status_code == 400

    token = _login(client, "reader_1", "password1")
    profile = client.get("/auth/me", headers=_headers(token))
    assert profile.status_code == 200
    assert profile.json()["username"] == "reader_1"
    assert profile.json()["reputation_points"] == 100


@pytest.mark.integration
def test_recommendation_and_points_flow(api, monkeypatch):
    client = api.client
    session = api.session

    _register(client, "reader_2", "reader_2@example.com", "password1")
    token = _login(client, "reader_2", "password1")

    recommendation_service.embedding_matrix = np.empty((0, 384), dtype=np.float32)
    recommendation_service.metadata_list = []

    async def fake_award_points(user_id, amount, transaction_type, db, reference_id=None):
        user = db.get_user(user_id)
        user.reputation_points += amount
        db.add(CentralLedger(user_id=user.id, amount=amount, transaction_type=transaction_type, reference_id=reference_id))

    monkeypatch.setattr(economy_service, "award_points", fake_award_points)

    recommendation_service.model = type(
        "EmbeddingStub",
        (),
        {"encode": staticmethod(lambda text: np.array([1.0] + [0.0] * 383, dtype=np.float32))},
    )()

    add_media = client.post(
        "/recommendation/media",
        headers=_headers(token),
        json={"title": "Dune", "media_type": "book", "description": "Sci-fi epic"},
    )
    assert add_media.status_code == 201
    media_id = add_media.json()["id"]

    duplicate = client.post(
        "/recommendation/media",
        headers=_headers(token),
        json={"title": "Dune", "media_type": "book", "description": "Sci-fi epic"},
    )
    assert duplicate.status_code == 409

    recommendation_service.embedding_matrix = np.array(
        [
            [1.0] + [0.0] * 383,
            [0.2] + [0.0] * 383,
        ],
        dtype=np.float32,
    )
    recommendation_service.metadata_list = [
        {"id": media_id, "title": "Dune", "media_type": "book"},
        {"id": "other", "title": "Other", "media_type": "movie"},
    ]

    search = client.get("/recommendation/search?query=epic%20space%20adventure&top_k=1")
    assert search.status_code == 200
    assert search.json()[0]["title"] == "Dune"

    too_many = client.get("/recommendation/search?query=epic%20space%20adventure&top_k=100")
    assert too_many.status_code == 422

    profile = client.get("/auth/me", headers=_headers(token))
    assert profile.json()["reputation_points"] == 105


@pytest.mark.integration
def test_community_and_faction_flow(api, monkeypatch):
    client = api.client
    session = api.session

    _register(client, "reader_3", "reader_3@example.com", "password1")
    token = _login(client, "reader_3", "password1")

    media = MediaItem(title="Interstellar", type="movie")
    session.add(media)

    async def fake_award_points(user_id, amount, transaction_type, db, reference_id=None):
        user = db.get_user(user_id)
        user.reputation_points += amount
        db.add(CentralLedger(user_id=user.id, amount=amount, transaction_type=transaction_type, reference_id=reference_id))

    async def fake_build_taste_profile(*args, **kwargs):
        return None

    monkeypatch.setattr(economy_service, "award_points", fake_award_points)
    monkeypatch.setattr(faction_service, "build_taste_profile", fake_build_taste_profile)

    thread = client.post(
        "/community/threads",
        headers=_headers(token),
        json={"title": "Interstellar discussion", "content": "A great movie", "media_id": str(media.id), "tags": ["movies"]},
    )
    assert thread.status_code == 201
    thread_id = thread.json()["_id"]

    comment = client.post(
        f"/community/threads/{thread_id}/comments",
        headers=_headers(token),
        json={"content": "I agree"},
    )
    assert comment.status_code == 201

    thread_list = client.get("/community/threads")
    assert thread_list.status_code == 200
    assert thread_list.json()[0]["_id"] == thread_id

    comments = client.get(f"/community/threads/{thread_id}/comments")
    assert comments.status_code == 200
    assert comments.json()[0]["_id"] == comment.json()["_id"]

    interact = client.post(f"/community/interact/{media.id}", headers=_headers(token))
    assert interact.status_code == 200

    profile = client.get("/auth/me", headers=_headers(token))
    assert profile.json()["reputation_points"] == 106


@pytest.mark.integration
def test_route_guards(api):
    client = api.client

    _register(client, "reader_4", "reader_4@example.com", "password1")
    token = _login(client, "reader_4", "password1")

    invalid_bounty = client.post(
        "/economy/bounties/invalid-id-here/resolve",
        headers=_headers(token),
        json={"winner_id": str(api.session.users[0].id) if api.session.users else "00000000-0000-0000-0000-000000000000"},
    )
    assert invalid_bounty.status_code == 422

    invalid_thread = client.post(
        "/community/threads/invalid-id-here/comments",
        headers=_headers(token),
        json={"content": "I agree"},
    )
    assert invalid_thread.status_code == 400
