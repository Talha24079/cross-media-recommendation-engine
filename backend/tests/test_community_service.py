from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from bson import ObjectId

from services.community_service import CommunityService


@pytest.mark.asyncio
async def test_create_thread_comment_and_list_round_trip(fake_mongo):
    service = CommunityService(fake_mongo)

    thread = await service.create_thread(author_id="user-1", title="Dune", content="Discussion", media_id="media-1", tags=["books"])
    assert thread["title"] == "Dune"

    comment = await service.create_comment(thread_id=thread["_id"], author_id="user-2", content="I agree")
    assert comment["content"] == "I agree"

    threads = await service.get_threads()
    comments = await service.get_comments(thread["_id"])

    assert threads[0]["_id"] == thread["_id"]
    assert comments[0]["_id"] == comment["_id"]


@pytest.mark.asyncio
async def test_get_threads_returns_newest_first(fake_mongo):
    service = CommunityService(fake_mongo)
    collection = fake_mongo.get_collection("forum_threads")

    old_thread = {
        "_id": ObjectId(),
        "title": "Old thread",
        "content": "Old",
        "author_id": "user-1",
        "media_id": None,
        "tags": [],
        "created_at": datetime.now(timezone.utc) - timedelta(days=1),
        "updated_at": datetime.now(timezone.utc) - timedelta(days=1),
    }
    new_thread = {
        "_id": ObjectId(),
        "title": "New thread",
        "content": "New",
        "author_id": "user-2",
        "media_id": None,
        "tags": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    collection.documents.extend([old_thread, new_thread])

    threads = await service.get_threads()

    assert [thread["title"] for thread in threads] == ["New thread", "Old thread"]
