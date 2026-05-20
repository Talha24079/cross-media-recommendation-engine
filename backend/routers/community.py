import uuid
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db, get_mongodb
from core.security import get_current_user
from models.user import User
from schemas.community import CommentCreate, CommentResponse, ThreadCreate, ThreadResponse
from services import economy_service, faction_service, realtime_broadcast
from services.user_preferences_service import UserPreferencesService
from services.community_authors import (
    enrich_comments,
    enrich_single_comment,
    enrich_single_thread,
    enrich_threads,
)
from services.community_service import CommunityService

router = APIRouter(prefix="/community", tags=["community"])


def get_community_service(db: AsyncIOMotorDatabase = Depends(get_mongodb)) -> CommunityService:
    return CommunityService(db)


@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread: ThreadCreate,
    current_user: User = Depends(get_current_user),
    service: CommunityService = Depends(get_community_service),
    db: AsyncSession = Depends(get_db),
):
    result = await service.create_thread(
        author_id=str(current_user.id),
        title=thread.title,
        content=thread.content,
        media_id=str(thread.media_id) if thread.media_id else None,
        tags=thread.tags,
    )
    await economy_service.award_points(current_user.id, 3, "THREAD_CREATED", db)
    await db.commit()
    enriched = await enrich_single_thread(result, db)
    await realtime_broadcast.notify_threads_list()
    return enriched


@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(
    skip: int = 0,
    limit: int = 20,
    service: CommunityService = Depends(get_community_service),
    db: AsyncSession = Depends(get_db),
):
    rows = await service.get_threads(skip=skip, limit=limit)
    return await enrich_threads(rows, db)


@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    thread_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    service: CommunityService = Depends(get_community_service),
    db: AsyncSession = Depends(get_db),
):
    if not ObjectId.is_valid(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread_id format")

    result = await service.create_comment(
        thread_id=thread_id,
        author_id=str(current_user.id),
        content=comment.content,
        parent_id=comment.parent_id,
    )
    await economy_service.award_points(current_user.id, 2, "COMMENT_POSTED", db)
    await db.commit()
    enriched = await enrich_single_comment(result, db)
    await realtime_broadcast.notify_thread_comments(thread_id)
    return enriched


@router.get("/threads/{thread_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    thread_id: str,
    service: CommunityService = Depends(get_community_service),
    db: AsyncSession = Depends(get_db),
):
    if not ObjectId.is_valid(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread_id format")
    rows = await service.get_comments(thread_id=thread_id)
    return await enrich_comments(rows, db)


@router.get("/my-faction")
async def get_my_faction(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await faction_service.get_faction_info(current_user.id, db)


@router.post("/interact/{media_id}")
async def interact_with_media(
    media_id: uuid.UUID,
    favorite: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongodb),
):
    await faction_service.build_taste_profile(current_user.id, [str(media_id)], db)

    if favorite:
        preferences_service = UserPreferencesService(mongo_db)
        await preferences_service.add_favorite_from_media(
            str(current_user.id),
            str(media_id),
            db,
        )

    await economy_service.award_points(current_user.id, 1, "MEDIA_INTERACTION", db)
    await db.commit()

    message = "Interaction recorded. Taste profile updated. +1 point awarded."
    if favorite:
        message = "Saved to favorites and interaction recorded. +1 point awarded."

    return {"message": message}
