from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.media import MediaItem
from schemas.recommendation import MediaItemCreate, MediaItemResponse, RecommendationResponse
from services import recommendation_service, economy_service

router = APIRouter(prefix="/recommendation", tags=["recommendation"])

@router.post("/media", response_model=MediaItemResponse, status_code=status.HTTP_201_CREATED)
async def add_media_item(
    item: MediaItemCreate, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if recommendation_service.model is None:
        recommendation_service.init_model()
        
    # Content Moderation: Duplicate detection
    # Search for similar items first
    try:
        search_text = f"{item.title} {item.description or ''}"
        similar_items = recommendation_service.search_similar(search_text, top_k=1)
        if similar_items and similar_items[0]["score"] > 0.90:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Similar media item already exists: '{similar_items[0]['title']}' (Score: {similar_items[0]['score']:.2f})"
            )
    except HTTPException:
        raise
    except Exception as e:
        # If cache is empty or other non-fatal error, continue
        pass

    # Generate embedding
    try:
        embedding = recommendation_service.model.encode(f"{item.title} {item.description or ''}")
        # Convert to list for pgvector compatibility in asyncpg
        embedding_list = embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")

    db_item = MediaItem(
        title=item.title,
        type=item.media_type,
        description=item.description,
        embedding=embedding_list
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    # Update cache
    recommendation_service.add_to_cache(db_item, embedding)
    
    # Gamification: Award points for adding media
    await economy_service.award_points(current_user.id, 5, "MEDIA_CONTRIBUTION", db, reference_id=db_item.id)
    await db.commit()

    return MediaItemResponse(
        id=db_item.id,
        title=db_item.title,
        media_type=db_item.type,
        description=db_item.description
    )

@router.get("/search", response_model=List[RecommendationResponse])
async def recommend(
    query: str = Query(..., min_length=1, max_length=500), 
    top_k: int = Query(10, ge=1, le=50)
):
    if recommendation_service.model is None:
        recommendation_service.init_model()
        
    try:
        results = recommendation_service.search_similar(query, top_k=top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
