from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_mongodb, get_db
from core.security import get_current_user
from models.user import User
from schemas.community import ThreadCreate, ThreadResponse, CommentCreate, CommentResponse
from services.community_service import CommunityService
from services import faction_service, economy_service
import uuid
from bson.errors import InvalidId
from bson.objectid import ObjectId

router = APIRouter(prefix="/community", tags=["community"])

def get_community_service(db: AsyncIOMotorDatabase = Depends(get_mongodb)) -> CommunityService:
    return CommunityService(db)

@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread: ThreadCreate,
    current_user: User = Depends(get_current_user),
    service: CommunityService = Depends(get_community_service),
    db: AsyncSession = Depends(get_db)
):
    result = await service.create_thread(
        author_id=str(current_user.id),
        title=thread.title,
        content=thread.content,
        media_id=str(thread.media_id) if thread.media_id else None,
        tags=thread.tags
    )
    # Gamification: Award 3 points for creating a thread
    await economy_service.award_points(current_user.id, 3, "THREAD_CREATED", db)
    await db.commit()
    return result

@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(
    skip: int = 0,
    limit: int = 20,
    service: CommunityService = Depends(get_community_service)
):
    return await service.get_threads(skip=skip, limit=limit)

@router.post("/threads/{thread_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    thread_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    service: CommunityService = Depends(get_community_service),
    db: AsyncSession = Depends(get_db)
):
    if not ObjectId.is_valid(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread_id format")

    result = await service.create_comment(
        thread_id=thread_id,
        author_id=str(current_user.id),
        content=comment.content,
        parent_id=comment.parent_id
    )
    # Gamification: Award 2 points for commenting
    await economy_service.award_points(current_user.id, 2, "COMMENT_POSTED", db)
    await db.commit()
    return result

@router.get("/threads/{thread_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    thread_id: str,
    service: CommunityService = Depends(get_community_service)
):
    if not ObjectId.is_valid(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread_id format")
    return await service.get_comments(thread_id=thread_id)


@router.get("/my-faction")
async def get_my_faction(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns the current user's faction and fellow faction members."""
    return await faction_service.get_faction_info(current_user.id, db)


@router.post("/interact/{media_id}")
async def interact_with_media(
    media_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a user's interaction with a media item.
    Updates their taste profile by averaging embeddings of all interacted media.
    """
    await faction_service.build_taste_profile(current_user.id, [str(media_id)], db)
    
    # Gamification: Award 1 point for media interaction
    await economy_service.award_points(current_user.id, 1, "MEDIA_INTERACTION", db)
    await db.commit()
    
    return {"message": "Interaction recorded. Taste profile updated. +1 point awarded."}
