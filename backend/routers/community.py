from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_mongodb
from core.security import get_current_user
from models.user import User
from schemas.community import ThreadCreate, ThreadResponse, CommentCreate, CommentResponse
from services.community_service import CommunityService

router = APIRouter(prefix="/community", tags=["community"])

def get_community_service(db: AsyncIOMotorDatabase = Depends(get_mongodb)) -> CommunityService:
    return CommunityService(db)

@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread: ThreadCreate,
    current_user: User = Depends(get_current_user),
    service: CommunityService = Depends(get_community_service)
):
    return await service.create_thread(
        author_id=str(current_user.id),
        title=thread.title,
        content=thread.content,
        media_id=str(thread.media_id) if thread.media_id else None,
        tags=thread.tags
    )

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
    service: CommunityService = Depends(get_community_service)
):
    return await service.create_comment(
        thread_id=thread_id,
        author_id=str(current_user.id),
        content=comment.content,
        parent_id=comment.parent_id
    )

@router.get("/threads/{thread_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    thread_id: str,
    service: CommunityService = Depends(get_community_service)
):
    return await service.get_comments(thread_id=thread_id)
